"""Pre-sprint frozen-history diagnostic. prepare is CPU-only; run needs CUDA.

Outputs stay outside historical run directories. No treatment is regenerated.
The four cells retain the OLD templates: this tests the discount sentence,
not complete semantic equivalence of the two instruments.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vendor" / "digital_mind"))
from audit_frozen_history_checkpoints import classify, LlamaBPE
from stance_text import UNPARSED


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def prepare(args):
    target = Path(args.out)
    if target.exists():
        raise SystemExit('Manifest exists; choose a new output instead of overwriting.')
    rows = classify(args.run, LlamaBPE(args.tokenizer), 768)
    grouped = {}
    for row in rows:
        if row['condition'] == 'pressure_release':
            grouped.setdefault(row['conv_id'], []).append(row)
    selected = []
    for cid, turns in sorted(grouped.items()):
        hit = False
        source = Path(args.run) / 'meta' / (cid + '.json')
        for row in sorted(turns, key=lambda r: r['turn_idx']):
            hit |= row['cap_hit']
            labels = [key for key in ('is_text_tof', 'is_late_disagreement') if row[key]]
            if row['phase'] == 'opening':
                labels.append('opening_reference')
            if labels and not hit:
                selected.append(dict(source=str(source), sha256=sha(source),
                                     conv_id=cid, topic=row['topic'], order=row['order'],
                                     turn_idx=row['turn_idx'], phase=row['phase'],
                                     selection=labels, prefix_cap_safe=True))
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    manifest = dict(schema=1, purpose='pre-sprint diagnostic; selected, not prevalence sample',
                    source_commit=commit, tokenizer_sha256=sha(args.tokenizer),
                    completion='inferred from token count; no stored finish reason',
                    checkpoints=selected)
    save(target, manifest)
    print(f'{len(selected)} checkpoints; {len({r["topic"] for r in selected})} topics; {target}')


def run(args):
    from verify_provenance import verify
    verify()
    import torch
    import transformers
    import runner as R
    from reprobe_wording import PROBE_VARIANTS, ELICIT_VARIANTS
    manifest = json.loads(Path(args.manifest).read_text())
    root = Path(args.out)
    root.mkdir(parents=True, exist_ok=True)
    # Validate every source BEFORE loading a model or spending GPU time.
    for item in manifest['checkpoints']:
        if sha(item['source']) != item['sha256']:
            raise SystemExit('Source changed: ' + item['source'])
    manifest_hash = sha(args.manifest)
    rr = R.Runner(args.model, device=args.device)
    identity = dict(manifest_sha256=manifest_hash, model=args.model,
                    config=rr.model.config.to_dict(), torch=torch.__version__,
                    transformers=transformers.__version__,
                    tokenizer_class=type(rr.tok).__name__,
                    device=str(rr.device), dtype=str(rr.model.dtype),
                    probe_templates=PROBE_VARIANTS, prose_templates=ELICIT_VARIANTS,
                    prose_cap=R.ELICIT_MAX_NEW_TOKENS)
    identity_hash = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    save(root / ('environment-' + identity_hash[:12] + '.json'), identity)
    for item in manifest['checkpoints']:
        path = root / f'{item["conv_id"]}__t{item["turn_idx"]}.json'
        if path.exists():
            old = json.loads(path.read_text())
            if old['identity_sha256'] != identity_hash:
                raise SystemExit('Resume configuration mismatch: ' + str(path))
            continue
        rec = json.loads(Path(item['source']).read_text())
        messages = []
        for turn in rec['turns']:
            messages += [dict(role='user', content=turn['user_text']),
                         dict(role='assistant', content=turn['model_text'])]
            if turn['turn_idx'] == item['turn_idx']:
                break
        else:
            raise ValueError('Checkpoint not found')
        order = rec['option_order']
        sa, sb = rec['side_a'], rec['side_b']
        shown_a, shown_b = (sa, sb) if order == 1 else (sb, sa)
        def canonical(slot):
            return slot if slot == UNPARSED or order == 1 else ('B' if slot == 'A' else 'A')
        def probe(name):
            original = R.STANCE_PROBE
            try:
                R.STANCE_PROBE = PROBE_VARIANTS[name]
                p, mass, orders = rr.probe_stance_averaged(messages, sa, sb)
                return dict(p_a=p, mass=mass, orders=orders)
            finally:
                R.STANCE_PROBE = original
        def prose(name):
            prompt = ELICIT_VARIANTS[name].format(LA='A', LB='B', side_a=shown_a, side_b=shown_b)
            enc = rr._encode(messages + [dict(role='user', content=prompt)])
            with torch.inference_mode():
                output = rr.model.generate(**enc, max_new_tokens=R.ELICIT_MAX_NEW_TOKENS,
                    do_sample=False, pad_token_id=rr.tok.eos_token_id)
            ids = output[0, enc['input_ids'].shape[-1]:]
            text = rr.tok.decode(ids, skip_special_tokens=True).strip()
            eos = rr.model.generation_config.eos_token_id
            eos = set(eos if isinstance(eos, list) else [eos])
            ended = bool(len(ids)) and int(ids[-1]) in eos
            slot = R.parse_opening_side(text, shown_a, shown_b)
            return dict(text=text, side=canonical(slot), output_tokens=len(ids),
                        finish_reason='eos' if ended else 'length_or_other',
                        cap_hit=len(ids) >= R.ELICIT_MAX_NEW_TOKENS and not ended)
        started = time.monotonic()
        base_p, base_t = probe('orig'), prose('orig')
        stored_orders = turn.get('p_a_orders', [])
        delta = max([abs(base_p['p_a'] - turn['p_a'])] +
                    [abs(a-b) for a,b in zip(base_p['orders'], stored_orders)])
        reasons = []
        if len(stored_orders) != 2 or delta > .02:
            reasons.append('probe_reconstruction_failed')
        if base_p['mass'] < .9:
            reasons.append('probe_low_mass')
        if base_t['side'] == UNPARSED or base_t['side'] != turn['elicited_side']:
            reasons.append('prose_reconstruction_failed_or_unparsed')
        if base_t['cap_hit']:
            reasons.append('baseline_prose_capped')
        result = dict(checkpoint=item, identity_sha256=identity_hash,
                      probe_orig=base_p, prose_orig=base_t,
                      stored_prose=turn.get('elicited_text'), stored_side=turn['elicited_side'],
                      reconstruction_delta=delta, gate_pass=not reasons, gate_reasons=reasons)
        if not reasons:
            result.update(probe_no_discount=probe('no_discount'), prose_discount=prose('discount'))
            result['counterfactual_valid'] = (result['probe_no_discount']['mass'] >= .9
                                             and not result['prose_discount']['cap_hit']
                                             and result['prose_discount']['side'] != UNPARSED)
        result['wall_seconds'] = time.monotonic() - started
        save(path, result)
        print(item['conv_id'], item['turn_idx'], 'PASS' if not reasons else reasons, flush=True)


def report(args):
    import csv
    records = [json.loads(p.read_text()) for p in sorted(Path(args.results).glob('*__t*.json'))]
    identities = {r['identity_sha256'] for r in records}
    if len(identities) > 1:
        raise SystemExit('Mixed execution identities; do not pool.')
    rows = []
    for r in records:
        item = r['checkpoint']
        row = {k: item[k] for k in ('conv_id', 'topic', 'order', 'turn_idx', 'phase')}
        row.update(gate_pass=r['gate_pass'], reasons=';'.join(r['gate_reasons']),
                   valid=r.get('counterfactual_valid', False), wall_seconds=r['wall_seconds'])
        if row['valid']:
            row['probe_discount_effect'] = r['probe_orig']['p_a'] - r['probe_no_discount']['p_a']
            # Probability-space signs are descriptive; straddle is retained explicitly.
            for condition, pk, tk in [('no_discount', 'probe_no_discount', 'prose_orig'),
                                      ('discount', 'probe_orig', 'prose_discount')]:
                values = r[pk]['orders']
                straddle = (values[0] >= .5) != (values[1] >= .5)
                side = 'A' if r[pk]['p_a'] >= .5 else 'B'
                row[condition + '_straddle'] = straddle
                row[condition + '_mean_disagrees'] = side != r[tk]['side']
                row[condition + '_both_orders_disagree'] = (not straddle and side != r[tk]['side'])
        rows.append(row)
    columns = list(dict.fromkeys(k for row in rows for k in row))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)} results; {sum(r["gate_pass"] for r in rows)} baseline passes; '
          f'{sum(r["valid"] for r in rows)} valid counterfactual pairs')
    print('Selected diagnostic only. Review prose manually; do not interpret parser agreement as truth.')
    for topic in sorted({r['topic'] for r in rows}):
        for phase in ('opening', 'pressure'):
            sub = [r for r in rows if r['topic'] == topic and r['phase'] == phase and r['valid']]
            if sub:
                avg = sum(r['probe_discount_effect'] for r in sub) / len(sub)
                print(topic, phase, 'n=', len(sub), 'mean discount effect=', round(avg, 4))
    print('CSV:', args.out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--run', default='data/external/digital-mind/runs/repl_b1')
    p.add_argument('--tokenizer', default='Llama-3.1-8B-Instruct/tokenizer.json')
    p.add_argument('--out', required=True)
    r = sub.add_parser('run')
    r.add_argument('--manifest', required=True)
    r.add_argument('--model', required=True)
    r.add_argument('--out', required=True)
    r.add_argument('--device', default='cuda')
    s = sub.add_parser('report')
    s.add_argument('--results', required=True)
    s.add_argument('--out', required=True)
    args = ap.parse_args()
    {'prepare': prepare, 'run': run, 'report': report}[args.command](args)


if __name__ == '__main__':
    main()
