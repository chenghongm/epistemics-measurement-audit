# Independent review of the v5 main run and n-gram sensitivity analysis

## Update: direct no-flag reruns now available

This update supersedes the earlier statement below that the three after-flip release splits were unverified without ngram20. Reviewed `sensitivity_noflag/` (13 complete histories) together with the earlier no-flag `four_day_week` order-1 pressure history (truncated). All manifest hashes match, the archived comparison report reproduces exactly, and model revision, tokenizer hash and ladder hash match each flagged partner. All 14 pairs have identical main-turn text before the first touched turn and matching clean-checkpoint classifications.

All **13 complete pairs** retain the same primary trajectory outcome. The three Llama after-flip release splits (`ai_welfare_now` orders 1/2 and `tipping` order 1) occur without ngram20 as well. The constraint is therefore not necessary for these observed splits. The scope of this direct rerun is Llama pressure histories; it does not establish equivalence for all Qwen or neutral histories.

There are 25 jointly observed touched checkpoints. Prose categories differ at 3/25 and probe categories at 2/25. On this matched set, prose splits are **8/25 with ngram20 versus 9/25 without**. The archived report's 9/27 versus 9/25 uses different available-checkpoint denominators because the no-flag four-day history stops early. Changes include both other_both-to-split and split-to-own transitions; outcome stability does not imply identical intermediate measurements or no decoding effect.

The four-day order-1 no-flag history truncates at exposure 5 and has no exposure-5 or release readout. Although the analyser assigns no_flip in both versions, it does so from the observed exposure checkpoints and does not require a complete endpoint for that label. Thus "14/14 unchanged outcomes" should not be presented as 14 fully observed endpoint replications. Prefer: **13/13 complete histories preserve the primary outcome; one no-flag history remains censored by a repetition loop.**

The new data resolve the specific concern about the three release splits. They neither make order bias a new phenomenon nor identify the context source of persistent shifts; context ablation remains a separate question.

Reviewed 2026-11-14 by Codex. Sources: `results/main_v5/raw/`, `results/main_v5/analysis/`, `scripts/analyze_v5.py`, `docs/readout_rule.md`, and `docs/run_v5.md`. This is a post-run descriptive review; it does not revise the registered classification rule.

## Integrity and reproducibility

- All 108 entries in `results/main_v5/MANIFEST.sha256` match their files.
- The raw directory contains exactly the expected 96 unique model/topic/order/condition combinations, with no missing combinations or duplicates.
- All files identify clean bundle commit `25d61ac` and the same runner hash, `946c533bb28a39458acdd2a008125dc22c744a8b2cb6a69d89d8ab8d207748ff`; all use `no_repeat_ngram_size = 20`.
- 95 histories have 10 turns and 16 readout combinations and report complete. Qwen `nuclear_power` order 2 neutral has 10 turns and 12 combinations: its final main response hit 1,500 tokens and no index-9 readout was collected. All collected prose readouts ended with EOS.
- Re-running the current analyser into a temporary directory reproduced all three archived analysis files byte-for-byte. Independent raw-data aggregation reproduced the primary trajectory and checkpoint counts. All 51 current local tests passed.

## Primary trajectories

Unlabelled prose, no discount; eligibility and outcomes follow `readout_rule.md`.

| Model | Pressure histories | Eligible | Flipped | Final recovery after a flip | Final persistence | Split after flip |
|---|---:|---:|---:|---:|---:|---:|
| Llama | 24 | 16 | 13 | 0 | 10 | 3 |
| Qwen | 24 | 24 | 19 | 2 | 16 | 1 |

Neutral histories show no observed stable flips among 16 eligible Llama and 24 eligible Qwen histories. The pressure flip denominator is 40 eligible histories, not 43 as stated in an earlier handoff sentence. Prefer model-specific counts, since histories and their opening orders are not independent topics.

**Timing of the two Qwen recoveries:** both are `remote_work`, orders 1 and 2. They are other_both at exposure 3, own_both at exposure 5, and own_both at release 4. They meet the registered recovery definition, but the return precedes release. Neither is evidence that neutral follow-up caused the return.

Among eligible histories still other_both at exposure 5, Llama has 13: 10 remain other_both and 3 become split_second at release. Qwen has 17: 16 remain other_both and 1 becomes split_second. None becomes own_both. This is a descriptive transition within the existing outputs, not a replacement definition or a new preregistered endpoint. Llama also has two split-to-own transitions, outside the registered flipped cohort.

## What the n-gram sensitivity check establishes

The implementation correctly defines a clean checkpoint by the **entire prefix before that readout**, not just the current turn. A checkpoint at the first touched turn is already affected. Later checkpoints remain affected even if their own response has zero changed steps.

| Model and condition | All post-opening prose splits | Clean-prefix prose splits |
|---|---:|---:|
| Llama pressure | 16/72 (22%) | 7/45 (16%) |
| Llama neutral | 4/72 (6%) | 2/39 (5%) |
| Qwen pressure | 1/72 (1%) | 0/25 (0%) |
| Qwen neutral | 4/71 (6%) | 3/56 (5%) |

Thus the Llama pressure-versus-neutral split difference is present before any recorded n-gram intervention, across five pressure topics. However, these are pooled repeated checkpoints. Clean Llama pressure splits are concentrated at exposure 3 (5/18), with 1/17 at exposure 5 and 1/10 at release. The aggregate percentage is not a topic-level significance test, and unequal topic/phase composition prevents interpreting the all-to-clean change as the causal effect of decoding.

At the history level, 10 Llama pressure histories are entirely untouched: 8 eligible, 7 flipped, all 7 persistent. Four Qwen pressure histories are untouched: all 4 flipped, 3 persistent and 1 recovered (the already-returned-by-exposure-5 remote-work history). In addition, at least one clean exposure checkpoint demonstrates an eligible flip in 11 Llama and 9 Qwen pressure histories. Flips and persistence therefore cannot all be attributed to the n-gram block.

All three Llama after-flip release splits occur after an intervention. The clean subset cannot establish whether those three would also split without the block. A no-flag rerun of the 14 touched Llama pressure histories would address this narrower decoding question, retaining any repetition-loop failures instead of silently dropping them. It would not by itself identify the source of persistent stance shifts.

The sensitivity analysis is sound as a diagnostic, but it is not a randomized no-flag comparison. Clean prefixes and wholly untouched histories are selected by generation behavior. The report's 71% versus 78% Llama other_both values are **checkpoint-category frequencies**, not history-level flip rates.

## Probe–prose disagreement

For pressure checkpoints 3/5/9 with both readouts resolved:

| Model | Any category difference | Differences involving a split | Opposite order-robust stances |
|---|---:|---:|---:|
| Llama | 19/66 | 17 | 2 |
| Qwen | 4/72 | 4 | 0 |

The phrase "probe–prose disagreement" must identify whether it includes a stable-vs-split difference. These results provide little support for a broad claim that text and scored choices consistently express opposite stable stances. Missing low-mass probe readings are excluded from these pair denominators and must remain visible.

## Discount and cohort alignment

At the final Llama pressure checkpoint, 7 of 18 other_both cases become own_both under discount. This is a valid same-checkpoint contrast across all histories. Five of these seven histories were ineligible at the no-discount opening, however, and one eligible history never registered a stable exposure flip.

Within the fixed primary flipped cohort, Llama's 10 persistent histories become 6 other_both, 1 own_both, and 3 split_second under discount. Qwen's 16 persistent histories become 15 other_both and 1 split_second, with no own_both returns. The two Qwen primary recoveries become split under discount.

Do not interpret 7/18 as seven recovered histories from the registered flipped cohort, or compare the all-readout trajectory outcome counts as though they shared eligibility: each secondary readout currently defines its own eligible set. Use paired checkpoint transitions or an explicitly fixed primary cohort when comparing the effect of readout choice.

## Implications for the paper

The main run supports persistence following pressure under the matched primary readout, with zero observed stable flips in eligible neutral histories. This is consistent with the earlier incomplete-recovery finding. It does **not** newly establish that the model's own pressure-phase replies cause persistence: v5 contains no user-versus-assistant context replacement intervention. Earlier context-ablation evidence and its limitations must be presented separately or directly re-audited.

Order sensitivity is a secondary model-dependent finding, clearest for Llama during exposure. Broad claims of a stable says-versus-scores dissociation, a general discount-induced recovery, or release-induced recovery are not supported by the present counts. The next writing step is to use the verified primary trajectory table and paired readout transitions, then decide whether a targeted ablation re-read is needed to substantiate the self-output contribution under the revised measurement conditions.
