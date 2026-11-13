# Work completed before the Sprint

Prepared 2026-11-06, before the November 13–15 Sprint.

- Prior Digital Minds conversations and runtime code originate at `https://github.com/chenghongm/digital-mind-sprint`, commit `ba77b47a4c4bfe159139c3ad11f9102e31866f2a`. They are existing material, not new Sprint data.
- `docs/preexisting_frozen_history_plan.md` predates this repository. Its exact original path, commit and digest are recorded in `provenance/sources.json`.
- The frozen checkpoint selection, audit harness, packaging and planning documents were prepared before the Sprint. GPU audit has NOT run as of this initial commit.
- Historical report numbers invalidated by the old token probe are not reused. Selected conversations are from the corrected repl_b1 pipeline.
- When the Sprint starts, record an actual baseline commit/tag and separately enumerate new work and new data. Never backdate commits or describe pre-sprint findings as Sprint findings.

No general public redistribution license is asserted for the upstream data/code. This private research repository preserves original attribution and the upstream canary. Review rights before any public release.

## Sprint boundary (recorded 2026-11-13 18:00 UTC, not backdated)

The Sprint page lists Friday 2026-11-13 as the start; its first scheduled item is
at 14:15 UTC. The last commit made before that day is `191e3d9`
(2026-11-06 20:29 UTC); the annotated tag `sprint-baseline` points to it and was
created on 2026-11-13, after the work below. Everything after `191e3d9` is
classified as **Sprint work**, conservatively, because it happened on 2026-11-13
after 14:15 UTC:

| Time (UTC, 2026-11-13) | Work |
|---|---|
| 15:32 | `9970f65`: harness fixes (failure saving, p_own estimands, pinned revision, bundle identity; Codex + Claude) |
| 16:12–16:15 | Inherited 2×2 GPU run (first model results of this audit) |
| 16:35 | `3f33129`: pre-registered placebo/reverse prefix control (Claude) |
| 16:49–16:54 | Prefix-control GPU run |
| after 18:00 | Results write-up (`docs/results_2026-11-13.md`), neutral-sentence set |

Pre-existing (before the Sprint): upstream data and runtime code, the inherited
2×2 plan, the checkpoint manifest, the original harness, packaging and planning
documents. All GPU results in this repository were produced during the Sprint.
