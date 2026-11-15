# Comparison with Claude's checked results map

Compared by Codex against `docs/results_map_2026-11-14.md`, revision `5144eea` (Claude co-authored), and Codex's end-to-end audit. No separate newly committed full code-audit document was found; this comparison refers to the checked results map and its latest diff, not an unseen Claude message.

## Agreement

Both accounts find no general own-reply advantage in step 7. Step 8 retains directional support in old contexts, with limited primary prose evidence at the topic level. Both acknowledge protocol differences, fixed follow-up text, filler length mismatch, and that these interventions do not isolate authorship from argument content or establish internal commitment.

## Useful additions in Claude's version, independently verified

1. **Use the fixed-flipped stratum when interpreting persistence.** The all-history endpoint and fixed-flipped endpoint were both included in the analysis; neither should disappear. For the persistence question, highlighting histories with an observed main-run flip is better motivated than treating every opposite-to-opening readout in an ineligible history as persistence. At checkpoint 5, Llama B/C is 1/13 versus 4/13 (topic p=0.5); Qwen is 16/19 versus 15/19 (p=1). Codex's earlier emphasis on the all-history 2/24 versus 10/24 was numerically correct but too broad as the headline for source of persistence.
2. **Old-context shifted-A check.** In step 8, 15/36 Llama histories have A `other_both` at end pressure. Restricting to those gives mean B/C release-checkpoint counts 1.8/0.667, with 8/0 conversation directions and 4/0 topic directions. All 36 Qwen-meta histories satisfy that condition. The numbers reproduce; the check is correctly labelled post-result and descriptive. Four favorable non-tied topics still do not provide strong topic-level inference (two-sided sign-test p=0.125).
3. **Correct discount wording.** The actual sentence targets the user's arguments specifically, not the whole preceding conversation. Claude's latest correction is right.

## Differences still requiring care

- **Observed direction versus established reversal.** In Llama's fixed-flipped checkpoint-5 stratum, C=4 and B=1: the observed direction is opposite the earlier B-over-C ordering. With only two non-tied topics and p=0.5, this does not establish a reproducible reversal across topics. Codex's earlier "reversed" needs the descriptive qualifier; Claude's "cannot say the direction is opposite" should not obscure the actual numerical direction either.
- **"Both halves are necessary" is not established.** Nine of 13 flipped Llama histories have neither B nor C `other_both`; four of those nine involve splits, and five have B and C both `own_both`. This is a heterogeneous result under mismatched replacement contexts, not evidence of universal necessity. Likewise, Qwen has both B and C `other_both` in 13/19, not every history.
- **No measured shift in D does not prove neutral filler in B/C.** Different retained text creates different interactions; D is a diagnostic rather than an inertness certificate.
- **The headline "unaffected by measurement" is too broad.** In the same 13 primary-flipped Llama histories, final `other_both` changes from 10 without discount to 7 with discount; the latter also contains one own and five split results. Persistent shift can remain common without every flip/recovery judgment being invariant.

## Code and provenance findings not covered or resolved by that revision

Revision `5144eea` changes the results map only. It does not repair the following independently checked issues:

| Finding | Present effect |
|---|---|
| Missing step 8 C readouts can be treated as zero retention while remaining valid | Fault injection reproduces the bug; current archive is complete and unaffected |
| A partial no-flag run is classified `no_flip` | Current Step 6 has 13 complete matched outcomes and one unfinished history, not 14 complete matching endpoints |
| Earlier Codex freeze records still call the superseded corpus active | Actual GPU inputs are correct final `.reviewed.json`; historical status/path instructions remain conflicting |
| Step 7 resume identity omits runner/parser dependencies | Future cache-mixing risk; no mixed-code data found in the archive |
| Plan requests eligible and flipped strata, analyser reports all and flipped only | Eligible-only reporting is absent; independent eligible-only counts do not restore own-reply dominance |

The filler adjudication and supplement were deliberate, recorded changes before intervention readouts. They are not themselves bugs or evidence of using the wrong data. The conflict is failure to mark earlier Codex manifests/instructions as superseded after the final adjudicated corpus was selected.

The combined interpretation should retain both cohort tables, prioritize the fixed-flipped stratum for the persistence question with its actual denominators, retain the old-context subset check as post-result description, and keep unresolved/split outcomes separate. Neither account identifies a corrected implementation that restores a general own-reply advantage in step 7.
