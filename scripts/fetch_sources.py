"""Fetch only pinned historical files, validate before installing them."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from verify_provenance import ROOT, digest, verify


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from-local', type=Path)
    args = ap.parse_args()
    source = json.loads((ROOT / 'provenance/sources.json').read_text())
    staged = []
    for entry in source['files']:
        target = ROOT / entry['local_path']
        if target.exists():
            blob = target.read_bytes()
        elif args.from_local:
            blob = (args.from_local / entry['upstream_path']).read_bytes()
        else:
            request = urllib.request.Request(entry['raw_url'], headers={'User-Agent': 'epistemics-measurement-audit'})
            with urllib.request.urlopen(request, timeout=60) as response:
                blob = response.read()
        if digest(blob) != entry['sha256']:
            raise ValueError('Hash mismatch; refusing to overwrite input: ' + entry['upstream_path'])
        staged.append((target, blob))
    for target, blob in staged:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob)
            os.chmod(target, 0o444)
    print('Verified inputs:', verify())


if __name__ == '__main__':
    main()
