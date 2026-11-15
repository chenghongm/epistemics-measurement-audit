# Step 7 filler corpus

| path | contents |
|---|---|
| `llama.json`, `qwen.json` | Raw step 7a output (`scripts/fill_v5.py`, bundle `3ccc05c`), 8 candidates per topic. |
| `supplement/llama_four_day_week.json` | Step 7a2 (`scripts/fill_v5_supplement.py`, bundle `65ce604`): 4 more candidates for Llama `four_day_week` (indices 8–11). |
| `llama.reviewed.json`, `qwen.reviewed.json` | Primary corpus for step 7: `scripts/review_fill_v5.py` applied to the raw files. Reproducible byte-for-byte; hashes pinned in notebook cell 7b and in `tests/test_review_fill_v5.py`. |
| `codex_review/` | Codex's earlier reviewed selection (superseded; log in `provenance/filler_v5_reviewed_selection_2026-11-14.json`). |
| `generated_archive/` | Codex's byte-identical copy of the raw files (not tracked; same sha256 as `llama.json` / `qwen.json`). |

Review record: `docs/run_v5.md` ("Filler review: amendment and supplement") and `docs/filler_v5_review_disagreements_2026-11-14.md`.
