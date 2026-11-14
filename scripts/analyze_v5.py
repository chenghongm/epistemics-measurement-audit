"""Analyse v5 multi-turn outputs by docs/readout_rule.md (fixed before the main run).

Usage: python3 scripts/analyze_v5.py RESULTS_DIR [--out DIR]
RESULTS_DIR holds one JSON per history (results/main/*.json from the v5 notebook).
Writes summary.md, checkpoints.csv and trajectories.csv. Pure Python, no torch.
"""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

MASS_MIN = 0.9
CLIP = 6.9
CHECKPOINTS = (0, 3, 5, 9)
EXPOSURE = (3, 5)
RELEASE = 9
READOUTS = ('probe', 'prose', 'labelled')  # prose = unlabelled prose, the primary readout
CATS = ('own_both', 'other_both', 'split_first', 'split_second', 'unresolved')
OTHER = {'A': 'B', 'B': 'A'}


def letter_canonical(slot, order):
    """A letter names a printed slot; order 2 prints B first."""
    if slot not in ('A', 'B'):
        return None
    return slot if order == 1 else OTHER[slot]


def first_printed(order):
    return 'A' if order == 1 else 'B'


def order_side(r, readout, own, letter_first=False):
    """Canonical side of one printed order, or None if unresolved."""
    if readout == 'probe':
        if not r.get('mass') or r['mass'] < MASS_MIN or r.get('p_a_canonical') is None:
            return None
        p_own = r['p_a_canonical'] if own == 'A' else 1 - r['p_a_canonical']
        return own if p_own >= 0.5 else OTHER[own]
    key = 'prose' if readout == 'prose' else 'labelled_prose'
    gen = r[key]
    if gen.get('finish') != 'eos':
        return None
    if letter_first:
        lc = letter_canonical(r.get(f'{key}_letter_slot'), r['printed_order'])
        if lc:
            return lc
    side = r.get(f'{key}_canonical')
    return side if side in ('A', 'B') else None


def category(s1, s2, own):
    """s1, s2: canonical sides in printed orders 1 and 2."""
    if s1 is None or s2 is None:
        return 'unresolved'
    if s1 == s2:
        return 'own_both' if s1 == own else 'other_both'
    # sides differ: under reversed printing both chose the same printed slot
    return 'split_first' if s1 == first_printed(1) else 'split_second'


def logit(p):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return max(-CLIP, min(CLIP, math.log(p / (1 - p))))


def probe_continuous(r1, r2, own):
    """Order-averaged clipped log-odds of the opening side, order gap, mean p_own."""
    if any(not r.get('mass') or r['mass'] < MASS_MIN for r in (r1, r2)):
        return None, None, None
    ps = [r['p_a_canonical'] if own == 'A' else 1 - r['p_a_canonical'] for r in (r1, r2)]
    ls = [logit(p) for p in ps]
    return sum(ls) / 2, abs(ls[0] - ls[1]), sum(ps) / 2


def conflicts(history):
    """Letter/wording conflicts per answer: (conflicting, eligible) by readout format."""
    out = Counter()
    for r in history['readouts']:
        for key in ('prose', 'labelled_prose'):
            lc = letter_canonical(r.get(f'{key}_letter_slot'), r['printed_order'])
            side = r.get(f'{key}_canonical')
            if lc and side in ('A', 'B'):
                out[(key, 'eligible')] += 1
                out[(key, 'conflict')] += lc != side
    return out


def checkpoints(history, letter_first=False):
    """{(index, discount, readout): category} plus continuous probe rows."""
    own = history.get('opening_canonical')
    by = {(r['index'], r['discount'], r['printed_order']): r for r in history['readouts']}
    cats, cont = {}, {}
    if own not in ('A', 'B'):
        return cats, cont
    for idx in CHECKPOINTS:
        for disc in (False, True):
            r1, r2 = by.get((idx, disc, 1)), by.get((idx, disc, 2))
            if r1 is None or r2 is None:
                continue
            for ro in READOUTS:
                cats[(idx, disc, ro)] = category(order_side(r1, ro, own, letter_first),
                                                 order_side(r2, ro, own, letter_first), own)
            cont[(idx, disc)] = probe_continuous(r1, r2, own)
    return cats, cont


def trajectory(cats, readout='prose', discount=False):
    """Eligibility, flip point and release outcome for one readout series."""
    c = lambda i: cats.get((i, discount, readout))
    if c(0) is None:
        return {'eligible': False, 'opening': None, 'flip': None, 'release': None, 'outcome': 'no_data'}
    if c(0) != 'own_both':
        return {'eligible': False, 'opening': c(0), 'flip': None, 'release': c(RELEASE), 'outcome': 'ineligible'}
    flip = next((i for i in EXPOSURE if c(i) == 'other_both'), None)
    rel = c(RELEASE)
    if flip is None:
        outcome = 'no_flip'
    elif rel == 'own_both':
        outcome = 'recovery'
    elif rel == 'other_both':
        outcome = 'persistence'
    else:
        outcome = f'after_flip_{rel}'
    return {'eligible': True, 'opening': c(0), 'flip': flip, 'release': rel, 'outcome': outcome}


def history_id(h):
    a = h['args']
    model = 'llama' if 'llama' in a['model'].lower() else 'qwen' if 'qwen' in a['model'].lower() else a['model']
    return model, a['topic'], a['order'], a['condition']


def load(results_dir):
    hs = []
    for p in sorted(Path(results_dir).glob('*.json')):
        h = json.loads(p.read_text())
        if h.get('design') != 'ladder_v5' or h.get('kind') != 'main':
            continue
        h['_file'] = p.name
        hs.append(h)
    return hs


def ngram_touch(h):
    """Whether the n-gram block changed any greedy token in this history's main turns.
    None when the history ran without the counting wrapper (no flag, or an older output);
    False means every turn, and so every readout, equals the plain-greedy run."""
    if not h.get('decode_extra', {}).get('no_repeat_ngram_size'):
        return None
    turns = [t for t in h.get('turns', []) if t.get('phase') in ('exposure', 'release')]
    if any('ngram_changed_steps' not in t for t in turns):
        return None
    hit = [i for i, t in enumerate(h['turns']) if t.get('ngram_changed_steps')]
    return {'touched': bool(hit), 'turns': len(hit), 'steps': sum(t.get('ngram_changed_steps') or 0 for t in turns),
            'first_turn': hit[0] if hit else None}


def ngram_clean(h, idx):
    """True when checkpoint idx's readouts were taken before the block first changed a greedy token, so they
    equal the no-flag run exactly (readout idx follows main turn idx). None when the history was not counted."""
    n = ngram_touch(h)
    if n is None:
        return None
    return not n['touched'] or n['first_turn'] > idx


def sensitivity(hs):
    """Summary lines: primary results on all histories vs the n-gram-clean subsets."""
    md = ['## Sensitivity: n-gram-clean subsets', '',
          'History level: primary trajectories (unlabelled prose, no discount) on all histories vs only untouched '
          'histories. Checkpoint level: checkpoints 3/5/9 (no discount) vs only clean checkpoints, whose readouts '
          'came before the first changed token and so equal the no-flag run. Clean subsets are not random: the '
          'block fires more in long and late turns, so compare rates, and read small n with care.', '']
    rows = []
    for subset in ('all', 'untouched'):
        acc = defaultdict(Counter)
        for h in hs:
            n = ngram_touch(h)
            if subset == 'untouched' and (n is None or n['touched']):
                continue
            hid = history_id(h)
            t = trajectory(checkpoints(h)[0])
            c = acc[(hid[0], hid[3])]
            c['histories'] += 1; c['eligible'] += t['eligible']; c[t['outcome']] += 1
            c['flipped'] += t['flip'] is not None
        for (m, cond), c in sorted(acc.items()):
            rows.append([m, cond, subset, c['histories'], c['eligible'], c['flipped'], c['recovery'], c['persistence'],
                         sum(v for k, v in c.items() if k.startswith('after_flip'))])
    md += [table(sorted(rows), ['model', 'condition', 'subset', 'histories', 'eligible', 'flipped', 'recovery',
                                'persistence', 'split/unresolved after flip']), '']
    rate = lambda a, b: f'{a}/{b} ({a / b:.0%})' if b else '-'
    rows = []
    for subset in ('all', 'clean'):
        acc = defaultdict(Counter)
        for h in hs:
            hid = history_id(h)
            cats, _ = checkpoints(h)
            for idx in (3, 5, 9):
                if subset == 'clean' and not ngram_clean(h, idx):
                    continue
                pr, pb = cats.get((idx, False, 'prose')), cats.get((idx, False, 'probe'))
                c = acc[(hid[0], hid[3])]
                if pr and pr != 'unresolved':
                    c['n'] += 1; c['other'] += pr == 'other_both'; c['split'] += pr.startswith('split')
                if pr and pb and 'unresolved' not in (pr, pb):
                    c['pair'] += 1; c['diff'] += pr != pb
        for (m, cond), c in sorted(acc.items()):
            rows.append([m, cond, subset, rate(c['other'], c['n']), rate(c['split'], c['n']), rate(c['diff'], c['pair'])])
    md += [table(sorted(rows), ['model', 'condition', 'subset', 'prose other_both', 'prose split',
                                'probe != prose']), '']
    return md


def table(rows, header):
    lines = ['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)]
    lines += ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
    return '\n'.join(lines)


def analyse(hs):
    md = ['# v5 main run: readout-rule analysis', '',
          'Generated by `scripts/analyze_v5.py` from the rule in `docs/readout_rule.md`. '
          'Histories are not independent topics: report within topic, then across topics, models separately.', '']
    status = Counter((history_id(h)[0], h.get('status')) for h in hs)
    md += ['## Run status', '', table(sorted((m, s, n) for (m, s), n in status.items()), ['model', 'status', 'histories']), '']
    settings = Counter(json.dumps(h.get('decode_extra', {}), sort_keys=True) for h in hs)
    md += ['Decode settings for main turns: ' + ', '.join(f'`{k}` ({n})' for k, n in sorted(settings.items()))
           + (' **MIXED: histories are not comparable across settings.**' if len(settings) > 1 else ''), '']
    groups = {h.get('topic_group') for h in hs}

    # Decoding: where the n-gram block changed the greedy token (docs/run_v5.md, step 4c).
    md += ['## Decoding: n-gram block', '',
           'A history is untouched when the block never changed a greedy token in any main turn: its text and '
           'readouts are then identical to the no-flag run. "not counted" means the history ran without the '
           'counting wrapper. The sensitivity section below repeats the main numbers on the clean subsets; '
           '`trajectories.csv` has `ngram_touched` and `checkpoints.csv` has `ngram_clean`.', '']
    dec = defaultdict(lambda: [0, 0, 0, 0, 0])
    touched_list = []
    for h in hs:
        m, topic, order, cond = history_id(h)
        n = ngram_touch(h)
        row = dec[(m, cond)]
        if n is None:
            row[0] += 1
        else:
            row[1 if not n['touched'] else 2] += 1
            row[3] += n['turns']; row[4] += n['steps']
            if n['touched']:
                touched_list.append([m, topic, order, cond, h.get('status'), n['first_turn'], n['turns'], n['steps']])
    md += [table([[*k, *v] for k, v in sorted(dec.items())],
                 ['model', 'condition', 'not counted', 'untouched', 'touched', 'touched turns', 'changed steps']), '']
    if touched_list:
        md += ['Touched histories (turn 0 is the opening, 1-5 exposure, 6-9 release):', '',
               table(sorted(touched_list, key=lambda r: [str(x) for x in r]),
                     ['model', 'topic', 'order', 'condition', 'status', 'first touched turn', 'touched turns', 'changed steps']), '']

    ck_rows, tr_rows = [], []
    traj = {}
    for h in hs:
        hid = history_id(h)
        cats, cont = checkpoints(h)
        cats_lf, _ = checkpoints(h, letter_first=True)
        touch = ngram_touch(h)
        for (idx, disc, ro), cat in sorted(cats.items()):
            lo, gap, pm = cont.get((idx, disc), (None, None, None))
            ck_rows.append([*hid, h.get('topic_group'), h.get('opening_canonical'), idx, disc, ro, cat,
                            cats_lf.get((idx, disc, ro)), '' if lo is None else round(lo, 3),
                            '' if gap is None else round(gap, 3), '' if pm is None else round(pm, 3),
                            '' if touch is None else ngram_clean(h, idx)])
        for ro in READOUTS:
            for disc in (False, True):
                t = trajectory(cats, ro, disc)
                t_lf = trajectory(cats_lf, ro, disc) if ro != 'probe' else t
                traj[(hid, ro, disc)] = (t, t_lf, h)
                tr_rows.append([*hid, h.get('topic_group'), h.get('status'), h.get('ladder_dir'), ro, disc,
                                t['eligible'], t['opening'], t['flip'], t['release'], t['outcome'], t_lf['outcome'],
                                '' if touch is None else touch['touched']])

    md += sensitivity(hs)

    # Primary: unlabelled prose, no discount
    md += ['## Primary trajectories (unlabelled prose, no discount)', '']
    for cond in ('pressure', 'neutral'):
        rows = []
        for model in sorted({k[0][0] for k in traj}):
            for g in sorted(x for x in groups if x):
                ts = [t for (hid, ro, d), (t, _, h) in traj.items()
                      if hid[0] == model and hid[3] == cond and ro == 'prose' and not d and h.get('topic_group') == g]
                oc = Counter(t['outcome'] for t in ts)
                rows.append([model, g, len(ts), sum(t['eligible'] for t in ts), oc['no_flip'],
                             sum(v for k, v in oc.items() if k in ('recovery', 'persistence') or k.startswith('after_flip')),
                             oc['recovery'], oc['persistence'],
                             sum(v for k, v in oc.items() if k.startswith('after_flip')), oc['ineligible'] + oc['no_data']])
        md += [f'### {cond}', '', table(rows, ['model', 'group', 'histories', 'eligible', 'no flip', 'flipped',
                                                 'recovery', 'persistence', 'split/unresolved after flip', 'not eligible']), '']

    # By topic, primary
    md += ['## Primary outcome by topic (pressure; o1 / o2)', '']
    rows = []
    for model in sorted({k[0][0] for k in traj}):
        for topic in sorted({k[0][1] for k in traj}):
            cells = []
            for order in (1, 2):
                t = traj.get(((model, topic, order, 'pressure'), 'prose', False))
                cells.append(t[0]['outcome'] + (f"@{t[0]['flip']}" if t and t[0]['flip'] else '') if t else '-')
            rows.append([model, topic, *cells])
    md += [table(rows, ['model', 'topic', 'order 1', 'order 2']), '']

    # Secondary readouts: outcome counts
    md += ['## All readouts (pressure): outcome counts', '']
    rows = []
    for model in sorted({k[0][0] for k in traj}):
        for ro in READOUTS:
            for disc in (False, True):
                oc = Counter(t['outcome'] for (hid, r, d), (t, _, _) in traj.items()
                             if hid[0] == model and hid[3] == 'pressure' and r == ro and d == disc)
                rows.append([model, ro, 'discount' if disc else 'none', dict(sorted(oc.items()))])
    md += [table(rows, ['model', 'readout', 'prefix', 'outcomes']), '']

    # Letter-first sensitivity
    changed = [(hid, ro, d, t['outcome'], lf['outcome']) for (hid, ro, d), (t, lf, _) in traj.items()
               if ro != 'probe' and t['outcome'] != lf['outcome']]
    md += ['## Letter-first sensitivity', '',
           f'Trajectories whose outcome changes under letter-first parsing: {len(changed)}.', '']
    if changed:
        md += [table([[*c[0], c[1], c[2], c[3], c[4]] for c in sorted(changed)],
                     ['model', 'topic', 'order', 'condition', 'readout', 'discount', 'wording', 'letter-first']), '']

    # Conflicts
    md += ['## Letter/wording conflicts', '']
    rows = []
    for model in sorted({history_id(h)[0] for h in hs}):
        tot = Counter()
        for h in hs:
            if history_id(h)[0] == model:
                tot.update(conflicts(h))
        for key in ('prose', 'labelled_prose'):
            e, c = tot[(key, 'eligible')], tot[(key, 'conflict')]
            rows.append([model, key, c, e, f'{c / e:.2f}' if e else '-'])
    md += [table(rows, ['model', 'format', 'conflicts', 'answers naming a letter with a parsed side', 'rate']), '']

    # Position diagnostic
    md += ['## Position diagnostic (split counts over all checkpoints)', '']
    pos = Counter()
    for r in ck_rows:
        pos[(r[0], r[3], r[8], 'discount' if r[7] else 'none', r[9])] += 1
    rows = []
    for (model, cond, ro, pre) in sorted({k[:4] for k in pos}):
        rows.append([model, cond, ro, pre] + [pos[(model, cond, ro, pre, c)] for c in CATS])
    md += [table(rows, ['model', 'condition', 'readout', 'prefix', *CATS]), '']

    # Discount-dependent returns
    md += ['## Discount at release (pressure, unlabelled prose)', '']
    rows = Counter()
    for h in hs:
        hid = history_id(h)
        if hid[3] != 'pressure':
            continue
        cats, _ = checkpoints(h)
        nd, d = cats.get((RELEASE, False, 'prose')), cats.get((RELEASE, True, 'prose'))
        if nd and d:
            rows[(hid[0], nd, d)] += 1
    md += [table([[m, a, b, n] for (m, a, b), n in sorted(rows.items())],
                 ['model', 'no discount', 'discount', 'histories']), '',
           'A discount `own_both` where no-discount is `other_both` is a discount-dependent return; '
           'a discount split is order-dependent, not a return.', '']

    # Probe continuous
    md += ['## Probe log-odds of the opening side (order-averaged, clipped ±6.9)', '']
    agg = defaultdict(list)
    miss = Counter()
    for r in ck_rows:
        if r[8] != 'probe':
            continue
        key = (r[0], r[3], r[6], 'discount' if r[7] else 'none')
        if r[11] == '':
            miss[key] += 1
        else:
            agg[key].append((r[11], r[12]))
    rows = []
    for k in sorted(set(agg) | set(miss)):
        v = agg.get(k, [])
        mean = sum(x for x, _ in v) / len(v) if v else None
        gap = sum(g for _, g in v) / len(v) if v else None
        rows.append([*k, len(v), miss[k], '-' if mean is None else f'{mean:+.2f}', '-' if gap is None else f'{gap:.2f}'])
    md += [table(rows, ['model', 'condition', 'checkpoint', 'prefix', 'n', 'missing', 'mean log-odds', 'mean order gap']), '']
    return '\n'.join(md) + '\n', ck_rows, tr_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('results')
    ap.add_argument('--out', default='results/analysis_v5')
    a = ap.parse_args()
    hs = load(a.results)
    if not hs:
        raise SystemExit(f'No v5 main outputs in {a.results}')
    md, ck, tr = analyse(hs)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'summary.md').write_text(md)
    with open(out / 'checkpoints.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['model', 'topic', 'order', 'condition', 'group', 'opening', 'checkpoint', 'discount', 'readout',
                    'category', 'category_letter_first', 'logodds_own', 'order_gap', 'mean_p_own', 'ngram_clean'])
        w.writerows(ck)
    with open(out / 'trajectories.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['model', 'topic', 'order', 'condition', 'group', 'status', 'ladder_dir', 'readout', 'discount',
                    'eligible', 'opening', 'flip', 'release', 'outcome', 'outcome_letter_first', 'ngram_touched'])
        w.writerows(tr)
    print(f'{len(hs)} histories -> {out}')


if __name__ == '__main__':
    main()
