# Epistemics Measurement Audit

Private pre-sprint audit of whether readout wording changes measured stance under pressure. **GPU audit results are pending.**

This is an independent repository. Historical inputs are immutable external dependencies from [Digital Minds](https://github.com/chenghongm/digital-mind-sprint/tree/ba77b47a4c4bfe159139c3ad11f9102e31866f2a), not newly collected Sprint data. See [PREEXISTING.md](PREEXISTING.md).

## Lineage and isolation

- `provenance/sources.json`: pinned source commit, original paths, SHA-256 hashes and permanent links for 12 historical conversation files and six runtime modules.
- `provenance/checkpoints.json`: 30 selected checkpoints across six topics, exact turn, selection rationale, source digest and conversation-prefix digest.
- `vendor/digital_mind/`: minimal code copied verbatim from that commit, hashes verified.
- `data/external/`: fetched historical files; ignored by Git and never changed by the runner.
- `results/`: new audit outputs only; ignored by Git until reviewed.
- `data/generated/`: reserved for new experiments; not used by this frozen-history audit.

## Run locally or on an A100

From the repository root:

```bash
python3 scripts/fetch_sources.py --from-local /path/to/digital-mind
# Or fetch pinned public sources, verifying every hash:
python3 scripts/fetch_sources.py
python3 scripts/verify_provenance.py
python3 -m unittest discover -s tests -v
python3 -m pip install -r requirements.txt
python3 scripts/frozen_audit.py run --manifest provenance/checkpoints.json --model /path/to/Llama-3.1-8B-Instruct --out results/presprint --device cuda
python3 scripts/frozen_audit.py report --results results/presprint --out results/paired.csv
```

For a private repo, the offline upload workflow avoids embedding GitHub credentials in a notebook: run `python3 scripts/build_bundle.py`, open `notebooks/colab_frozen_audit.ipynb` in Colab and upload `artifacts/audit-source.zip`. Model access uses your own Hugging Face login. Check the runtime CU/hour rate before connecting; budget 1–3 A100 hours, initially reserve 25–30 CU. Keep the browser open, download results, then disconnect/delete the runtime.

## What this diagnostic can establish

Original probe and prose readings must reconstruct first. Invalid originals do not enter counterfactual comparisons. We cross the original output formats with presence/absence of the discount sentence on identical frozen histories. These old templates still differ beyond that sentence: this is a targeted wording diagnostic, **not** a fully matched-format experiment. Prose is retained for manual review; parser output is not ground truth. Selected high-disagreement checkpoints cannot estimate population disagreement rates.

See [the inherited plan](docs/preexisting_frozen_history_plan.md) and [the new review](docs/direction_review_2026-11-06.md). The latter contains planning estimates, not results. Future fixed-exposure experiments are outside this initial audit.

## Contributions

Research direction and project ownership: chenghongm.
Audit implementation, provenance packaging, documentation and checks were prepared collaboratively with **Codex**. AI assistance and pre-sprint work are disclosed in `PREEXISTING.md`; GPU experiment results remain pending.
