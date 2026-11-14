"""Checks of scripts/compare_noflag_v5.py on hand-built flagged / no-flag pairs."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import compare_noflag_v5 as cmp
from test_analyze_v5 import history


def with_turns(h, texts, changed=None):
    h['turns'] = [{'phase': 'opening', 'text': texts[0]}] + [
        {'phase': 'exposure' if i < 5 else 'release', 'text': t,
         **({} if changed is None else {'ngram_changed_steps': changed[i], 'ngram_first_changed_step': None})}
        for i, t in enumerate(texts[1:])]
    if changed is not None:
        h['decode_extra'] = {'no_repeat_ngram_size': 20}
    return h


class CompareTests(unittest.TestCase):
    def test_split_only_with_flag(self):
        texts = [f't{i}' for i in range(10)]
        flag = with_turns(history('A', {0: ('A', 'A'), 3: ('B', 'B'), 5: ('B', 'B'), 9: ('A', 'B')}),
                          texts[:8] + ['x8', 'x9'], [0, 0, 0, 0, 0, 0, 0, 1, 0])   # first change in turn 8
        noflag = with_turns(history('A', {0: ('A', 'A'), 3: ('B', 'B'), 5: ('B', 'B'), 9: ('B', 'B')}), texts)
        c = cmp.compare_pair(flag, noflag)
        self.assertEqual((c['first'], c['prefix_same'], c['clean_same']), (8, True, True))
        self.assertEqual((c['traj_flag']['outcome'], c['traj_noflag']['outcome']), ('after_flip_split_first', 'persistence'))
        self.assertEqual(c['touched'], [(9, 'prose', 'split_first', 'other_both'), (9, 'probe', 'own_both', 'own_both')])
        md = cmp.report({('llama', 'four_day_week', 1, 'pressure'): flag}, {('llama', 'four_day_week', 1, 'pressure'): noflag})
        self.assertIn('| flag | 1/1 |', md)
        self.assertIn('| no-flag | 0/1 |', md)

    def test_prefix_mismatch_is_flagged(self):
        texts = [f't{i}' for i in range(10)]
        flag = with_turns(history('A', {0: ('A', 'A')}), texts, [0] * 9)
        noflag = with_turns(history('A', {0: ('A', 'A')}), texts[:4] + ['other'] + texts[5:])
        self.assertFalse(cmp.compare_pair(flag, noflag)['prefix_same'])


if __name__ == '__main__':
    unittest.main()
