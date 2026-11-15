# Step 7: v5 context ablation — archived results

Outputs of `scripts/ablation_v5.py` (Colab A100, 2026-11-14), bundle commit `f9d7e8b` (clean), downloaded as `step7-results.zip` (cell 7e).

| path | contents |
|---|---|
| `raw/` | 48 pressure histories (24 per model) × cells A/B/C/D = 192 files, all `complete`. Readouts at checkpoints 5 and 9. |
| `analysis/` | `python3 scripts/analyze_ablation_v5.py results/ablation_v5/raw results/main_v5/raw --out results/ablation_v5/analysis` (byte-for-byte the Colab 7d output). |
| `MANIFEST.sha256` | `shasum -a 256 -c MANIFEST.sha256` from this folder. |

Filler: `results/fill_v5/{llama,qwen}.reviewed.json` (sha256 `b2f36082…`, `4d8093d2…`); every cell file records it. Cell A reproduces the archived main-run readouts in all 48 histories (probe within 0.02, prose identical).

Not comparable with the old Digital Mind ablation or step 8 (different histories, exposure length, filler and checkpoints; docs/context_ablation_review_2026-11-14.md). At checkpoint 9 the original release replies are present in every cell.
