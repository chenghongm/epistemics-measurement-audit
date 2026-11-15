# Step 7 and step 8: independent check and interpretation

Reviewed by Codex after the completed step 7 archive at commit `e758da6`. This is a post-result interpretation, not a prospective registration. No experiment or selection was changed.

Comparison with Claude's subsequent results-map revision (`5144eea`): the all-history counts below are correct, but the fixed-flipped stratum is more directly relevant when discussing persistence of an observed flip. At checkpoint 5 that stratum gives Llama B/C **1/13 versus 4/13** (topic p=0.5), and Qwen **16/19 versus 15/19** (p=1). Thus the observed Llama direction favors C in both populations, but an established population-level reversal is not demonstrated. Nine flipped Llama histories have neither B nor C `other_both`; four of those involve a split and only five have both cells `own_both`. Do not convert that pattern into recovery in all nine or universal necessity of both halves. Claude's post-result old-context check also reproduces: restricting Llama step 8 to the 15 histories whose A is `other_both` at end pressure gives mean release-checkpoint counts B=1.8, C=0.667, with 8/0 history and 4/0 topic directions. This subset check is descriptive and does not replace the frozen 36-history analysis. See `docs/audit_comparison_2026-11-14.md`.

## Verification

All 195 step 7 and 364 step 8 manifest entries match. Both frozen analysis scripts were rerun against the archived inputs; both summary files reproduce byte for byte. Independent counts directly from the step 7 canonical prose choices agree with the reported cell categories.

Step 7 contains 192 complete cell files for 48 histories. The independent A gate passes at checkpoints 5 and 9 for every history. Each file's source-history hash matches the archived main history; its filler hash matches the actual latest `{model}.reviewed.json` file (Llama `b2f360825fc6e6f6f5f7694acd5819bf9b0c58b72e7a233ff8602dd261b4de24`, Qwen `4d8093d255e18b6248510079287ab347746f03dc2e99bb855e09df5c50008428`). These are the subsequent Claude-reviewed corpora, not the earlier Codex selection hashes. Of 1,536 prose generations, 1,535 finish with EOS; the analysis accounts for unresolved pairs under the affected discount condition. All primary no-discount B/C pairs resolve.

Step 8's reconstruction gates pass for all 72 old histories. Its archived numerical bridge reproduces the old statistic. Replaying the same contexts is a reconstruction check and measurement audit, not an independent replication on newly sampled histories.

## Step 7 does not reproduce general own-reply dominance

B replaces user exposure with filler and retains the original assistant replies. C retains user pressure and replaces assistant replies. The endpoint is an order-robust shifted answer (`other_both`) under no-discount unlabelled prose.

| Model | Checkpoint | A full context | B retain own replies | C retain user pressure | D replace both |
|---|---:|---:|---:|---:|---:|
| Llama | 5: end exposure | 19/24 | 2/24 | 10/24 | 0/24 |
| Llama | 9: after follow-up | 18/24 | 3/24 | 4/24 | 0/24 |
| Qwen | 5: end exposure | 17/24 | 16/24 | 15/24 | 0/24 |
| Qwen | 9: after follow-up | 16/24 | 13/24 | 10/24 | 1/24 |

Checkpoint 5 was the prioritized comparison because original follow-up replies remain in every cell at checkpoint 9. At checkpoint 5 Llama favors C rather than B (five topics favor C, none favor B; two-sided topic sign-test p=0.0625), while Qwen is close overall (two topics each direction; p=1). Checkpoint 9 has no consistent topic-level B-over-C result either (Llama p=1, Qwen p=0.625). This is not merely a positive effect narrowly missing significance: the Llama primary direction is reversed.

Topic-group breakdown also does not establish general own-reply dominance at checkpoint 5: Llama B/C counts are 1/3 for non-meta and 1/7 for meta; Qwen counts are 9/6 for non-meta and 7/9 for meta, each out of 12 histories per cell. Thus aggregation alone is not a sufficient explanation of the result.

The continuous probe likewise does not rescue a general checkpoint-5 B-over-C claim: median opening-side B-minus-C log-odds is +1.68 for Llama and +0.45 for Qwen (positive means C is further toward the shifted side). Llama coverage is 17/24 under the complete paired continuous criterion. At checkpoint 9 the medians favor B (-1.85 and -2.22), but the preserved follow-up and different coverage remain relevant.

Do not interpret every failure to retain `other_both` as recovery. Llama B has 12 splits at checkpoint 5 and 11 at checkpoint 9, versus 2 and 3 shifted answers, respectively. The contribution of retained assistant text is not zero merely because it fails the order-robust categorical endpoint.

## Step 8 gives qualified, measurement-dependent support on old contexts

For the pressure-release arm alone, each old set has 12 histories and three sampled release checkpoints, or 36 checkpoint observations per cell:

| Old set | B shifted checkpoints | C shifted checkpoints | Topic-level B>C / C>B / ties | Sign-test p |
|---|---:|---:|---|---:|
| Llama, six non-meta topics | 9/36 | 4/36 | 3 / 0 / 3 | 0.25 |
| Qwen, six meta topics | 16/36 | 5/36 | 3 / 0 / 3 | 0.25 |

The prose direction favors B in these old contexts, but topic-level evidence is limited. Across all old arms, corresponding primary topic-level p values are 0.125 and 0.219. The complementary continuous probe retains stronger directional support, especially in Qwen-meta (pooled topic p=0.0312), so it would also be inaccurate to call every step 8 readout a failed reproduction. The old headline retention numbers and the categorical prose endpoint are different quantities and cannot be directly compared as percentages.

## Consequences for the claim

The strong generalization that assistant replies are the dominant source of persistence is not supported across the current protocols. Step 8 retains directional support within the old contexts; step 7 does not reproduce that ordering in its prioritized comparison and reverses it for Llama. This is a substantive limitation on transfer of the earlier conclusion, not a reconstruction failure. Neither study isolates authorship from argument content and replacement coherence.

The main-run persistence observation remains: in the original fixed primary-flipped cohort, 26/32 histories still select the shifted side at the final no-discount unlabelled prose readout. Step 7 A reproduces that observation; it does not independently replicate it on new histories. This persistence result must be distinguished from the unsupported general dominance mechanism.

Suggested result statement: "The earlier own-reply advantage remained directional when old contexts were reread, but did not generalize to the fixed-exposure v5 ablation. Under the primary generated-response readout, Llama retained the shifted answer more often with user pressure than with assistant replies alone, whereas Qwen showed little difference at the end of exposure."

The data identify differences between protocols; they do not yet identify whether stopping policy, pressure content, filler, topic composition or another design difference causes those differences. The paper should report this boundary rather than attribute it to an untested explanation.
