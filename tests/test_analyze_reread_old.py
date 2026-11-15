"""Checks of scripts/analyze_reread_old.py on synthetic re-read outputs over the archived old inputs."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'vendor/digital_mind'))
import analyze_reread_old as ar
import reread_old_ablation as ro

DATA = ROOT / 'data/external/digital-mind'


def readouts(rec, shifted):
    """v5-style readouts at every checkpoint; shifted=True puts both printed orders on the other side."""
    own = rec['opening_side']; side = ('B' if own == 'A' else 'A') if shifted else own
    out = []
    for label, idx in ro.checkpoints(rec).items():
        for disc in (False, True):
            for order in (1, 2):
                out.append({'checkpoint': label, 'index': idx, 'discount': disc, 'printed_order': order, 'mass': 0.99,
                            'p_a_canonical': 0.9 if side == 'A' else 0.1, 'prose': {'finish': 'eos', 'text': ''},
                            'prose_canonical': side, 'prose_letter_slot': None})
    return out


@unittest.skipUnless((DATA / 'topics_6x6.json').exists(), 'needs data/external (provenance/reread_sources.json)')
class AnalyseTests(unittest.TestCase):
    def test_retention(self):
        self.assertIsNone(ar.retention({'A': 0.5, 'B': 0.5, 'C': 0.5, 'D': 0.48}))
        b, c = ar.retention({'A': 0.2, 'B': 0.3, 'C': 0.6, 'D': 0.7}); self.assertAlmostEqual(b, 0.8); self.assertAlmostEqual(c, 0.2)

    def test_b_keeps_c_returns_and_gate(self):
        recs, old, _, _, _ = ro.load_set(DATA, 'repl_b1')
        convs = sorted(c for c, r in recs.items() if r['condition'] == 'pressure_release')[:3]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'repl_b1'; out.mkdir()
            for i, c in enumerate(convs):
                rec = recs[c]
                ok = i != 2   # the third conversation fails the gate at release_8
                rows = [{'checkpoint': l, 'turn_idx': idx, 'cell': x, 'p_a': 0.5, 'p_orders': [0.5, 0.5],
                         'ok': ok or l != 'release_8'} for l, idx in ro.checkpoints(rec).items() for x in ro.CELLS]
                (out / f'{c}__gate.json').write_text(json.dumps({'conv_id': c, 'rows': rows}))
                for x, shifted in (('A', True), ('B', True), ('C', False), ('D', False)):
                    (out / f'{c}__{x}.json').write_text(json.dumps(
                        {'conv_id': c, 'cell': x, 'opening_side': rec['opening_side'], 'readouts': readouts(rec, shifted)}))
            md = ar.analyse(ar.load(d, DATA))
        self.assertIn('| repl_b1 | pressure_release | 12 | 12 | 11 | 1 |', md)      # 3 convs x 4 checkpoints gated
        # two conversations pass all release checkpoints: B keeps 3/3, C 0/3
        # the two passing conversations are o1/o2 of one topic: 2/0 conversations, but 1/0 of 1 topic
        self.assertIn('| repl_b1 | pressure_release | 2 | 2 | 3.00 | 3.00 | 0.00 | 0.00 | 2 / 0 | 1 / 0 of 1 | 1 | 2 / 0 of 2 |', md)
        self.assertIn('+0.64 / +0.24 (n=11)', md)   # the old headline, from the old files
        self.assertIn('| repl_b1 | B | 6 | 0% | 0% |', md)

    def test_unresolved_c_excluded(self):
        recs, old, _, _, _ = ro.load_set(DATA, 'repl_b1')
        c = sorted(r for r in recs if recs[r]['condition'] == 'pressure_release')[0]; rec = recs[c]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'repl_b1'; out.mkdir()
            rows = [{'checkpoint': l, 'turn_idx': i, 'cell': x, 'p_a': .5, 'p_orders': [.5, .5], 'ok': True}
                    for l, i in ro.checkpoints(rec).items() for x in ro.CELLS]
            (out / f'{c}__gate.json').write_text(json.dumps({'conv_id': c, 'rows': rows}))
            for x, shifted in (('A', True), ('B', True), ('C', False), ('D', False)):
                rs = readouts(rec, shifted)
                if x == 'C':
                    for r in rs:
                        r['prose']['finish'] = 'length_or_other'
                (out / f'{c}__{x}.json').write_text(json.dumps({'conv_id': c, 'cell': x, 'opening_side': rec['opening_side'], 'readouts': rs}))
            md = ar.analyse(ar.load(d, DATA))
        self.assertIn('| repl_b1 | pressure_release | 1 | 0 | - | - | - | - | 0 / 0 | 0 / 0 of 0 | - | 0 / 0 of 0 |', md)

    def test_missing_readouts_excluded_not_zero(self):
        # C keeps the shift, but its no-discount release_8 rows are absent: the conversation must drop out,
        # not count as C keeping 2 of 3 (Codex end-to-end audit, finding 1)
        recs, old, _, _, _ = ro.load_set(DATA, 'repl_b1')
        c = sorted(r for r in recs if recs[r]['condition'] == 'pressure_release')[0]; rec = recs[c]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'repl_b1'; out.mkdir()
            rows = [{'checkpoint': l, 'turn_idx': i, 'cell': x, 'p_a': .5, 'p_orders': [.5, .5], 'ok': True}
                    for l, i in ro.checkpoints(rec).items() for x in ro.CELLS]
            (out / f'{c}__gate.json').write_text(json.dumps({'conv_id': c, 'rows': rows}))
            for x in ro.CELLS:
                rs = readouts(rec, x in 'ABC')
                if x == 'C':
                    rs = [r for r in rs if not (r['checkpoint'] == 'release_8' and not r['discount'])]
                (out / f'{c}__{x}.json').write_text(json.dumps({'conv_id': c, 'cell': x, 'opening_side': rec['opening_side'], 'readouts': rs}))
            md = ar.analyse(ar.load(d, DATA))
        primary = md.split('## Secondary')[0]
        self.assertIn('| repl_b1 | pressure_release | 1 | 0 | - | - | - | - | 0 / 0 | 0 / 0 of 0 | - |', primary)

    def test_arms_of_one_topic_are_one_unit(self):
        recs, old, _, _, _ = ro.load_set(DATA, 'repl_b1')
        cs = [c for c in sorted(recs) if recs[c]['topic'] == recs['pressure_release__000__o1']['topic']]   # 3 arms x 2 orders
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / 'repl_b1'; out.mkdir()
            for c in cs:
                rec = recs[c]
                rows = [{'checkpoint': l, 'turn_idx': i, 'cell': x, 'p_a': .5, 'p_orders': [.5, .5], 'ok': True}
                        for l, i in ro.checkpoints(rec).items() for x in ro.CELLS]
                (out / f'{c}__gate.json').write_text(json.dumps({'conv_id': c, 'rows': rows}))
                for x, shifted in (('A', True), ('B', True), ('C', False), ('D', False)):
                    (out / f'{c}__{x}.json').write_text(json.dumps({'conv_id': c, 'cell': x, 'opening_side': rec['opening_side'], 'readouts': readouts(rec, shifted)}))
            md = ar.analyse(ar.load(d, DATA))
        self.assertEqual(len(cs), 6)
        self.assertIn('| repl_b1 | all arms | 6 | 6 | 3.00 | 3.00 | 0.00 | 0.00 | 6 / 0 | 1 / 0 of 1 | 1 |', md)


if __name__ == '__main__':
    unittest.main()
