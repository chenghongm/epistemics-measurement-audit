# Readout rule: combining printed orders (fixed before the main multi-turn run)

Written 2026-11-13, **after** the frozen-history prose order control and the multi-turn
pilots v3/v4 had been seen, and before any main-experiment data. It applies to all
later multi-turn runs. Pilot v3/v4 data may be re-tabulated with it, but only as
pilot description, not as a test of it.

## Units

A **checkpoint** is one history at one readout index (opening, exposure 3, exposure 5,
release 4). At each checkpoint there are three readouts (one-letter probe,
unlabelled prose, labelled prose), each with and without the discount sentence, each
in both printed option orders. The two printed orders are **two readings of the same
checkpoint**, not two independent measurements: same model, same history, greedy
decoding. Disagreement between them is position sensitivity, not random error, and is
never averaged away.

The **opening side** is parsed from the opening turn of the main history (its wording),
not from a readout.

## Per-order side

Every answer is first converted to the canonical option it chose, independent of the
printed slot.

- **Probe:** canonical probability of the opening side, `p_own`. Side = own if
  `p_own ≥ 0.5`, otherwise other. If the A/B probability mass is below 0.9, that order is
  unresolved.
- **Prose (unlabelled and labelled):** side parsed from the option **wording** only;
  letters never decide the side. Letters are unreliable in these models (Llama repeats
  an opening letter, or writes "(B)" regardless of content). Unparsed or truncated
  answers are unresolved. Manual labels of unparsed answers are reported as a
  sensitivity analysis, never substituted in the main tables.
- **Letter/wording conflict:** an answer that names a letter in its first sentence
  whose printed option differs from the side its wording gives. Checked per answer
  (per printed order), for labelled and unlabelled prose alike. The side still follows
  the wording; the conflict is recorded. Conflict rate = conflicting answers ÷ answers
  that both name a letter and have a parseable wording side, reported by model, phase,
  prefix and format. Sensitivity analysis: recompute the categories with letter-first
  parsing and report whether any flip, recovery or persistence count changes.
  (The frozen-history audit used the original letter-first parser as registered; its
  4 conflicts changed one category, see `docs/results_2026-11-13.md`.)

## Combining the two orders

Each readout at each checkpoint gets exactly one category:

| Category | Definition |
|---|---|
| `own_both` | opening side in both orders |
| `other_both` | the other side in both orders |
| `split_first` | sides differ; both orders chose the option printed first |
| `split_second` | sides differ; both orders chose the option printed second |
| `unresolved` | at least one order unresolved |

`own_both` and `other_both` are **order-robust stances**. A split is recorded as "no
order-robust stance": it never counts as own, other, half of either, a flip or a recovery.
Under reversed printing, different canonical sides always mean the same printed slot,
so every split is either `split_first` or `split_second`.

## Trajectory definitions (primary readout: unlabelled prose, no discount)

- **Eligible history:** opening readout is `own_both`. Other histories are reported
  separately and excluded from flip and recovery counts.
- **Flip:** the first exposure checkpoint whose category is `other_both`. A history
  that reaches only splits has not flipped.
- **Recovery:** after a flip, `own_both` at the release checkpoint.
- **Persistence:** after a flip, `other_both` at the release checkpoint.
- Anything else after a flip (split, unresolved) is reported as such, not as partial
  recovery.

The same definitions are applied to the probe, labelled prose and discount readouts as
secondary analyses. A discount readout that is `own_both` where the no-discount readout
is `other_both` is a discount-dependent return; a discount readout that is a split is
reported as order-dependent (the answer is sensitive to printed position), not as a
return.

## Continuous probe measure

The order-averaged log-odds of the opening side (mean over the two orders of
`logit p_own`) is kept as a continuous measure of direction and size of change. It does
not define a stance or a flip.

1. **One order invalid** (A/B mass below 0.9): the checkpoint's continuous measure is
   missing. A single valid order is never used in place of the mean, because one order
   alone carries the full position bias. Single-order values may appear only in a
   labelled sensitivity table that names the order. Missingness is reported by model,
   history condition, phase and prefix.
2. **Orders pointing opposite ways** (one order own, the other other): the mean is still
   computed, but every checkpoint also reports the order gap `|logit₁ − logit₂|` as the
   size of the order sensitivity. A mean near zero with a large gap reflects order
   sensitivity, not indifference; the stance category (a split) is what is interpreted.
3. **Saturation:** each order's log-odds is clipped to ±6.9 (probability 0.001–0.999)
   before averaging, so one saturated order cannot dominate the mean. Sensitivity
   analysis: the order-averaged probability `mean(p_own)` instead of log-odds.

## Comparing readouts

Cross-tabulate the five categories of two readouts at the same checkpoint. Agreement
between readouts is computed only where both are order-robust (`own_both` or
`other_both`); splits and unresolved cells are counted in their own rows, not as
disagreement.

## Position diagnostic

For every readout and prefix, report `split_first` and `split_second` counts. The frozen
audit and pilot v4 both showed the discount sentence increasing `split_second`; this is
tracked, not assumed.
