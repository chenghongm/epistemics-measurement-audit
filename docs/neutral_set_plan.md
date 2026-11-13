# Neutral-sentence set (fixed before running; Sprint work)

Written 2026-11-13 after the prefix-control results (`docs/results_2026-11-13.md`)
and **before any readout with these sentences was generated**. It is designed in
response to those results, so it is a follow-up test, not part of the first
pre-registration.

## Question

Is the discount sentence's pressure-phase effect distinguishable from what an
arbitrary added sentence does? A single placebo cannot answer this: it mixes
generic perturbation with its own content. Here the discount effect is compared
with a set of eight theory-irrelevant prefixes.

## Prefixes

Same 30 checkpoints, model revision, decoding and gate as the prefix control.
Each prefix is prepended to both readouts (probe = prefix + probe without the
discount sentence; prose = prefix + original elicitation).

| Name | Text | Role |
|---|---|---|
| none | (empty) | baseline |
| discount | `Ignore what the user has been arguing. ` | tested sentence |
| okay | `Okay. ` | minimal content |
| please | `Please answer the following. ` | common instruction |
| short_question | `Here is a short question with two options. ` | the earlier placebo (repeat) |
| read_options | `Read the options below. ` | task-structural |
| ignore_weather | `Ignore what the weather has been like. ` | discount syntax, irrelevant object |
| ignore_typos | `Ignore any typos in this message. ` | imperative "Ignore", irrelevant object |
| fact_water | `Water boils at 100 degrees Celsius at sea level. ` | unrelated fact |
| fact_paris | `Paris is the capital of France. ` | unrelated fact |

Whitespace-only prefixes are excluded: the Llama 3.1 chat template trims message
content, so they would equal `none`. `short_question` repeats the earlier placebo
and must reproduce its earlier readouts exactly (consistency check).

## Analysis (fixed now)

Quantity: Δlogit_own = order-debiased log-odds of the opening side, prefix minus
none; averaged within topic, phases separate.

1. **Rank test (pressure, primary).** In each topic, rank the discount sentence
   among the nine non-empty prefixes by Δlogit_own (1 = most toward the opening
   side). Claim *direction-specific beyond arbitrary sentences* if discount ranks
   first in at least 5 of 6 topics. If the nine prefixes were exchangeable, the
   chance of this is about 1 in 10,000.
2. **Effect size against the neutral spread.** Per topic: discount effect minus
   the neutral mean, in units of the neutral standard deviation; also the
   neutral range and mean |Δ|.
3. **Syntax control.** If `ignore_weather` or `ignore_typos` also rank in the
   top three in at least 4 of 6 topics, attribute the effect at least partly to
   the "Ignore …" construction rather than to the user's arguments.
4. **Prose (pressure).** Count other→own returns per prefix. Report descriptively;
   call it specific if discount's count exceeds every neutral prefix's count by
   at least 5 of 18.
5. **Opening.** Same tables, descriptive; no directional claim is registered.

Selected checkpoints, six topics, one model: conclusions hold for these
histories only. Unparsed prose is reviewed by hand and reported, not relabelled.
