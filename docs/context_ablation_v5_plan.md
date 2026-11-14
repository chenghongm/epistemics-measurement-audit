# Context ablation of v5 histories — design draft, 2026-11-14

Status: design draft before ablation readouts. No ablation GPU run has started. This follows the main run and its results; it is a follow-up experiment, not part of the original main-run registration. Freeze the filler corpus, manifest, reconstruction criteria and analysis before execution.

## Question

Does the persistent shift in the v5 histories depend more on the retained pressure-phase assistant replies than on the retained user pressure messages, under matched measurement instructions and order-robust readouts?

Use the archived pressure histories rather than regenerate conversations. Distinguish these context-replacement interventions from rerunning a conversation under a different pressure policy.

## Four cells

| Cell | User exposure messages | Assistant exposure replies |
|---|---|---|
| A | Original | Original |
| B | Frozen on-topic filler questions | Original |
| C | Original | Frozen on-topic filler replies |
| D | Frozen on-topic filler questions | Frozen on-topic filler replies |

Preserve the opening in every cell. Replace only the five exposure turns, indices 1–5; preserve message roles and turn count. At index 9, also retain the original four follow-up exchanges in every cell. D is a replacement baseline, not an empty context or an assumed return to opening.

Read at exposure 5 and release 4 (index 9). The index-5 contrast contains no later assistant replies that might already repeat the shifted position. The index-9 contrast measures the effect of retaining exposure text conditional on the fixed, already-generated follow-up; it does not remove the influence already carried into follow-up replies. A null at index 9 alone would therefore not refute all contributions of the model's own text.

## Sampling and readouts

Include all 48 pressure histories, both models and all twelve topics/orders. Do not select on a large residual or a convenient B/C difference. Report the existing primary eligible and flipped cohorts separately without redefining eligibility from ablated readings. Retain original opening wording as the own-side anchor.

At both checkpoints and every cell collect probe and unlabelled prose, none/discount and both printed orders, using the exact v5 readout templates. Prose wording determines side; splits and unresolved remain separate. Labelled prose is not required for the initial ablation. Planned full grid including reconstruction: 48 histories × 2 checkpoints × 4 cells × 2 prefixes × 2 orders = 1,536 prose generations and 1,536 probe forwards. Measure actual runtime on a small fixed subset before projecting cost. All model execution is on Colab, not local hardware.

## Filler preparation and validation

First inspect the earlier frozen filler corpora and their provenance for topic coverage and suitability. Do not assume the existing neutral histories are interchangeable with filler, and do not reuse follow-up questions at exposure positions without checking duplication. Freeze a separate corpus of on-topic, nondirectional question/answer pairs before collecting B/C/D results. Do not choose filler by the resulting stance.

Use each model's actual tokenizer to record replacement lengths and complete cell context lengths, by role and exposure position. Aim for comparable lengths, disclose remaining differences, and inspect reference coherence in B and C. Fixed filler, role preservation and length reporting do not establish perfect semantic or length control. Reject truncated filler. Specify corpus selection and acceptable length criteria before execution; these remain to be finalized.

## Reconstruction and analysis

Reproduce A under the pinned model/tokenizer, dtype, templates and readout settings. Predeclare a numerical probe tolerance and exact generated-prose match rule, with failures recorded and excluded from paired claims. Reuse the project's original reconstruction gate after verifying its exact specifications. Do not interpret replacement effects where A reconstruction fails.

Primary behavioral comparison: within each history, contrast A/B/C/D categories under no-discount unlabelled prose, anchored to the original opening. Compare B with C for retention of the shifted side and report the paired transition table, splits, unresolved and coverage. Separate models and topic groups; summarize within topics before cross-topic comparisons. All histories and the fixed primary-flipped cohort answer different descriptive questions and need separate denominators.

Probe provides a continuous complementary comparison: raw paired changes relative to D, order-specific probabilities, mass coverage, averaged clipped log-odds and order gap as specified in the readout rule. Do not use an unstable retention ratio as the sole endpoint when A and D nearly coincide. Discount is a secondary crossed measurement condition, not an alternative eligibility filter. Report D relative to the original neutral history as a diagnostic rather than demanding equality.

Stratify by recorded n-gram intervention status and checkpoint cleanliness. These remain properties of the original histories; re-reading does not undo them. Do not attribute B/C differences to internal commitment or belief without additional evidence. Findings concern contributions of retained contextual text under the specified replacement operation.

## Next implementation tasks

1. Inspect and select or prepare the fixed filler corpus, freeze length criteria and its hashes.
2. Build a manifest-driven replay runner with A reconstruction, per-cell provenance and resumable output; verify replacement indices and role mapping locally without loading models.
3. Run a small predetermined Colab reconstruction/timing batch, then execute the frozen grid and report all failures.
