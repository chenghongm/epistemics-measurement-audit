"""Analysis of the v5 context ablation (scripts/ablation_v5.py), frozen before any B/C/D readout.

Usage: python3 scripts/analyze_ablation_v5.py ABLATION_DIR RAW_DIR [--out DIR]
RAW_DIR holds the archived v5 histories (results/main_v5/raw); pressure ones are the source histories,
neutral ones give the D-vs-neutral diagnostic. Writes summary.md and cells.csv. Pure Python.

Fixed here:
- Categories follow docs/readout_rule.md (analyze_v5.category), anchored to the original opening side.
- Gate, applied independently of the runner: a (history, checkpoint) enters paired claims only if every
  cell-A readout at that checkpoint reproduces the archive (probe within ablation_v5.PROBE_TOL, prose text
  identical) and all four cell files exist.
- Primary estimand: no-discount unlabelled prose, at checkpoint 5 and at checkpoint 9 (reported
  separately, 5 first). Per history, a cell "keeps the shift" if its category is other_both. B vs C is
  the paired 2x2 of keeps-the-shift over valid pairs: a pair with B or C unresolved (truncated prose,
  unparsed wording) is excluded and counted, never scored as "does not keep". A split is a resolved
  outcome and counts as not keeping; pairs with a split are listed.
- Inference unit is the topic (the two orders of a topic share topic, ladder and often the opening): per
  topic d = sum of (B keeps - C keeps), exact two-sided sign test over topics with d != 0. History counts
  are descriptive. (Revised after the Codex review, before any B/C/D readout.)
- Two cohorts, separate denominators: all pressure histories with a parsed opening, and the fixed
  primary-flipped cohort (flip under the main analysis's primary trajectory). Neither is redefined from
  ablated readings.
- Splits and unresolved are counted as their own categories, never merged into a side.
- Secondary: the same B-vs-C table under the discount prefix; probe order-averaged clipped log-odds of
  the opening side, as paired differences (B-D, C-D, B-C) with sign counts (no retention ratio as an
  endpoint); strata by model, topic group and n-gram status of the source history; per-topic cells.
- Diagnostics: context tokens per cell and checkpoint, filler/original token ratios by role, position
  and topic, and D against the matched neutral history at the same checkpoint.
"""
import argparse
import csv
import json
import math
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

import ablation_v5 as ab
import analyze_v5 as an

CELLS = ab.CELLS
CKS = ab.CHECKPOINTS


def sign_test(b, c):
    """Exact two-sided binomial p for b vs c discordant pairs."""
    n = b + c
    if n == 0:
        return None
    k = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, p)


def load(ablation_dir, raw_dir):
    raw = {}
    for p in sorted(Path(raw_dir).glob('*.json')):
        h = json.loads(p.read_text())
        if h.get('design') == 'ladder_v5' and h.get('kind') == 'main':
            raw[ab.history_name(h)] = h
    cells = defaultdict(dict)
    for p in sorted(Path(ablation_dir).glob('*__?.json')):
        r = json.loads(p.read_text())
        if r.get('design') == ab.DESIGN:
            cells[r['history']][r['cell']] = r
    return raw, cells


def as_history(rec, own):
    """Wrap a cell record so analyze_v5.checkpoints can categorise its readouts."""
    rs = [dict(r, labelled_prose={'finish': 'n/a'}, labelled_prose_canonical=None, labelled_prose_letter_slot=None)
          for r in rec['readouts']]
    return {'opening_canonical': own, 'readouts': rs}


def gate(src, cells):
    """{checkpoint: (passed, reason)} for one history."""
    out = {}
    for k in CKS:
        if any(c not in cells or cells[c].get('status') not in ('complete', 'reconstruction_failed') for c in CELLS):
            out[k] = (False, 'missing_cell')
            continue
        rows = [r for r in cells['A']['readouts'] if r['index'] == k]
        rec = ab.reconstruction(src, rows)
        keys = sorted((r['discount'], r['printed_order']) for r in rows)
        # exactly the four (discount, order) readouts, each reproducing the archive
        ok = keys == [(d, o) for d in (False, True) for o in (1, 2)] and all(p and q for p, q in rec.values())
        out[k] = (ok, None if ok else 'reconstruction')
    return out


def categories(src, cells):
    """{(cell, checkpoint, discount, readout): category} and {(cell, checkpoint, discount): probe log-odds}."""
    own = src['opening_canonical']
    cats, lo = {}, {}
    for c, rec in cells.items():
        cc, cont = an.checkpoints(as_history(rec, own))
        for (idx, disc, ro), cat in cc.items():
            if ro in ('probe', 'prose'):
                cats[(c, idx, disc, ro)] = cat
        for (idx, disc), v in cont.items():
            lo[(c, idx, disc)] = v[0]
    return cats, lo


def neutral_name(name):
    return name[:-len('pressure')] + 'neutral'


def analyse(raw, cells):
    pressure = {n: h for n, h in raw.items() if h['args']['condition'] == 'pressure' and h.get('opening_canonical') in ('A', 'B')}
    info = {}
    for n, src in pressure.items():
        cs = cells.get(n, {})
        g = gate(src, cs)
        cats, lo = categories(src, cs) if cs else ({}, {})
        flip = an.trajectory(an.checkpoints(src)[0])['flip'] is not None
        touch = an.ngram_touch(src)
        info[n] = {'gate': g, 'cats': cats, 'lo': lo, 'flipped': flip, 'model': n.split('_')[0],
                   'group': src.get('topic_group'), 'topic': src['args']['topic'], 'order': src['args']['order'],
                   'ngram': 'untouched' if touch and not touch['touched'] else 'touched' if touch else 'not_counted',
                   'cells': cs}
    md = ['# v5 context ablation: analysis', '',
          'Generated by `scripts/analyze_ablation_v5.py` (frozen before B/C/D readouts). Cells: A original, '
          'B filler user + own replies, C user pressure + filler replies, D both filler. '
          '"keeps" = category other_both (the shifted side under both printed orders).', '']

    # Coverage and gate
    rows = []
    for m in sorted({i['model'] for i in info.values()}):
        for k in CKS:
            g = Counter(i['gate'][k][1] or 'passed' for i in info.values() if i['model'] == m)
            rows.append([m, k, sum(1 for i in info.values() if i['model'] == m), g['passed'], g['missing_cell'], g['reconstruction']])
    md += ['## Coverage and reconstruction gate', '',
           an.table(rows, ['model', 'checkpoint', 'pressure histories', 'passed', 'missing cell', 'failed reconstruction']), '']

    def paired(sel, k, disc=False, ro='prose'):
        """Paired B/C keeps-the-shift among valid pairs (neither B nor C unresolved). A split is a resolved
        outcome (both orders answered, on different sides) and counts as not keeping; it is also listed.
        Significance is at the topic level only: per topic, d = sum over its histories of (B keeps - C keeps),
        and the sign test runs over topics with d != 0 (histories of one topic are not independent)."""
        get = lambda i, c: i['cats'].get((c, k, disc, ro))
        valid = [i for i in sel if get(i, 'B') not in (None, 'unresolved') and get(i, 'C') not in (None, 'unresolved')]
        both = bo = co = neither = split = 0
        d = defaultdict(int)
        for i in valid:
            b, c = get(i, 'B') == 'other_both', get(i, 'C') == 'other_both'
            both += b and c; bo += b and not c; co += c and not b; neither += not b and not c
            split += get(i, 'B').startswith('split') or get(i, 'C').startswith('split')
            d[i['topic']] += b - c
        tb, tc = sum(v > 0 for v in d.values()), sum(v < 0 for v in d.values())
        p = sign_test(tb, tc)
        keeps = lambda c: f"{sum(get(i, c) == 'other_both' for i in sel)}/{sum(get(i, c) not in (None, 'unresolved') for i in sel)}"
        return [len(sel), len(valid), len(sel) - len(valid), keeps('A'), keeps('D'), both, bo, co, neither, split,
                f'{tb} / {tc} of {len(d)}', '-' if p is None else f'{p:.3g}']

    head = ['histories', 'valid B/C pairs', 'excluded (B or C unresolved)', 'A keeps', 'D keeps', 'B&C keep',
            'only B keeps', 'only C keeps', 'neither', 'pairs with a split', 'topics B>C / C>B', 'topic sign test p']

    def passed(k, **f):
        return [i for i in info.values() if i['gate'][k][0] and all(i[a] == v for a, v in f.items())]

    for disc, title in ((False, 'Primary: B vs C, unlabelled prose, no discount'),
                        (True, 'Secondary: B vs C, unlabelled prose, discount prefix')):
        md += [f'## {title}', '']
        rows = []
        for m in sorted({i['model'] for i in info.values()}):
            for cohort in ('all', 'flipped'):
                for k in CKS:
                    sel = [i for i in passed(k, model=m) if cohort == 'all' or i['flipped']]
                    rows.append([m, cohort, k, *paired(sel, k, disc)])
        md += [an.table(rows, ['model', 'cohort', 'checkpoint', *head]), '']

    md += ['## Category counts per cell (unlabelled prose, no discount, gate passed)', '']
    rows = []
    for m in sorted({i['model'] for i in info.values()}):
        for k in CKS:
            for c in CELLS:
                cnt = Counter(i['cats'].get((c, k, False, 'prose')) for i in passed(k, model=m))
                rows.append([m, k, c] + [cnt[x] for x in an.CATS])
    md += [an.table(rows, ['model', 'checkpoint', 'cell', *an.CATS]), '']

    md += ['## Strata: primary B vs C by topic group and n-gram status (all cohort)', '']
    rows = []
    for m in sorted({i['model'] for i in info.values()}):
        for key in ('group', 'ngram'):
            for v in sorted({i[key] for i in info.values() if i['model'] == m}):
                for k in CKS:
                    rows.append([m, key, v, k, *paired(passed(k, model=m, **{key: v}), k)])
    md += [an.table(rows, ['model', 'stratum', 'value', 'checkpoint', *head]), '']

    md += ['## Probe: paired log-odds of the opening side (order-averaged, clipped, no discount)', '',
           'Lower = further toward the shifted side. B<C counts histories (descriptive) and topics (mean over the '
           "topic's histories) where B sits further toward the shift than C; significance only at the topic level.", '']
    rows = []
    med = lambda v: f'{st.median(v):+.2f}' if v else '-'
    for m in sorted({i['model'] for i in info.values()}):
        for k in CKS:
            d = defaultdict(list); bytopic = defaultdict(list)
            for i in passed(k, model=m):
                lo = {c: i['lo'].get((c, k, False)) for c in CELLS}
                if any(v is None for v in lo.values()):
                    d['missing'].append(1); continue
                d['A-D'].append(lo['A'] - lo['D']); d['B-D'].append(lo['B'] - lo['D'])
                d['C-D'].append(lo['C'] - lo['D']); d['B-C'].append(lo['B'] - lo['C'])
                bytopic[i['topic']].append(lo['B'] - lo['C'])
            tm = [st.mean(v) for v in bytopic.values()]
            tb, tc = sum(x < 0 for x in tm), sum(x > 0 for x in tm)
            p = sign_test(tb, tc)
            rows.append([m, k, len(d['B-C']), len(d['missing']), med(d['A-D']), med(d['B-D']), med(d['C-D']), med(d['B-C']),
                         f"{sum(x < 0 for x in d['B-C'])} / {sum(x > 0 for x in d['B-C'])}", f'{tb} / {tc} of {len(tm)}',
                         '-' if p is None else f'{p:.3g}'])
    md += [an.table(rows, ['model', 'checkpoint', 'n', 'missing', 'median A-D', 'median B-D', 'median C-D', 'median B-C',
                           'histories B<C / B>C', 'topics B<C / B>C', 'topic sign test p']), '']

    md += ['## Per topic (unlabelled prose, no discount; A/B/C/D)', '']
    short = {'own_both': 'own', 'other_both': 'other', 'split_first': 'split1', 'split_second': 'split2',
             'unresolved': 'unres', None: '-'}
    rows = []
    for n, i in sorted(info.items()):
        cellstr = lambda k: ('/'.join(short[i['cats'].get((c, k, False, 'prose'))] for c in CELLS)
                             + ('' if i['gate'][k][0] else f" (excluded: {i['gate'][k][1]})"))
        rows.append([i['model'], i['topic'], i['order'], 'yes' if i['flipped'] else 'no', cellstr(5), cellstr(9)])
    md += [an.table(rows, ['model', 'topic', 'order', 'flipped (main)', 'checkpoint 5', 'checkpoint 9']), '']

    md += ['## Length diagnostics', '', 'Median context tokens (including the readout-free prefix and generation prompt):', '']
    rows = []
    for m in sorted({i['model'] for i in info.values()}):
        for k in CKS:
            v = {c: sorted(i['cells'][c]['ctx_tokens'][str(k)] for i in info.values()
                           if i['model'] == m and c in i['cells']) for c in CELLS}
            rows.append([m, k] + [st.median(v[c]) if v[c] else '-' for c in CELLS])
    md += [an.table(rows, ['model', 'checkpoint', *CELLS]), '', 'Median filler/original token ratio by role and position:', '']
    rows = []
    for m in sorted({i['model'] for i in info.values()}):
        for role in ('user', 'assistant'):
            r = []
            for pos in range(1, 6):
                v = sorted(t[f'{role}_filler'] / t[f'{role}_original'] for i in info.values() if i['model'] == m
                           and 'A' in i['cells'] for t in i['cells']['A']['token_lengths']
                           if t['position'] == pos and t[f'{role}_original'])
                r.append(f'{st.median(v):.2f}' if v else '-')
            rows.append([m, role, *r])
    md += [an.table(rows, ['model', 'role', *[f'pos {p}' for p in range(1, 6)]]), '', 'Median filler/original ratio by topic (assistant role):', '']
    rows = []
    for m in sorted({i['model'] for i in info.values()}):
        for t in sorted({i['topic'] for i in info.values()}):
            v = sorted(x['assistant_filler'] / x['assistant_original'] for i in info.values()
                       if i['model'] == m and i['topic'] == t and 'A' in i['cells']
                       for x in i['cells']['A']['token_lengths'] if x['assistant_original'])
            rows.append([m, t, f'{st.median(v):.2f}' if v else '-'])
    md += [an.table(rows, ['model', 'topic', 'assistant filler/original']), '']

    md += ['## Diagnostic: D against the matched neutral history (unlabelled prose, no discount)', '']
    cnt = Counter()
    for n, i in info.items():
        nh = raw.get(neutral_name(n))
        if nh is None:
            continue
        nc, _ = an.checkpoints(nh)
        for k in CKS:
            if i['gate'][k][0]:
                cnt[(i['model'], k, i['cats'].get(('D', k, False, 'prose')), nc.get((k, False, 'prose')))] += 1
    md += [an.table([[*key, v] for key, v in sorted(cnt.items(), key=lambda kv: [str(x) for x in kv[0]])],
                    ['model', 'checkpoint', 'D', 'neutral', 'histories']), '']

    csv_rows = []
    for n, i in sorted(info.items()):
        for (c, k, disc, ro), cat in sorted(i['cats'].items(), key=lambda kv: [str(x) for x in kv[0]]):
            lo = i['lo'].get((c, k, disc))
            csv_rows.append([n, i['model'], i['topic'], i['order'], i['group'], i['ngram'], i['flipped'], c, k, disc, ro,
                             cat, '' if lo is None else round(lo, 3), i['gate'][k][0]])
    return '\n'.join(md) + '\n', csv_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ablation'); ap.add_argument('raw')
    ap.add_argument('--out', default='results/analysis_ablation_v5')
    a = ap.parse_args()
    raw, cells = load(a.ablation, a.raw)
    md, rows = analyse(raw, cells)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / 'summary.md').write_text(md)
    with open(out / 'cells.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['history', 'model', 'topic', 'order', 'group', 'ngram', 'flipped_main', 'cell', 'checkpoint',
                    'discount', 'readout', 'category', 'logodds_own', 'gate_passed'])
        w.writerows(rows)
    print(f'{len(cells)} histories with cells -> {out}')


if __name__ == '__main__':
    main()
