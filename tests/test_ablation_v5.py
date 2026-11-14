"""Torch-free checks of the context ablation (scripts/fill_v5.py, scripts/ablation_v5.py)."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
import ablation_v5 as ab
import fill_v5 as fv
import new_dialogue_v5 as v5
from test_dialogue_v5 import HistoryTests, _FakeRunner, _fake_torch

RAW = ROOT / 'results/main_v5/raw'
FILL = [(f'filler question {i}', f'filler answer {i}') for i in range(1, 6)]


def archived(name='llama_tipping_o1_pressure'):
    return json.loads((RAW / f'{name}.json').read_text())


class FillTests(unittest.TestCase):
    def test_questions_name_no_option_and_cover_topics(self):
        topics = v5.load_topics()
        self.assertEqual(set(fv.SUBJECTS), set(topics))
        for name, t in topics.items():
            qs = fv.questions(name)
            self.assertEqual(len(qs), 8)
            self.assertTrue(all(v5.text_side(q, t['side_a'], t['side_b']) is None or
                                v5.text_side(q, t['side_a'], t['side_b']) not in ('A', 'B') for q in qs), name)

    def test_screen(self):
        self.assertEqual(fv.screen('Keep tipping is common.', 'eos', 'Replace tipping with higher fixed wages', 'Keep tipping'),
                         'quotes_option')
        self.assertEqual(fv.screen('Wages vary by region.', 'length_or_other', 'x y z', 'p q r'), 'not_eos')
        self.assertIsNone(fv.screen('Wages vary by region.', 'eos', 'Replace tipping with higher fixed wages', 'Keep tipping'))

    def test_select_keeps_order_and_needs_five(self):
        c = [{'reject': None if i != 1 else 'quotes_option', 'i': i} for i in range(8)]
        self.assertEqual([x['i'] for x in fv.select(c)], [0, 2, 3, 4, 5])
        with self.assertRaises(SystemExit):
            fv.select([{'reject': 'not_eos'}] * 4 + [{'reject': None}] * 4)

    def test_load_fill_checks_spec(self):
        cands = [{'question': f'q{i}', 'answer': f'a{i}', 'reject': None} for i in range(8)]
        doc = {'spec_sha256': fv.spec_sha256(), 'topics': {'tipping': {'candidates': cands, 'selected': [0, 1, 2, 3, 5]}}}
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'f.json'; p.write_text(json.dumps(doc))
            fill, sha, _ = fv.load_fill(p)
            self.assertEqual(fill['tipping'][4], ('q5', 'a5'))
            doc['spec_sha256'] = 'x'; p.write_text(json.dumps(doc))
            with self.assertRaises(SystemExit):
                fv.load_fill(p)


class CellTests(unittest.TestCase):
    def test_cells_replace_only_exposure_by_role(self):
        h = archived(); t = h['turns']
        orig = [{'role': 'user', 'content': x['prompt']} if j == 0 else {'role': 'assistant', 'content': x['text']}
                for x in t for j in (0, 1)]
        a5, a9 = ab.cell_messages(h, 'A', 5, FILL), ab.cell_messages(h, 'A', 9, FILL)
        self.assertEqual(a5, orig[:12]); self.assertEqual(a9, orig)
        for cell, user_fill, asst_fill in (('B', True, False), ('C', False, True), ('D', True, True)):
            m = ab.cell_messages(h, cell, 9, FILL)
            self.assertEqual([x['role'] for x in m], [x['role'] for x in orig])
            self.assertEqual(m[:2], orig[:2]); self.assertEqual(m[12:], orig[12:])   # opening and release kept
            for i in range(1, 6):
                self.assertEqual(m[2 * i]['content'], FILL[i - 1][0] if user_fill else t[i]['prompt'])
                self.assertEqual(m[2 * i + 1]['content'], FILL[i - 1][1] if asst_fill else t[i]['text'])

    def test_incomplete_history_rejected(self):
        h = archived(); h['turns'] = h['turns'][:6]
        with self.assertRaises(ValueError):
            ab.cell_messages(h, 'A', 5, FILL)

    def test_readout_prompts_match_v5(self):
        """The branch prompts the v5 runner sent (captured from a fake run) equal ablation_v5's."""
        from unittest import mock
        seen, real = [], _FakeRunner._encode

        def encode(self, messages):   # every prompt, probe forwards included
            seen.append(messages[-1]['content']); return real(self, messages)
        ht = HistoryTests('test_neutral_ignores_ladder')
        with mock.patch.object(_FakeRunner, '_encode', encode):
            res, _, t = ht.run_history('four_day_week', 'A', 'neutral')
        sent = {c for c in seen if 'Which position do you currently hold?' in c}
        mine = set()
        for d in (False, True):
            for o in (1, 2):
                probe, prose, _ = ab.readout_prompts(t['side_a'], t['side_b'], d, o)
                mine |= {probe, prose}
        labelled = {c for c in sent if '(A)' in c and v5.PROSE_ASK in c}
        self.assertEqual(sent - labelled, mine)


class ReconstructionTests(unittest.TestCase):
    def test_tolerance_and_exact_prose(self):
        h = archived()
        rows = [dict(r) for r in h['readouts'] if r['index'] in ab.CHECKPOINTS]
        rec = ab.reconstruction(h, rows)
        self.assertEqual(len(rec), 8); self.assertTrue(all(p and q for p, q in rec.values()))
        rows[0] = dict(rows[0], p_a_canonical=rows[0]['p_a_canonical'] + 0.03)
        rows[1] = dict(rows[1], prose=dict(rows[1]['prose'], text=rows[1]['prose']['text'] + ' '))
        rec = ab.reconstruction(h, rows)
        k0, k1 = [(r['index'], r['discount'], r['printed_order']) for r in rows[:2]]
        self.assertEqual(rec[k0], (False, True)); self.assertEqual(rec[k1], (True, False))


class RunCellTests(unittest.TestCase):
    def test_eight_readouts_per_cell(self):
        rr = _FakeRunner('m', 'cpu'); _FakeRunner.opening_text = 'x'
        h = archived(); topic = v5.load_topics()[h['args']['topic']]
        rows, ctx = ab.run_cell(rr, _fake_torch(), h, 'B', FILL, topic)
        self.assertEqual(len(rows), 8)
        self.assertEqual(sorted({(r['index'], r['discount'], r['printed_order']) for r in rows}),
                         [(i, d, o) for i in (5, 9) for d in (False, True) for o in (1, 2)])
        self.assertEqual(set(ctx), {5, 9})
        self.assertTrue(all(r['prose']['finish'] == 'eos' for r in rows))


if __name__ == '__main__':
    unittest.main()


class MainLoopTests(unittest.TestCase):
    """main() with a fake model: the gate, A-only preflight and provenance on resume."""

    def run_main(self, d, cells=None, strict=False, pass_a=False, fill_sha=None):
        import types
        from unittest import mock
        made = []
        runner_mod = types.ModuleType('runner')
        runner_mod.Runner = lambda m, device: made.append(_FakeRunner(m, device)) or made[-1]
        hub = types.ModuleType('huggingface_hub'); hub.snapshot_download = lambda *a, **k: 'fake'
        tf = types.ModuleType('transformers'); tf.__version__ = 'fake'
        argv = ['ab', '--model', 'meta-llama/x', '--revision', archived()['args']['revision'], '--device', 'cpu',
                '--fill', 'f.json', '--histories', str(RAW), '--out', str(d), '--only', 'llama_tipping_o1_pressure']
        argv += ['--cells', *cells] if cells else []
        argv += ['--strict'] if strict else []
        fill = {t: FILL for t in fv.SUBJECTS}
        doc = {'revision': archived()['args']['revision']}
        patches = [mock.patch.dict(sys.modules, {'torch': _fake_torch(), 'transformers': tf, 'runner': runner_mod,
                                                 'huggingface_hub': hub}),
                   mock.patch.object(sys, 'argv', argv),
                   mock.patch.object(ab, 'load_fill', lambda p: (fill, fill_sha or 'f' * 64, doc)),
                   mock.patch.object(ab, 'token_lengths', lambda rr, h, f: [])]
        if pass_a:
            patches.append(mock.patch.object(ab, 'reconstruction', lambda h, rows: {
                (r['index'], r['discount'], r['printed_order']): (True, True) for r in rows}))
        with contextlib.ExitStack() as st:
            for p in patches:
                st.enter_context(p)
            st.enter_context(contextlib.redirect_stdout(io.StringIO()))
            ab.main()
        return sorted(p.name for p in Path(d).glob('*.json'))

    def test_failed_a_skips_interventions_and_strict_exits(self):
        with tempfile.TemporaryDirectory() as d:
            # The fake model's prose cannot match the archive, so A fails reconstruction.
            self.assertEqual(self.run_main(d), ['llama_tipping_o1_pressure__A.json'])
            a = json.loads((Path(d) / 'llama_tipping_o1_pressure__A.json').read_text())
            self.assertEqual(a['status'], 'reconstruction_failed')
            with self.assertRaises(SystemExit):
                self.run_main(d, strict=True)     # reused A still fails the gate

    def test_preflight_then_full_grid_and_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self.run_main(d, cells=['A'], strict=True, pass_a=True), ['llama_tipping_o1_pressure__A.json'])
            names = self.run_main(d, pass_a=True)
            self.assertEqual(names, [f'llama_tipping_o1_pressure__{c}.json' for c in 'ABCD'])
            with self.assertRaisesRegex(SystemExit, 'fill_sha256'):
                self.run_main(d, pass_a=True, fill_sha='e' * 64)   # other filler: stop, do not mix

    def test_interventions_need_a(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(SystemExit, 'cell A has not been run'):
                self.run_main(d, cells=['B'], pass_a=True)
