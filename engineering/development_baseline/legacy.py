"""Historical publication integrity against its actual Git revision, not new defaults."""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from . import ROOT
from .selection import encoded

REVISION='578ee3950b872bf30fbf9e4207b2bda85951bdd7'
OUTPUT='docs/archives/pre-comfort-default'
LEGACY_CHECKOUTS={
    'pre-comfort-default':REVISION,
    'v0.4.0':'205e8dc158c83fcdc2dca9ceb8bad0a7e8b3f61e',
    'v0.5.1':'2617b04e722ca24b7ad9120f94610fe869f27053',
    'v0.5-maglev':'92e1385e03dcd5c6f76a5b0a9dd5ba348f50d164',
}
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

def checkout(root, release, destination):
    """Create a detached historical worktree outside the active checkout."""
    root=Path(root).resolve()
    if release not in LEGACY_CHECKOUTS:
        raise ValueError('Choose one of: '+', '.join(LEGACY_CHECKOUTS))
    target=Path(destination).expanduser()
    if not target.is_absolute():
        raise ValueError('Historical worktree path must be absolute')
    target=target.resolve(strict=False)
    if target == root or root in target.parents:
        raise ValueError('Historical worktree must be outside the active repository')
    if target.exists() or target.is_symlink():
        raise ValueError('Refusing to replace an existing historical worktree path')
    if not target.parent.is_dir():
        raise ValueError('Historical worktree parent directory must already exist')
    revision=LEGACY_CHECKOUTS[release]
    resolved=subprocess.check_output(['git','rev-parse','--verify',revision+'^{commit}'],
                                     cwd=root,text=True).strip()
    if resolved != revision:
        raise ValueError('Pinned historical revision does not resolve exactly')
    result=subprocess.run(['git','worktree','add','--detach',str(target),revision],
                          cwd=root,text=True,capture_output=True)
    if result.returncode:
        # The target did not exist before this call. Remove only a partial tree
        # created by Git; leave every pre-existing path untouched.
        subprocess.run(['git','worktree','remove','--force',str(target)],
                       cwd=root,text=True,capture_output=True)
        if target.exists() and target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        raise RuntimeError((result.stderr or result.stdout or 'git worktree add failed').strip())
    actual=subprocess.check_output(['git','-C',str(target),'rev-parse','HEAD'],
                                   cwd=root,text=True).strip()
    if actual != revision:
        raise RuntimeError('Created historical checkout does not match the pinned revision')
    return dict(release=release,revision=revision,path=str(target),detached=True,
        physical_accepted=False,current_candidate_data_imported=False,
        next_step='Run the historical tools from this worktree; keep generated outputs inside it.')

def main(argv=None,root=ROOT):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',nargs='?',default='status',
                   help='status, verify, or checkout a pinned historical release')
    p.add_argument('release',nargs='?',help='v0.4.0, v0.5.1, or v0.5-maglev')
    p.add_argument('--path',type=Path,help='new absolute worktree path outside this repository')
    a=p.parse_args(argv)
    if a.action in ('verify','audit'):
        if a.release is not None or a.path is not None:
            p.error('verify accepts no release or path')
        from engineering.station_rail.history import verify as verify_v05
        result=dict(pre_comfort=verify(root),v05_maglev=verify_v05(root))
    elif a.action in ('status','readiness'):
        if a.release is not None or a.path is not None:
            p.error('status accepts no release or path')
        result=dict(source_revision=REVISION,role='Historical comparison only',current_default='engineering/development-baseline.toml',
            archive=OUTPUT+'/README.md',historical_writers_in_current_tree=False,
            reproducible_checkouts=list(LEGACY_CHECKOUTS),physical_accepted=False)
    elif a.action == 'checkout':
        if a.release is None or a.path is None:
            p.error('checkout requires RELEASE and --path ABSOLUTE_PATH')
        try:
            result=checkout(root,a.release,a.path)
        except ValueError as error:
            p.error(str(error))
        except (OSError,RuntimeError) as error:
            print(json.dumps(dict(checkout='failed',release=a.release,path=str(a.path),
                error=str(error),historical_source_changed=False,
                current_candidate_data_imported=False,physical_accepted=False),indent=2))
            return 2
    else:
        print('Historical writer refused in the active checkout. Use `./osr legacy checkout RELEASE --path /absolute/path` for a pinned detached worktree.')
        return 2
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
