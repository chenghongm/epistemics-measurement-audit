"""Torch-free checks of scripts/reread_old_ablation.py against the archived old ablation inputs."""
import ast
import importlib
import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'vendor/digital_mind'))
import reread_old_ablation as ro

DATA = ROOT / 'data/external/digital-mind'


def fake_runner():
    """The template constants of the vendored runner.py, without importing torch."""
    m = types.ModuleType('runner')
    tree = ast.parse((ROOT / 'vendor/digital_mind/runner.py').read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and getattr(node.targets[0], 'id', '') in (
                'RELEASE_TEMPLATES', 'DISTRACTOR_TEMPLATES'):
            setattr(m, node.targets[0].id, ast.literal_eval(node.value))
    m.NEUTRAL_TEMPLATES = m.RELEASE_TEMPLATES
    m.Runner = object; m.ProbeMassError = Exception; m.MIN_PROBE_MASS = 0.5
    return m


def load_ca():
    with mock.patch.dict(sys.modules, {'runner': fake_runner()}):
        sys.modules.pop('context_ablation', None)
        return importlib.import_module('context_ablation')


@unittest.skipUnless((DATA / 'topics_6x6.json').exists(), 'needs data/external (provenance/reread_sources.json)')
class RereadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.CA = load_ca()
        cls.sets = {s: ro.load_set(DATA, s) for s in ro.SETS}

    def test_sets_and_checkpoints(self):
        for s, (recs, old, fills, subjects, hashes) in self.sets.items():
            self.assertEqual(len(recs), 36, s); self.assertEqual(len(old), 144, s)
            self.assertEqual({r['condition'] for r in recs.values()},
                             {'pressure_release', 'pressure_switch', 'pressure_sustained'})
            for rec in recs.values():
                ck = ro.checkpoints(rec)
                self.assertEqual(list(ck), ['end_pressure', 'release_4', 'release_8', 'release_12'])
                self.assertEqual(ck['release_12'], len(rec['turns']) - 1)
                for c in ro.CELLS:   # the old cell files hold a reading at every checkpoint
                    rows = {r['turn_idx']: r for r in old[(rec['conv_id'], c)]['rows']}
                    for idx in ck.values():
                        self.assertIsNotNone(rows[idx]['p_a']); self.assertEqual(len(rows[idx]['p_orders']), 2)

    def test_replacement_counts_match_old_ablation(self):
        """The rebuilt contexts replace exactly the turns the old ablation replaced, in every cell."""
        n = 0
        for s, (recs, old, fills, subjects, _) in self.sets.items():
            for conv, rec in recs.items():
                press = self.CA.pressure_turn_idx(rec, subjects[rec['topic']])
                for cell in ro.CELLS:
                    _, notes = self.CA.stitch(rec, fills[self.CA.fill_id(rec)], cell, 'replace', len, press)
                    self.assertEqual(notes['replaced'], old[(conv, cell)]['notes']['replaced'], (conv, cell))
                    self.assertEqual(old[(conv, cell)]['fill_id'], self.CA.fill_id(rec))
                    n += 1
        self.assertEqual(n, 288)

    def test_cells_by_role(self):
        recs, old, fills, subjects, _ = self.sets['repl_b1']
        rec = recs['pressure_release__000__o1']
        ctx = ro.contexts(self.CA, rec, fills[self.CA.fill_id(rec)], subjects, len)
        idx = ro.checkpoints(rec)['release_12']
        a, b, c, d = (ctx[x][idx] for x in ro.CELLS)
        orig = [m for t in rec['turns'] for m in ({'role': 'user', 'content': t['user_text']},
                                                  {'role': 'assistant', 'content': t['model_text']})]
        self.assertEqual(a, orig)
        press = sorted(self.CA.pressure_turn_idx(rec, subjects[rec['topic']]))
        for i, t in enumerate(rec['turns']):
            u, m = 2 * i, 2 * i + 1
            changed = t['turn_idx'] in press
            self.assertEqual(b[u] != orig[u], changed); self.assertEqual(b[m], orig[m])
            self.assertEqual(c[u], orig[u]); self.assertEqual(c[m] != orig[m], changed)
            self.assertEqual(d[u] != orig[u], changed); self.assertEqual(d[m] != orig[m], changed)

    def test_sustained_replaces_release_labelled_pushback(self):
        recs, old, fills, subjects, _ = self.sets['repl_b1']
        rec = next(r for r in recs.values() if r['condition'] == 'pressure_sustained')
        press = self.CA.pressure_turn_idx(rec, subjects[rec['topic']])
        self.assertEqual(len(press), len(rec['turns']) - 1)   # everything after the opening is pressure by content

    def test_gate_check(self):
        old = {'rows': [{'turn_idx': 3, 'p_a': 0.40, 'p_orders': [0.3, 0.5]}, {'turn_idx': 4, 'p_a': None, 'p_orders': None}]}
        self.assertEqual(ro.gate_check(old, 3, 0.41, [0.31, 0.51]), (True, 0.01))
        self.assertFalse(ro.gate_check(old, 3, 0.40, [0.33, 0.5])[0])
        self.assertEqual(ro.gate_check(old, 4, 0.4, [0.4, 0.4]), (False, 'no_old_reading'))
        self.assertEqual(ro.gate_check(old, 9, 0.4, [0.4, 0.4]), (False, 'no_old_reading'))

    def test_system_turns(self):
        self.assertIsNone(self.CA.run_system(str(DATA / 'runs/repl_b1')))
        self.assertTrue(self.CA.run_system(str(DATA / 'runs/qwen_6x6')).startswith('Cutting Knowledge Date'))


if __name__ == '__main__':
    unittest.main()


class GateCompletenessTests(unittest.TestCase):
    def test_exact_four_cells(self):
        row = lambda c, ok=True: {'checkpoint': 'release_4', 'cell': c, 'ok': ok}
        self.assertTrue(ro.gate_passed({'rows': [row(c) for c in 'ABCD']}, 'release_4'))
        self.assertFalse(ro.gate_passed({'rows': [row(c) for c in 'ABC']}, 'release_4'))          # missing D
        self.assertFalse(ro.gate_passed({'rows': [row(c) for c in 'ABCDD']}, 'release_4'))        # duplicate
        self.assertFalse(ro.gate_passed({'rows': [row(c) for c in 'ABC'] + [row('D', False)]}, 'release_4'))
        self.assertFalse(ro.gate_passed({'rows': [row(c) for c in 'ABCD']}, 'release_8'))         # no rows there
