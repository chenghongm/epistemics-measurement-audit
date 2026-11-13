# Handoff — 2026-11-06

## Start here

Local repo: `/Users/chm.1/pyenvs/genai/epistemics-measurement-audit`
Private remote: https://github.com/chenghongm/epistemics-measurement-audit
Branch: `codex/pre-sprint-audit`.
User prefers concise updates and low token usage. Do not reread the full chat or repeat completed literature searches. Include `Co-authored-by: Codex <codex@openai.com>` in assisted commits.

## Objective and decisions

Complete the pre-sprint frozen-history audit promptly, then use its results to decide the November 13–15 AI x Epistemics Sprint project. Do not treat completion of this old audit plan as a new research contribution.

Audit: on identical stored histories, cross original one-letter/probability versus prose readouts with presence/absence of `Ignore what the user has been arguing.` The old templates differ beyond this sentence: this is a targeted diagnostic, not full semantic matching. Neither probe nor text is ground truth for internal belief. Recovery is baseline return, not factual correctness.

Potential Sprint extension: common semantic prompts and fixed pressure exposure; no readout-based stopping. Eight topics/two models was a proposed scope, not a finalized or executed experiment. Source-label experiments are not the current primary recommendation.

Official rules allow existing work but require disclosure of pre-sprint code/results and a clear account of work completed during the Sprint. See `PREEXISTING.md`. Keep actual timestamps; no backdating.

## Completed

- Independent local/private GitHub repo created and pushed; original Digital Mind checkout was left clean after migrating only this chat's new files.
- Upstream pinned to Digital Mind commit `ba77b47a4c4bfe159139c3ad11f9102e31866f2a`.
- `provenance/sources.json`: 12 historical files, six verbatim vendored runtime modules, inherited plan, hashes and permanent links.
- `provenance/checkpoints.json`: 30 unique opening/flip/latest-disagreement checkpoints across six topics; source and exact prefix hashes. Candidate prefixes did not hit the old 768-token cap; historical finish reasons were not recorded, so natural completion is inferred only.
- Hash verification and four provenance tests passed, including a clean-clone/local-fetch check. Python and notebook syntax checked.
- Audit harness, report entry point, input fetcher, offline Colab bundler and notebook prepared.
- **No GPU audit has run. No model reconstruction has passed yet. No substantive audit findings exist.** CPU/synthetic checks are not model results.

## Next action

1. Inspect `scripts/frozen_audit.py` and the inherited plan only as needed; do not expand scope.
2. Run `python3 scripts/verify_provenance.py` and `python3 -m unittest discover -s tests -v` from this repo.
3. Rebuild `artifacts/audit-source.zip` with `python3 scripts/build_bundle.py`; use `notebooks/colab_frozen_audit.ipynb` in Colab A100. Existing generated bundle is ignored by Git; rebuild after code changes.
4. User must select the runtime, inspect actual CU/hour, upload the bundle and complete Hugging Face login; no active remote runtime/session is connected here. Never put credentials in committed notebooks.
5. Run original-condition reconstruction first. Harness saves reconstruction and ProbeMassError failures and gates counterfactuals per checkpoint. Other runtime errors still stop execution. Inspect broad gate failures promptly rather than spending the full budget. Results go to `results/`, never historical inputs.
6. Download results ZIP before disconnecting. Manually review prose/ambiguous labels; parser has a known negation limitation. Check failures, straddle and probability coverage separately. Do not count repeated turns/options as independent topics.
7. Report topic-level paired diagnostic effects and determine whether to advance, repair prompts, or change direction.

## Compute and limits

Continue using Colab; no platform migration. Pre-sprint budget estimate: 1–3 A100 hours, reserve 25–30 CU pending the actual runtime rate. Historical 5.3 CU/hour is outdated; user observed six-plus. At 6.3 CU/hour, three hours is 18.9 CU; recent user reports include higher rates. CU/hour and dollars/hour are distinct. Do not spend GPU time idle.

## Files to consult

- `README.md`: execution commands and isolation structure.
- `docs/preexisting_frozen_history_plan.md`: inherited audit protocol, not newly authored for this Sprint.
- `docs/direction_review_2026-11-06.md`: new review and tentative future scope; planning estimates, not findings.
- `PREEXISTING.md`, `CONTRIBUTORS.md`: attribution/disclosure.

## Technical cautions

Requirements are not version-pinned; historical CUDA/model reconstruction remains unverified. Preserve environment metadata in outputs. Source files are ignored external dependencies and can be fetched locally from `/Users/chm.1/pyenvs/genai/digital-mind` or by pinned URLs. The initial audit harness's `prepare` subcommand is inherited preparation logic; use the already frozen provenance manifest, not an ad hoc re-selection. Any harness/template edit requires rebuilding the bundle. Report generation does not itself prove all manifest checkpoints ran; reconcile results against all 30 entries before declaring completion.

## Update 2026-11-13

2×2 ran on Colab A100-40GB (revision `0e9e39f…`, transformers 5.22.1): 30/30 gate pass, exact reconstruction (Δ 0, prose text identical). Results ZIP in `artifacts/` (ignored). Prefix control also ran (16:49 UTC); results in `docs/results_2026-11-13.md`. All 2026-11-13 work is Sprint work; baseline tag `sprint-baseline` = `191e3d9`. Next: `prefix-run --set neutral` (8 neutral prefixes, `docs/neutral_set_plan.md`), same revision; save the download as `artifacts/neutral-results.zip`.
