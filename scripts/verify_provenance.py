"""Verify pinned historical inputs and exact message prefixes without a GPU."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def digest(content):
    return hashlib.sha256(content).hexdigest()


def verify(root=ROOT):
    sources = json.loads((root / 'provenance/sources.json').read_text())
    manifest = json.loads((root / 'provenance/checkpoints.json').read_text())
    if sources['commit'] != manifest['source_commit']:
        raise ValueError('Source commit mismatch')
    checked = {}
    for entry in sources['files'] + sources['vendored_code']:
        path = root / entry['local_path']
        if digest(path.read_bytes()) != entry['sha256']:
            raise ValueError('Content hash mismatch: ' + entry['local_path'])
        checked[entry['local_path']] = entry
    seen = set()
    for item in manifest['checkpoints']:
        key = (item['conv_id'], item['turn_idx'])
        if key in seen:
            raise ValueError('Duplicate checkpoint: ' + str(key))
        seen.add(key)
        if checked[item['source']]['sha256'] != item['sha256']:
            raise ValueError('Checkpoint source digest mismatch')
        rec = json.loads((root / item['source']).read_text())
        if (rec['conv_id'], rec['topic'], rec['option_order']) != (item['conv_id'], item['topic'], item['order']):
            raise ValueError('Checkpoint identity mismatch')
        prefix = []
        for turn in rec['turns']:
            prefix += [dict(role='user', content=turn['user_text']),
                       dict(role='assistant', content=turn['model_text'])]
            if turn['turn_idx'] == item['turn_idx']:
                break
        else:
            raise ValueError('Checkpoint turn missing')
        actual = digest(json.dumps(prefix, ensure_ascii=False, separators=(',', ':')).encode())
        if actual != item['prefix_sha256']:
            raise ValueError('History prefix mismatch: ' + str(key))
    plan = sources['preexisting_plan']
    if digest((root / 'docs/preexisting_frozen_history_plan.md').read_bytes()) != plan['sha256']:
        raise ValueError('Preexisting plan changed')
    return len(sources['files']), len(manifest['checkpoints'])


if __name__ == '__main__':
    files, points = verify()
    print(f'PASS: {files} historical files, {points} exact prefixes, vendored code and inherited plan verified.')
