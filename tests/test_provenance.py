import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
from verify_provenance import ROOT, verify


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        for folder in ['provenance', 'vendor', 'docs', 'data']:
            shutil.copytree(ROOT / folder, self.root / folder)

    def test_frozen_inputs(self):
        self.assertEqual(verify(self.root), (12, 30))

    def test_changed_history_is_rejected(self):
        source = json.loads((self.root / 'provenance/sources.json').read_text())['files'][0]
        path = self.root / source['local_path']
        path.chmod(0o644)
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'Content hash mismatch'):
            verify(self.root)

    def test_changed_checkpoint_is_rejected(self):
        path = self.root / 'provenance/checkpoints.json'
        doc = json.loads(path.read_text())
        doc['checkpoints'][0]['prefix_sha256'] = '0' * 64
        path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, 'History prefix mismatch'):
            verify(self.root)

    def test_duplicate_checkpoint_is_rejected(self):
        path = self.root / 'provenance/checkpoints.json'
        doc = json.loads(path.read_text())
        doc['checkpoints'].append(doc['checkpoints'][0])
        path.write_text(json.dumps(doc))
        with self.assertRaisesRegex(ValueError, 'Duplicate checkpoint'):
            verify(self.root)


if __name__ == '__main__':
    unittest.main()
