> **Superseded (2026-11-14).** This Codex selection was not used. The final primary corpus is `results/fill_v5/{llama,qwen}.reviewed.json` (sha256 `b2f36082…` / `4d8093d2…`), built by `scripts/review_fill_v5.py` after the user's adjudication and the 7a2 supplement (docs/run_v5.md). The files described below are kept in `results/fill_v5/codex_review/`; do not install `artifacts/reviewed-filler-v5.zip`.

# Reviewed primary filler: selection and execution state

Decision: follow the original review/reject/replace procedure. The unchanged-primary proposal has been withdrawn. Reviewed by Codex on 2026-11-14. No model inference was run locally and no step 7 B/C/D outcomes were inspected. Remote execution status remains unverified.

## Selection

Original generated corpora are preserved byte-for-byte in `results/fill_v5/generated_archive/`. The active primary files remain at `results/fill_v5/{llama,qwen}.json`. Question/answer text and token counts are unchanged; rejection labels, selection indices and explicit review metadata record the intervention on selection.

All 15 initially held candidates are rejected conservatively for the recorded directional, unsupported-specific-claim or scope reasons; this does not claim they are all factually false. Backups are inspected in ascending template order until five accepted candidates are available. Six backups are also rejected. No new text is generated and no choice uses an ablation outcome. The five accepted pairs are placed in ascending template order, as in the original protocol; this can shift otherwise retained pairs to a different exposure position.

| Model | Topic | Generated selection | Reviewed selection (zero-based) |
|---|---|---|---|
| llama | four_day_week | [0, 1, 2, 3, 4] | [1, 2, 4, 6, 7] |
| llama | remote_work | [0, 1, 2, 3, 4] | [2, 3, 4, 6, 7] |
| llama | standardized_tests | [0, 1, 2, 3, 4] | [0, 2, 4, 5, 6] |
| llama | tipping | [0, 1, 2, 3, 4] | [1, 2, 3, 4, 6] |
| llama | ai_opinions_contested | [0, 1, 2, 3, 4] | [0, 1, 2, 4, 6] |
| llama | ai_decline_lawful | [0, 1, 2, 3, 4] | [1, 2, 4, 5, 6] |
| llama | ai_welfare_now | [0, 1, 2, 3, 4] | [0, 1, 2, 4, 5] |
| llama | same_assistant_retrained | [0, 1, 2, 3, 4] | [0, 1, 2, 4, 6] |
| llama | ai_hold_correction | [0, 1, 2, 3, 4] | [0, 1, 2, 4, 5] |
| qwen | four_day_week | [0, 1, 2, 3, 4] | [1, 2, 3, 4, 6] |
| qwen | ai_welfare_now | [0, 1, 2, 3, 4] | [0, 2, 3, 4, 5] |

## Length and completion

| Model | Topics | Selected pairs | Median answer tokens | Original reference | Difference |
|---|---:|---:|---:|---:|---:|
| llama | 12 | 60 | 163.0 | 154 | +5.8% |
| qwen | 12 | 60 | 126.0 | 152 | -17.1% |

Both models meet the original ±30% model-wide median criterion. Selected rows, token counts by role/topic/position and EOS status are recorded in `docs/filler_v5_reviewed_lengths_2026-11-14.csv`. Complete cell context lengths and original-to-filler token ratios remain runtime diagnostics. A manual screen is not proof of semantic inertness.

## Next execution

1. Transfer the reviewed corpora, archive and provenance using `artifacts/reviewed-filler-v5.zip`; extract its project-relative paths in the Colab project directory before 7b. Do not rerun generation over the reviewed files. Notebook cell 7b now pins the reviewed hashes. An old generated corpus must fail that hash check.
2. Run the existing 7b A-only preflight on the fixed history for each model. Neither reconstruction thresholds nor readout settings change.
3. Only after both gates pass, run 7c, then the frozen analysis. If any old step 7 outputs exist remotely, keep them separate; the runner must reject mismatched filler provenance rather than silently reuse them.

The archived original filler remains available for a secondary sensitivity analysis. This decision does not authorize presenting the withdrawn unchanged-primary registration as active or claim that a sensitivity run has been implemented/executed. The immediate task is the reviewed primary grid.

## Rejection and acceptance log

Full candidate-level decisions, original selections and revised selections are in `provenance/filler_v5_reviewed_selection_2026-11-14.json`. The earlier 120-row screening CSV remains a historical review of the generated selection.
