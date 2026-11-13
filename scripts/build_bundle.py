"""Build an offline Colab bundle from verified sources; never include weights or credentials."""
import json
import zipfile
from frozen_audit import repository_identity
from verify_provenance import ROOT, verify


def build():
    verify()
    sources = json.loads((ROOT / 'provenance/sources.json').read_text())
    names = ['provenance/sources.json', 'provenance/checkpoints.json',
             'docs/preexisting_frozen_history_plan.md', 'docs/prefix_control_plan.md', 'docs/neutral_set_plan.md', 'PREEXISTING.md', 'requirements.txt']
    names += [entry['local_path'] for entry in sources['files'] + sources['vendored_code']]
    names += [str(p.relative_to(ROOT)) for p in (ROOT / 'scripts').glob('*.py')]
    out = ROOT / 'artifacts/audit-source.zip'
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('provenance/build.json', json.dumps(repository_identity(ROOT), indent=2) + '\n')
        for name in sorted(set(names)):
            archive.write(ROOT / name, name)
    print(out)


if __name__ == '__main__':
    build()
