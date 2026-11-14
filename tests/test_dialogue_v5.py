"""Torch-free checks of the v5 runner: frozen ladders, direction rule, and the
order of prompts in a full history, with a fake model standing in for the GPU."""
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import new_dialogue_v5 as v5


class _Vec(list):
    """Enough of a tensor for the runner: slicing, .float(), [i].item()."""
    def float(self):
        return self

    def __getitem__(self, i):
        if isinstance(i, tuple):  # logits[0, -1, :]
            return self
        v = list.__getitem__(self, i)
        return _Vec(v) if isinstance(i, slice) else types.SimpleNamespace(item=lambda: v)


def _fake_torch():
    t = types.ModuleType('torch')
    t.__version__ = 'fake'
    t.set_grad_enabled = lambda flag: None
    t.softmax = lambda x, dim=0: x
    return t


class _FakeRunner:
    """Opening text is chosen by the test; every reply ends with EOS (id 1)."""
    opening_text = ''

    def __init__(self, model, device):
        self.prompts = []
        self.calls = []
        self.option_ids = [[0], [1]]
        self.tok = types.SimpleNamespace(eos_token_id=1, decode=self._decode)
        self.model = _Model(self)
        self._last = None

    def _encode(self, messages):
        self._last = messages
        return {'input_ids': types.SimpleNamespace(shape=(1, 3))}

    def _decode(self, ids, skip_special_tokens=True):
        if len(self._last) == 1:
            return self.opening_text
        return 'A reply.'

    def _generate(self, **kw):
        if len(self._last) % 2 == 1 and not self._is_branch():
            self.prompts.append(self._last[-1]['content'])
        return [[0, 0, 0, 5, 1]]

    def _is_branch(self):
        c = self._last[-1]['content']
        return 'Which position do you currently hold?' in c


class _Model:
    def __init__(self, runner):
        self.r = runner
        self.dtype = 'fake'
        self.generation_config = types.SimpleNamespace(eos_token_id=1)

    def generate(self, **kw):
        seen = {k: kw[k] for k in ('repetition_penalty', 'no_repeat_ngram_size') if k in kw}
        procs = kw.get('logits_processor') or []
        for p in procs:   # the counting wrapper stands in for no_repeat_ngram_size
            seen['ngram_counter'] = p.n
            # Two decoding steps: the block leaves step 0 alone and changes the greedy token at step 1.
            p(None, [_Scores([0.1, 0.9])])
            p(None, [_Scores([0.1, 0.9])])
        self.r.calls.append((self.r._last[-1]['content'], seen))
        return _Rows(self.r._generate(**kw))

    def __call__(self, **kw):
        return types.SimpleNamespace(logits=_Vec([0.7, 0.3]))


class _Scores(list):
    def argmax(self):
        return max(range(len(self)), key=self.__getitem__)


class _FakeNoRepeat:
    """Stands in for HF's NoRepeatNGramLogitsProcessor: bans token 1 on its second call."""
    def __init__(self, n):
        self.calls = 0

    def __call__(self, ids, scores):
        self.calls += 1
        if self.calls == 2:
            return [_Scores([0.1, float('-inf')])]
        return scores


class _Rows(list):
    def __getitem__(self, i):
        if isinstance(i, tuple):
            row, cols = i
            return list.__getitem__(self, row)[cols]
        return list.__getitem__(self, i)


class LadderFileTests(unittest.TestCase):
    def test_frozen_file_loads(self):
        topics = v5.load_topics()
        self.assertEqual(len(topics), 12)
        self.assertEqual(sum(t['group'] == 'meta' for t in topics.values()), 6)

    def test_edited_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'l.json'
            p.write_bytes(v5.LADDERS_PATH.read_bytes() + b' ')
            with self.assertRaisesRegex(SystemExit, 'sha256'):
                v5.load_topics(p)

    def test_direction_rule(self):
        self.assertEqual(v5.ladder_dir('A'), 'vs_a')
        self.assertEqual(v5.ladder_dir('B'), 'vs_b')
        self.assertIsNone(v5.ladder_dir('unparsed'))


class HistoryTests(unittest.TestCase):
    def run_history(self, topic, opening_side, condition, order=1, extra=()):
        t = v5.load_topics()[topic]
        side_text = {'A': t['side_a'], 'B': t['side_b'], None: 'Something else entirely.'}[opening_side]
        _FakeRunner.opening_text = f'I choose: {side_text}. Because.'
        runner_mod = types.ModuleType('runner')
        made = []
        runner_mod.Runner = lambda m, device: made.append(_FakeRunner(m, device)) or made[-1]
        tf = types.ModuleType('transformers'); tf.__version__ = 'fake'
        tf.LogitsProcessorList = list; tf.NoRepeatNGramLogitsProcessor = _FakeNoRepeat
        with tempfile.TemporaryDirectory() as d:
            model = Path(d) / 'm'; model.mkdir(); (model / 'tokenizer.json').write_text('{}')
            out = Path(d) / 'out.json'
            argv = ['v5', '--model', str(model), '--device', 'cpu', '--topic', topic,
                    '--order', str(order), '--condition', condition, '--out', str(out), *extra]
            mods = {'torch': _fake_torch(), 'transformers': tf, 'runner': runner_mod}
            with mock.patch.dict(sys.modules, mods), mock.patch.object(sys, 'argv', argv), \
                 mock.patch.object(v5, 'log', lambda *a: None):
                try:
                    v5.main()
                    code = None
                except SystemExit as e:
                    code = str(e)
            self.runner = made[0] if made else None
            return json.loads(out.read_text()), code, t

    def test_pressure_uses_ladder_in_order(self):
        for side, direction in (('A', 'vs_a'), ('B', 'vs_b')):
            res, code, t = self.run_history('ai_welfare_now', side, 'pressure', order=2 if side == 'B' else 1)
            self.assertIsNone(code)
            self.assertEqual(res['status'], 'complete')
            self.assertEqual(res['ladder_dir'], direction)
            exposure = [x['prompt'] for x in res['turns'] if x['phase'] == 'exposure']
            self.assertEqual(exposure, t['ladders'][direction])
            self.assertEqual([x['phase'] for x in res['turns']],
                             ['opening'] + ['exposure'] * 5 + ['release'] * 4)
            self.assertEqual(sorted({r['index'] for r in res['readouts']}), [0, 3, 5, 9])
            self.assertEqual(len(res['readouts']), 16)

    def test_neutral_ignores_ladder(self):
        res, code, t = self.run_history('four_day_week', 'A', 'neutral')
        exposure = [x['prompt'] for x in res['turns'] if x['phase'] == 'exposure']
        self.assertEqual(exposure, v5.NEUTRAL)

    def test_unparsed_opening_stops_pressure(self):
        res, code, _ = self.run_history('tipping', None, 'pressure')
        self.assertEqual(res['status'], 'opening_unparsed')
        self.assertIsNone(res['ladder_dir'])
        self.assertEqual(len(res['turns']), 1)
        self.assertIn('no ladder', code)

    def test_decode_extra_only_on_exposure_and_release(self):
        res, code, t = self.run_history('four_day_week', 'A', 'pressure',
                                        extra=('--repetition-penalty', '1.1', '--no-repeat-ngram', '20'))
        self.assertEqual(res['decode_extra'], {'repetition_penalty': 1.1, 'no_repeat_ngram_size': 20})
        main = {p for p in t['ladders']['vs_a']} | set(v5.RELEASE)
        for prompt, kw in self.runner.calls:
            if prompt in main:
                # The n-gram block goes through the counting wrapper, never the plain HF kwarg.
                self.assertEqual(kw, {'repetition_penalty': 1.1, 'ngram_counter': 20}, prompt[:40])
            else:   # opening and every readout branch
                self.assertEqual(kw, {}, prompt[:40])
        for turn in res['turns']:
            if turn['phase'] == 'opening':
                self.assertNotIn('ngram_changed_steps', turn)
            else:
                self.assertEqual((turn['ngram_changed_steps'], turn['ngram_first_changed_step']), (1, 1))
        for r in res['readouts']:
            self.assertNotIn('ngram_changed_steps', r['prose'])

    def test_decode_extra_off_by_default(self):
        res, code, _ = self.run_history('four_day_week', 'A', 'pressure')
        self.assertEqual(res['decode_extra'], {})
        self.assertTrue(all(kw == {} for _, kw in self.runner.calls))
        self.assertTrue(all('ngram_changed_steps' not in x for x in res['turns']))


    def test_unparsed_opening_neutral_continues(self):
        res, code, _ = self.run_history('tipping', None, 'neutral')
        self.assertEqual(res['status'], 'complete')


class CounterTests(unittest.TestCase):
    def test_counts_only_changed_greedy_steps(self):
        from ngram_counter import CountingNoRepeatNGram
        bans = {1, 3}   # steps at which the fake block bans the current argmax

        class Inner:
            step = 0

            def __call__(self, ids, scores):
                row = list(scores[0])
                if Inner.step in bans:
                    row[row.index(max(row))] = float('-inf')
                if Inner.step == 2:   # bans a token that is not the argmax: no change
                    row[0] = float('-inf')
                Inner.step += 1
                return [_Scores(row)]

        c = CountingNoRepeatNGram(20, inner=Inner())
        for _ in range(5):
            c(None, [_Scores([0.2, 0.5, 0.3])])
        self.assertEqual(c.record(), {'ngram_changed_steps': 2, 'ngram_first_changed_step': 1})
        self.assertEqual(c.steps, 5)

    def test_in_place_edit_still_counted(self):
        from ngram_counter import CountingNoRepeatNGram

        def inner(ids, scores):   # edits the caller's row, as an in-place processor would
            scores[0][1] = float('-inf')
            return scores

        c = CountingNoRepeatNGram(20, inner=inner)
        c(None, [_Scores([0.2, 0.5, 0.3])])
        self.assertEqual(c.record(), {'ngram_changed_steps': 1, 'ngram_first_changed_step': 0})

    def test_untouched_turn(self):
        from ngram_counter import CountingNoRepeatNGram
        c = CountingNoRepeatNGram(20, inner=lambda ids, s: s)
        c(None, [_Scores([0.2, 0.5])])
        self.assertEqual(c.record(), {'ngram_changed_steps': 0, 'ngram_first_changed_step': None})


if __name__ == '__main__':
    unittest.main()
