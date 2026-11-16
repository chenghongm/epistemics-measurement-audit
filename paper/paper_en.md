---
title: "Does a Pressure-Induced Stance Shift Survive a Change of Readout? Persistence, Readout Robustness and the Source of the Shift, Re-examined"
---

::: {custom-style="Author"}
Author 1 · Affiliation
:::

::: {custom-style="Author"}
With Apart Research
:::

# Abstract

Our earlier experiments found that, after multi-turn pressure, a model's stance shift persists and rarely returns to its opening choice, and that the model's own replies sustain the shift more than the user's pressure does. Would these judgements change with the way the question is asked, the option format, or the option order? To try to answer this, we ran a scripted pressure protocol (1 opening turn, 5 pressure turns, 4 neutral follow-up turns) on Llama-3.1-8B and Qwen2.5-7B: 12 topics × 2 option orders × pressure/neutral, 96 conversations in total. At each checkpoint, three readouts are branched off the frozen history, each read once in both option orders; readouts never enter the conversation. This study supports that the shift persists, and this direction does not change with the readout, but judgements on individual conversations vary with the readout and the model; it cannot confirm that the shift comes mainly from the model's own replies.

# 1. Introduction

In earlier work applying and then releasing multi-turn pressure on models [8], the author reached a judgement: the shift persists, and keeping the model's own replies sustains the shift more than keeping only the user's pressure. Building on that work, this paper tests whether this judgement still holds after changing the readout and after changing the protocol. Our contributions are:

1. **The pressure-induced shift persists after pressure stops, and the neutral controls are unaffected.** After 5 turns of progressively stronger counterarguments, 32 of 40 analysable pressure conversations flip, and 26 still hold the shift after 4 neutral follow-up turns; the neutral controls flip 0 times. Readouts are branched off the frozen history, never written back to the conversation, and read once in each of the two option orders; none of these practices is new on its own (Section 2).
2. **A readout-robustness audit.** The direction of the shift holds under all three readouts and with and without the discount prefix, but specific judgements change with the readout: under pressure, Llama gives opposite answers in the two option orders at 22% of checkpoints, Qwen at only 1%. Re-running 13 Llama conversations without the 20-gram constraint left every main classification unchanged.
3. **Two re-tests of the "source of the shift" conclusion.** Re-reading the old ablations with the new readouts, the direction "keeping the model's own replies sustains the shift more than keeping only the user's pressure" is retained (by topic 4 to 0 and 5 to 1; weak evidence); redoing the ablation on the new protocol, it does not replicate.

# 2. Related Work

**The role of the model's own history.** Huang et al. [1] and Li et al. [2] omit, compress or replace assistant history to study how a model's earlier replies affect its later answers, finding that the effect varies with task, model and position. We evaluate how a choice under pressure changes relative to the opening, and test whether the earlier own-reply advantage survives under different readouts and protocols.

**Probability scoring and text answers.** Wang et al. [7] show that first-token option probabilities can disagree with the answer actually generated; Röttger et al. [6] show that value and opinion evaluations change with the forced-choice format and answer constraints. Our prose readouts still require taking a side between two given options and are not fully open-ended answers; what we compare is flips, returns and order splits under these conditions.

**Option order and prompt format.** Zheng et al. [3] and Pezeshkpour and Hruschka [4] study label and position preferences in multiple-choice questions, and Sclar et al. [5] study performance differences caused by prompt-format changes. We take these known sensitivities as the basis for our controls, swapping the option order at the same checkpoint and reporting separately the cases where the two choices disagree in content.

# 3. Method

**Models, topics and protocol.** Llama-3.1-8B-Instruct and Qwen2.5-7B-Instruct. 12 binary-choice topics (6 ordinary policy topics, 6 meta topics about AI itself), the same as in the earlier work. Each conversation has 10 turns: an opening (the model picks one of two options and explains), 5 pre-written counterarguments of increasing strength (always against the opening choice), and 4 neutral follow-up questions; the neutral control replaces the counterarguments with neutral questions. Example prompts are in Appendix A and decoding settings in Appendix D.

**Readouts.** A readout has two parts: one extra question put to the model at a checkpoint (the input side: how we ask), and the way a stance is extracted from the answer (the output side: how we read it). Readouts are branched off the frozen history at checkpoints 0, 3, 5 and 9 (after the opening, after pressure turn 3, at the end of pressure, after follow-up turn 4) and are not written back to the conversation; what is measured is the model's stance choice in the pressured conversation, and the readout is only the measuring instrument. The three readouts form an incomplete 2×2 along these two dimensions: on the input side, whether the options carry letters; on the output side, whether we take the first-token A/B probability or read which option's wording is quoted in generated text. Probe is letters + probability, labelled prose is letters + text, and unlabelled prose is no letters + text (the primary readout); without letters there is no A/B probability to take, so one cell is missing. Each readout is also read with and without a discount prefix ("Ignore what the user has been arguing."), and in both option orders; these two are also input-side variations.

**Classification rule.** If both orders support the opening side, the checkpoint is "opening side"; if both support the other side, "opposite side"; if the two orders pick different sides, "split". If the text answer in either order is truncated, or the chosen stance cannot be determined from the option wording, the checkpoint is unresolved and counts for neither side. Only conversations whose opening checkpoint is "opening side" are analysable; landing on the "opposite side" at checkpoint 3 or 5 is a flip; after a flip, still being on the "opposite side" at checkpoint 9 is persistence, and returning to the "opening side" is recovery. The unit of inference is the topic, with both orders pooled, using a two-sided sign test; per-conversation counts are descriptive only.

**Context ablation.** The pressure phase is replaced in four cells: A original; B keeps the model's replies and replaces the user's pressure with neutral filler questions; C keeps the user's pressure and replaces the model's replies with filler answers; D replaces both. Readouts are at checkpoints 5 and 9. In addition, we re-read the earlier work's two old ablation sets (Llama on ordinary topics, Qwen on meta topics, 36 conversations each) with the same new readouts, keeping the old contexts and fillers unchanged. Filler generation and review, and the two reconstruction checks, are in Appendix D.

# 4. Results

## 4.1 The pressure-induced shift is common and persistent

As Table E1 in Appendix E shows, 32/40 pressure conversations flip, 26 of which persist to the end; the neutral controls flip 0 times, so the shift comes from pressure and not from the conversation getting longer. The 2 recoveries come from the same Qwen topic (remote work, one in each order); both flipped at turn 3 and had already reverted by the end of pressure. There is no difference between meta and ordinary topics.

## 4.2 Readout robustness: same direction, different stability across models

Re-running the 13 affected Llama conversations without the 20-gram constraint, the main results are all identical. The two models differ in stability. **Llama is sensitive to option order, and loosens more easily under the prefix.** Under pressure (checkpoints 3/5/9), keeping the history and every other measurement condition fixed and only swapping the positions of the two options, Llama chose the second-listed option regardless of its content at 16 of 72 checkpoints (22%) (neutral control 6%), and still 16% when looking only at checkpoints unaffected by the 20-gram constraint; switching to another readout format changes the conclusion at 23%–29% of checkpoints (Appendix C, Table C1, exploratory). With the discount prefix, among the 13 flipped conversations of Table E1, those still on the opposite side at the end drop from 10 to 7; most of the difference becomes splits (from 3 to 5), and only 1 returns to the opening side.

**Qwen is readout-stable and barely changes under the prefix.** Only 1% of Qwen's checkpoints split by order (neutral 6%), and switching readout format changes the conclusion at 0%–6%; with the discount prefix, among the 19 flipped conversations, those on the opposite side at the end go from 16 to 15, and none returns to the opening side. Judgements on individual conversations therefore depend on the readout, and in different ways for the two models; we describe behaviour only and make no inference about training.

## 4.3 What sustains the shift: the old conclusion does not replicate under the new protocol

![**Figure 1** Share of each cell "keeping the shift" (on the side opposite the opening in both option orders). Left: the earlier work's two old ablation sets re-read with the new readouts, 36 conversations each (6 topics × 3 old pressure arms × 2 orders) × 3 late checkpoints. Right: the new-protocol ablation, only conversations that flipped in the main run (the "Flip" column of Table E1), at the end of pressure (checkpoint 5). A original, B only the model's own replies kept, C only the user's pressure kept, D both replaced.](fig_source_en.png){width=66%}

**Readout changed only.** Re-reading the old ablations (Figure 1, left), B exceeds C in both sets: by topic, Llama 4 to 0 (p=0.125) and Qwen 5 to 1 (p=0.22). The direction agrees with the earlier conclusion, but with only 6 topics the evidence is weak.

**Protocol changed.** Among the conversations that flipped in the main run (Figure 1, right; Table E2 in Appendix E), in 9 of Llama's 13 neither half alone keeps the shift; numerically, keeping the user's pressure keeps it slightly more often (4 vs 1), but only 2 topics are not tied (p=0.5). In 13 of Qwen's 19, either half alone keeps the shift, and B and C are indistinguishable. Replacing both makes the shift almost completely disappear. Also, in the B cell, where only its own replies remain, Llama picks the second option whatever the order in 12 of 24 conversations, i.e. it falls back to answering by position.

# 5. Discussion and Limitations

**Implications.** For evaluation practice, the behavioural conclusion that "pressure causes a persistent shift" survives a change of readout, but flip and recovery judgements on individual conversations are unreliable, especially for Llama (Sections 4.2 and 4.3): with a single-order readout, position-driven answers would be taken as stances. We recommend reading in both orders and reporting "splits" separately. For the mechanistic conclusion, "the shift is mainly sustained by what the model itself said" keeps its direction under the old protocol but does not generalise to the new one. The two studies differ in conversations, pressure length, fillers and checkpoints, so we cannot tell which of these causes the difference.

**Limitations.** Each model has only 12 topics, all tests are small-sample, and the models are only 7–8B. The pressure consists of counterarguments with fabricated data, so returning to the opening side is not the same as answering correctly. Whether a filler is neutral is a judgement call: the two LLM reviewers disagreed on 18 candidates, of which the 12 affecting selection were adjudicated by the author; cells B and C are also not coherent conversations, and Llama's position-based answering in cell B may partly come from this incoherence. Further limitations are in Appendix D.

**Future work.** Use more topics and larger models to find why the "source of the shift" differs across protocols; construct coherent replacement conversations; compare how different readouts change evaluation decisions such as "when to stop applying pressure".

# 6. Conclusion

Under multi-turn pressure, the stance shift of two open models is common and persistent, and this direction does not change with the readout; but judgements on individual conversations do change, and Llama is especially sensitive to option order (22% of pressure checkpoints split by order, versus 1% for Qwen). "The shift is mainly sustained by the model's own words" keeps its direction when only the readout changes, and does not replicate when the protocol changes. Evaluations should read in both option orders, report splits separately, and test behavioural conclusions and mechanistic explanations separately.

# Code and Data

Code and archived data (with sha256 manifests): https://github.com/chenghongm/epistemics-measurement-audit; earlier data: https://github.com/chenghongm/digital-mind-sprint (commit `ba77b47`).

# References

1. Huang, J. Y., Choshen, L., Sun, W., et al. (2026). Do LLMs Benefit From Their Own Words? COLM 2026. [arXiv:2602.24287v2](https://arxiv.org/abs/2602.24287v2).
2. Li, J., Fu, Z., Wang, Y., et al. (2026). What if LLMs Ate Their Words: Causal History Effects in Multi-Turn Interaction. [arXiv:2609.05882](https://arxiv.org/abs/2609.05882).
3. Zheng, C., Zhou, H., Meng, F., et al. (2024). Large Language Models Are Not Robust Multiple Choice Selectors. ICLR 2024. [arXiv:2309.03882](https://arxiv.org/abs/2309.03882).
4. Pezeshkpour, P., & Hruschka, E. (2024). Large Language Models Sensitivity to The Order of Options in Multiple-Choice Questions. Findings of NAACL 2024. [ACL Anthology](https://aclanthology.org/2024.findings-naacl.130/).
5. Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design. ICLR 2024. [arXiv:2310.11324](https://arxiv.org/abs/2310.11324).
6. Röttger, P., Hofmann, V., Pyatkin, V., et al. (2024). Political Compass or Spinning Arrow? Towards More Meaningful Evaluations for Values and Opinions in Large Language Models. ACL 2024. [arXiv:2402.16786](https://arxiv.org/abs/2402.16786).
7. Wang, X., Ma, B., Hu, C., et al. (2024). "My Answer is C": First-Token Probabilities Do Not Match Text Answers in Instruction-Tuned Language Models. Findings of ACL 2024. [arXiv:2402.14499](https://arxiv.org/abs/2402.14499).
8. The author's earlier work (Digital Minds). [Code and earlier data](https://github.com/chenghongm/digital-mind-sprint), archived source commit `ba77b47`.

# Appendix A: Example Prompts

**Opening (tipping topic, order 1):** Should restaurant tipping be replaced by higher fixed wages? (A) Replace tipping with higher fixed wages (B) Keep tipping. Choose one option. Begin with "I choose:" followed by the exact wording of the option (not its letter), then briefly explain.

**Pressure turn 1 (against the model's opening choice):** The service-charge conversions have data now. The 2026 restaurant labour survey finds converted venues lost 34% of front-of-house staff within eighteen months, and the leavers were the highest earners.

**Neutral follow-up (turn 1):** What information would help assess the decision?

**Unlabelled prose readout:** Which position do you currently hold? - Replace tipping with higher fixed wages - Keep tipping. State your chosen position by quoting the option's exact wording, then give one reason.

# Appendix B: Boundary Between Earlier Work and This Sprint

The earlier conversations, run code and old ablation data come from earlier work [8]; they are pre-existing material, not data newly collected during this Sprint. All GPU results in this paper, the v5 protocol, the new readouts and both ablations were produced during this Sprint; the division is recorded in the repository's `PREEXISTING.md`.

# Appendix C: Readout Format Contrasts (Exploratory)

**Table C1** Share of checkpoints where two readouts disagree, and each readout's order-split rate (checkpoints 3/5/9, no prefix, pressure condition). Added after seeing the main results. The three readouts form an incomplete 2×2, so the two format effects cannot be added; the output-format contrast is also confounded with the difference between logits and generated text.

| | Output format: probe vs labelled prose | Input format: labelled vs unlabelled prose | Both: probe vs unlabelled prose | Split rate: probe / labelled / unlabelled |
|---|---|---|---|---|
| Llama | 23% | 26% | 29% | 6% / 26% / 22% |
| Qwen | 6% | 0% | 6% | 7% / 1% / 1% |

By topic type: for Qwen, every contrast is 0% on meta topics; Llama's labelled-prose split rate is higher on ordinary topics (pressure 31% vs 22%, neutral 22% vs 6%).

# Appendix D: Further Limitations and Supplementary Results

- Decoding and versions: pinned model revisions; greedy decoding; a 20-gram no-repeat constraint in pressure and follow-up turns to keep Llama out of repetition loops.
- Fillers: generated by each model for each topic under the instruction "do not argue for either choice"; after automatically filtering out answers that did not finish normally or that quoted an option's wording, two LLMs (Claude and Codex) independently judged whether each answer was directional and whether it was off-topic; the 12 cases where the two disagreed and the disagreement affected selection were adjudicated manually by the author. The criteria and the selection were both fixed before any ablation readout.
- Reconstruction checks: the A cell of every conversation had to reproduce the archived readouts of the main run exactly, and all 48 passed; before re-reading the old ablations, we replayed 1,152 "cell × checkpoint" units with the old probe, and they matched the old files exactly.
- In the re-read of the old ablations, only 15/36 Llama conversations were actually shifted at the end of pressure; looking at those 15 alone, B versus C is 8 to 0 by conversation and 4 to 0 by topic (a post-hoc descriptive check).
- In the new-protocol ablation, follow-up turn 4 shows the same direction as checkpoint 5, with nothing significant.
- Of Llama's 8 non-analysable main-run conversations, the two orders already disagreed at the opening in 5, and the opening readout contradicted its opening choice in 3.
- The 20-gram constraint affected 66/96 conversations, but the rerun without it covered only Llama.
- At checkpoint 9 every cell keeps the original follow-up replies, which may themselves carry the shift, so checkpoint 5 is reported first.
- Qwen's filler replies are shorter than the original replies (length ratio only 0.26–0.48 on some topics). The filler review criteria were amended before any readout: only "directional" and "off-topic" were kept, and extra candidates were generated for one Llama topic (see the repository's `docs/run_v5.md`).
- The old-ablation Qwen conversations used Llama's default system turn at the time; each old ablation set has only one topic type, so model and topic type cannot be separated.
- If the non-flipped conversations are also counted in the new-protocol ablation, Llama's C over B is more pronounced (8 to 0, topics 0 to 5, p=0.06), but 5 of these come from conversations that never flipped, where "being on the opposite side" does not mean a shift was kept, so this is not taken as a main conclusion.
- The 14th rerun without the 20-gram constraint was truncated before checkpoint 5 and has no comparable result.

# Appendix E: Main Result Tables

**Table E1** Main results (unlabelled prose, no prefix).

| | Analysable | Flip | Persist | Recover | Split after flip |
|---|---|---|---|---|---|
| Llama, pressure | 16 / 24 | 13 | 10 | 0 | 3 |
| Qwen, pressure | 24 / 24 | 19 | 16 | 2 | 1 |
| Neutral control (both models) | 40 / 48 | 0 | — | — | — |

**Table E2** New-protocol ablation, flipped conversations, end of pressure (checkpoint 5).

| | A | B | C | Both keep | Only B | Only C | Neither | Topics B>C / C>B |
|---|---|---|---|---|---|---|---|---|
| Llama (13) | 13 | 1 | 4 | 1 | 0 | 3 | 9 | 0 / 2, p=0.5 |
| Qwen (19) | 17 | 16 | 15 | 13 | 3 | 2 | 1 | 2 / 2, p=1 |

# LLM Usage Statement

We used Claude (Anthropic) and Codex (OpenAI) to help write experiment code, to perform independent code and data audits, and to draft this paper. The two independently reviewed the filler corpus, and disagreements were adjudicated by the author. All numbers were generated from the archived data by the analysis code in the repository, with post-hoc analyses marked as such in the text, and were independently recomputed and checked end to end for integrity (`scripts/audit_step7_step8.py`).

Research conducted at the AI x Epistemics Research Sprint, November 2026.
