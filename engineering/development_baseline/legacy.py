"""Historical publication integrity against its actual Git revision, not new defaults."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
from . import ROOT
from .selection import encoded

REVISION='578ee3950b872bf30fbf9e4207b2bda85951bdd7'
OUTPUT='docs/archives/pre-comfort-default'
PACKETS=('docs/design-engine/ferrite-maglev/reference',
         'docs/design-engine/ferrite-maglev/engineering-readiness',
         'docs/design-engine/ferrite-maglev/comfort-options',
         'docs/design-engine/ferrite-maglev/comfort-design',
         'docs/design-engine/ferrite-maglev/research-closure')

def _git(root,name):
    if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('Ordinary historical path required')
    return subprocess.check_output(['git','show',REVISION+':'+name],cwd=root)

def create_archive(root=ROOT):
    root=Path(root).resolve();folder=root/OUTPUT;folder.mkdir(parents=True,exist_ok=True)
    expectations={};packets=[]
    for base in PACKETS:
        raw=_git(root,base+'/manifest.json');manifest=json.loads(raw)
        packets.append(dict(path=base,manifest_sha256=sha256(raw).hexdigest(),
            source_revision=REVISION,role='Historical source-bound evidence; not the current development default'))
        for n,d in manifest['source_sha256'].items():
            if n in expectations and expectations[n]!=d:raise ValueError('Historical source scopes disagree: '+n)
            expectations[n]=d
        expectations.update({base+'/'+n:d for n,d in manifest['files_sha256'].items()})
    copies={}
    for name in ('OpenSourceRail-Book.pdf','OpenSourceRail-Book.receipt.json','docs/ROADMAP.md'):
        raw=_git(root,name);target=folder/Path(name).name
        if target.exists() and target.read_bytes()!=raw:raise ValueError('Refuse changing an immutable historical copy')
        target.write_bytes(raw);copies[target.relative_to(root).as_posix()]=dict(origin=name,sha256=sha256(raw).hexdigest())
    city_readmes={}
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',REVISION,'cities/catalogue'],cwd=root).decode().splitlines()
    for name in paths:
        if name.endswith('/city.json'):
            readme=name[:-len('city.json')]+'README.md'
            city_readmes[readme]=sha256(_git(root,readme)).hexdigest()
    value=dict(schema='osr-legacy-publication-catalogue/1',source_revision=REVISION,
        historical_packets=packets,source_and_payload_sha256=dict(sorted(expectations.items())),
        former_city_readme_sha256=city_readmes,immutable_copies=copies,
        historical_data_rewritten=False,numerical_calculations_reexecuted=False,
        physical_acceptance_granted=False)
    (folder/'manifest.json').write_bytes(encoded(value))
    (folder/'README.md').write_text('# Historical publications before the comfort default\n\n'
        'These records preserve the source-bound publications at revision `'+REVISION+'`. '
        'The current comfort development design is selected through '
        '[the repository selector](../../../engineering/development-baseline.toml) and '
        '[current engineering dossier](../../design-engine/current/README.md).\n\n'
        'Historical source hashes are checked against the recorded Git revision. They are '
        'not edited to match a different working tree. City root introductions can therefore '
        'move to the new default while earlier city calculations and source records remain traceable.\n\n'
        '[Former reader](OpenSourceRail-Book.pdf) · [Former roadmap](ROADMAP.md) · [Archive receipt](manifest.json).\n\n'
        'Use `./osr legacy verify` for historical source/payload integrity. This does not '
        'rerun numerical solvers or grant physical acceptance. Historical writers require '
        'a separate checkout of the recorded revision; they cannot overwrite current publications.\n')
    return value

def verify(root=ROOT):
    root=Path(root).resolve();v=json.loads((root/OUTPUT/'manifest.json').read_bytes())
    if v['source_revision']!=REVISION:raise ValueError('Historical revision differs')
    expected=dict(v['source_and_payload_sha256']);expected.update(v['former_city_readme_sha256'])
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    try:
        for name,digest in sorted(expected.items()):
            proc.stdin.write((REVISION+':'+name+'\n').encode());proc.stdin.flush()
            header=proc.stdout.readline().decode().split()
            if len(header)!=3 or header[1]!='blob':raise ValueError('Historical Git blob missing: '+name)
            raw=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
            if sha256(raw).hexdigest()!=digest:raise ValueError('Historical source/payload differs: '+name)
    finally:
        proc.stdin.close();proc.wait()
    for name,row in v['immutable_copies'].items():
        if sha256((root/name).read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Historical copy changed: '+name)
    return dict(current=True,scope='Historical source and payload integrity against Git',source_revision=REVISION,
        blobs_verified=len(expected),numerical_calculations_reexecuted=False,physical_accepted=False)

def main(argv=None,root=ROOT):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',nargs='?',default='status')
    a=p.parse_args(argv)
    if a.action in ('verify','audit'):result=verify(root)
    elif a.action in ('status','readiness'):
        result=dict(source_revision=REVISION,role='Historical comparison only',current_default='engineering/development-baseline.toml',
            archive=OUTPUT+'/README.md',historical_writers_in_current_tree=False,physical_accepted=False)
    else:
        print('Historical writer refused in the active checkout. Create an isolated Git worktree at '+REVISION+' and run its original tools there.')
        return 2
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
