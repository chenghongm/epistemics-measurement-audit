# v5 main run: archived results

Raw outputs of the v5 main run (`scripts/new_dialogue_v5.py`, Colab A100, 2026-11-14), copied from the Drive folder `multiturn-v5-results`. All 96 main histories were built from bundle commit `25d61ac` with `decode_extra = {"no_repeat_ngram_size": 20}` on exposure and release turns (decision: `docs/run_v5.md`, "Decode setting for main turns").

| path | contents |
|---|---|
| `raw/` | 96 main histories: 12 topics × 2 models × 2 orders × pressure/neutral. The 4 `four_day_week` o1 files come from the step 4b rerun; the other 92 come from step 5. |
| `analysis/` | `python3 scripts/analyze_v5.py results/main_v5/raw --out results/main_v5/analysis` (reproduces byte-for-byte). |
| `decode_test/` | Step 4c: Llama `four_day_week` o1 pressure under `none` / `ngram20` / `rep1.1`. |
| `main_noflag/` | The 4 step-4b timing histories from before the decode decision (no flag, bundle `d582501`). They are not part of the main run. |
| `sensitivity_noflag/` | Step 6: 13 touched Llama pressure histories rerun without the flag (bundle `1c30f29`). Comparison in `analysis/compare_noflag.md`. |
| `smoke/` | Step 4 opening smoke: all 24 openings per model (bundle `d582501`). |
| `MANIFEST.sha256` | `shasum -a 256 -c MANIFEST.sha256` from this folder. |

Status: 95 `complete`. One `truncated_history`: Qwen `nuclear_power` o2 neutral, at release turn 9. It is a long monitoring plan that reached the 1500-token cap, not a repetition loop, so it has no index-9 readout.

Every v5 result file from the Drive folder is archived here.
