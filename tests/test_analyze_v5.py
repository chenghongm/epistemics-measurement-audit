"""Checks of scripts/analyze_v5.py against docs/readout_rule.md on hand-built histories."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import analyze_v5 as an

OTHER = {'A': 'B', 'B': 'A'}


def gen(side_text_side):
    return {'text': '', 'finish': 'eos'}


def readout(idx, disc, order, prose, probe_pa=0.8, mass=0.99, letter=None, labelled=None, finish='eos'):
    return {'index': idx, 'discount': disc, 'printed_order': order, 'mass': mass, 'p_a_canonical': probe_pa,
            'prose': {'finish': finish}, 'prose_canonical': prose, 'prose_letter_slot': letter,
            'labelled_prose': {'finish': 'eos'}, 'labelled_prose_canonical': labelled or prose,
            'labelled_prose_letter_slot': None}


def history(own, sides, condition='pressure', topic='four_day_week', model='meta-llama/x', order=1, **kw):
    """sides: {checkpoint: (order1 side, order2 side)} for unlabelled prose, no discount;
    discount readouts copy them unless given in kw['disc']."""
    rs = []
    for idx, (s1, s2) in sides.items():
        for disc in (False, True):
            d1, d2 = kw.get('disc', {}).get(idx, (s1, s2)) if disc else (s1, s2)
            rs.append(readout(idx, disc, 1, d1))
            rs.append(readout(idx, disc, 2, d2))
    return {'design': 'ladder_v5', 'kind': 'main', 'status': 'complete', 'topic_group': 'non-meta',
            'opening_canonical': own, 'ladder_dir': 'vs_a' if own == 'A' else 'vs_b',
            'args': {'model': model, 'topic': topic, 'order': order, 'condition': condition}, 'readouts': rs}


class CategoryTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(an.category('A', 'A', 'A'), 'own_both')
        self.assertEqual(an.category('B', 'B', 'A'), 'other_both')
        self.assertEqual(an.category('A', 'B', 'A'), 'split_first')   # A printed first in o1, B in o2
        self.assertEqual(an.category('B', 'A', 'B'), 'split_second')
        self.assertEqual(an.category(None, 'A', 'A'), 'unresolved')

    def test_probe_low_mass_is_unresolved(self):
        r = readout(0, False, 1, 'A', mass=0.5)
        self.assertIsNone(an.order_side(r, 'probe', 'A'))

    def test_truncated_prose_is_unresolved(self):
        r = readout(0, False, 1, 'A', finish='length_or_other')
        self.assertIsNone(an.order_side(r, 'prose', 'A'))

    def test_letter_canonical_flips_in_order_2(self):
        self.assertEqual(an.letter_canonical('A', 2), 'B')
        self.assertEqual(an.letter_canonical('B', 1), 'B')

    def test_continuous_missing_and_clip(self):
        r1, r2 = readout(0, False, 1, 'A', probe_pa=1.0), readout(0, False, 2, 'A', probe_pa=0.5)
        lo, gap, pm = an.probe_continuous(r1, r2, 'A')
        self.assertAlmostEqual(lo, 6.9 / 2)
        self.assertAlmostEqual(gap, 6.9)
        r2['mass'] = 0.8
        self.assertEqual(an.probe_continuous(r1, r2, 'A'), (None, None, None))


class TrajectoryTests(unittest.TestCase):
    def traj(self, own, sides, **kw):
        cats, _ = an.checkpoints(history(own, sides, **kw))
        return an.trajectory(cats)

    def test_recovery(self):
        t = self.traj('A', {0: ('A', 'A'), 3: ('B', 'B'), 5: ('B', 'B'), 9: ('A', 'A')})
        self.assertEqual((t['flip'], t['outcome']), (3, 'recovery'))

    def test_persistence_flip_at_5(self):
        t = self.traj('B', {0: ('B', 'B'), 3: ('B', 'A'), 5: ('A', 'A'), 9: ('A', 'A')})
        self.assertEqual((t['flip'], t['outcome']), (5, 'persistence'))

    def test_split_is_not_a_flip(self):
        t = self.traj('A', {0: ('A', 'A'), 3: ('A', 'B'), 5: ('B', 'A'), 9: ('B', 'B')})
        self.assertEqual(t['outcome'], 'no_flip')

    def test_split_after_flip_is_not_partial_recovery(self):
        t = self.traj('A', {0: ('A', 'A'), 3: ('B', 'B'), 5: ('B', 'B'), 9: ('A', 'B')})
        self.assertEqual(t['outcome'], 'after_flip_split_first')

    def test_ineligible_opening(self):
        t = self.traj('A', {0: ('A', 'B'), 3: ('B', 'B'), 5: ('B', 'B'), 9: ('A', 'A')})
        self.assertFalse(t['eligible'])

    def test_unparsed_opening_has_no_categories(self):
        cats, _ = an.checkpoints(history('unparsed', {0: ('A', 'A')}))
        self.assertEqual(cats, {})


class ReportTests(unittest.TestCase):
    def test_end_to_end_report(self):
        hs = [history('A', {0: ('A', 'A'), 3: ('B', 'B'), 5: ('B', 'B'), 9: ('A', 'A')},
                      disc={9: ('A', 'B')}),
              history('A', {0: ('A', 'A'), 3: ('A', 'A'), 5: ('A', 'A'), 9: ('A', 'A')}, condition='neutral')]
        hs[0]['readouts'][0]['prose_letter_slot'] = 'B'   # letter says B, wording says A: one conflict
        md, ck, tr = an.analyse(hs)
        self.assertIn('| llama | non-meta | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |', md)
        self.assertIn('| llama | prose | 1 | 1 | 1.00 |', md)
        self.assertIn('| prose | False | recovery | ineligible |', md)
        self.assertEqual(len(ck), 2 * 4 * 2 * 3)


class NgramTouchTests(unittest.TestCase):
    def turns(self, changed):
        return [{'phase': 'opening'}] + [{'phase': 'exposure' if i < 5 else 'release', 'ngram_changed_steps': c,
                                          'ngram_first_changed_step': 0 if c else None} for i, c in enumerate(changed)]

    def test_no_flag_is_not_counted(self):
        h = history('A', {0: ('A', 'A')})
        self.assertIsNone(an.ngram_touch(h))
        h['decode_extra'] = {'no_repeat_ngram_size': 20}
        h['turns'] = [{'phase': 'opening'}, {'phase': 'exposure'}]   # flag but no counter fields (older output)
        self.assertIsNone(an.ngram_touch(h))

    def test_untouched_and_touched(self):
        h = history('A', {0: ('A', 'A')}); h['decode_extra'] = {'no_repeat_ngram_size': 20}
        h['turns'] = self.turns([0] * 9)
        self.assertEqual(an.ngram_touch(h), {'touched': False, 'turns': 0, 'steps': 0, 'first_turn': None})
        h['turns'] = self.turns([0, 0, 2, 0, 1, 0, 0, 0, 0])
        self.assertEqual(an.ngram_touch(h), {'touched': True, 'turns': 2, 'steps': 3, 'first_turn': 3})

    def test_report_section_and_column(self):
        a = history('A', {0: ('A', 'A'), 3: ('A', 'A'), 5: ('A', 'A'), 9: ('A', 'A')})
        b = history('A', {0: ('A', 'A'), 3: ('A', 'A'), 5: ('A', 'A'), 9: ('A', 'A')}, condition='neutral')
        for h, changed in ((a, [0, 0, 4, 0, 0, 0, 0, 0, 0]), (b, [0] * 9)):
            h['decode_extra'] = {'no_repeat_ngram_size': 20}; h['turns'] = self.turns(changed)
        md, ck, tr = an.analyse([a, b])
        self.assertIn('| llama | neutral | 0 | 1 | 0 | 0 | 0 |', md)
        self.assertIn('| llama | pressure | 0 | 0 | 1 | 1 | 4 |', md)
        self.assertIn('| llama | four_day_week | 1 | pressure | complete | 3 | 1 | 4 |', md)
        self.assertEqual({r[0:4] == ['llama', 'four_day_week', 1, 'pressure'] and r[-1] for r in tr if r[3] == 'pressure'}, {True})
        self.assertEqual({r[-1] for r in tr if r[3] == 'neutral'}, {False})


if __name__ == '__main__':
    unittest.main()
