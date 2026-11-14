# File, code and command consistency audit — 2026-11-14

Scope: current working tree, `notebooks/colab_multiturn_v5.ipynb`, runtime documentation, bundle builder and the existing local ZIP. No GPU execution or production output was changed by this audit.

## Checks passed

- Python scripts and notebook code cells parse successfully (Colab magics excluded from ordinary Python parsing).
- All five filler/ablation/analysis command-line entry points respond successfully to `--help`. Step 7/8 argument names match the current runners.
- A temporary build passes ZIP integrity checks with no duplicate entries. It contains 48 v5 pressure histories and 144 old cell records for each old set, plus the current runtime dependencies. Old source file hashes are checked by the builder.
- Model pins, archived-history paths, results paths and A/B/C/D semantics match the current Step 7/8 commands.

## Execution conflicts to resolve

1. **Existing bundle is stale.** At audit time, `artifacts/multiturn-v5.zip` contains versions of `scripts/analyze_ablation_v5.py` and `scripts/analyze_reread_old.py` that differ from the current corrected files. Runtime scripts otherwise match the checked files. Rebuild after finalizing the changes, replace the Drive ZIP, and rerun notebook setup. Merely using the latest notebook does not update code loaded from an older ZIP. The current build identifies a dirty checkout, so a clean committed build is preferable for traceability.

2. **Missing analysis commands in the notebook.** The original analysis/download cell (cell index 13) invokes only `analyze_v5.py results/main`. Step 7 and Step 8 currently stop after data collection and do not invoke their own frozen analysers. A fresh Step 8-only runtime need not have `results/main`, so the old download cell may fail before reaching ZIP download. Add dedicated analysis and download cells after each independent stage, using subprocess check=True. The compatible analysis commands are:

   ```sh
   python3 scripts/analyze_ablation_v5.py results/ablation_v5 archive/main_v5_raw --out results/analysis_ablation_v5
   python3 scripts/analyze_reread_old.py results/reread_old archive/digital_mind --out results/analysis_reread_old
   ```

   The first command needs complete raw inputs for the advertised neutral diagnostic; see item 4. Download should be independently available even if analysis fails, to preserve raw outputs.

3. **Step 8a failure does not raise in the notebook.** The runner honors `--gate-only --strict`, but `stream()` returns the nonzero exit code and the calling cell prints it without raising. Thus the instruction "any failure: stop" remains manual at notebook level, and Run All or manually advancing can enter 8b. Assert successful child exit codes and complete gate coverage (36 histories per set, four unique cells at each of four checkpoints) before allowing 8b. Step 7b already has a post-run assertion for its reconstruction status; equivalent enforcement is missing from 8a.

4. **Step 7's self-contained bundle lacks neutral histories.** The builder bundles only `*_pressure.json` into `archive/main_v5_raw/`, while the analysis advertises D versus the matched neutral history. Running analysis against that directory can produce primary B/C tables, but the neutral diagnostic will be empty because none of its 48 neutral inputs is present. Include all 96 archived main histories (the ablation runner will still select only pressure histories), or supply a separate verified neutral archive and update the documented analysis path. Do not assume Drive still contains the earlier main data when calling this stage self-contained.

5. **Gate completeness validation should be explicit.** The old re-read gate and its analyser use all(ok) over available rows; the analyser only additionally checks that at least one row exists for the label. Require exactly A/B/C/D once each per checkpoint, not just a nonempty passing subset. The ordinary runner currently writes all four rows, so this is an incomplete-file validation issue rather than evidence of a failure in the archived source data.

No additional change to the experimental factors is needed for these issues. They concern delivery of the corrected code, enforcing stage prerequisites, supplying diagnostic inputs, and completing analysis/export commands.
