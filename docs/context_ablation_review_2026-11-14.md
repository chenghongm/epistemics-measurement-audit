# Review of the prepared context-ablation implementation

## Verification of the three requested fixes

Rechecked the subsequent implementation: both analysers now exclude B/C unresolved prose comparisons from the primary comparison and report valid coverage; splits remain valid outcomes and are counted separately. The old re-read requires resolved B/C prose at all three release checkpoints for its three-checkpoint count. Topic-level scores now determine sign-test p-values, grouping opening orders and, in pooled old analyses, arms within topic. All four median calculations in `analyze_ablation_v5.py` and the filler-length notebook print use `statistics.median`. Regression tests cover truncated C responses, two orders or six arm/order histories of one topic counting as one inference unit, and an even-sample median. All 87 current tests pass. These changes resolve the three findings from the second review for the specified completed output structure; they do not establish GPU reconstruction or filler validation, which remain execution checks.

## Second review: updated Step 7 and added Step 8

The updated implementation addresses the earlier resume/provenance and A-reconstruction enforcement findings, and Step 7b is now A-only. Analysis scripts have been added. Step 8 is the requested measurement-only re-read of the old ablations; Step 7 remains a distinct v5 extension. All 82 current tests pass (the unchanged vendored old code emits file-handle ResourceWarnings).

Remaining findings before intervention analysis is frozen:

1. **Unresolved/missing prose contributes as a negative primary endpoint.** In `analyze_ablation_v5.py`, `paired()` compares each category to other_both and treats every other value, including unresolved or a missing key, as false. A local synthetic check made all C prose outputs truncated while B was other_both: the script still counted one "only B keeps" comparison. `analyze_reread_old.py` likewise leaves k at zero when cats returns None and adds zero for unresolved readings, but reports k as a count out of three. Preserve resolved paired coverage, unresolved/missing counts, and separate split categories. Missing or truncated readouts must not silently become evidence of lost retention. Counting splits as absence of an order-robust shifted stance can be an explicit endpoint, but does not mean stable return to the opening side.
2. **Sign-test independence is not established.** Both analysers compute p-values across conversation/order units. Two opening orders share a topic and filler, and the old three pressure arms share pre-divergence history. The pooled 36 conversations per old set are not 36 independent topics. Summarize paired effects within topic first, keep arms/models separate, and use topic-level inference or make these small-sample results descriptive. This does not invalidate the underlying paired context comparisons, but can materially change significance claims.
3. **Incorrect even-sample median in the new v5 analysis.** `analyze_ablation_v5.py` uses sorted(v)[len(v)//2] for log-odds medians, context-token medians and token-ratio medians. For even samples this is the upper middle observation, not the midpoint of the two middle observations. Use statistics.median consistently. The old re-read analyser already uses statistics.median.

Step 8's reuse of stored filler, original system turn, old stitching code and old-probe per-order reconstruction is appropriate. Its bridge explicitly compares all twelve old release readings with the three sampled release checkpoints, which is necessary to distinguish subsampling from new-readout effects. A further defensive improvement is to require the exact four unique cell gate rows at each checkpoint rather than trusting all(ok) over whatever rows happen to be present; normal complete outputs currently generate those four rows.

Recommended priority: run old-history reconstruction (8a) while correcting and freezing the analysis. Do not collect the new B/C/D readouts (7c or 8b) until the endpoint missingness and inference rules are explicit. The earlier comments below describe the first version and are superseded where fixed above.

Reviewed by Codex, 2026-11-14, before GPU execution of this ablation. Files reviewed: `docs/context_ablation_v5_plan.md`, step 7 in `docs/run_v5.md` and the Colab notebook, `scripts/ablation_v5.py`, `scripts/fill_v5.py`, and associated tests. All 68 current local tests pass. These tests validate wiring, not filler neutrality or substantive effects.

## Assessment

The four-cell, fixed-history design is suitable for a follow-up on v5. Roles, opening, exposure positions, readout templates and option-order mapping are preserved. Reading at both exposure 5 and release 4 is useful. Sampling all 48 pressure histories avoids selecting only favorable residual shifts. Keeping the original opening anchor and reporting the existing eligible/flipped cohorts separately is appropriate.

However, this is a **new-protocol ablation on v5 histories**, not a measurement-only re-audit of the old context-ablation result. The earlier plan used different exposure stopping and follow-up lengths, histories and filler. A/B/C/D retention numbers should not be directly compared across those studies. If the immediate objective is to validate the earlier source-of-persistence conclusion while changing only the readout, replay the old frozen A/B/C/D contexts instead. Both studies are useful, but the choice must be explicit before spending the full-grid compute.

## Implementation changes before the full grid

1. **Validate provenance on resume.** `ablation_v5.py` currently skips any existing cell with status complete. Before skipping, compare its filler SHA, source-history SHA, model/revision, readout/code identity and cell/checkpoint settings against the requested run. Otherwise changing reviewed filler can silently mix old and new cell results in one output directory. The notebook's reviewed-filler hash check does not validate already-existing cell files.
2. **Make reconstruction a machine-enforced gate.** Step 7b currently prints FAILED and asks the operator to stop; the runner writes failed-A files with status complete and continues B/C/D. Raise an error on failed preflight reconstruction, and skip paired intervention cells when that history's A fails during the full batch. Preserve the failed output and its reason for accounting. The final analyser must also apply the gate independently.
3. **Freeze the analysis before collecting B/C/D results, including preflight.** The full-grid analysis script is still pending. Step 7b currently calls the runner for all four cells of its two selected histories, so it generates intervention results before step 7c. Freeze the B-vs-C estimand, categories, fixed cohort, missingness rules and length diagnostics before 7b, or make 7b an A-only reconstruction/timing stage and clearly separate any intervention pilot from the subsequent test.

## Filler and interpretation

The 8-candidate/first-5-accepted rule and the one-time length adjustment are specified before intervention outputs and are reasonable preparation rules. Fresh generation avoids copying stance-bearing answers from the main neutral histories. Nevertheless, failure to quote either exact option is not evidence of semantic neutrality: an accepted paraphrase may still advocate a side. Review selected questions and answers for directional recommendations, unsupported factual claims and gross mismatch with the retained adjacent turns, before freezing the corpus; document any rejection rules without selecting on B/C outcomes.

The proposed model-wide median length criterion (within 30% of the original pressure-reply median) is a useful initial check but cannot establish matching by topic or position. Retain per-topic and role-specific token ratios and complete context lengths. A 120-word request is an instruction, not a guarantee of a 150-token reply. Do not use the median alone to declare length controlled.

At checkpoint 9, original release-phase assistant replies remain in every cell and may already carry the shift forward. The plan correctly acknowledges this: the contrast tests the retained exposure text conditional on the fixed follow-up, not the effect of removing every shifted assistant statement. Emphasize checkpoint 5 alongside checkpoint 9. A B-over-C contrast concerns these particular texts and replacements; it does not isolate authorship from argument content or demonstrate an internal commitment mechanism.

## Recommended execution order

First settle whether this batch is the v5 extension or the old-history re-audit. For a v5 extension, filler generation/review can proceed while the resume checks, enforced reconstruction gate and frozen analyser are completed. Only then proceed from reconstruction/timing to the full intervention grid. Do not treat passing local tests as evidence that those scientific and execution checks have already passed.
