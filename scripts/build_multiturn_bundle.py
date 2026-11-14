"""Build the offline Colab bundle for the v5 multi-turn run; never include weights or credentials."""
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ['scripts/new_dialogue_v5.py', 'scripts/analyze_v5.py', 'scripts/opening_smoke_v5.py', 'docs/main_run_ladders.json', 'docs/main_run_ladders.md',
         'docs/readout_rule.md', 'requirements.txt']


def build(out=ROOT / 'artifacts/multiturn-v5.zip'):
    git = lambda *a: subprocess.check_output(['git', *a], cwd=ROOT, text=True).strip()
    identity = {'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain'))}
    if identity['dirty']:
        print('WARNING: working tree is dirty; the bundle will not match a commit')
    names = FILES + [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'vendor/digital_mind').glob('*.py'))]
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('provenance/build.json', json.dumps(identity, indent=2) + '\n')
        for name in names:
            archive.write(ROOT / name, name)
    print(out, identity)


if __name__ == '__main__':
    build()
