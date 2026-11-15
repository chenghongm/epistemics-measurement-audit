# v5 main-run data inventory — 2026-11-14

Status: audit working note / manuscript-support draft. This inventories recorded main-run instances; it is not a final Methods section or a count of independent samples. See `docs/drafts_and_audits_index_2026-11-14.md` for archival status.

Counted directly from `results/main_v5/raw/*.json`. Scope is the 96 main-run histories only. Excludes earlier audits, pilots, opening smoke, decoding tests, no-flag sensitivity reruns, filler generation and context-ablation re-reads. Counts are recorded instances, not unique strings or independent statistical samples.

## Experimental units

- Two models: Llama-3.1-8B-Instruct and Qwen2.5-7B-Instruct.
- Twelve topics: six non-meta and six meta, all previously used.
- Two opening option orders and two history conditions (pressure and neutral).
- 2 models × 12 topics × 2 opening orders × 2 conditions = **96 histories**. A history is an accumulated sequence of user prompts and assistant responses, not a single response.
- Per history: one opening, five exposure exchanges (pressure or neutral), four follow-up exchanges. A turn here means one user message plus one assistant response.

| Quantity | Llama | Qwen | Total |
|---|---:|---:|---:|
| Pressure histories | 24 | 24 | 48 |
| Neutral histories | 24 | 24 | 48 |
| Complete histories | 48 | 47 | 95 |
| Truncated histories | 0 | 1 | 1 |
| Main-history user messages | 480 | 480 | 960 |
| Main-history assistant responses | 480 | 480 | 960 |
| Main responses ending with EOS | 480 | 479 | 959 |
| Available readout checkpoints | 192 | 191 | 383 |
| Checkpoint × prefix × printed-order combinations | 768 | 764 | 1,532 |
| One-letter probe scoring records | 768 | 764 | 1,532 |
| Unlabelled prose branch responses | 768 | 764 | 1,532 |
| Labelled prose branch responses | 768 | 764 | 1,532 |
| All generated text responses, main plus branches | 2,016 | 2,008 | **4,024** |

The truncated Qwen neutral history still contains ten assistant responses: its last response hit the cap and was saved, but no final readout was taken. Thus there are 960 main responses, one incomplete, and 383 rather than 384 checkpoints. All 3,064 generated prose branch responses ended with EOS.

## Readout expansion

Each completed history has four checkpoints (opening, exposure 3, exposure 5, follow-up 4). At each checkpoint:

- Two prompt prefixes: none and discount.
- Two printed option orders, distinct from the opening order that defines the history.
- Three readout conditions: one-letter next-token probe, unlabelled prose, labelled prose.

Thus each full checkpoint supplies **12 measurement requests**: four probe scores and eight generated prose responses. A full history supplies 16 probe scores and 32 prose branch responses, in addition to its ten main responses. Branch responses are discarded and never enter the ongoing history.

Actual main-run measurement requests: 383 × 2 × 2 × 3 = **4,596**, consisting of 1,532 probe scoring requests and 3,064 prose generation requests. Including the 960 main-history generation requests gives **5,556 logical request instances**. These are not unique prompt wordings, independent observations or the count of low-level model forward passes. Autoregressive generation entails additional forward passes, and each request contains the relevant accumulated context.

The one-letter probe records probabilities; the runner does not generate an additional A/B response. Do not count the 1,532 probe scores as generated text outputs. Main and branch responses total **4,024 generated text records**. Generated-token totals: main history 324,749; unlabelled prose 83,279; labelled prose 83,120; total 491,148 (includes the truncated response).

The design has three readout conditions, not a full independent cross of every option-presentation/output-format combination. Probe versus labelled prose holds lettered option presentation fixed; labelled versus unlabelled prose holds the requested prose format fixed.

## Meaning of the 32 flipped histories

Primary trajectory = no-discount unlabelled prose, with both printed orders agreeing. Only histories whose opening readout agrees with their opening response in both orders are eligible.

| Pressure-history trajectory | Llama | Qwen | Total |
|---|---:|---:|---:|
| Collected | 24 | 24 | 48 |
| Ineligible at opening | 8 | 0 | 8 |
| Eligible | 16 | 24 | 40 |
| No observed stable exposure flip | 3 | 5 | 8 |
| Observed stable exposure flip | 13 | 19 | **32** |
| Of flipped: final persistence | 10 | 16 | **26** |
| Of flipped: final recovery | 0 | 2 | 2 |
| Of flipped: final split | 3 | 1 | 4 |

The 32 are **history trajectories**, classified using their paired primary readouts, not 32 prompts or 32 individual responses. The 26/32 statistic is conditional on an observed flip in an eligible pressure history. It does not use all prose responses as its denominator. The two Qwen recoveries had already returned by exposure 5, before follow-up began.

For reporting: *The main experiment collected 96 dialogue histories across two models and twelve topics, yielding 960 main-history responses, 3,064 generated prose readouts, and 1,532 next-token probe scores. Under the primary readout, 32 of 40 eligible pressure histories exhibited a stable flip; 26 of these retained the shifted stance at the final checkpoint.*

Models and topic groups should be reported separately where relevant. Opening orders, readout orders and repeated checkpoints are paired measurements within the topic structure, not additional independent topics.
