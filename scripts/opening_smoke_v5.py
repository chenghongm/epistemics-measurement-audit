"""Opening-only smoke for v5: load the model once, generate every topic x order opening
exactly as new_dialogue_v5.py does (same prompt, greedy, same cap), and report the
wording-only parse. Greedy decoding makes these the main run's openings. No readouts."""
import argparse, hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import new_dialogue_v5 as v5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True); ap.add_argument('--revision'); ap.add_argument('--device', required=True)
    ap.add_argument('--out', required=True, help='one JSON for all openings of this model')
    ap.add_argument('--topics', nargs='*')
    a = ap.parse_args()
    topics = v5.load_topics()
    names = a.topics or list(topics)
    import torch, transformers
    from runner import Runner
    model = a.model
    if a.revision:
        from huggingface_hub import snapshot_download
        model = snapshot_download(a.model, revision=a.revision, ignore_patterns=['original/*'])
    start = time.monotonic(); rr = Runner(model, device=a.device); torch.set_grad_enabled(False)
    out = Path(a.out)
    res = json.loads(out.read_text()) if out.exists() else {
        'kind': 'opening_smoke', 'design': v5.DESIGN, 'ladders_sha256': v5.LADDERS_SHA256, 'build': v5.build_identity(),
        'model': a.model, 'revision': a.revision, 'torch': torch.__version__, 'transformers': transformers.__version__,
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'v5_sha256': hashlib.sha256(Path(v5.__file__).read_bytes()).hexdigest(), 'openings': []}
    if res.get('revision') != a.revision:
        raise SystemExit(f'{out} was made with revision {res.get("revision")}')
    done = {(o['topic'], o['order']) for o in res['openings']}
    eos = rr.model.generation_config.eos_token_id; eos = set(eos if isinstance(eos, list) else [eos])
    for name in names:
        t = topics[name]; sa, sb = t['side_a'], t['side_b']
        for order in (1, 2):
            if (name, order) in done:
                continue
            displayed = (sa, sb) if order == 1 else (sb, sa)
            prompt = f"{t['question']}\n(A) {displayed[0]}\n(B) {displayed[1]}\n{v5.OPENING_ASK}"
            t0 = time.monotonic(); enc = rr._encode([{'role': 'user', 'content': prompt}])
            ids = rr.model.generate(**enc, max_new_tokens=v5.HISTORY_MAX_NEW_TOKENS, do_sample=False,
                                    pad_token_id=rr.tok.eos_token_id)[0, enc['input_ids'].shape[-1]:]
            text = rr.tok.decode(ids, skip_special_tokens=True).strip()
            side = v5.text_side(text, sa, sb)
            res['openings'].append({'topic': name, 'group': t['group'], 'order': order, 'text': text, 'tokens': len(ids),
                                    'finish': 'eos' if len(ids) and int(ids[-1]) in eos else 'length_or_other',
                                    'seconds': time.monotonic() - t0, 'opening_canonical': side,
                                    'opening_letter_slot': v5.letter_slot(text, *displayed)})
            v5.save(out, res)
            v5.log(f'{name} o{order}: {side}, {len(ids)} tokens, {time.monotonic() - t0:.1f}s')
    res['elapsed_seconds'] = time.monotonic() - start; v5.save(out, res)
    ops = res['openings']
    print(f"parsed {sum(o['opening_canonical'] in ('A', 'B') for o in ops)}/{len(ops)}, "
          f"truncated {sum(o['finish'] != 'eos' for o in ops)}")
    for o in ops:
        if o['opening_canonical'] not in ('A', 'B') or o['finish'] != 'eos':
            print('  CHECK', o['topic'], f"o{o['order']}", o['opening_canonical'], o['finish'], repr(o['text'][:160]))


if __name__ == '__main__':
    main()
