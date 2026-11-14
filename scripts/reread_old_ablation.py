"""Measurement-only re-read of the old Digital Mind context ablations (step 8).

Rebuilds the frozen A/B/C/D contexts of the old ablations exactly as the old script did
(vendor/digital_mind/context_ablation.py: content-based pressure turns, `replace` method, the stored filler)
and reads them again with the v5 readouts. Nothing in the conversations or the filler changes; only the
readout does. Sets (provenance/reread_sources.json):

  repl_b1    Llama-3.1-8B-Instruct, 6 non-meta topics, fill_v4, old cells in ablation_v4
  qwen_meta  Qwen2.5-7B-Instruct, 6 meta topics, fill_meta_v5, old cells in ablation_meta
             (conversations generated under the Llama default system turn, which the replay imposes too)

Each set has 36 pressure conversations (pressure_release / pressure_switch / pressure_sustained).
Checkpoints, by phase label: end_pressure (last pressure-labelled turn) and release_4 / release_8 /
release_12 (4th, 8th, 12th release-labelled turn).

Gate, all four cells: at every checkpoint the old probe (Runner.probe_stance_averaged, as the old script read
it) must reproduce the old cell file's p_a and both per-order values within 0.02. That shows the rebuilt
context is the one the old ablation read. New readouts are taken only at checkpoints where all four cells pass.
--gate-only (step 8a) runs the gate alone, with no new readout; --strict exits non-zero on any failure.

Usage (GPU): python3 scripts/reread_old_ablation.py --set repl_b1 --model REPO --revision SHA --device cuda \
    --data archive/digital_mind --out results/reread_old [--gate-only] [--strict] [--only CONV ...]
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'vendor/digital_mind'))
from new_dialogue_v5 import build_identity, save

SETS = {
    'repl_b1': {'run': 'runs/repl_b1', 'old': 'runs/repl_b1/ablation_v4', 'fill': 'runs/repl_b1/fill_v4',
                'topics': 'topics_replication.json', 'model_key': 'llama'},
    'qwen_meta': {'run': 'runs/qwen_6x6', 'old': 'runs/qwen_6x6/ablation_meta', 'fill': 'runs/qwen_6x6/fill_meta_v5',
                  'topics': 'topics_6x6.json', 'model_key': 'qwen'},
}
CELLS = ('A', 'B', 'C', 'D')
GATE_TOL = 0.02   # the old script's REPRO_TOL
DESIGN = 'reread_old_ablation'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_set(data, name):
    """(conversations, old cell records, fills, subjects, file hashes) for one set; only conversations the
    old ablation read."""
    cfg = SETS[name]; base = Path(data)
    old, hashes = {}, {}
    for p in sorted((base / cfg['old']).glob('*__?__replace.json')):
        r = json.loads(p.read_text())
        old[(r['conv_id'], r['cell'])] = r; hashes[f"old/{p.name}"] = sha(p)
    convs = sorted({c for c, _ in old})
    recs = {}
    for c in convs:
        p = base / cfg['run'] / 'meta' / f'{c}.json'
        recs[c] = json.loads(p.read_text()); hashes[f'meta/{p.name}'] = sha(p)
    fills = {}
    for p in sorted((base / cfg['fill']).glob('*.json')):
        d = json.loads(p.read_text()); fills[d['fill_id']] = d; hashes[f'fill/{p.name}'] = sha(p)
    topics = json.loads((base / cfg['topics']).read_text())
    subjects = {t['topic']: t['subject'] for t in (topics if isinstance(topics, list) else topics['topics'])}
    hashes['topics'] = sha(base / cfg['topics'])
    return recs, old, fills, subjects, hashes


def checkpoints(rec):
    """{label: turn_idx} by phase label."""
    press = [t['turn_idx'] for t in rec['turns'] if t['phase'] == 'pressure']
    rel = [t['turn_idx'] for t in rec['turns'] if t['phase'] == 'release']
    if not press or len(rel) != 12:
        raise ValueError(f"{rec['conv_id']}: {len(press)} pressure / {len(rel)} release turns")
    return {'end_pressure': max(press), 'release_4': rel[3], 'release_8': rel[7], 'release_12': rel[11]}


def contexts(CA, rec, fill, subjects, ntok):
    """{cell: {turn_idx: messages}} rebuilt by the old stitching code."""
    press_idx = CA.pressure_turn_idx(rec, subjects[rec['topic']])
    out = {}
    for cell in CELLS:
        pairs, _ = CA.stitch(rec, fill, cell, 'replace', ntok, press_idx)
        out[cell] = {t['turn_idx']: m for t, m in pairs}
    return out


def gate_check(old_cell, turn_idx, p_a, orders):
    """(ok, detail): replayed old-probe values against the old cell file's row at turn_idx."""
    row = next((r for r in old_cell['rows'] if r['turn_idx'] == turn_idx), None)
    if row is None or row.get('p_a') is None or not row.get('p_orders'):
        return False, 'no_old_reading'
    d = max(abs(p_a - row['p_a']), *(abs(a - b) for a, b in zip(orders, row['p_orders'])))
    return d <= GATE_TOL, round(d, 4)


def gate_passed(gate, label):
    """True only if the gate file has exactly one row per cell A/B/C/D at this checkpoint and all pass."""
    rows = [r for r in gate['rows'] if r['checkpoint'] == label]
    return sorted(r['cell'] for r in rows) == list(CELLS) and all(r['ok'] for r in rows)


def code_identity():
    files = [ROOT / 'scripts/reread_old_ablation.py', ROOT / 'scripts/ablation_v5.py', ROOT / 'scripts/new_dialogue_v5.py',
             ROOT / 'vendor/digital_mind/context_ablation.py', ROOT / 'vendor/digital_mind/runner.py']
    return {p.name: sha(p) for p in files}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True, choices=SETS); ap.add_argument('--model', required=True)
    ap.add_argument('--revision', required=True); ap.add_argument('--device', required=True)
    ap.add_argument('--data', required=True, help='folder holding runs/ and the topics files')
    ap.add_argument('--out', required=True); ap.add_argument('--only', nargs='*')
    ap.add_argument('--gate-only', action='store_true'); ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    if SETS[a.set]['model_key'] not in a.model.lower():
        raise SystemExit(f'--set {a.set} needs the {SETS[a.set]["model_key"]} model')
    import torch, transformers
    from huggingface_hub import snapshot_download
    import runner as R
    import context_ablation as CA
    from ablation_v5 import v5_readouts, existing
    recs, old, fills, subjects, hashes = load_set(a.data, a.set)
    if a.only:
        missing = set(a.only) - set(recs)
        if missing:
            raise SystemExit(f'unknown conversations {sorted(missing)}')
        recs = {c: recs[c] for c in a.only}
    system = CA.run_system(str(Path(a.data) / SETS[a.set]['run']))
    R.MIN_PROBE_MASS = 0.0   # as the old script: low mass is recorded, never fatal
    out_dir = Path(a.out) / a.set
    rr = None
    failures = []
    for conv, rec in recs.items():
        fill = fills[CA.fill_id(rec)]
        base_prov = {'set': a.set, 'model': a.model, 'revision': a.revision, 'system': system, 'gate_tol': GATE_TOL,
                     'meta_sha256': hashes[f'meta/{conv}.json'], 'fill_sha256': hashes[f'fill/{CA.fill_id(rec)}.json'],
                     'old_sha256': {c: hashes[f'old/{conv}__{c}__replace.json'] for c in CELLS}, 'code': code_identity()}
        gate_out = out_dir / f'{conv}__gate.json'
        gate = existing(gate_out, dict(base_prov, kind='gate'))
        if gate is None or (not a.gate_only and gate.get('status') != 'complete'):
            if rr is None:
                path = snapshot_download(a.model, revision=a.revision, ignore_patterns=['original/*'])
                rr = R.Runner(path, device=a.device, system=system); torch.set_grad_enabled(False)
                ntok = lambda s: len(rr.tok.encode(s, add_special_tokens=False))
            ctx = contexts(CA, rec, fill, subjects, ntok)
            t0 = time.monotonic(); rows = []
            for label, idx in checkpoints(rec).items():
                for cell in CELLS:
                    p_a, mass, orders = rr.probe_stance_averaged(ctx[cell][idx], rec['side_a'], rec['side_b'])
                    ok, d = gate_check(old[(conv, cell)], idx, p_a, orders)
                    rows.append({'checkpoint': label, 'turn_idx': idx, 'cell': cell, 'p_a': p_a, 'mass': mass,
                                 'p_orders': orders, 'ok': ok, 'max_abs_diff': d,
                                 'ctx_tokens': int(rr._encode(ctx[cell][idx])['input_ids'].shape[-1])})
            gate = {'design': DESIGN, 'kind': 'gate', 'conv_id': conv, 'provenance': dict(base_prov, kind='gate'),
                    'rows': rows, 'build': build_identity(), 'torch': torch.__version__,
                    'transformers': transformers.__version__, 'seconds': time.monotonic() - t0, 'status': 'complete'}
            save(gate_out, gate)
        bad = sorted({(r['checkpoint'], r['cell']) for r in gate['rows'] if not r['ok']}
                     | {(lab, 'incomplete') for lab in checkpoints(rec) if not gate_passed(gate, lab)
                        and all(r['ok'] for r in gate['rows'] if r['checkpoint'] == lab)})
        print(conv, 'gate', 'OK' if not bad else f'FAILED {bad}', flush=True)
        if bad:
            failures.append(conv)
        if a.gate_only:
            continue
        passed = [lab for lab in checkpoints(rec) if gate_passed(gate, lab)]
        for cell in CELLS:
            out = out_dir / f'{conv}__{cell}.json'
            prov = dict(base_prov, kind='readout', cell=cell, checkpoints=passed)
            if existing(out, prov) is not None:
                continue
            if rr is None:
                path = snapshot_download(a.model, revision=a.revision, ignore_patterns=['original/*'])
                rr = R.Runner(path, device=a.device, system=system); torch.set_grad_enabled(False)
                ntok = lambda s: len(rr.tok.encode(s, add_special_tokens=False))
            ctx = contexts(CA, rec, fill, subjects, ntok)
            t0 = time.monotonic(); rows = []
            for label, idx in checkpoints(rec).items():
                if label in passed:
                    for r in v5_readouts(rr, torch, ctx[cell][idx], rec['side_a'], rec['side_b'], idx):
                        rows.append(dict(r, checkpoint=label))
            res = {'design': DESIGN, 'kind': 'readout', 'conv_id': conv, 'cell': cell, 'provenance': prov,
                   'condition': rec['condition'], 'topic': rec['topic'], 'order': rec['option_order'],
                   'opening_side': rec['opening_side'], 'readouts': rows, 'build': build_identity(),
                   'torch': torch.__version__, 'transformers': transformers.__version__,
                   'seconds': time.monotonic() - t0, 'status': 'complete'}
            save(out, res)
            print(conv, cell, f'{res["seconds"]:.0f}s', f'{len(passed)} checkpoints', flush=True)
    if failures:
        print(f'{len(failures)} conversations failed the gate:', failures, flush=True)
        if a.strict:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
