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

Neutral set ran (A100-80GB, exact cross-run consistency): discount first of nine in 5/6 pressure topics, prose 13/18 vs ≤2/18 for neutrals; details in `docs/results_2026-11-13.md`.

Prose order/label control added (`docs/prose_order_plan.md`, pre-registered): the format diagnostic and a slot re-read of the neutral-set prose suggest part of the discount prose effect is a shift toward the second printed option. Next: `prose-order-run` (none/discount × lettered/bulleted × both printed orders), same revision; save the download as `artifacts/prose-order-results.zip`. Fixed-exposure pilot v2 and format diagnostic are separate (`docs/new_pilot_plan.md`, `docs/format_control_*`).

Prose order control ran (A100-40GB, 30/30 gate, exact): registered verdict "survives" (bulleted 13 up / 0 down), but order-robust returns are 5/18 lettered and 8/18 bulleted, not 13/18; discount shifts prose toward the second printed option. Results doc and supported claims revised.

## Update 2026-11-14

Main-run topics and ladders fixed before any main-run data: `docs/main_run_ladders.md` and `.json`. These are 6 old + 6 meta topics (the Digital Mind `topics_6x6.json` set). Both directions are written for each topic: 14 ladders reused verbatim, 10 new. Next: an opening smoke on Llama and Qwen to check the wording-only parse rate (meta openings were parsed from letters before), then the main run.

v5 runner: `scripts/new_dialogue_v5.py` is v4 with `PRESSURE` replaced by the frozen ladders (hash-pinned; `vs_a`/`vs_b` from the opening's wording side; an unparsed opening stops a pressure history, while neutral histories continue). Torch-free tests: `tests/test_dialogue_v5.py`. Bundle: `python3 scripts/build_multiturn_bundle.py` → `artifacts/multiturn-v5.zip`; notebook `notebooks/colab_multiturn_v5.ipynb` (step 4 opening-only smoke, `scripts/opening_smoke_v5.py`; step 4b timing on 4 histories with a CU projection; step 5 main, 96 histories). Analysis: `scripts/analyze_v5.py` (readout rule). Steps and pre-GPU checks: `docs/run_v5.md`. Not yet run on a GPU. The 4 `test_provenance` errors need `data/` from `scripts/fetch_sources.py` and predate v5.

### 2026-11-14 Colab status (step 4 smoke and step 4b timing done)

Results are in chm.1's Drive under `multiturn-v5-results` (shared read-only with the Drive account connected to Claude). The runs used bundle `d582501`; the run code is identical to `1693fde`.

- **Opening smoke:** 48/48 openings parse from wording (all copy the option text, all end with EOS, no letters). Llama's side depends on printed order for `curbside_plastics`, `ai_decline_lawful` and `same_assistant_retrained`; Qwen's side never does. New ladders actually used: Llama `curbside_plastics` vs_b, `ai_decline_lawful` vs_b, `same_assistant_retrained` vs_b; Qwen `four_day_week` vs_b. The other 6 new directions are unused (all openings on the other side).
- **Timing** (`four_day_week` o1): the completed histories took 165 s (Llama neutral), 246 s (Qwen neutral) and 223 s (Qwen pressure), excluding process start. That projects to about 6–7 GPU hours for 96 histories.
- **Blocking decision before step 5:** Llama pressure `four_day_week` o1 hit `truncated_history` at exposure turn 5. This is not a long answer but a greedy repetition loop ("so 100% / 20% = 5, and 5 * 20% = 100%, but …") after it starts conceding. Raising the cap does not help. If such loops cluster where the model yields, the hard stop drops histories selectively. Options: (1) keep the rule and report truncation by model and condition, with the readouts before truncation; (2) add a mild `repetition_penalty` (e.g. 1.1) to main-history turns only, both models and conditions, written up as a pre-data protocol change, and rerun the 4 timing histories. Recommended: (2). The user has not decided.
- Qwen's release replies grow to about 1000 tokens (cap 1500); watch for truncations on other topics.
- Notebook `1693fde` streams child output; with the older notebook, histories print nothing until they finish.
- Added (off by default) `--no-repeat-ngram N` and `--repetition-penalty X` to `new_dialogue_v5.py`, applied to exposure and release turns only (not the opening, not readouts) and recorded as `decode_extra`. Notebook step 4c reruns the looping history under none / ngram20 / rep1.1 into `results/decode_test/`. HF `repetition_penalty` also penalises end-of-turn tokens and option wording already in context; `no_repeat_ngram_size` only blocks verbatim n-gram repeats. Decide from 4c, then document the choice before step 5. If a flag is adopted, the 4 timing histories must be rerun with it.
