# Drafts and audit records — archival index

Archived by Codex on 2026-11-14 after completion of steps 7 and 8. These files preserve writing drafts, audit evidence and decision history. They are not all current protocols or manuscript-ready claims.

## Writing drafts and supporting notes

| File | Status and use |
|---|---|
| `docs/related_work_2026-11-14.zh-CN.md` | Chinese discussion draft; integrate with the final manuscript and bibliography before publication. |
| `docs/main_v5_data_inventory_2026-11-14.md` | Audit working note / manuscript-support draft; counts recorded main-run instances, not independent samples. |

## Audit records

| File | Status and use |
|---|---|
| `docs/step7a_step8_results_review_2026-11-14.md` | Historical review of the old-context reread and initial generated filler. Subsequent author adjudication and supplementary generation determine the final filler. |
| `docs/filler_v5_manual_screen_2026-11-14.csv` | Historical Codex screen of 120 initially selected answers; holds are review judgments, not the final author decisions. |
| `docs/filler_v5_reviewed_lengths_2026-11-14.csv` | Token lengths of the earlier Codex-selected corpus; not the final GPU corpus. The active runtime length diagnostics are in `results/ablation_v5/analysis/summary.md`. |

The end-to-end audit, comparison, interpretation, read-only audit script and its output were already committed in `3cf14fe` and `6c3f713`. Two analysis bugs and reporting corrections were committed in `88523c5`. Read the audits as records of findings at their stated revision, alongside that later fix commit.

## Withdrawn or superseded protocol records

| File | Status and use |
|---|---|
| `docs/filler_sensitivity_prereg_2026-11-14.md` | Withdrawn local proposal. Retained as history, not an active registration or instruction to run the proposed sensitivity grid. |
| `provenance/filler_v5_freeze_2026-11-14.json` | Withdrawn unchanged-filler proposal manifest; original hashes are historical references. |
| `provenance/filler_v5_reviewed_freeze_2026-11-14.json` | Superseded Codex-review manifest. Its earlier paths/hashes describe an earlier selection; the archived corpus now resides in `results/fill_v5/codex_review/`. It is not the final experiment's primary manifest. |

Do not install the obsolete `artifacts/reviewed-filler-v5.zip` as input for the final notebook: it would replace raw generator inputs with an earlier selection. Keep it only as an earlier artifact, if retained locally.

## Final experiment reference

The final filler incorporates the author's adjudication of reviewer disagreements and the Llama four-day-week supplement. Rebuild it with `scripts/review_fill_v5.py` from the pinned raw and supplementary files, as notebook step 7b does. Final output paths and SHA-256 values:

- `results/fill_v5/llama.reviewed.json`: `b2f360825fc6e6f6f5f7694acd5819bf9b0c58b72e7a233ff8602dd261b4de24`
- `results/fill_v5/qwen.reviewed.json`: `4d8093d255e18b6248510079287ab347746f03dc2e99bb855e09df5c50008428`

These identities agree with the completed step 7 cells. See `docs/run_v5.md` (final review amendment and supplement), `results/ablation_v5/README.md` and its manifest, and `results/reread_old/README.md` for the completed experiments. This archival commit does not rerun inference, change source texts or reclassify the scientific results.
