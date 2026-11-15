import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import fill_v5 as fv
import fill_v5_supplement as sup


class SupplementTest(unittest.TestCase):
    def test_same_subject_and_suffix_new_templates(self):
        qs = sup.questions('four_day_week')
        self.assertEqual(len(qs), 4)
        self.assertTrue(all(q.endswith(fv.SUFFIX) and fv.SUBJECTS['four_day_week'] in q for q in qs))
        self.assertFalse(set(qs) & set(fv.questions('four_day_week')))

    def test_appended_after_original_candidates(self):
        self.assertEqual(sup.FIRST_INDEX, len(fv.TEMPLATES))
        self.assertNotEqual(sup.spec_sha256(), fv.spec_sha256())


if __name__ == '__main__':
    unittest.main()
