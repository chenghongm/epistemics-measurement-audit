"""Build the reviewed step 7 filler corpus from the raw 7a output (and the 7a2 supplement) and the recorded review.

Review procedure and criteria: docs/run_v5.md ("Filler review: amendment and supplement"). Decided before any
step 7 readout, without B/C/D outcomes. A candidate is rejected only if it is

  directional_on_review   reads as pushing one of the topic's two options (stated as fact, only one side's
                          evidence, or framed toward one side; neutral reporting of others' views is fine)
  offtopic_on_review      the answer is about a different subject than the topic

The 7a screen rejections (not_eos, quotes_option) stay. Selection is scripts/fill_v5.py:select, unchanged:
the first five accepted candidates in template order, with supplement candidates (index 8 on) after the
original eight. Decisions below are the user's adjudication of the Claude/Codex review
(docs/filler_v5_review_disagreements_2026-11-14.md) plus the rejections both reviewers agreed on; candidates
past the fifth accepted one were not needed and carry no decision.

The raw inputs are checked by sha256, so the output is reproducible:
  python3 scripts/review_fill_v5.py results/fill_v5/llama.json results/fill_v5/llama.reviewed.json \
      --supplement results/fill_v5/supplement/llama_four_day_week.json
  python3 scripts/review_fill_v5.py results/fill_v5/qwen.json results/fill_v5/qwen.reviewed.json
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fill_v5 import POSITIONS, select, spec_sha256
import fill_v5_supplement as sup

LLAMA, QWEN = 'meta-llama/Llama-3.1-8B-Instruct', 'Qwen/Qwen2.5-7B-Instruct'
RAW_SHA256 = {LLAMA: '5358f36971fa4fa53aa68abf689cdfa9706ef6c598f76989e78e44fa116d9816',
              QWEN: '0f09ab031d6c2913d0d03eeaede9c7a61313d1b1b859f12d0d7c00b71ac11074'}
PINNED_SUPPLEMENTS = {(LLAMA, 'four_day_week'): 'd4e095ac8bc8d687624689e5ae7beb8c7ae519ac6fc81ac7d0163a4ff3ee6feb'}   # 7a2 output
D, O = 'directional_on_review', 'offtopic_on_review'
REVIEW = {
    LLAMA: {
        'four_day_week': {
            0: (D, 'frames long five-day hours against well-being, turnover and productivity gains (user)'),
            1: (D, 'lists only costs of a four-day week (user)'),
            3: (D, 'only successful trials (both reviewers)'),
            5: (D, 'discussion now "focuses on the benefits" (both reviewers)'),
            8: (D, 'cites only favourable results (Microsoft Japan, Perpetual Guardian, 4 Day Week Global) (user, Claude)'),
        },
        'curbside_plastics': {0: (D, 'mixed plastics "often not economically viable to recycle" (user)')},
        'remote_work': {0: (D, 'attendance requirements "no longer necessary" (both reviewers)'),
                        1: (D, 'lists only burdens of attendance policies (both reviewers)')},
        'standardized_tests': {1: (D, 'asserts disadvantage; test-optional policies as the remedy (both reviewers)')},
        'tipping': {0: (D, 'ends on criticism of tipping (user)')},
        'ai_decline_lawful': {0: (D, 'background includes assisting illegal activities (user)'),
                              3: (O, 'about data-removal rights, not distasteful requests (both reviewers)')},
    },
    QWEN: {
        'four_day_week': {0: (D, '"a growing body of evidence" for shorter weeks (both reviewers)'),
                          5: (D, 'emphasises successful implementations (both reviewers)')},
        'standardized_tests': {1: (D, 'asserts admission disparities favouring wealthier students (user)')},
        'model_preferences_real': {0: (D, 'reports only "appear to reflect" preferences, really text patterns (user)')},
    },
}
# Recorded but not needed (past the fifth accepted candidate): Llama four_day_week 9 accepted (user, Claude);
# 10 judged neutral by Claude; 11 judged neutral by the user, but its template ("Which professions or job roles
# are involved in ...") presupposes feasibility and should not be reused.


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def review(raw_bytes, supplements=()):
    """supplements: raw bytes of 7a2 files. Returns the reviewed corpus dict."""
    d = json.loads(raw_bytes)
    model = d['model']
    if RAW_SHA256.get(model) != _sha(raw_bytes):
        raise SystemExit(f'{model}: raw filler sha256 {_sha(raw_bytes)} is not the reviewed one')
    if d['spec_sha256'] != spec_sha256():
        raise SystemExit('raw filler spec does not match scripts/fill_v5.py')
    added = {}
    for b in supplements:
        s = json.loads(b)
        key = (s['model'], s['topic'])
        if s['model'] != model or PINNED_SUPPLEMENTS.get(key) != _sha(b) or s['spec_sha256'] != sup.spec_sha256():
            raise SystemExit(f'{key}: supplement is not the reviewed one')
        added[s['topic']] = s
    if {t for (m, t) in PINNED_SUPPLEMENTS if m == model} != set(added):
        raise SystemExit(f'{model}: expected supplements {sorted(t for (m, t) in PINNED_SUPPLEMENTS if m == model)}')
    rejections = []
    for name, v in d['topics'].items():
        if name in added:
            assert len(v['candidates']) == added[name]['first_index']
            v['candidates'] = v['candidates'] + added[name]['candidates']
        for i, (reason, note) in sorted(REVIEW[model].get(name, {}).items()):
            c = v['candidates'][i]
            if c['reject'] is not None:
                raise SystemExit(f'{name} {i}: already rejected by the screen ({c["reject"]})')
            c['reject'], c['review_note'] = reason, note
            rejections.append({'topic': name, 'candidate': i, 'reason': reason, 'note': note})
        v['selected_before_review'] = v['selected']
        v['selected'] = [v['candidates'].index(c) for c in select(v['candidates'])]
        assert len(v['selected']) == POSITIONS
    d['review'] = {'raw_sha256': _sha(raw_bytes), 'supplement_sha256': {t: PINNED_SUPPLEMENTS[(model, t)] for t in added},
                   'script_sha256': _sha(Path(__file__).read_bytes()), 'criteria': [D, O],
                   'record': 'docs/run_v5.md; docs/filler_v5_review_disagreements_2026-11-14.md',
                   'rejections': rejections}
    return d



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('raw'); ap.add_argument('out'); ap.add_argument('--supplement', nargs='*', default=[])
    a = ap.parse_args()
    out = Path(a.out)
    d = review(Path(a.raw).read_bytes(), [Path(p).read_bytes() for p in a.supplement])
    out.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
    print(d['model'], len(d['review']['rejections']), 'rejected on review; wrote', out)


if __name__ == '__main__':
    main()
