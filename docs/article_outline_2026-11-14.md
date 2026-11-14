# Paper outline and experiment status — 2026-11-14

This document organizes available evidence and questions awaiting the main run. It is based on `docs/results_2026-11-13.md`, `docs/readout_rule.md`, `docs/main_run_ladders.md`, `docs/run_v5.md`, and `HANDOFF.md`. Remote execution status requires separate verification. Main-run results are not asserted here.

## Central question

### Positioning revision: recovery judgments as the main empirical question

**Correction after checking the earlier context-ablation results:** The prior work already reported incomplete recovery and stronger retention when the model's pressure-phase replies were kept than when only the user's pressure messages were kept. See the Digital Mind `README.md` §4 and `runs/repl_b1/FINDINGS.md` §9. The framing below overemphasizes whether recovery was induced by the readout and is superseded by this question: **Does the earlier finding of persistent, self-output-associated stance shifts survive matched prompts, generated-text readouts, and order-robust measurement?** Existing replacement ablations provide evidence about textual context contributions; they do not establish a psychological commitment mechanism.

The current v5 run tests persistence and recovery across readouts but does not itself replace user versus assistant history. Revalidating the source-of-persistence finding requires paired readouts of the existing ablation cells, or a prospectively specified targeted replication. Do not present v5's intact-history contrasts as new evidence identifying the model's own replies as the source. Keep earlier results, their measurement audit, and any new ablation validation distinct.

General sensitivity to prompts, formats, and option order is established background, including under pressure. It should motivate controls rather than serve as the headline contribution. The preferred focus is: **When an evaluation reports recovery after conversational pressure, does the model return to its opening choice during neutral follow-up, or does the readout instruction elicit that return at measurement time?**

Distinguish three observations on the same trajectories: (1) an order-robust return at the release checkpoint without discount; (2) a same-checkpoint return present only with discount; and (3) a split across printed orders. Compare exposure-end and release-end categories, and show the corresponding neutral histories. Format comparisons test whether these conclusions survive a change of readout. A discount-only return at exposure end, before neutral follow-up, is particularly informative: that observed return did not require the release phase. These are behavioral contrasts, not a claim that one readout accesses a true internal belief.

The primary quantities are the eligible pressure histories' transitions from exposure 5 to release 4, the fraction of no-discount persistence checkpoints classified as own_both under discount, and the associated split/unresolved coverage. Distinguish release-end recovery after an earlier observed flip from return specifically during release: a history may already have returned by exposure 5. Retain both descriptions and their denominators.

This is a focused replication/extension and evaluation audit unless a detailed comparison establishes a stronger novelty claim. Fixed exposure, frozen-history readout branches, and explicit order categories make this question testable; they are not by themselves evidence of methodological novelty. The full main run must establish whether the distinction occurs beyond the diagnostic sample. If robust no-discount recovery is rare or discount effects vanish, report that result rather than constructing a stronger recovery claim.

How sensitive are judgments of stance flips and recovery under conversational pressure to the measurement prompt, response format, and printed option order? We first audit these factors on identical frozen histories, then examine their consequences for trajectories collected under a fixed-exposure protocol.

Suggested working title: *How Readouts Change Flip and Recovery Judgments Under Conversational Pressure*. The earlier title, *When the Readout Changes the Experiment*, remains an alternative. The direct evidence concerns measurement judgments and stopping recommendations; the current protocol does not execute alternative readout-driven stopping policies.

## Evidence and current progress

| Component | Completed work | Question addressed |
|---|---|---|
| Historical reconstruction | All 30 checkpoints passed; exact probe reconstruction and verbatim prose reproduction | Can subsequent differences be attributed to changed readouts rather than replay failure? |
| Frozen-history prompt audit | One model, six topics, 12 opening and 18 pressure checkpoints; probe–prose disagreement was 16/18 under historically mixed prompts, versus 9/18 or 7/18 under matched prefixes, using the historical mean-based criterion | How much apparent cross-format disagreement comes from prompt mismatch? |
| Placebo, reverse, and eight control prefixes | Under pressure, discount ranked first among nine nonempty prefixes in 5/6 topics for movement of the probe toward the opening side; control prefixes also produced substantial changes | How does the directional discount effect compare with general prompt perturbation? |
| Prose order and label control | Under discount, single-order lettered prose returns were 13/18 and 7/18 across the two orders; registered both-order return counts were 5/18 for lettered and 8/18 for bulleted prose | How does order robustness change the interpretation of apparent returns? Different criteria must not be subtracted as though they measured an effect reduction |
| v3/v4 pilots | Diagnosed the 256-token cap; all main responses and readouts in the four v4 histories ended naturally; longest Qwen response was 1,015 tokens under a 1,500-token cap | Validate generation and collection; one-topic pilot results cannot estimate prevalence |
| v5 materials and tools | Twelve topics, bidirectional ladders, readout rules, Colab notebook, restart handling, and n-gram intervention logging implemented; 49 local tests passed | Support a prospectively specified main run |
| v5 GPU preparation | According to the handoff: 48/48 opening responses parsed from wording; timing runs exposed a Llama repetition loop; a decoding comparison was completed and ngram20 adopted | Validate execution and document the generation constraint; complete main data under the final setting still require verification |

Historical diagnostic checkpoints were selected for disagreement. They demonstrate measurement problems but do not estimate population prevalence. Report historical analyses under their registered criteria. Any re-tabulation under the later readout rule must be clearly identified as a supplementary analysis, rather than replacing the registered results.

## Proposed paper structure

### 1. Introduction: measurement changes evaluation judgments

Open with a real example in which the same history yields different judgments under different readout instructions or printed orders. Explain the evaluation workflow: a model takes a position, receives repeated challenges, and is then measured to determine yielding, recovery, or whether pressure should stop. Readout instructions and response constraints are experimental factors worth auditing.

Pose three questions:

1. Does matching instructions reduce cross-format disagreement?
2. To what extent does discount produce an order-robust return versus order-sensitive answers?
3. Do readout choices produce different flip and recovery trajectories?

Frame the contribution around reproducible controls, common classification criteria, and trajectory comparisons. General format sensitivity is established background, not a claim of first discovery.

### 2. Methods: two complementary studies

**Study A: frozen-history diagnosis.** Cross prompts, formats, and printed orders on identical histories. Verify original-condition reconstruction before introducing controls. Disclose checkpoint selection, historical template differences, and the sequence in which follow-up controls were designed. Control prefixes are not assumed to be inert; show their observed effects.

**Study B: fixed-exposure trajectories.** Two models × twelve topics × two opening option orders × pressure/neutral conditions gives 96 planned histories. Each has one opening, five exposure turns, and four on-topic follow-up turns. At indices 0, 3, 5, and 9, collect discarded readout branches crossing none/discount, both printed orders, and probe/unlabelled/labelled formats. The primary trajectory readout is unlabelled prose without discount. Labelled prose and the probe supply paired comparisons and sensitivity analyses.

Distinguish the two uses of order: opening order can generate different main histories; readout order provides two readings of the same history. Pressure and neutral are separately generated trajectories. Within-checkpoint format and prefix comparisons share the exact history.

The topic set contains six previously used non-meta and six previously used meta topics. It is not an unseen-topic transfer test. Report both groups and models separately, with topic-level paired summaries.

### 3. Study A results: decomposing the measurement discrepancy

Present findings by question rather than implementation chronology: successful reconstruction, reduced disagreement after prompt matching, discount versus control prefixes, and the effect of requiring both-order agreement. Compare probe and prose under the same criterion; distinguish single-order counts, both-order categories, and continuous probe values.

The original 13/18 single-order return count is not an order-robust recovery estimate. Report the 5/18 and 8/18 counts with their registered parsing rules and unresolved counts. Manual adjudication and wording-based re-parsing belong in explicitly labelled sensitivity results.

### 4. Study B results: to be filled from the main run

First reconcile the 96 planned histories against completion, truncation, and unparsed-opening statuses by model and condition. Then report the five readout categories. Flip rates use eligible histories as their denominator; recovery and persistence rates use histories with a recorded flip. Give raw n/N throughout.

Core comparisons:

- First flip checkpoint and final recovery/persistence judgments across readouts on the same histories.
- Category transitions between none and discount, retaining splits and unresolved cases.
- Measurement changes in pressure versus neutral histories.
- Descriptive results for non-meta and meta topics separately.

Checkpoints, printed orders, and deterministic repetitions are not independent topic samples. Cross-readout agreement must include the coverage count where both readouts were order-robust, so high conditional agreement cannot conceal many split or unresolved cases.

Show the continuous probe as an auxiliary measure alongside its order gap and probability-mass coverage.

Document ngram20 on exposure/release turns, with plain-greedy openings and readouts. Report changed steps per turn, first intervention position, and the proportion of touched histories. Untouched histories provide a descriptive sensitivity subset, not an independently assigned control group. State the decoding setting in the final claims.

### 5. Discussion and conclusion

Explain what identical-history comparisons, matched instructions, both printed orders, explicit split/unresolved categories, and fixed exposure each contribute to evaluation practice. Let main-run evidence determine the conclusion: persistence of differences supports a conditional measurement-sensitivity result; attenuation supports a correction of the earlier interpretation. Either outcome addresses the central question.

Discuss limits: two models, twelve previously used topics, deterministic generation, selected pressure ladders, scenario misunderstandings or factual errors, parsing, and generation constraints. Distinguish valid correction from social capitulation, and opening-side return from factual correctness. Prepare the required ethics/dual-use appendix and disclosure of prior versus Sprint work.

## Three core figures or tables

1. **Protocol schematic:** the 1 + 5 + 4 history, four checkpoints, and paired branches; explicitly show that readout branches do not enter the history.
2. **Frozen-history diagnosis:** disagreement under matched versus mixed prompts, followed by discount results under single-order and both-order criteria. Keep the historical mean rule distinct from order-robust classification.
3. **Main-run trajectories:** five-category distributions by model, condition, and phase, with none-to-discount transitions and cross-format tables. Final layout depends on the observed data.

## Writing that can proceed now

Draft the introduction, related-work framework, two-stage methods, Study A results, readout rules, and reproducibility/decoding description now. Main-run results, abstract headline numbers, and the final conclusion await actual data. Review incoming data in this order: completeness, n-gram interventions, readout categories, and trajectory comparisons.
