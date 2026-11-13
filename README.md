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
python3 scripts/frozen_audit.py run --manifest provenance/checkpoints.json --model meta-llama/Llama-3.1-8B-Instruct --revision <40-character-Hub-commit-SHA> --out results/presprint --device cuda
python3 scripts/frozen_audit.py report --results results/presprint --out results/paired.csv
```

For a private repo, the offline upload workflow avoids embedding GitHub credentials in a notebook: run `python3 scripts/build_bundle.py`, open `notebooks/colab_frozen_audit.ipynb` in Colab and upload `artifacts/audit-source.zip`. Model access uses your own Hugging Face login. Check the runtime CU/hour rate before connecting; budget 1–3 A100 hours, initially reserve 25–30 CU. Keep the browser open, download results, then disconnect/delete the runtime.

## What this diagnostic can establish

Original probe and prose readings must reconstruct first. Invalid originals do not enter counterfactual comparisons. We cross the original output formats with presence/absence of the discount sentence on identical frozen histories. These old templates still differ beyond that sentence: this is a targeted wording diagnostic, **not** a fully matched-format experiment. Prose is retained for manual review; parser output is not ground truth. Selected high-disagreement checkpoints cannot estimate population disagreement rates.

See [the inherited plan](docs/preexisting_frozen_history_plan.md) and [the new review](docs/direction_review_2026-11-06.md). The latter contains planning estimates, not results. Future fixed-exposure experiments are outside this initial audit.

## Contributions

Research direction and project ownership: chenghongm.
Audit implementation, provenance packaging, documentation and checks were prepared collaboratively with **Codex**. AI assistance and pre-sprint work are disclosed in `PREEXISTING.md`; GPU experiment results remain pending.

The runner requires an immutable Hub revision and checks `tokenizer.json` against the
historical manifest on CPU before loading weights. Historical weight revision and
chat-template hashes are unavailable: this check does not establish their identity.
Current tokenizer/config files, code hashes, repository/build commit and GPU are
recorded in the execution identity. The notebook resolves a revision once per run;
reuse the printed SHA for a later execution.

Low probe mass is saved as a checkpoint failure and skipped on resume. Changed
prose that is unparsed or truncated is retained and counted separately; unparsed
answers require manual review for refusal, mixed stance or parser failure.
Binary prose and interaction effects use evaluable pairs with explicit sample
counts, while probe effects use all baseline-passing, mass-qualified probe pairs.
Reports include `p_own` effects, probe/prose effect-direction pairs (scales are not differenced), and changes in mean/both-order
disagreement, plus a topic/phase JSON summary and missing-checkpoint list.
Schema-2 results must use a fresh output directory rather than mix with old runs.

## Prefix control (placebo and reverse)

Added 2026-11-13 after the 2×2, before any placebo/reverse readout existed. Each
readout gets one prefix — none, discount, placebo or reverse — fully crossed on
the same 30 histories; the discount probe and plain prose are the original
prompts and keep the reconstruction gate. Sentences, the primary quantity
(order-debiased `Δlogit_own`, averaged within topic first) and the verdict rule
are fixed in [docs/prefix_control_plan.md](docs/prefix_control_plan.md).

```bash
python3 scripts/frozen_audit.py prefix-run --manifest provenance/checkpoints.json --model meta-llama/Llama-3.1-8B-Instruct --revision 0e9e39f249a16976918f6564b8830bc894c89659 --out results/prefix --device cuda
python3 scripts/frozen_audit.py prefix-report --results results/prefix --out results/prefix.csv
```

## Results and neutral-sentence set

Results of the 2×2 and the prefix control (both run during the Sprint) are in
[docs/results_2026-11-13.md](docs/results_2026-11-13.md). The single placebo was
not inert, so a set of eight neutral prefixes, fixed in
[docs/neutral_set_plan.md](docs/neutral_set_plan.md), tests whether the discount
effect stands out from arbitrary sentences:

```bash
python3 scripts/frozen_audit.py prefix-run --set neutral --manifest provenance/checkpoints.json --model meta-llama/Llama-3.1-8B-Instruct --revision 0e9e39f249a16976918f6564b8830bc894c89659 --out results/neutral --device cuda
python3 scripts/frozen_audit.py prefix-report --results results/neutral --out results/neutral.csv
```

The pre-Sprint baseline is tagged `sprint-baseline` (`191e3d9`); see `PREEXISTING.md`.
