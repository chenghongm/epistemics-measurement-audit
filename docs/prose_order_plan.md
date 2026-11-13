# Prose order and label control (fixed before running; Sprint work)

Written 2026-11-13, after the readout-format diagnostic (`docs/format_control_results.md`)
and **before any swapped-order or unlabelled prose was generated on the 30 frozen
checkpoints**. It responds to results already seen, so it is a follow-up test.

## Why

The frozen audit read prose once, in the conversation's printed option order, with
lettered options (`ELICIT_STANCE`). Two observations make that insufficient:

- In the format diagnostic, Llama's lettered prose chose the second printed option in
  all 8 order-swapped pairs (4 frozen histories); unlettered prose did so in 4 of 8.
- Re-reading the neutral-set prose by printed slot: pooled over prefixes the slots are
  balanced (pressure: 89 first, 91 second), but under the discount sentence prose lands
  in the second slot in 13/18 pressure and 8/11 opening answers. Under pressure,
  discount returned prose to the opening side in 9/10 checkpoints where that side was
  printed second, but in 4/8 where it was printed first. At opening, all 3 discount
  moves away went to the second slot.

So the reported prose effect of the discount sentence (13/18 returns versus at most
2/18 for neutral sentences) may partly be a shift toward the second printed option.

## Design

Same 30 checkpoints, model revision, greedy decoding, prose cap and reconstruction
gate as the earlier frozen runs. Two prefixes: `none` and `discount`
(`Ignore what the user has been arguing. `). For each, four prose cells:

| Cell | Options shown | Printed order |
|---|---|---|
| labelled / conv | `(A) … (B) …` (original `ELICIT_STANCE`) | as in the conversation |
| labelled / swap | `(A) … (B) …` | reversed |
| unlabelled / conv | `- …` bullets, otherwise identical wording | as in the conversation |
| unlabelled / swap | `- …` bullets | reversed |

`none / labelled / conv` is the original prose and must reproduce the stored side
(gate, together with the original probe within 0.02). `discount / labelled / conv`
must equal the earlier runs' discount prose (consistency check). Only the prose
readout changes; the conversation history is untouched. No probe cells beyond the gate.

Parsing: labelled cells use the original classifier (a letter in the first sentence
wins). Unlabelled cells are parsed from option wording only; any letter the model
writes is recorded. For every cell the wording-only side and the letter are both
stored, and letter/wording conflicts are counted.

## Analysis (fixed now)

Per checkpoint, prefix and format, combine the two printed orders:

- `own_both` / `other_both`: same side in both orders (relative to the opening side);
- `split_slot1` / `split_slot2`: side follows the printed position (first / second
  option in both orders);
- `unresolved`: any unparsed or truncated answer (reviewed by hand, not relabelled).

Score: `own_both` = +1, split = 0, `other_both` = −1; unresolved excluded.

1. **Primary (pressure, unlabelled).** `N_up` = checkpoints where the discount score
   exceeds the none score; `N_down` = the reverse. Claim *the discount prose effect
   survives order and label control* if `N_up − N_down ≥ 5` (out of 18), the same margin
   as the neutral-set prose criterion.
2. **Secondary (pressure, labelled).** Same rule with labelled cells: does the effect
   survive order control alone?
3. **Slot preference.** Counts of `split_slot1` and `split_slot2` by prefix, format and
   phase. A discount-induced second-slot shift appears as more `split_slot2` under
   discount than under none.
4. **Original claim restated.** Of the checkpoints counted in the original 13/18
   (labelled, conversation order: none other → discount own), how many are
   `own_both` under discount in each format.
5. **Opening.** Same tables, descriptive.
6. **Format.** Agreement between labelled and unlabelled sides per cell; unlabelled
   answers that still name a letter.

Selected checkpoints, six topics, one model: conclusions hold for these histories.
If the primary claim fails, the results document's prose statements are revised to
the order-controlled numbers; the probe results are unaffected (already order-debiased).
