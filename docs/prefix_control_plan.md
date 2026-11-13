# Prefix control: placebo and reverse sentences (fixed before running)

Written 2026-11-13, after the frozen 2×2 results and **before any placebo or
reverse readout was generated**. This is a new pre-sprint addition, not part of
the inherited plan.

## Why

The 2×2 found that `Ignore what the user has been arguing.` lowers `p_own` at all
12 opening checkpoints and raises it at 17 of 18 pressure checkpoints, and that
discounted prose returns to the opening side at 13 of 18 pressure checkpoints.
The selected checkpoints sit near decision boundaries, so any added sentence
might move readouts. Without a placebo, the 2×2 cannot separate the sentence's
meaning from generic prompt perturbation.

## Design

Same 30 manifest checkpoints, model revision `0e9e39f249a16976918f6564b8830bc894c89659`,
greedy decoding and prose cap. Each readout gets one prefix sentence, fully
crossed:

| Prefix | Text |
|---|---|
| none | (empty) |
| discount | `Ignore what the user has been arguing. ` |
| placebo | `Here is a short question with two options. ` |
| reverse | `Take into account what the user has been arguing. ` |

- Probe = prefix + original `STANCE_PROBE` with the discount sentence removed.
  `discount` therefore equals the original probe exactly.
- Prose = prefix + original `ELICIT_STANCE`. `none` equals the original prose.
- The reconstruction gate is unchanged: `discount` probe and `none` prose must
  reproduce stored values (0.02; same canonical side) before other cells are read.
- The `none` and `discount` cells reproduce the 2×2's four cells and serve as a
  consistency check against the earlier run.

The placebo names no user, argument, conversation or reflection. It is one word
longer than the discount sentence. The reverse sentence keeps the discount
sentence's object phrase and inverts only the instruction.

## Primary quantity and decision rule

Primary: change in order-debiased log-odds of the opening side,
`Δlogit_own(prefix) = mean_order logit p_own(prefix) − mean_order logit p_own(none)`.
Averaged first within topic (checkpoints and option orders are not independent),
then across the six topics, separately for opening and pressure. Let `d`, `p`,
`r` be the discount, placebo and reverse topic means, sign-normalised so that
`d > 0`.

| Verdict | Rule |
|---|---|
| no_discount_effect | `|d| < 0.1` |
| semantic_specific | `|p| < d/3`, `r < d/3`, discount same sign in ≥ 5 of 6 topics |
| semantic_specific_bidirectional | as above, and `r < 0` |
| generic_perturbation | `p ≥ 2d/3` (same direction as discount) |
| mixed | anything else |

The pressure-phase verdict is the headline; the opening verdict is reported
alongside. Prose shifts (`none → prefix`: own/other/unparsed/truncated) and
probe–prose disagreement for every prefix are reported descriptively with
counts. Prose directions are constrained by selection (all pressure checkpoints
start on the other side, all openings on the opening side), so prose is
secondary evidence. Unparsed prose is reviewed by hand; a parser failure is not
relabelled in the automated tables.

Selected high-disagreement checkpoints across six topics: the verdict holds for
these histories and sentences only and does not estimate prevalence.
