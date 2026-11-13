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

    def test_prefix_templates_nest_the_original_prompts(self):
        import ast
        tree = ast.parse((Path(audit.__file__).resolve().parent.parent / 'vendor/digital_mind/runner.py').read_text())
        consts = {t.id: ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                  for t in n.targets if isinstance(t, ast.Name) and t.id in ('STANCE_PROBE', 'ELICIT_STANCE')}
        probes, proses = audit.prefix_templates(consts['STANCE_PROBE'], consts['ELICIT_STANCE'])
        self.assertEqual(probes['discount'], consts['STANCE_PROBE'])
        self.assertEqual(proses['none'], consts['ELICIT_STANCE'])
        self.assertEqual(proses['discount'], audit.DISCOUNT + consts['ELICIT_STANCE'])
        for name, prefix in audit.PREFIXES.items():
            self.assertTrue(probes[name].startswith(prefix + 'State the position YOU'))
            self.assertNotIn('{', prefix)
        with self.assertRaises(SystemExit):
            audit.prefix_templates('State the position.', consts['ELICIT_STANCE'])

    def test_gate_reasons(self):
        turn = dict(p_a=.6, p_a_orders=[.4, .8], elicited_side='A')
        ok = dict(p_a=.6, mass=.99, orders=[.4, .8])
        self.assertEqual(audit.gate(ok, dict(side='A', cap_hit=False), turn), (0, []))
        _, reasons = audit.gate(dict(ok, orders=[.37, .83]), dict(side='B', cap_hit=False), turn)
        self.assertEqual(reasons, ['probe_reconstruction_failed', 'prose_reconstruction_failed_or_unparsed'])
        _, reasons = audit.gate(dict(error='ProbeMassError'), dict(side='A', cap_hit=False), turn)
        self.assertEqual(reasons, ['baseline_probe_mass_error'])

    def test_own_logit_is_side_symmetric(self):
        self.assertAlmostEqual(audit.own_logit([.2, .9], 'A'), -audit.own_logit([.2, .9], 'B'))
        self.assertAlmostEqual(audit.own_logit([.5, .5], 'A'), 0)

    def test_control_verdict_rules(self):
        v = audit.control_verdict
        self.assertEqual(v(.05, 0, 0, 6, 6), 'no_discount_effect')
        self.assertEqual(v(1.0, .1, -.4, 6, 6), 'semantic_specific_bidirectional')
        self.assertEqual(v(1.0, .1, .2, 5, 6), 'semantic_specific')
        self.assertEqual(v(1.0, .1, .2, 4, 6), 'mixed')
        self.assertEqual(v(1.0, .8, -.4, 6, 6), 'generic_perturbation')
        # Sign-normalised: a negative discount effect with a matching negative placebo is generic.
        self.assertEqual(v(-1.0, -.8, .4, 6, 6), 'generic_perturbation')
        self.assertEqual(v(-1.0, .05, .5, 6, 6), 'semantic_specific_bidirectional')

    def test_prefix_report_end_to_end(self):
        def probe(p):
            return dict(p_a=p, mass=.99, orders=[p, p])
        def prose(side):
            return dict(side=side, cap_hit=False)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = [dict(conv_id=f'c{i}', topic=f't{i % 2}', order=1, turn_idx=1, phase='pressure') for i in range(4)]
            manifest = root / 'manifest.json'
            audit.save(manifest, dict(checkpoints=items))
            audit.save(root / 'environment-identity.json', dict(schema=2, design='prefix_crossed',
                       prefixes=audit.PREFIXES, manifest_sha256=audit.sha(manifest)))
            for item in items:
                audit.save(root / f'{item["conv_id"]}__t1.json', dict(
                    checkpoint=item, identity_sha256='identity', gate_pass=True, gate_reasons=[],
                    wall_seconds=1, opening_side='A',
                    probe=dict(none=probe(.3), discount=probe(.7), placebo=probe(.32), reverse=probe(.2)),
                    prose=dict(none=prose('B'), discount=prose('A'), placebo=prose('B'),
                               reverse=dict(side='unparsed', cap_hit=False))))
            out = root / 'prefix.csv'
            with contextlib.redirect_stdout(io.StringIO()):
                audit.prefix_report(SimpleNamespace(results=str(root), manifest=str(manifest), out=str(out)))
            phase = json.loads(Path(str(out) + '.summary.json').read_text())['phases']['pressure']
            self.assertEqual(phase['verdict'], 'semantic_specific_bidirectional')
            self.assertAlmostEqual(phase['discount']['topic_mean_dlogit'], 2 * audit.logit(.7))
            self.assertEqual(phase['discount']['prose_shifts'], {'other->own': 4})
            self.assertEqual(phase['reverse']['prose_shifts'], {'other->unparsed_review_required': 4})
            self.assertEqual(phase['disagreement']['none'], dict(n=4, disagree=0, straddle=0, prose={'other': 4}))
            self.assertEqual(phase['disagreement']['reverse']['n'], 0)

    def test_neutral_set_is_well_formed(self):
        import ast
        tree = ast.parse((Path(audit.__file__).resolve().parent.parent / 'vendor/digital_mind/runner.py').read_text())
        consts = {t.id: ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                  for t in n.targets if isinstance(t, ast.Name) and t.id in ('STANCE_PROBE', 'ELICIT_STANCE')}
        probes, proses = audit.prefix_templates(consts['STANCE_PROBE'], consts['ELICIT_STANCE'],
                                                audit.NEUTRAL_PREFIXES)
        self.assertEqual(probes['discount'], consts['STANCE_PROBE'])
        self.assertEqual(proses['none'], consts['ELICIT_STANCE'])
        self.assertEqual(audit.NEUTRAL_PREFIXES['short_question'], audit.PREFIXES['placebo'])
        self.assertEqual(len(audit.NEUTRAL_NAMES), 8)
        texts = [v for k, v in audit.NEUTRAL_PREFIXES.items() if k != 'none']
        self.assertEqual(len(set(texts)), len(texts))
        for text in texts:
            # The chat template trims content: a whitespace-only or space-led prefix would be altered.
            self.assertTrue(text.strip() and text[0] != ' ' and text.endswith('. ') and '{' not in text)

    def test_binomial_tail(self):
        self.assertAlmostEqual(audit.binomial_tail(6, 0, 1/9), 1)
        self.assertAlmostEqual(audit.binomial_tail(6, 5, 1/9), 6 * (1/9)**5 * (8/9) + (1/9)**6)

    def test_neutral_report_end_to_end(self):
        names = list(audit.NEUTRAL_PREFIXES)
        def probe(p):
            return dict(p_a=p, mass=.99, orders=[p, p])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = [dict(conv_id=f'c{i}', topic=f't{i}', order=1, turn_idx=1, phase='pressure') for i in range(6)]
            manifest = root / 'manifest.json'
            audit.save(manifest, dict(checkpoints=items))
            audit.save(root / 'environment-identity.json', dict(schema=2, design='neutral_set',
                       prefixes=audit.NEUTRAL_PREFIXES, manifest_sha256=audit.sha(manifest)))
            for i, item in enumerate(items):
                # Neutral prefixes spread around none (p=.3); discount highest except in topic t0,
                # where ignore_weather wins. ignore_weather is top-3 everywhere.
                ps = {n: .3 + .01 * (k - 4) for k, n in enumerate(names)}
                ps.update(none=.3, discount=.8 if i else .6, ignore_weather=.7)
                prose = {n: dict(side='B', cap_hit=False) for n in names}
                prose['discount'] = dict(side='A', cap_hit=False)
                audit.save(root / f'{item["conv_id"]}__t1.json', dict(
                    checkpoint=item, identity_sha256='identity', gate_pass=True, gate_reasons=[],
                    wall_seconds=1, opening_side='A',
                    probe={n: probe(p) for n, p in ps.items()}, prose=prose))
            out = root / 'neutral.csv'
            with contextlib.redirect_stdout(io.StringIO()):
                audit.prefix_report(SimpleNamespace(results=str(root), manifest=str(manifest), out=str(out)))
            summary = json.loads(Path(str(out) + '.summary.json').read_text())
            self.assertEqual(summary['design'], 'neutral_set')
            neutral = summary['phases']['pressure']['neutral']
            self.assertEqual(neutral['discount_first'], 5)
            self.assertEqual(neutral['discount_rank']['t0'], 2)
            self.assertAlmostEqual(neutral['p_first_at_least'], audit.binomial_tail(6, 5, 1/9))
            self.assertEqual(neutral['syntax_top3'], {'ignore_weather': 6, 'ignore_typos': 0})
            self.assertEqual(neutral['prose_other_to_own']['discount'], 6)
            self.assertEqual(neutral['verdicts'], dict(direction_specific=True, syntax_contributes=True,
                                                       prose_specific=True, registered=True))

    def test_prose_order_templates_change_only_the_option_lines(self):
        import ast
        tree = ast.parse((Path(audit.__file__).resolve().parent.parent / 'vendor/digital_mind/runner.py').read_text())
        elicit = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                      for t in n.targets if isinstance(t, ast.Name) and t.id == 'ELICIT_STANCE')
        t = audit.prose_order_templates(elicit)
        self.assertEqual(t[('none', 'labelled')], elicit)
        self.assertEqual(t[('discount', 'labelled')], audit.DISCOUNT + elicit)
        self.assertEqual(t[('none', 'unlabelled')].replace(audit.BULLET_OPTIONS, audit.LETTERED_OPTIONS), elicit)
        filled = t[('none', 'unlabelled')].format(LA='A', LB='B', side_a='X', side_b='Y')
        self.assertIn('- X\n- Y\n', filled)
        self.assertNotIn('(A)', filled)
        with self.assertRaises(SystemExit):
            audit.prose_order_templates('No options here.')

    def test_to_canonical_and_order_category(self):
        # Conversation order 2 printed (B-side, A-side); swapping prints (A-side, B-side).
        self.assertEqual(audit.to_canonical('A', 'b-text', 'a-text'), 'B')
        self.assertEqual(audit.to_canonical('A', 'a-text', 'a-text'), 'A')
        self.assertEqual(audit.to_canonical('B', 'b-text', 'a-text'), 'A')
        self.assertEqual(audit.to_canonical('unparsed', 'x', 'y'), 'unparsed')
        c = lambda side: dict(side=side, cap_hit=False)
        self.assertEqual(audit.order_category(c('A'), c('A'), 'A', 1), 'own_both')
        self.assertEqual(audit.order_category(c('B'), c('B'), 'A', 2), 'other_both')
        # Order 1: conv shows A first; answering B then A = second slot both times.
        self.assertEqual(audit.order_category(c('B'), c('A'), 'A', 1), 'split_slot2')
        # Order 2: conv shows B first; answering B then A = first slot both times.
        self.assertEqual(audit.order_category(c('B'), c('A'), 'A', 2), 'split_slot1')
        self.assertEqual(audit.order_category(c('unparsed'), c('A'), 'A', 1), 'unresolved')
        self.assertEqual(audit.order_category(dict(side='A', cap_hit=True), c('A'), 'A', 1), 'unresolved')

    def test_prose_order_report_end_to_end(self):
        c = lambda side, letter=None, wording=None: dict(side=side, cap_hit=False, letter_slot=letter,
                                                          wording_side=wording or side)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = [dict(conv_id=f'c{i}', topic=f't{i % 6}', order=1, turn_idx=1, phase='pressure') for i in range(8)]
            manifest = root / 'manifest.json'
            audit.save(manifest, dict(checkpoints=items))
            audit.save(root / 'environment-identity.json', dict(design='prose_order',
                       prefixes=audit.PROSE_ORDER_PREFIXES, manifest_sha256=audit.sha(manifest)))
            for i, item in enumerate(items):
                # Opening side A. none: other in both orders. discount: labelled follows the second slot
                # (B, then A) for every checkpoint; unlabelled is own_both for 6 of 8, other_both for 2.
                none = {k: c('B') for k in ('labelled/conv', 'labelled/swap', 'unlabelled/conv', 'unlabelled/swap')}
                disc = {'labelled/conv': c('B', 'B'), 'labelled/swap': c('A', 'B'),
                        'unlabelled/conv': c('A' if i < 6 else 'B'), 'unlabelled/swap': c('A' if i < 6 else 'B')}
                if i == 0:
                    disc['labelled/conv'] = c('A', 'A', 'B')  # letter says own, wording says other
                audit.save(root / f'{item["conv_id"]}__t1.json', dict(
                    checkpoint=item, identity_sha256='identity', gate_pass=True, gate_reasons=[],
                    wall_seconds=1, opening_side='A', prose=dict(none=none, discount=disc)))
            out = root / 'po.csv'
            with contextlib.redirect_stdout(io.StringIO()):
                audit.prose_order_report(SimpleNamespace(results=str(root), manifest=str(manifest), out=str(out)))
            ph = json.loads(Path(str(out) + '.summary.json').read_text())['phases']['pressure']
            self.assertEqual(ph['categories']['discount/labelled'], {'split_slot2': 7, 'own_both': 1})
            self.assertEqual(ph['effect']['labelled'], dict(n=8, up=8, down=0, same=0, survives=True))
            self.assertEqual(ph['effect']['unlabelled'], dict(n=8, up=6, down=0, same=2, survives=True))
            self.assertEqual(ph['single_order_claim']['unlabelled'], dict(n=1, discount_own_both=1))
            self.assertEqual(ph['letter_wording_conflicts'], 1)
            self.assertTrue(ph['registered'])

    def test_bundle_repository_metadata_without_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit.save(root / 'provenance/build.json', dict(commit='abc', dirty=True))
            self.assertEqual(audit.repository_identity(root), dict(commit='abc', dirty=True))


if __name__ == '__main__':
    unittest.main()
