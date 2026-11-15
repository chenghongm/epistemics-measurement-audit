"""Supplementary filler candidates for topics left with fewer than five neutral candidates after review (step 7a2).

Decided before any step 7 readout (docs/run_v5.md, "Filler review: amendment and supplement"): after review,
Llama four_day_week has 4 acceptable candidates out of 8. Rather than relax the review or shorten the cell, four
further questions are generated for that topic only, with the same subject phrase, suffix, decoding and screen
as scripts/fill_v5.py. They are reviewed by the same two criteria, and the first acceptable one, in the order
below, fills the fifth position. The original 8 candidates and their order are unchanged.

Usage (GPU): python3 scripts/fill_v5_supplement.py --model REPO --revision SHA --device cuda \
    --topic four_day_week --out results/fill_v5/supplement/llama_four_day_week.json
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
from fill_v5 import SUBJECTS, SUFFIX, MAX_NEW_TOKENS, screen

TEMPLATES = [
    'What data sources are commonly used in discussions of {s}?',
    'What role do laws and regulations play in {s}?',
    'How do practices related to {s} differ between small and large organisations?',
    'Which professions or job roles are involved in {s}?',
]
CORPUS = 'fill_v5_supplement'
FIRST_INDEX = 8   # appended after the original 8 candidates


def questions(topic):
    return [t.format(s=SUBJECTS[topic]) + SUFFIX for t in TEMPLATES]


def spec_sha256():
    spec = {'subjects': SUBJECTS, 'templates': TEMPLATES, 'suffix': SUFFIX, 'max_new_tokens': MAX_NEW_TOKENS,
            'first_index': FIRST_INDEX}
    return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True); ap.add_argument('--revision', required=True)
    ap.add_argument('--device', required=True); ap.add_argument('--topic', required=True, choices=SUBJECTS)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit('Output exists: choose a fresh path')
    import torch, transformers
    from huggingface_hub import snapshot_download
    from runner import Runner
    from new_dialogue_v5 import load_topics, build_identity
    t = load_topics()[a.topic]
    path = snapshot_download(a.model, revision=a.revision, ignore_patterns=['original/*'])
    rr = Runner(path, device=a.device); torch.set_grad_enabled(False)
    eos = rr.model.generation_config.eos_token_id; eos = set(eos if isinstance(eos, list) else [eos])
    cands = []
    for q in questions(a.topic):
        t0 = time.monotonic()
        enc = rr._encode([{'role': 'user', 'content': q}])
        ids = rr.model.generate(**enc, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                                pad_token_id=rr.tok.eos_token_id)[0, enc['input_ids'].shape[-1]:]
        finish = 'eos' if len(ids) and int(ids[-1]) in eos else 'length_or_other'
        text = rr.tok.decode(ids, skip_special_tokens=True).strip()
        cands.append({'question': q, 'answer': text, 'tokens': len(ids), 'finish': finish,
                      'question_tokens': len(rr.tok.encode(q, add_special_tokens=False)),
                      'seconds': time.monotonic() - t0, 'reject': screen(text, finish, t['side_a'], t['side_b']),
                      'supplement': True})
        print(a.topic, FIRST_INDEX + len(cands) - 1, cands[-1]['tokens'], 'tok', cands[-1]['reject'] or 'ok', flush=True)
    result = {'corpus': CORPUS, 'spec_sha256': spec_sha256(), 'model': a.model, 'revision': a.revision,
              'topic': a.topic, 'first_index': FIRST_INDEX, 'build': build_identity(), 'torch': torch.__version__,
              'transformers': transformers.__version__,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'candidates': cands}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print('wrote', out)


if __name__ == '__main__':
    main()
