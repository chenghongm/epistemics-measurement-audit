"""Build the offline Colab bundle for the v5 multi-turn run; never include weights or credentials."""
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ['scripts/new_dialogue_v5.py', 'scripts/ngram_counter.py', 'scripts/analyze_v5.py', 'scripts/opening_smoke_v5.py', 'scripts/fill_v5.py', 'scripts/fill_v5_supplement.py', 'scripts/ablation_v5.py', 'scripts/analyze_ablation_v5.py', 'scripts/reread_old_ablation.py', 'scripts/analyze_reread_old.py', 'docs/main_run_ladders.json', 'docs/main_run_ladders.md',
         'docs/readout_rule.md', 'requirements.txt']


def build(out=ROOT / 'artifacts/multiturn-v5.zip'):
    git = lambda *a: subprocess.check_output(['git', *a], cwd=ROOT, text=True).strip()
    identity = {'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain'))}
    if identity['dirty']:
        print('WARNING: working tree is dirty; the bundle will not match a commit')
    names = FILES + [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'vendor/digital_mind').glob('*.py'))]
    out.parent.mkdir(exist_ok=True)
    # All 96 archived main-run histories for the context ablation (step 7): the runner reads the pressure ones,
    # the analysis also needs the neutral ones (D vs matched neutral). Outside results/, which the notebook
    # links to Drive.
    raw = sorted((ROOT / 'results/main_v5/raw').glob('*.json'))
    if len(raw) != 96:
        raise SystemExit(f'expected 96 archived main histories, found {len(raw)}')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('provenance/build.json', json.dumps(identity, indent=2) + '\n')
        for name in names:
            archive.write(ROOT / name, name)
        for p in raw:
            archive.write(p, f'archive/main_v5_raw/{p.name}')
        # Old Digital Mind ablation inputs for the step 8 re-read, hash-checked against their manifest.
        import hashlib
        # Both manifests: 12 of the repl_b1 conversations were already pinned by the pre-sprint sources.json.
        entries = [e for m in ('sources.json', 'reread_sources.json')
                   for e in json.loads((ROOT / 'provenance' / m).read_text())['files']]
        for e in entries:
            blob = (ROOT / e['local_path']).read_bytes()
            if hashlib.sha256(blob).hexdigest() != e['sha256']:
                raise SystemExit(f"hash mismatch: {e['local_path']}")
            archive.writestr(f"archive/digital_mind/{e['upstream_path']}", blob)
    print(out, identity)


if __name__ == '__main__':
    build()
