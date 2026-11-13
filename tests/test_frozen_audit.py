"""CPU regression checks for failure handling and paired report estimands."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import frozen_audit as audit


class AuditTests(unittest.TestCase):
    def test_mass_error_is_serializable_and_other_errors_propagate(self):
        class ProbeMassError(RuntimeError):
            pass
        runner = Mock()
        runner.probe_stance_averaged.side_effect = ProbeMassError('mass 0.1')
        result = audit.safe_probe(runner, [], 'a', 'b', ProbeMassError)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'failure.json'
            audit.save(path, result)
            self.assertEqual(json.loads(path.read_text())['error'], 'ProbeMassError')
        runner.probe_stance_averaged.side_effect = RuntimeError('CUDA failed')
        with self.assertRaisesRegex(RuntimeError, 'CUDA failed'):
            audit.safe_probe(runner, [], 'a', 'b', ProbeMassError)

    def test_tokenizer_mismatch_prevents_weight_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'tokenizer.json').write_text('{}')
            download = Mock(return_value=tmp)
            with patch.dict(sys.modules, huggingface_hub=SimpleNamespace(snapshot_download=download)):
                with self.assertRaisesRegex(ValueError, 'Tokenizer mismatch'):
                    audit.pinned_model(SimpleNamespace(model='org/model', revision='a'*40),
                                       {'tokenizer_sha256': 'wrong'})
            self.assertEqual(download.call_count, 1)
            self.assertIn('allow_patterns', download.call_args.kwargs)

    def test_weight_download_skips_original_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'tokenizer.json').write_text('{}')
            download = Mock(return_value=tmp)
            with patch.dict(sys.modules, huggingface_hub=SimpleNamespace(snapshot_download=download)):
                audit.pinned_model(SimpleNamespace(model='org/model', revision='a'*40),
                                   {'tokenizer_sha256': audit.sha(Path(tmp, 'tokenizer.json'))})
            self.assertEqual(download.call_count, 2)
            self.assertIn('original/*', download.call_args.kwargs['ignore_patterns'])

    def test_effect_sign_tolerance(self):
        self.assertEqual(audit.effect_sign(.01), 0)
        self.assertEqual(audit.effect_sign(-.03), -1)
        self.assertEqual(audit.effect_sign(.2), 1)

    def test_own_direction(self):
        self.assertAlmostEqual(audit.own_probability(.8, 'A') - audit.own_probability(.6, 'A'), .2)
        self.assertAlmostEqual(audit.own_probability(.2, 'B') - audit.own_probability(.4, 'B'), .2)

    def test_report_retains_nonbinary_and_separates_denominators(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = [dict(conv_id=f'c{i}', topic='topic', order=1, turn_idx=0, phase='pressure') for i in range(3)]
            manifest = root / 'manifest.json'
            audit.save(manifest, dict(checkpoints=items))
            audit.save(root / 'environment-identity.json', dict(schema=2, manifest_sha256=audit.sha(manifest)))
            for i, item in enumerate(items):
                audit.save(root / f'c{i}__t0.json', dict(checkpoint=item, identity_sha256='identity',
                    gate_pass=True, gate_reasons=[], wall_seconds=1, opening_side='B',
                    probe_counterfactual_valid=True,
                    probe_orig=dict(p_a=.2, orders=[.2, .2]),
                    probe_no_discount=dict(p_a=.4, orders=[.4, .4]),
                    prose_orig=dict(side='A', cap_hit=False),
                    prose_discount=dict(side='B' if i != 1 else 'unparsed', cap_hit=i == 2)))
            out = root / 'paired.csv'
            with contextlib.redirect_stdout(io.StringIO()):
                audit.report(SimpleNamespace(results=str(root), manifest=str(manifest), out=str(out)))
            summary = json.loads(Path(str(out)+'.summary.json').read_text())['topics'][0]
            self.assertEqual(summary['prose_outcomes'], {'B': 1, 'unparsed_review_required': 1, 'truncated': 1})
            self.assertEqual(summary['probe_discount_effect_own']['n'], 3)
            self.assertNotIn('did_own', summary)
            # Opening B: probe p_own .8 vs .6 -> +1; prose A -> B (own) -> +1; one evaluable pair.
            self.assertEqual(summary['discount_sign_pairs'], {'+1/+1': 1})
            self.assertEqual(summary['mean_disagreement_change']['mean'], -1)

    def test_bundle_repository_metadata_without_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit.save(root / 'provenance/build.json', dict(commit='abc', dirty=True))
            self.assertEqual(audit.repository_identity(root), dict(commit='abc', dirty=True))


if __name__ == '__main__':
    unittest.main()
