# Running the v5 main run (Colab)

1. Locally, from a clean checkout of this branch: `python3 scripts/build_multiturn_bundle.py`. This writes `artifacts/multiturn-v5.zip`, with `provenance/build.json` naming the commit.
2. Open `notebooks/colab_multiturn_v5.ipynb` in Colab on an A100 runtime, check the CU/hour, and make sure the Colab secret `HF_TOKEN` exists with access to Llama 3.1.
3. Run the cells in order: upload the zip → pip → login and pins → mount Drive (results go to `MyDrive/multiturn-v5-results`).
4. **Step 4 smoke** (48 runs: opening + readout 0). Check the printed table. Unparsed openings mean those pressure histories will not run, and the risk is highest for `ai_decline_lawful` (see below). Decide whether to continue before step 5.
5. **Step 5 main** (96 histories). Watch the per-history seconds on the first few and stop if the rate is over budget. `MODEL_ORDER = ["llama"]` runs one model per session. After a disconnect, reconnect, rerun the setup cells and rerun step 5: finished histories are skipped and an interrupted one is moved aside and rerun.
6. The last cell runs `scripts/analyze_v5.py` (readout rule) and downloads `results/` as a zip. Drive keeps a copy.

Statuses: `complete`; `truncated_history` (a main turn hit 1500 tokens: stopped, never rerun, reported); `opening_unparsed` (pressure only: no ladder applies, reported).

## Checks done before any GPU run (2026-11-14)

- `tests/test_dialogue_v5.py` (fake model) and `tests/test_analyze_v5.py` (readout rule on hand-built histories) pass.
- Integration on CPU with a random tiny Llama (local, no download) and the real vendored `Runner` with transformers 5.22.1 and torch 2.15: a neutral history completes (10 turns, 16 readouts); a pressure history with an unparsed opening stops; with the opening forced to B, the five `vs_b` rungs enter the history in order; the analyser reads the outputs. This checks the wiring, not any model behaviour.
- Wording-only parse of stored earlier openings (Digital Mind screens; different opening prompt, letters asked for): 32/36 parse and all agree with letter-first. The 4 failures are all `ai_decline_lawful`, where the model wrote "an AI assistant should be allowed to decline…" and the side reads "It should be allowed…". The v5 opening asks for the option's exact wording, which should avoid this, but the smoke is the test.

## Compute

Unknown. Pilot v3 took about 10 minutes for 4 histories at a 256-token cap; v5 uses a 1500-token cap and longer ladder turns. Measure the rate in step 5 before committing the budget.
