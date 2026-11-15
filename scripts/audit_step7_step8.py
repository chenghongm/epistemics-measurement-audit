"""Read-only, GPU-free integrity audit of the archived main, step 7 and step 8 data.

Usage: python3 scripts/audit_step7_step8.py [--out /tmp/audit.json]
Checks actual outputs independently of stored gate flags and canonical prose labels.
This does not validate semantic neutrality or independently rerun model inference.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import ablation_v5 as ab
import analyze_ablation_v5 as aa
import analyze_v5 as an
import analyze_reread_old as ar
import reread_old_ablation as ro
import review_fill_v5 as rf
from new_dialogue_v5 import load_topics, text_side

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(root=ROOT):
    errors, counts = [], Counter()

    def require(ok, message):
        if not ok:
            errors.append(message)

    def labels(rows, sa, sb, location, keys=('prose',)):
        for row in rows:
            for key in keys:
                require(text_side(row[key]['text'], sa, sb) == row[key + '_canonical'],
                        f'{location}: stale {key} classification')
                counts['prose_labels_recomputed'] += 1

    for name in ('ablation_v5', 'reread_old'):
        base = root / 'results' / name
        for line in (base / 'MANIFEST.sha256').read_text().splitlines():
            expected, rel = line.split(maxsplit=1)
            path = base / rel.lstrip('*')
            require(path.exists() and sha(path) == expected, f'{name}: manifest mismatch {rel}')
            counts['manifest_entries'] += 1

    topics = load_topics()
    raw, cells = aa.load(root / 'results/ablation_v5/raw', root / 'results/main_v5/raw')
    require(len(raw) == 96, f'main histories: {len(raw)} != 96')
    require(len(cells) == 48, f'step 7 histories: {len(cells)} != 48')
    counts['main_histories'] = len(raw)
    for name, history in raw.items():
        topic = topics[history['args']['topic']]
        require(text_side(history['turns'][0]['text'], topic['side_a'], topic['side_b']) == history['opening_canonical'],
                f'{name}: opening canonical side mismatch')
        if history['args']['condition'] == 'pressure':
            direction = 'vs_a' if history['opening_canonical'] == 'A' else 'vs_b'
            require([t['prompt'] for t in history['turns'][1:6]] == topic['ladders'][direction],
                    f'{name}: exposure prompts do not match the opposite-side ladder')
        labels(history['readouts'], topic['side_a'], topic['side_b'], name, ('prose', 'labelled_prose'))

    reviewed = {}
    for model in ('llama', 'qwen'):
        base = root / 'results/fill_v5'
        supplements = [(base / 'supplement/llama_four_day_week.json').read_bytes()] if model == 'llama' else []
        rebuilt = rf.review((base / f'{model}.json').read_bytes(), supplements)
        blob = (json.dumps(rebuilt, indent=2, ensure_ascii=False) + '\n').encode()
        path = base / f'{model}.reviewed.json'
        require(blob == path.read_bytes(), f'{model}: reviewed filler rebuild differs')
        reviewed[model] = rebuilt, sha(path)
        for name, topic in rebuilt['topics'].items():
            require(len(topic['selected']) == 5, f'{model}/{name}: not five filler pairs')
            for i in topic['selected']:
                c = topic['candidates'][i]
                require(c['reject'] is None and c['finish'] == 'eos', f'{model}/{name}/{i}: rejected or truncated filler selected')
                counts['reviewed_filler_pairs'] += 1

    for name, cs in cells.items():
        src = raw[name]
        model = name.split('_')[0]
        require(set(cs) == set('ABCD'), f'{name}: missing/extra cells')
        topic = topics[src['args']['topic']]
        source_sha = sha(root / f'results/main_v5/raw/{name}.json')
        fill_doc, fill_sha = reviewed[model]
        v = fill_doc['topics'][src['args']['topic']]
        fill = [(v['candidates'][i]['question'], v['candidates'][i]['answer']) for i in v['selected']]
        for k, (ok, reason) in aa.gate(src, cs).items():
            require(ok, f'{name}/{k}: independently recomputed gate failed: {reason}')
            counts['step7_gated_checkpoints'] += 1
        for c, rec in cs.items():
            prov = rec['provenance']
            require(prov['source_history_sha256'] == source_sha and prov['fill_sha256'] == fill_sha,
                    f'{name}/{c}: source/filler provenance mismatch')
            expected = {(k, disc, o) for k in (5, 9) for disc in (False, True) for o in (1, 2)}
            actual = [(r['index'], r['discount'], r['printed_order']) for r in rec['readouts']]
            require(len(actual) == len(expected) and set(actual) == expected, f'{name}/{c}: incomplete/duplicate readouts')
            require(rec['status'] == 'complete', f'{name}/{c}: status is not complete')
            for k in (5, 9):
                msgs = ab.cell_messages(src, c, k, fill)
                require(len(msgs) == 2 * (k + 1), f'{name}/{c}/{k}: message count mismatch')
                for i in range(k + 1):
                    q, a = src['turns'][i]['prompt'], src['turns'][i]['text']
                    if 1 <= i <= 5:
                        if c in 'BD':
                            q = fill[i - 1][0]
                        if c in 'CD':
                            a = fill[i - 1][1]
                    require(msgs[2 * i] == {'role': 'user', 'content': q} and
                            msgs[2 * i + 1] == {'role': 'assistant', 'content': a},
                            f'{name}/{c}/{k}: role/content mismatch at turn {i}')
            labels(rec['readouts'], topic['side_a'], topic['side_b'], f'{name}/{c}')
            counts['step7_cells'] += 1

    sets = ar.load(root / 'results/reread_old', root / 'data/external/digital-mind')
    for set_name, (recs, old, gates, cs) in sets.items():
        require(len(recs) == len(gates) == len(cs) == 36, f'{set_name}: incomplete history coverage')
        for name, rec in recs.items():
            ck = ro.checkpoints(rec)
            g = gates[name]
            for label, idx in ck.items():
                require(ro.gate_passed(g, label), f'{set_name}/{name}/{label}: gate not complete/passing')
                for row in [r for r in g['rows'] if r['checkpoint'] == label]:
                    prior = next(r for r in old[(name, row['cell'])]['rows'] if r['turn_idx'] == idx)
                    diffs = [abs(row['p_a'] - prior['p_a'])] + [abs(a - b) for a, b in zip(row['p_orders'], prior['p_orders'])]
                    require(len(row['p_orders']) == len(prior['p_orders']) == 2 and max(diffs) <= ro.GATE_TOL,
                            f'{set_name}/{name}/{label}/{row["cell"]}: old probe values fail independent gate')
                    counts['step8_gate_rows_recomputed'] += 1
            require(set(cs[name]) == set('ABCD'), f'{set_name}/{name}: missing cells')
            for c, cell in cs[name].items():
                expected = {(label, disc, o) for label in ck for disc in (False, True) for o in (1, 2)}
                actual = [(r['checkpoint'], r['discount'], r['printed_order']) for r in cell['readouts']]
                require(len(actual) == len(expected) and set(actual) == expected, f'{set_name}/{name}/{c}: missing/duplicate rows')
                require(all(r['index'] == ck[r['checkpoint']] for r in cell['readouts']), f'{set_name}/{name}/{c}: checkpoint index mismatch')
                require(cell['opening_side'] == rec['opening_side'], f'{set_name}/{name}/{c}: opening anchor mismatch')
                labels(cell['readouts'], rec['side_a'], rec['side_b'], f'{set_name}/{name}/{c}')
                counts['step8_cells'] += 1
    return {'passed': not errors, 'counts': dict(counts), 'errors': errors,
            'limits': 'No GPU inference or semantic-neutrality validation; current data integrity only, not adversarial robustness of the frozen analysers.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = audit()
    blob = json.dumps(result, indent=2) + '\n'
    if args.out:
        args.out.write_text(blob)
    print(blob)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
