import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import review_fill_v5 as rv

FILL = ROOT / 'results/fill_v5'
NOTEBOOK_SHA = {'llama': 'b2f360825fc6e6f6f5f7694acd5819bf9b0c58b72e7a233ff8602dd261b4de24',
                'qwen': '4d8093d255e18b6248510079287ab347746f03dc2e99bb855e09df5c50008428'}


@unittest.skipUnless((FILL / 'llama.json').exists(), 'archived filler not present')
class ReviewTest(unittest.TestCase):
    def build(self, name):
        sup = [(FILL / 'supplement/llama_four_day_week.json').read_bytes()] if name == 'llama' else []
        d = rv.review((FILL / f'{name}.json').read_bytes(), sup)
        return (json.dumps(d, indent=2, ensure_ascii=False) + '\n').encode()

    def test_rebuild_matches_archived_and_notebook_hash(self):
        for name in ('llama', 'qwen'):
            b = self.build(name)
            self.assertEqual(b, (FILL / f'{name}.reviewed.json').read_bytes())
            self.assertEqual(hashlib.sha256(b).hexdigest(), NOTEBOOK_SHA[name])
            nb = (ROOT / 'notebooks/colab_multiturn_v5.ipynb').read_text()
            self.assertIn(NOTEBOOK_SHA[name], nb)

    def test_selection_is_first_five_accepted(self):
        d = json.loads(self.build('llama'))
        v = d['topics']['four_day_week']
        self.assertEqual(v['selected'], [2, 4, 6, 7, 9])
        self.assertTrue(all(v['candidates'][i]['reject'] is None for i in v['selected']))
        self.assertTrue(all(r['reason'] in (rv.D, rv.O) for r in d['review']['rejections']))

    def test_llama_needs_its_supplement(self):
        with self.assertRaises(SystemExit):
            rv.review((FILL / 'llama.json').read_bytes(), [])

    def test_wrong_raw_rejected(self):
        raw = json.loads((FILL / 'qwen.json').read_bytes()); raw['topics']['tipping']['selected'] = [0, 1, 2, 3, 5]
        with self.assertRaises(SystemExit):
            rv.review(json.dumps(raw).encode())


if __name__ == '__main__':
    unittest.main()
