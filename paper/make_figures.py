"""Figure 1 of paper/paper_zh.md, computed from the archived data (needs matplotlib).

Left: step 8 re-read of the old ablations, share of the 3 release checkpoints where each cell keeps the shifted
side (unlabelled prose, no discount; all 36 conversations per set, as in results/reread_old/analysis "Primary").
Right: step 7 v5 ablation, primary-flipped histories, checkpoint 5 (results/ablation_v5/analysis/cells.csv).

Usage: python paper/make_figures.py [en]   (writes paper/fig_source.png, or paper/fig_source_en.png with English labels)
"""
import csv
import glob
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
CELLS = 'ABCD'
COLORS = dict(zip(CELLS, ('#2a78d6', '#eb6834', '#1baf7a', '#eda100')))   # validated categorical slots 1-4
NAMES = {'A': 'A 原样', 'B': 'B 只留自己的回复', 'C': 'C 只留用户施压', 'D': 'D 两边都换'}
NAMES_EN = {'A': 'A original', 'B': 'B own replies only', 'C': 'C user pressure only', 'D': 'D both replaced'}
REL = ('release_4', 'release_8', 'release_12')


def side_cat(readouts, own, keep):
    side = {r['printed_order']: (r['prose_canonical'] if r['prose']['finish'] == 'eos' else None)
            for r in readouts if keep(r) and not r['discount']}
    s1, s2 = side.get(1), side.get(2)
    if s1 is None or s2 is None:
        return 'unresolved'
    return ('own' if s1 == own else 'other') if s1 == s2 else 'split'


def step8(set_name):
    """{cell: (kept checkpoints, total checkpoints)} over conversations whose B and C resolve at all three."""
    tot = {c: [0, 0] for c in CELLS}
    for f in sorted(glob.glob(str(ROOT / f'results/reread_old/{set_name}/*__A.json'))):
        cells = {c: json.load(open(f.replace('__A.json', f'__{c}.json'))) for c in CELLS}
        cats = {c: [side_cat(cells[c]['readouts'], cells[c]['opening_side'], lambda r, l=l: r['checkpoint'] == l)
                    for l in REL] for c in CELLS}
        if 'unresolved' in cats['B'] + cats['C']:
            continue
        for c in CELLS:
            tot[c][0] += cats[c].count('other'); tot[c][1] += 3
    return tot


def step7(model):
    tot = {c: [0, 0] for c in CELLS}
    for r in csv.DictReader(open(ROOT / 'results/ablation_v5/analysis/cells.csv')):
        if (r['model'] == model and r['flipped_main'] == 'True' and r['checkpoint'] == '5' and r['discount'] == 'False'
                and r['readout'] == 'prose' and r['gate_passed'] == 'True'):
            tot[r['cell']][0] += r['category'] == 'other_both'; tot[r['cell']][1] += 1
    return tot


def main():
    en = sys.argv[1:] == ['en']
    names = NAMES_EN if en else NAMES
    for p in ('/System/Library/Fonts/Hiragino Sans GB.ttc', '/System/Library/Fonts/STHeiti Light.ttc'):
        if Path(p).exists():
            font_manager.fontManager.addfont(p)
            plt.rcParams['font.family'] = font_manager.FontProperties(fname=p).get_name()
            break
    plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#52514e', 'axes.labelcolor': '#0b0b0b',
                         'xtick.color': '#52514e', 'ytick.color': '#52514e'})
    if en:
        panels = [('Re-read of old ablations (readout changed only)\n3 late checkpoints', [('Llama, non-meta\n36 conversations', step8('repl_b1')), ('Qwen, meta\n36 conversations', step8('qwen_meta'))]),
                  ('New-protocol ablation\nflipped conversations, end of pressure', [('Llama, flipped\n13 conversations', step7('llama')), ('Qwen, flipped\n19 conversations', step7('qwen'))])]
    else:
        panels = [('重读旧消融（只换读数）\n3 个后期检查点', [('Llama 普通话题\n36 段', step8('repl_b1')), ('Qwen meta 话题\n36 段', step8('qwen_meta'))]),
                  ('新协议消融\n已翻转对话，施压结束', [('Llama 已翻转\n13 段', step7('llama')), ('Qwen 已翻转\n19 段', step7('qwen'))])]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    w = 0.19
    for ax, (title, groups) in zip(axes, panels):
        for gi, (label, tot) in enumerate(groups):
            for ci, c in enumerate(CELLS):
                k, n = tot[c]; v = k / n if n else 0
                x = gi + (ci - 1.5) * (w + 0.02)
                ax.bar(x, max(v, 0.004), w, color=COLORS[c], label=names[c] if gi == 0 else None, zorder=2)
                ax.text(x, v + 0.02, f'{v:.0%}', ha='center', va='bottom', fontsize=7, color='#52514e')
        ax.set_xticks(range(len(groups)), [g for g, _ in groups])
        ax.set_title(title, fontsize=9, color='#0b0b0b')
        ax.set_ylim(0, 1.08); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
        ax.grid(axis='y', color='#e4e3df', linewidth=0.6, zorder=0)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
    axes[0].set_ylabel('Share keeping the shift' if en else '保持偏移的比例')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out = ROOT / ('paper/fig_source_en.png' if en else 'paper/fig_source.png')
    fig.savefig(out, dpi=220, facecolor='white')
    for title, groups in panels:
        for label, tot in groups:
            print(title.split(chr(10))[0], label.replace(chr(10), ' '), {c: f'{k}/{n}' for c, (k, n) in tot.items()})
    print('wrote', out)


if __name__ == '__main__':
    main()
