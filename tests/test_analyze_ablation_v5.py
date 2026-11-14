"""Checks of scripts/analyze_ablation_v5.py on cells built from archived histories."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import ablation_v5 as ab
import analyze_ablation_v5 as aa

RAW = ROOT / 'results/main_v5/raw'


def load_raw():
    return {ab.history_name(h): h for h in (json.loads(p.read_text()) for p in RAW.glob('*.json'))}


def cell(src, c, side=None, prose_text=None):
    """A cell record whose readouts copy the archive; side forces the prose side ('own'/'other')."""
    own = src['opening_canonical']; other = 'B' if own == 'A' else 'A'
    rs = []
    for r in src['readouts']:
        if r['index'] not in ab.CHECKPOINTS:
            continue
        r = copy.deepcopy(r)
        if side:
            r['prose_canonical'] = own if side == 'own' else other; r['prose']['finish'] = 'eos'
        if prose_text:
            r['prose']['text'] = prose_text
        rs.append(r)
    return {'design': ab.DESIGN, 'history': ab.history_name(src), 'cell': c, 'status': 'complete', 'readouts': rs,
            'ctx_tokens': {'5': 100, '9': 200},
            'token_lengths': [{'position': i, 'user_original': 50, 'user_filler': 60, 'assistant_original': 100,
                               'assistant_filler': 90} for i in range(1, 6)]}


class AnalyseTests(unittest.TestCase):
    def setUp(self):
        self.raw = load_raw()
        self.names = ['llama_ai_hold_correction_o1_pressure', 'llama_standardized_tests_o1_pressure']  # both flipped

    def test_b_keeps_c_returns(self):
        cells = {n: {'A': cell(self.raw[n], 'A'), 'B': cell(self.raw[n], 'B', 'other'),
                     'C': cell(self.raw[n], 'C', 'own'), 'D': cell(self.raw[n], 'D', 'own')} for n in self.names}
        md, rows = aa.analyse(self.raw, cells)
        # 24 llama pressure histories; 2 have all cells and pass the gate at both checkpoints
        self.assertIn('| llama | 5 | 24 | 2 | 22 | 0 |', md)
        # two topics, each B-only: topic-level sign test 2/0 of 2 topics
        self.assertIn('| llama | all | 5 | 2 | 2 | 0 | 2/2 | 0/2 | 0 | 2 | 0 | 0 | 0 | 2 / 0 of 2 | 0.5 |', md)
        self.assertIn('| llama | flipped | 9 | 2 |', md)
        self.assertTrue(any(r[0] == self.names[0] and r[7] == 'B' and r[11] == 'other_both' for r in rows))

    def test_failed_reconstruction_excluded(self):
        n = self.names[0]
        cells = {n: {'A': cell(self.raw[n], 'A', prose_text='changed'), 'B': cell(self.raw[n], 'B', 'other'),
                     'C': cell(self.raw[n], 'C', 'own'), 'D': cell(self.raw[n], 'D', 'own')}}
        md, rows = aa.analyse(self.raw, cells)
        self.assertIn('| llama | 5 | 24 | 0 | 23 | 1 |', md)
        self.assertIn('(excluded: reconstruction)', md)
        self.assertEqual({r[-1] for r in rows if r[0] == n}, {False})

    def test_unresolved_c_is_excluded_not_scored(self):
        """Codex's case: B keeps the shift, every C prose answer truncated -> no 'only B keeps'."""
        n = self.names[0]
        c = cell(self.raw[n], 'C')
        for r in c['readouts']:
            r['prose']['finish'] = 'length_or_other'
        cells = {n: {'A': cell(self.raw[n], 'A'), 'B': cell(self.raw[n], 'B', 'other'), 'C': c, 'D': cell(self.raw[n], 'D', 'own')}}
        md, _ = aa.analyse(self.raw, cells)
        self.assertIn('| llama | all | 5 | 1 | 0 | 1 | 1/1 | 0/1 | 0 | 0 | 0 | 0 | 0 | 0 / 0 of 0 | - |', md)

    def test_topic_is_the_unit(self):
        """Two orders of one topic, both B-only: one topic, so no significance from two histories."""
        ns = ['llama_ai_hold_correction_o1_pressure', 'llama_ai_hold_correction_o2_pressure']
        cells = {n: {'A': cell(self.raw[n], 'A'), 'B': cell(self.raw[n], 'B', 'other'),
                     'C': cell(self.raw[n], 'C', 'own'), 'D': cell(self.raw[n], 'D', 'own')} for n in ns}
        md, _ = aa.analyse(self.raw, cells)
        self.assertIn('| 0 | 2 | 0 | 0 | 0 | 1 / 0 of 1 | 1 |', md)

    def test_even_median(self):
        n0, n1 = self.names
        cells = {n: {'A': cell(self.raw[n], 'A'), 'B': cell(self.raw[n], 'B', 'other'),
                     'C': cell(self.raw[n], 'C', 'own'), 'D': cell(self.raw[n], 'D', 'own')} for n in self.names}
        cells[n0]['A']['ctx_tokens'] = {'5': 100, '9': 200}; cells[n1]['A']['ctx_tokens'] = {'5': 300, '9': 200}
        md, _ = aa.analyse(self.raw, cells)
        lengths = md[md.index('Median context tokens'):]
        self.assertIn('| llama | 5 | 200.0 | 100.0 | 100.0 | 100.0 |', lengths)   # median of [100, 300] is 200, not 300

    def test_sign_test(self):
        self.assertIsNone(aa.sign_test(0, 0))
        self.assertAlmostEqual(aa.sign_test(2, 0), 0.5)
        self.assertAlmostEqual(aa.sign_test(10, 0), 2 / 1024)


if __name__ == '__main__':
    unittest.main()


class GateCompletenessTests(unittest.TestCase):
    def test_a_needs_all_four_readouts(self):
        raw = load_raw(); n = 'llama_ai_hold_correction_o1_pressure'
        cells = {c: cell(raw[n], c) for c in 'ABCD'}
        self.assertEqual(aa.gate(raw[n], cells), {5: (True, None), 9: (True, None)})
        cells['A']['readouts'] = [r for r in cells['A']['readouts'] if not (r['index'] == 5 and r['discount'])]
        self.assertEqual(aa.gate(raw[n], cells)[5], (False, 'reconstruction'))
