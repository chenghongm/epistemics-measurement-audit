"""Pre-sprint frozen-history diagnostic. prepare is CPU-only; run needs CUDA.

Outputs stay outside historical run directories. No treatment is regenerated.
The four cells retain the OLD templates: this tests the discount sentence,
not complete semantic equivalence of the two instruments.
"""
import argparse
import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vendor" / "digital_mind"))
from audit_frozen_history_checkpoints import classify, LlamaBPE
from stance_text import UNPARSED, classify_opening


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


def repository_identity(repo):
    if (repo / '.git').exists():
        return dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip(),
                    dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True).strip()))
    metadata = repo / 'provenance/build.json'
    return json.loads(metadata.read_text()) if metadata.exists() else dict(commit=None, dirty=None)


def safe_probe(runner, messages, sa, sb, error_type):
    try:
        p, mass, orders = runner.probe_stance_averaged(messages, sa, sb)
        return dict(p_a=p, mass=mass, orders=orders)
    except error_type as exc:
        return dict(error=type(exc).__name__, message=str(exc))


def pinned_model(args, manifest):
    """Validate tokenizer on CPU before downloading weights or constructing Runner."""
    from huggingface_hub import snapshot_download
    if not re.fullmatch(r'[0-9a-f]{40}', args.revision):
        raise ValueError('--revision must be an immutable 40-character Hub commit SHA')
    if Path(args.model).exists():
        raise ValueError('Use a Hub model ID and pinned revision; local weight provenance is unknown')
    path = Path(snapshot_download(args.model, revision=args.revision,
                                 allow_patterns=['*.json', '*.jinja', 'tokenizer.*', '*.model']))
    actual = sha(path / 'tokenizer.json')
    if actual != manifest['tokenizer_sha256']:
        raise ValueError('Tokenizer mismatch before weight loading: ' + actual)
    files = {p.name: sha(p) for p in sorted(path.iterdir())
             if p.is_file() and (p.suffix in ('.json', '.jinja', '.model') or p.name.startswith('tokenizer.'))}
    # The historical manifest pins tokenizer.json only, not the old chat template.
    # Record the complete current tokenizer/config identity without claiming an old-template match.
    # Skip Meta's duplicate original/ checkpoint (~16 GB consolidated.*.pth); Runner loads safetensors.
    snapshot_download(args.model, revision=args.revision, ignore_patterns=['original/*'])
    return str(path), files


def own_probability(p_a, opening_side):
    if opening_side not in ('A', 'B'):
        raise ValueError('Unknown opening side: ' + opening_side)
    return p_a if opening_side == 'A' else 1 - p_a


SIGN_TOL = .02  # same as the reconstruction tolerance: smaller probe changes are within replay noise


def effect_sign(value, tol=SIGN_TOL):
    return 0 if abs(value) <= tol else (1 if value > 0 else -1)


def prose_outcome(cell):
    if cell['cap_hit']:
        return 'truncated'
    return cell['side'] if cell['side'] in ('A', 'B') else 'unparsed_review_required'


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
    model_path, tokenizer_files = pinned_model(args, manifest)
    rr = R.Runner(model_path, device=args.device)
    repo = Path(__file__).resolve().parent.parent
    sources = json.loads((repo / 'provenance/sources.json').read_text())
    identity = dict(schema=2, manifest_sha256=manifest_hash, model=args.model,
                    model_revision=args.revision, tokenizer_files=tokenizer_files,
                    historical_chat_template_verified=False,
                    repository=repository_identity(repo),
                    runtime_hashes={str(p.relative_to(repo)): sha(p) for p in
                                    sorted((repo / 'scripts').glob('*.py'))},
                    vendor_hashes={e['local_path']: sha(repo / e['local_path']) for e in sources['vendored_code']},
                    gpu_name=torch.cuda.get_device_name(rr.device) if str(rr.device).startswith('cuda') else None,
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
                return safe_probe(rr, messages, sa, sb, R.ProbeMassError)
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
            verdict = classify_opening(text, shown_a, shown_b)
            slot = verdict.side
            return dict(text=text, side=canonical(slot), classifier=asdict(verdict), output_tokens=len(ids),
                        finish_reason='eos' if ended else 'length_or_other',
                        cap_hit=len(ids) >= R.ELICIT_MAX_NEW_TOKENS and not ended)
        started = time.monotonic()
        base_p, base_t = probe('orig'), prose('orig')
        stored_orders = turn.get('p_a_orders', [])
        delta = None if 'error' in base_p else max([abs(base_p['p_a'] - turn['p_a'])] +
                    [abs(a-b) for a,b in zip(base_p['orders'], stored_orders)])
        reasons = []
        if 'error' in base_p:
            reasons.append('baseline_probe_mass_error')
        elif len(stored_orders) != 2 or delta > .02:
            reasons.append('probe_reconstruction_failed')
        if 'error' not in base_p and base_p['mass'] < .9:
            reasons.append('probe_low_mass')
        if base_t['side'] == UNPARSED or base_t['side'] != turn['elicited_side']:
            reasons.append('prose_reconstruction_failed_or_unparsed')
        if base_t['cap_hit']:
            reasons.append('baseline_prose_capped')
        result = dict(checkpoint=item, opening_side=rec['opening_side'], identity_sha256=identity_hash,
                      probe_orig=base_p, prose_orig=base_t,
                      stored_prose=turn.get('elicited_text'), stored_side=turn['elicited_side'],
                      reconstruction_delta=delta, gate_pass=not reasons, gate_reasons=reasons)
        if not reasons:
            result.update(probe_no_discount=probe('no_discount'), prose_discount=prose('discount'))
            result['probe_counterfactual_valid'] = ('error' not in result['probe_no_discount']
                                                       and result['probe_no_discount']['mass'] >= .9)
            result['prose_discount_outcome'] = prose_outcome(result['prose_discount'])
            result['counterfactual_valid'] = (result['probe_counterfactual_valid']
                                             and result['prose_discount_outcome'] in ('A', 'B'))
        result['wall_seconds'] = time.monotonic() - started
        save(path, result)
        print(item['conv_id'], item['turn_idx'], 'PASS' if not reasons else reasons, flush=True)


def report(args):
    import csv
    from collections import Counter
    records = [json.loads(p.read_text()) for p in sorted(Path(args.results).glob('*__t*.json'))]
    if len({r['identity_sha256'] for r in records}) > 1:
        raise SystemExit('Mixed execution identities; do not pool.')
    manifest = json.loads(Path(args.manifest).read_text())
    expected = {(i['conv_id'], i['turn_idx']) for i in manifest['checkpoints']}
    actual = [(r['checkpoint']['conv_id'], r['checkpoint']['turn_idx']) for r in records]
    if len(actual) != len(set(actual)) or set(actual) - expected:
        raise SystemExit('Duplicate or unexpected checkpoints')
    if records:
        env = json.loads((Path(args.results) / ('environment-' + records[0]['identity_sha256'][:12] + '.json')).read_text())
        if env['manifest_sha256'] != sha(args.manifest) or env.get('schema') != 2:
            raise SystemExit('Manifest mismatch or legacy results; use schema-2 execution results')
    rows = []
    for r in records:
        item = r['checkpoint']
        row = {k: item[k] for k in ('conv_id', 'topic', 'order', 'turn_idx', 'phase')}
        row.update(gate_pass=r['gate_pass'], reasons=';'.join(r['gate_reasons']),
                   wall_seconds=r['wall_seconds'])
        if r['gate_pass']:
            own = r['opening_side']
            outcome = prose_outcome(r['prose_discount'])
            row.update(opening_side=own, prose_discount_outcome=outcome,
                       probe_counterfactual_valid=r['probe_counterfactual_valid'])
            if outcome in ('A', 'B'):
                row['prose_discount_effect_own'] = (int(outcome == own) - int(r['prose_orig']['side'] == own))
            if r['probe_counterfactual_valid']:
                row['probe_discount_effect_own'] = (own_probability(r['probe_orig']['p_a'], own)
                                                    - own_probability(r['probe_no_discount']['p_a'], own))
                for condition, pk, tk in [('no_discount', 'probe_no_discount', 'prose_orig'),
                                          ('discount', 'probe_orig', 'prose_discount')]:
                    values = r[pk]['orders']
                    straddle = (values[0] >= .5) != (values[1] >= .5)
                    side = 'A' if r[pk]['p_a'] >= .5 else 'B'
                    row[condition + '_straddle'] = straddle
                    if prose_outcome(r[tk]) in ('A', 'B'):
                        row[condition + '_mean_disagrees'] = int(side != r[tk]['side'])
                        row[condition + '_both_orders_disagree'] = int(not straddle and side != r[tk]['side'])
                if outcome in ('A', 'B'):
                    # Probe (probability) and prose (indicator) effects are on different scales;
                    # compare only their directions, never their difference.
                    row['discount_sign_pair'] = '{:+d}/{:+d}'.format(
                        effect_sign(row['probe_discount_effect_own']), row['prose_discount_effect_own'])
                    for rule in ('mean', 'both_orders'):
                        suffix = '_mean_disagrees' if rule == 'mean' else '_both_orders_disagree'
                        row[rule + '_disagreement_change'] = (row['discount' + suffix]
                                                              - row['no_discount' + suffix])
        rows.append(row)
    columns = list(dict.fromkeys(k for row in rows for k in row))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f'{len(rows)}/{len(expected)} checkpoints; missing={len(expected - set(actual))}; '
          f'baseline passes={sum(r["gate_pass"] for r in rows)}')
    print('Selected diagnostic only. Unparsed prose requires manual refusal/mixed/parser review; '
          'truncation is a measurement failure. Binary effects are conditional on evaluable pairs.')
    summaries = []
    metrics = ('probe_discount_effect_own', 'prose_discount_effect_own',
               'mean_disagreement_change', 'both_orders_disagreement_change',
               'no_discount_mean_disagrees', 'discount_mean_disagrees',
               'no_discount_both_orders_disagree', 'discount_both_orders_disagree')
    for topic, phase in sorted({(r['topic'], r['phase']) for r in rows}):
        sub = [r for r in rows if r['topic'] == topic and r['phase'] == phase]
        passing = [r for r in sub if r['gate_pass']]
        summary = dict(topic=topic, phase=phase, n=len(sub), baseline_passes=len(passing),
                       prose_outcomes=dict(Counter(r['prose_discount_outcome'] for r in passing)),
                       probe_invalid=sum(not r['probe_counterfactual_valid'] for r in passing),
                       discount_sign_pairs=dict(Counter(r['discount_sign_pair'] for r in passing
                                                        if 'discount_sign_pair' in r)))
        for key in metrics:
            values = [r[key] for r in passing if key in r]
            summary[key] = dict(n=len(values), mean=sum(values)/len(values),
                                min=min(values), max=max(values)) if values else dict(n=0)
        summaries.append(summary)
        print(json.dumps(summary, ensure_ascii=False))
    save(str(args.out) + '.summary.json', dict(missing=sorted(expected - set(actual)), topics=summaries,
         definitions=dict(discount_sign_pair='probe/prose direction of the discount effect on own side; '
                                             'probe sign is 0 within +/-0.02; scales are not differenced',
                          disagreement_change='discount minus no-discount disagreement; paired binary outcomes only')))
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
    r.add_argument('--revision', required=True, help='Immutable Hugging Face model commit SHA')
    r.add_argument('--out', required=True)
    r.add_argument('--device', default='cuda')
    s = sub.add_parser('report')
    s.add_argument('--results', required=True)
    s.add_argument('--manifest', default='provenance/checkpoints.json')
    s.add_argument('--out', required=True)
    args = ap.parse_args()
    {'prepare': prepare, 'run': run, 'report': report}[args.command](args)


if __name__ == '__main__':
    main()
