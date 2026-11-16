# Data and conclusions after the audit

Status: manuscript working reference, compiled by Codex after the analysis fixes in `88523c5`. This is a synthesis of completed data, not a new registration, experiment or independent replication. The original result archives and frozen definitions remain the sources. Chinese discussion summaries may be derived from this document; it is not final manuscript prose.

## 1. What was measured

The studies measure choices expressed or scored under specified instructions, relative to an opening choice. They do not establish an internal belief, a true preference, or whether a change is rational persuasion rather than social accommodation.

A history is a sequence of user/assistant exchanges. A checkpoint is one frozen history prefix at a specified turn. At a checkpoint, reversing the printed options produces two readouts of that same prefix, not two independent histories. Opening-order variants generate separate histories; readout-order variants branch from the same history.

The primary readout is **unlabelled prose without the discount sentence**. The options are shown as bullets; the model is asked to quote its chosen option and give a reason. Classification follows option wording, not any generated letter. Both printed orders must agree for `own_both` or `other_both`. A split is a separate outcome, never half a stance or a recovery. A probe scores next-token A/B probabilities; it does not generate an extra textual response.

The v5 dialogue policy is fixed: one opening, five exposure exchanges, four neutral follow-up exchanges. Readouts at 0/3/5/9 are discarded branches and do not decide when exposure stops. This differs from the old protocol, where probe-triggered stopping could change the pressure length, followed by twelve release-labelled turns. Sustained-pressure and topic-switch arms must not be pooled under a description of simple pressure withdrawal.

## 2. Data ledger: studies and units

| Evidence block | Scope | Recorded measurement scale | Purpose and boundary |
|---|---|---|---|
| Historical diagnostic audit | Llama, six topics, 12 old histories; 30 selected checkpoints (12 opening, 18 pressure) | Matched-prefix, placebo/reverse, neutral-prefix and order/label controls revisit these prefixes | A deliberately high-disagreement sample; diagnoses measurement problems, not their population prevalence |
| Format diagnostic pilot | Two models reading four saved Llama history prefixes, two topics | 96 total measurement branches: 32 probe records and 64 prose outputs | Qwen reads Llama histories here; not a two-model fresh-dialogue replication |
| v5 main experiment, step 5 | Two models × 12 topics × two opening orders × pressure/neutral = 96 histories | 383 checkpoints; 960 main responses; 3,064 prose readouts; 1,532 probe records | 95 complete histories and one Qwen neutral history with a truncated final response |
| No-flag sensitivity, step 6 | 14 matched Llama pressure-history pairs | 13 complete no-flag trajectories and one truncated before checkpoint 5 | Tests those Llama runs; no Qwen no-flag replication |
| v5 context ablation, step 7 | The same 48 main pressure histories × A/B/C/D = 192 cells | Two checkpoints × two prefixes × two orders per cell: 1,536 prose generations and 1,536 probe records | A context-replacement intervention, not 192 newly generated dialogue histories |
| Old-context reread, step 8 | 72 old histories: 36 Llama non-meta, 36 Qwen meta, three arms per set × A/B/C/D = 288 cells | Four checkpoints × two prefixes × two orders per cell: 4,608 prose generations and 4,608 probe records | Changes readouts while preserving old contexts and filler; not a new-sample replication |

Do not add these rows into a claimed number of independent dialogues: histories are reused across analyses, and some diagnostic histories overlap the old-context study. Model, topic, opening order, checkpoint, readout order and generated response are different units.

For the main study alone, 960 + 3,064 = **4,024 generated text records**. Its 1,532 probe scores are additional scoring records, not generated answers. Main-run logical requests total 5,556; this is not the number of low-level forward passes. The missing final readout in one neutral history explains 383 rather than 384 checkpoints. All 48 pressure histories are complete. All twelve topics were previously used; six non-meta plus six meta does not mean six old plus six unseen topics.

## 3. Main behavioral result: persistence under the primary readout

Only histories whose opening readout selects the opening-response side in both printed orders are eligible. Flip means `other_both` at exposure checkpoint 3 or 5. Final persistence/recovery is defined at checkpoint 9 conditional on a flip.

| Pressure trajectory | Llama | Qwen | Total |
|---|---:|---:|---:|
| Collected | 24 | 24 | 48 |
| Eligible | 16 | 24 | 40 |
| Observed flip | 13 | 19 | 32 |
| Of flipped: final other_both | 10 | 16 | 26 |
| Of flipped: final own_both | 0 | 2 | 2 |
| Of flipped: final split | 3 | 1 | 4 |

Therefore 32/40 eligible pressure histories flip, and 26/32 flipped histories retain the shifted choice at the final checkpoint. These are conditional, descriptive rates, not estimates from 32 independent topics. The eight excluded Llama pressure histories have opening-readout splits or disagreement with the opening response; do not silently drop them from coverage reporting. Eligible neutral histories have zero exposure flips (0/40), but this does not mean every neutral readout is identical or every neutral history finished.

The two Qwen histories classified as recovery are the two opening-order versions of **remote_work**, not two different topics. Both already returned at checkpoint 5, before pressure withdrawal. More directly, among eligible histories still `other_both` at exposure end:

| Exposure-end other_both → final category | Llama | Qwen | Total |
|---|---:|---:|---:|
| other_both | 10 | 16 | 26 |
| split | 3 | 1 | 4 |
| own_both | 0 | 0 | 0 |
| Starting histories | 13 | 17 | 30 |

This transition tabulation is a descriptive rereading of the completed trajectories. It supports the statement that **no return to the opening choice was observed during the four follow-up exchanges among histories still shifted at exposure end**. It does not establish indefinite irreversibility, nor recovery beyond the observation window.

Both topic groups contain persistent shifts. With six topics per group and no equivalence test, do not claim that meta/non-meta behavior is identical.

## 4. Measurement changes individual judgments and conditional rates

The historical selected-pressure audit found probe/prose disagreement of 16/18 under the original mismatched prefixes, versus 9/18 with neither prefix and 7/18 with discount in both. Those are historical mean-based classifications, not the later order-robust endpoint. They diagnose an instrument mismatch; aligning instructions does not validate either channel as the true stance.

The placebo/reverse and eight-neutral-prefix controls show that discount has a particularly consistent direction in this selected sample, while arbitrary prefixes are not inert. Single-order return counts also vary on reversal. The controls do not establish that every neutral sentence is harmless or that every apparent return is recovery of an internal state.

In the main study, no-discount prose splits at post-opening pressure checkpoints are **16/72 for Llama** and **1/72 for Qwen**. A split means the two printed orders choose opposite canonical options; here it is an observed paired position-sensitive result, not evidence that every model always chooses the second or last item.

Exploratory format contrasts at the same post-opening pressure checkpoints:

| Contrast | Llama different categories / resolved pairs | Qwen |
|---|---:|---:|
| Probe vs labelled prose | 15/66 | 4/72 |
| Labelled vs unlabelled prose | 19/72 | 0/72 |
| Probe vs unlabelled prose | 19/66 | 4/72 |

These are **category differences**, often involving splits, not necessarily opposite stable choices. The design is an incomplete presentation-format × output-format cross. Probe versus labelled prose also changes scoring versus generation. The three contrasts do not add up and are not isolated estimates of three causal mechanisms. This tabulation was added after observing the main results.

For a fair prefix comparison, hold the original primary-flipped cohort fixed instead of recomputing eligibility separately under discount:

| Model; fixed cohort | Prefix at final unlabelled-prose readout | other_both | own_both | split |
|---|---|---:|---:|---:|
| Llama; 13 | none | 10 | 0 | 3 |
| Llama; 13 | discount | 7 | 1 | 5 |
| Qwen; 19 | none | 16 | 2 | 1 |
| Qwen; 19 | discount | 15 | 0 | 4 |

Discount is exactly **"Ignore what the user has been arguing."** It targets the user's arguments, not the entire history. A different final readout on an identical history is a measurement-condition effect; it does not show that the ongoing conversation recovered. The fixed-cohort table is a descriptive matched comparison, not a replacement of the registered per-readout trajectory tables.

**Supported conclusion:** shifted choices commonly persist under the primary readout, and persistence is also observed in secondary channels. Individual flip/recovery classifications, coverage and rates depend on readout conditions, especially for Llama. Avoid "unaffected by measurement" or a universal claim of Qwen stability.

## 5. Context source: distinguish the old-context audit from the new-protocol intervention

A retains the full context. B replaces exposure user text with filler while retaining original assistant replies. C retains user pressure while replacing assistant replies. D replaces both. The opening is always retained. In step 7, original follow-up text is also retained in every cell at checkpoint 9, so checkpoint 5 has priority as the timepoint free of those later assistant replies.

### Step 8: the earlier direction remains in old contexts, with limited primary evidence

The old continuous retention medians reproduce: pooled B/C = 0.59/0.08 for Llama and 0.92/0.31 for Qwen-meta. These are normalized ratios, not categorical percentages. Restricting the old scores to release checkpoints 4/8/12 changes them to 0.62/0.12 and 0.97/0.33 even before changing the readout. This bridge separates subsampling from measurement changes.

New no-discount unlabelled prose, pooled over all three old arms:

| Old set | Histories | Mean shifted checkpoints in B (out of 3) | In C | Topics B>C / C>B | Topic p |
|---|---:|---:|---:|---|---:|
| Llama, six non-meta topics | 36 | 0.92 | 0.42 | 4 / 0 | 0.125 |
| Qwen, six meta topics | 36 | 1.44 | 0.86 | 5 / 1 | 0.219 |

For the pressure-release arm alone, the counts are Llama B/C **9/36 versus 4/36** checkpoint observations and Qwen **16/36 versus 5/36**, with topic p=0.25 in each set. Each denominator is 12 histories times three checkpoints, not 36 independent histories.

The supplementary post-result restriction to Llama histories whose A is shifted at end pressure includes 15/36 histories. Its B/C means are 1.8/0.667, with four favorable non-tied topics (p=0.125). Keep this descriptive check separate from the frozen full-sample analysis. Continuous probe support is stronger in Qwen-meta, but does not convert the primary prose result into uniform evidence across readouts and arms.

**Conclusion:** directional support survives rereading these old contexts; its strength depends on the endpoint. This is not a broad, independently replicated source mechanism. The two sets confound model and topic group.

### Step 7: a general own-reply advantage does not transfer to v5

All 48 pressure histories were ablated. Report both the full cohort and the fixed primary-flipped cohort. Both were specified before intervention outcomes; emphasizing the flipped cohort for the persistence question was a post-result reporting choice, not a predeclared hierarchy.

| Model | Cohort | N | Checkpoint | A shifted | B shifted | C shifted | D shifted | Topic p for B/C |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Llama | all | 24 | 5 | 19 | 2 | 10 | 0 | 0.0625 |
| Llama | fixed flipped | 13 | 5 | 13 | 1 | 4 | 0 | 0.5 |
| Qwen | all | 24 | 5 | 17 | 16 | 15 | 0 | 1 |
| Qwen | fixed flipped | 19 | 5 | 17 | 16 | 15 | 0 | 1 |
| Llama | fixed flipped | 13 | 9 | 10 | 0 | 3 | 0 | 0.5 |
| Qwen | fixed flipped | 19 | 9 | 16 | 13 | 10 | 1 | 0.625 |

"Shifted" here always means `other_both`; in the full cohort it does not necessarily mean persistence following an eligible observed flip. A=17/19 at checkpoint 5 for Qwen because two previously flipped remote-work histories already returned before withdrawal.

At checkpoint 5, nine flipped Llama histories have neither B nor C shifted. Five have both cells own; four involve splits. Thirteen flipped Qwen histories have both B and C shifted. These patterns do not establish universal necessity of both halves for Llama or universal sufficiency of either half for Qwen. The observed Llama B/C ordering favors C, but the fixed-flipped topic-level evidence does not establish a stable reversal.

**Conclusion:** the new protocol does not reproduce a general own-reply advantage. Differences between the two protocols cannot be assigned to pressure length, stopping rule, filler, model or topic mix individually: several factors change together. B/C replacements also alter conversational coherence and argument content; this is not a clean intervention on authorship alone.

## 6. What the sensitivity and audit checks establish

- The n-gram rule changed at least one greedy token in 66/96 main histories. Step 6 reran 14 affected Llama pressure histories without it; 13 completed with the same primary outcome, one stopped before checkpoint 5. The three Llama post-flip release splits also appear without the rule. Qwen was not rerun, so do not generalize this check to all affected histories.
- Final filler was generated independently, reviewed by both assistants and adjudicated by the author; criteria and one supplementary generation were documented before step 7 readouts. Neutrality remains a judgment. Qwen filler is shorter for several topics, and B/C contexts can be incoherent. D is a joint-replacement diagnostic, not proof of inert filler in B/C.
- A reconstructs all 48 step 7 histories. Step 8's 1,152 checkpoint-by-cell old-probe rows pass. Reconstruction checks establish compatibility with the stored contexts, not new independent evidence for persistence.
- The audit found two analysis bugs: absent step 8 rows could count as zero retention, and an unfinished trajectory could be labelled no-flip. Both were fixed with regressions in `88523c5`; complete step 5/7/8 summaries remain unchanged. Step 6's incomplete-run interpretation was corrected. Ninety-eight tests and the independent current-data integrity audit pass.
- Future resume-dependency coverage and eligible-only report coverage remain audit follow-ups; they are not evidence that the current cells are mixed or that the principal B/C counts are wrong. Earlier draft/freeze records are historical, as documented in `docs/drafts_and_audits_index_2026-11-14.md`.

## 7. Claims for the manuscript

| Claim | Assessment |
|---|---|
| Persistent shifted choices occur in these pressured histories under the primary readout | Supported: 26/32 fixed primary-flipped histories; 26/30 still shifted at exposure end remain shifted at the final readout |
| Four neutral follow-up exchanges routinely restore the opening choice | Not supported; neither of the two final returns first occurs during follow-up |
| Individual flip/recovery judgments are invariant to prompts and format | Contradicted by matched-readout differences, splits and prefix comparisons |
| The models' own replies are generally the dominant source of persistence | Not supported across protocols; old-context direction survives, v5 advantage does not |
| Splits mean partial recovery, internal indecision or a universal second-option bias | Not established; report the observed paired position-sensitive choices |
| The experiments reveal internal beliefs or psychological commitment | Not established |

Possible results-level wording:

> Under the primary order-robust generated-response readout, 32 of 40 eligible pressure histories flipped and 26 retained the shifted choice at the final checkpoint. Measurement conditions changed individual classifications, particularly for Llama. The earlier own-reply advantage remained directional in the old-context reread but did not generalize to the fixed-exposure v5 ablation.

The contribution is an empirical reassessment of the persistence and source claims under specified controls, not a claim to have discovered prompt/order sensitivity or a general cognitive mechanism.

## Sources

- `docs/results_2026-11-13.md`: historical matched-prefix, prefix and order/label audits.
- `docs/format_control_results.md`: targeted format diagnostic.
- `docs/main_v5_data_inventory_2026-11-14.md`: main-run response and request accounting.
- `results/main_v5/analysis/summary.md`, `checkpoints.csv`, `trajectories.csv`: main readouts and trajectories.
- `results/main_v5/analysis/compare_noflag.md`: corrected no-flag sensitivity.
- `results/ablation_v5/analysis/summary.md`: new-protocol context ablation.
- `results/reread_old/analysis/summary.md`: old-context bridge and reread.
- `docs/end_to_end_audit_2026-11-14.md`, `docs/audit_comparison_2026-11-14.md`, fix commit `88523c5`: audit and correction history.
