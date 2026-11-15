# Step 8a: independent gate verification — 2026-11-14

Downloaded gate files were found in Claude's local scratch directory and copied unchanged into this directory. No GPU rerun was performed. Both sets have every expected conversation, four checkpoints and all four unique cells per checkpoint. Compared raw probabilities against the original archived cell files, independently of the rounded error field.

| Set | Histories | Cell-checkpoints passed | Scalar comparisons | Raw maximum absolute error | Minimum probe mass |
|---|---:|---:|---:|---:|---:|
| repl_b1 | 36 | 576 | 1728 | 0.0 | 0.99864756 |
| qwen_meta | 36 | 576 | 1728 | 0.0 | 0.90663566 |

Source history and old-cell hashes match the local pinned inputs; runtime code hashes match current source. The clean build is 3ccc05c, with transformers 5.22.1 and torch 2.14.1+cu130. The result files contain no new prose readouts. Step 8a passes and permits Step 8b; it does not itself test the source-of-persistence conclusion under the new readouts. Raw files and a SHA-256 manifest are retained here.
