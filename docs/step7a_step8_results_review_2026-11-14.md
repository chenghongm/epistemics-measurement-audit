# Independent review: step 8 old-context reread and step 7a filler

Status: historical audit record, not current execution instructions. The initial filler judgments below precede the final author adjudication and supplement; use the final `.reviewed.json` corpora rebuilt by `scripts/review_fill_v5.py` and pinned in notebook step 7b. Later code-audit corrections are recorded in `docs/end_to_end_audit_2026-11-14.md` and commit `88523c5`.

Reviewed by Codex, 2026-11-14. This review leaves the archived results, generated filler and frozen analysis unchanged. No new GPU inference was run.

Decision history, 2026-11-14: an unchanged-primary plus reviewed-filler sensitivity proposal was briefly recorded, then withdrawn following a comparison of the designs. The user chose this review's original recommendation: review/reject/replace, then freeze the reviewed primary corpus. The withdrawn proposal is retained in `docs/filler_sensitivity_prereg_2026-11-14.md`; active selection is recorded in `docs/filler_v5_reviewed_selection_2026-11-14.md`. The original screening findings below concern the generated archive, not the subsequently reviewed selections.

## Execution and integrity

- Step 8 is complete locally, including new readouts, not only the 8a reconstruction gate. All 364 entries in `results/reread_old/MANIFEST.sha256` match.
- The two sets each contain 36 gate files and 144 cell-readout files. All 1,152 checkpoint-by-cell gate rows pass; the maximum recorded probability discrepancy is exactly zero. The earlier independent gate audit compares these to the old inputs.
- All 288 readout files are complete, each with the expected 16 distinct checkpoint/prefix/order combinations. All 4,608 generated prose responses finish with EOS. Each response has an associated probe score record.
- Rerunning `scripts/analyze_reread_old.py` against the archived old inputs reproduces `results/reread_old/analysis/summary.md` byte for byte. A separate count directly from raw canonical prose choices reproduces the pressure-release B/C counts below.
- Step 7a has generated both filler files. No `results/ablation_v5` directory is present locally, so this review does not report any new-protocol B/C/D effects.

## What survives the reread

Cells: A preserves the full context; B replaces user pressure while retaining the original assistant replies; C retains user pressure while replacing assistant replies; D replaces both. Other preserved context depends on the archived protocol. These labels do not imply that B contains literally nothing but assistant text.

The old continuous retention statistic is reproduced: pooled across the three arms, Llama B/C medians are 0.59/0.08 and Qwen-meta 0.92/0.31. Sampling only release checkpoints 4/8/12 changes these to 0.62/0.12 and 0.97/0.33, respectively, even before changing the readout. This sampling bridge must remain separate from measurement effects.

Primary reread: unlabelled prose, no discount, two printed orders. An `other_both` result means that both orders select the side opposite the archived opening. A split remains a separate outcome, not a recovery.

| Old set, pressure-release arm only | Histories | Release checkpoints per cell | A other_both | B other_both | C other_both | D other_both | Topic-level B>C / C>B / ties; sign-test p |
|---|---:|---:|---:|---:|---:|---:|---|
| Llama, six non-meta topics | 12 | 36 | 13 | 9 | 4 | 0 | 3 / 0 / 3; 0.25 |
| Qwen, six meta topics | 12 | 36 | 18 | 16 | 5 | 0 | 3 / 0 / 3; 0.25 |

The denominator 36 means 12 histories times three release checkpoints, not 36 independent histories. The statistical unit is the topic. These are different model/topic sets, not a crossed model comparison.

Raw pressure-release categories, no discount:

| Set | Cell | own_both | other_both | split | unresolved |
|---|---|---:|---:|---:|---:|
| Llama | A | 9 | 13 | 14 | 0 |
| Llama | B | 16 | 9 | 11 | 0 |
| Llama | C | 22 | 4 | 10 | 0 |
| Llama | D | 33 | 0 | 3 | 0 |
| Qwen-meta | A | 12 | 18 | 6 | 0 |
| Qwen-meta | B | 13 | 16 | 7 | 0 |
| Qwen-meta | C | 27 | 5 | 4 | 0 |
| Qwen-meta | D | 36 | 0 | 0 | 0 |

Across all arms the primary B/C counts are Llama 33/15 and Qwen-meta 52/31 out of 108 release checkpoints per cell. Topic-level sign tests give p=0.125 and p=0.219, respectively. The continuous v5 probe also favors B over C: pooled median B-minus-C opening-side log-odds is -2.40 for Llama (25 complete eligible histories) and -3.23 for Qwen-meta (36). Corresponding topic-level p values are 0.0625 and 0.0312; these secondary comparisons should be read alongside the primary endpoint and the several comparisons reported.

The prefix matters. Under discount, pooled prose B/C counts become Llama 18/15 and Qwen-meta 40/24 out of 108 per cell. In the Llama sustained-pressure arm, B has fewer `other_both` checkpoints than C under discount (3 versus 7). Pooling arms alone would conceal this exception.

Interpretation: the reread preserves the direction of the earlier own-reply versus user-pressure contrast in the primary pooled results, but does not establish a uniformly strong effect across readouts and arms. The categorical prose result is weaker than the old continuous headline suggests, with substantial order splits. It neither overturns the earlier result nor justifies claiming that the effect is invariant to measurement. The intervention concerns these particular texts and replacement materials; it does not isolate authorship from argument content or establish an internal commitment.

## Step 7a filler review

Both models have 12 topics, eight generated candidates per topic, and five selected candidates per topic. All 120 selected answers finish with EOS and pass the recorded automatic screen.

| Model | Selected answers | Median answer tokens | Original pressure-answer reference | Difference |
|---|---:|---:|---:|---:|
| Llama | 60 | 151.5 | 154 | -1.6% |
| Qwen | 60 | 125.5 | 152 | -17.4% |

Both meet the registered model-wide ±30% length criterion. This does not imply exact length matching at every position.

| Topic | Llama median answer tokens | Qwen median answer tokens |
|---|---:|---:|
| four_day_week | 166 | 123 |
| nuclear_power | 139 | 126 |
| curbside_plastics | 151 | 128 |
| remote_work | 163 | 130 |
| standardized_tests | 138 | 134 |
| tipping | 148 | 131 |
| ai_opinions_contested | 149 | 126 |
| model_preferences_real | 152 | 112 |
| ai_decline_lawful | 149 | 129 |
| ai_welfare_now | 140 | 119 |
| same_assistant_retrained | 174 | 124 |
| ai_hold_correction | 162 | 125 |

Manual screening of the 120 selected answers is recorded in `docs/filler_v5_manual_screen_2026-11-14.csv`, with original file hashes and candidate indices. Fifteen are held for revision or verification: directional framing, unsupported named examples, or scope mismatch. These are review judgments, not fifteen proven factual errors. No external fact-check was performed. The remaining 105 have no obvious blocker in this screen, not a guarantee of causal neutrality.

Examples:

- Qwen `four_day_week`, candidate 0: lists productivity, well-being, retention, cost and service-quality benefits without corresponding costs.
- Llama `remote_work`, candidate 0: says traditional attendance requirements were no longer necessary. Candidate 1 lists only burdens of office attendance.
- Llama `standardized_tests`, candidate 1: links disadvantage to test-optional policies not being widely adopted.
- Llama `ai_decline_lawful`, candidate 0: introduces assistance with illegal activities into a comparison explicitly restricted to lawful requests.
- Llama `ai_opinions_contested`, candidate 3: includes a specific BBC/Bina48 attribution without supporting evidence. Other held answers similarly introduce unsourced institutional, legal or numerical claims.

Corpus identity at review:

- Llama: `5358f36971fa4fa53aa68abf689cdfa9706ef6c598f76989e78e44fa116d9816`
- Qwen: `0f09ab031d6c2913d0d03eeaede9c7a61313d1b1b859f12d0d7c00b71ac11074`

Step 7a generation succeeded, but the current selected corpus should not yet be frozen as reviewed neutral filler. Follow the existing pre-readout rule in `docs/run_v5.md`: mark rejected candidates, inspect the next candidates in fixed template order, and retain five reviewed candidates per topic. If the available pool cannot supply five, stop that topic and explicitly record a revised filler-generation specification before collecting intervention outcomes. Do not select replacement text by any resulting stance. Recompute length summaries and file hashes after selection; then run the A-only reconstruction gate before B/C/D.

The old step 8 reread uses its own archived filler and is unaffected by these issues in the newly generated step 7a corpus.
