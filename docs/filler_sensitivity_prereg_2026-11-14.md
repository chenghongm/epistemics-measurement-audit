# Step 7 filler freeze and paired sensitivity analysis

**WITHDRAWN, 2026-11-14, before any locally observed step 7 intervention results.** After comparing the designs, the user chose the original review/reject/replace procedure. The reviewed corpus is the primary condition; this document's unchanged-primary and position-preserving replacement rules are no longer execution instructions. The original procedure selects the first five accepted candidates in template order. The historical proposal below is retained for transparency. See `docs/filler_v5_reviewed_selection_2026-11-14.md` and the reviewed-corpus manifest for the active state. No sensitivity run is claimed by this document.

Status: local prospective analysis registration, 2026-11-14, following the user's decision to freeze the generated filler unchanged. This is an amendment to the earlier mandatory-replacement recommendation, not a claim of public or independent registration. Step 8 results and the step 7a filler review were already available. No step 7 intervention results are present in the local checkout at registration; remote execution status has not been verified.

## Frozen primary condition

Use the existing selected candidates and all original question/answer text in `results/fill_v5/llama.json` and `results/fill_v5/qwen.json` unchanged. Their exact hashes, the review CSV, and this protocol are recorded in `provenance/filler_v5_freeze_2026-11-14.json`. Neither candidate rejection fields nor selected indices are changed in these primary files.

The existing step 7 grid, A reconstruction gate, primary endpoint, cohorts, inference unit, and missingness rules stay unchanged. Describe this material as **frozen generated on-topic filler**, not as established semantically neutral text. Report the 15 review holds and their reasons alongside the primary results. The holds are screening judgments, not 15 verified factual errors.

## One prespecified sensitivity: reviewed replacement filler

Question: does the B-versus-C contrast change when the filler items identified before intervention outcomes are replaced?

The affected set is fixed by rows marked `hold_for_revision_or_verification` in the frozen review CSV: nine Llama topics and two Qwen topics, each with both opening orders (22 histories). Do not add or remove topics using primary ablation outcomes. The remaining 26 histories require no sensitivity rerun because their filler remains identical.

Prepare a separate reviewed corpus without editing the primary files:

1. Preserve every unflagged selected question/answer pair at its original exposure position. Replace each flagged position with a complete question/answer pair from the same model and topic's unused generated candidates. Inspect unused candidates in ascending candidate index, assign them to flagged exposure positions in ascending position order, and use each candidate at most once per topic.
2. Accept only EOS-complete text that neither quotes an option's wording nor clearly recommends or selectively argues for one option, contains no unresolved specific factual claim, and has no gross scope mismatch. A balanced description of competing considerations is acceptable. Review the question and answer together. Log every acceptance/rejection and reason. No selection may use a B/C/D outcome or the opening side.
3. If fewer suitable unused pairs exist than flagged positions, stop preparation for that topic. Do not invent a post-result fallback or silently drop it from the paired denominator. Any new generation specification must be documented as a further amendment before new generation/readouts, with timing and any prior outcome access disclosed.
4. Retain the existing model-wide median answer-length criterion (within 30% of 154 Llama / 152 Qwen tokens), and record lengths by topic, role and position for both corpora. Length and question-content changes remain possible explanations of any sensitivity effect; this does not isolate semantic direction alone.
5. Freeze the revised corpus hashes and replacement log before inspecting primary step 7 B/C/D results. If this ordering cannot be met, explicitly label the subsequent revised-corpus check as post-result rather than prospectively specified in its final stimuli.

## Execution

Use the same archived histories, pinned models, readout prompts, generation settings, A/B/C/D construction, checkpoints 5 and 9, none/discount prefixes and both printed orders. Retain the original release exchanges at checkpoint 9 in both versions. Store revised-corpus runs under a separate output root; never overwrite or mix original-corpus cell files.

Run A-only reconstruction before the revised B/C/D grid. The existing runner's provenance checks remain enforced. A failed reconstruction excludes the corresponding history/checkpoint from paired claims, with the reason reported. No threshold is relaxed for the sensitivity run.

The affected 22-history A/B/C/D grid contains 22 × 2 checkpoints × 4 cells × 2 prefixes × 2 orders = **704 prose generations plus 704 probe forwards**, including reconstruction. This is an additional prospective workload, not a measured runtime estimate. No local model execution is needed; use Colab.

## Analysis and reporting

The primary sensitivity comparison is at checkpoint 5, no-discount unlabelled prose. For each filler version define, per history, `d = I(B is other_both) - I(C is other_both)`. Report original and revised B/C category tables and the paired change `d_revised - d_original` on the same affected histories. Checkpoint 9 is secondary. Discount and probe differences are complementary diagnostics, not alternative primary endpoints.

Only compare histories/checkpoints whose A gate passes in both versions and whose B/C prose resolves in both versions. Report the full fixed affected denominator, gate failures, unresolved/missing counts and the final paired denominator. Splits are valid outcomes: they contribute zero to the `other_both` indicator but are reported separately and never called recovery. Also report category transition tables for B, C and D between versions.

Keep models and topic groups separate. Average the paired change over the two opening orders within each topic before any topic-level sign test. With only two affected Qwen topics, emphasize descriptive results rather than a significance claim. Preserve the original fixed primary-flipped cohort as a separate descriptive stratum, without redefining it using either ablation version.

Present the original 48-history primary result and the 22-history sensitivity side by side, but use the original **same 22 histories** as the actual paired comparator. Do not compare the revised subset directly against the original full-sample rate. Report all directions of change, including weakening or reversal; do not select whichever filler produces a stronger B-over-C result. No equivalence margin is specified, so unchanged signs or a nonsignificant test do not establish equivalence.

This sensitivity assesses dependence on the flagged filler replacements. It does not validate all unflagged text as inert or isolate authorship from argument content. It does not alter the completed step 8 reread, which uses separate archived filler.
