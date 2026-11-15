# Step 8: re-read of the old Digital Mind context ablations — archived results

Outputs of `scripts/reread_old_ablation.py` (Colab A100, 2026-11-14), bundle commit `3ccc05c` (clean checkout), torch 2.14.1+cu130, transformers 5.22.1. Downloaded from Colab as `step8-results.zip` (cell 8d); the same files were written to the Drive folder `multiturn-v5-results/reread_old/`.

| path | contents |
|---|---|
| `repl_b1/` | Llama-3.1-8B-Instruct rev `0e9e39f…`. 36 pressure conversations × (gate + A/B/C/D readouts). |
| `qwen_meta/` | Qwen2.5-7B-Instruct rev `a09a354…`. 36 pressure conversations × (gate + A/B/C/D readouts). |
| `analysis/summary.md` | `python3 scripts/analyze_reread_old.py results/reread_old data/external/digital-mind --out results/reread_old/analysis` (reproduces byte-for-byte the Colab 8c output). |
| `gate_review_2026-11-14.md`, `gate_audit_2026-11-14.json` | Codex's independent check of the 8a gate files against the old cell files (before 8b). |
| `MANIFEST.sha256` | `shasum -a 256 -c MANIFEST.sha256` from this folder. |

Gate (step 8a): all 576 checkpoint × cell rows per set (36 conversations × 4 checkpoints × 4 cells) reproduce the old probe within 0.02; the raw maximum error is 0.0. All 288 readout files are `complete` with all 4 checkpoints (end_pressure, release_4/8/12). The gate files in this folder are the Colab copies; their content equals the earlier 8a copies (only JSON whitespace differed).

Inputs (old conversations, stored filler, old cell files) are listed with hashes in `provenance/reread_sources.json`.
