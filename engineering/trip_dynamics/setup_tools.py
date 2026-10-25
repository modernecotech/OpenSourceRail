"""Download exact solver bootstraps into an explicit private directory."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tarfile
from urllib.parse import urldefrag
import urllib.request


def install(output):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=True)
    record = json.loads(Path(__file__).with_name('solver-environment.json').read_bytes())
    for key, filename, subfolder in [('getdp', 'getdp-3.5.0-Linux64c.tgz', ''),
                                     ('micromamba', 'micromamba-2.9.0-0.tar.bz2', 'micromamba')]:
        expected = record[key]; target = output/filename
        url = expected.get('reproduction_url', expected['url'])
        if not target.exists() and key=='micromamba':
            # Earlier retained setup recipes used these cache filenames. Only
            # the same exact archive bytes can substitute for a new download.
            for name in ('micromamba-pinned.tar.bz2','micromamba.tar.bz2'):
                cached=output/name
                if (cached.is_file() and not cached.is_symlink() and cached.stat().st_size==expected['bytes']
                        and sha256(cached.read_bytes()).hexdigest()==expected['sha256']):
                    target=cached
                    break
        if not target.exists():
            request = urllib.request.Request(url, headers={'User-Agent':'OpenSourceRail-trip-toolchain/1'})
            temporary = target.with_suffix(target.suffix+'.pending')
            try:
                with urllib.request.urlopen(request, timeout=30) as response, temporary.open('xb') as stream:
                    count = 0
                    while True:
                        chunk = response.read(1024*1024)
                        if not chunk: break
                        count += len(chunk)
                        if count > expected['bytes']:
                            raise ValueError('solver archive exceeds its pinned byte count')
                        stream.write(chunk)
                if temporary.stat().st_size != expected['bytes'] or sha256(temporary.read_bytes()).hexdigest() != expected['sha256']:
                    raise ValueError('solver archive differs from its exact download pin')
                temporary.rename(target)
            finally:
                temporary.unlink(missing_ok=True)
        if target.is_symlink() or sha256(target.read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('existing private solver archive differs')
        destination = output/subfolder
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(target) as archive:
            # Installing into the stable private tools directory must not
            # replace an already-present executable with different bytes.
            executable = 'getdp-3.5.0-Linux64/bin/getdp' if key=='getdp' else 'bin/micromamba'
            members = [m for m in archive.getmembers() if m.name.lstrip('./')==executable]
            if len(members)!=1 or not members[0].isfile():
                raise ValueError('pinned archive executable inventory differs')
            expected_binary = sha256(archive.extractfile(members[0]).read()).hexdigest()
            existing = destination/executable
            if existing.exists() and (existing.is_symlink() or sha256(existing.read_bytes()).hexdigest()!=expected_binary):
                raise ValueError('existing private executable differs; leaving it unchanged: '+str(existing))
            if not existing.exists():
                archive.extractall(destination, filter='data')
    return dict(getdp=str(output/'getdp-3.5.0-Linux64/bin/getdp'),
                micromamba=str(output/'micromamba/bin/micromamba'), global_environment_modified=False)


def _locked_packages(root):
    lock=Path(root)/'engineering/trip_dynamics/environment-linux-64.lock'
    source=Path(root)/'engineering/trip_dynamics/solver-environment.json'
    if lock.is_symlink() or source.is_symlink():
        raise ValueError('ordinary repository lock and package pins required')
    lock_bytes,source_bytes=lock.read_bytes(),source.read_bytes()
    if len(lock_bytes)>1024*1024 or len(source_bytes)>4*1024*1024:
        raise ValueError('bounded private environment specifications required')
    lines=[s.strip() for s in lock_bytes.decode().splitlines() if s.strip() and not s.lstrip().startswith('#')]
    if not lines or lines.pop(0)!='@EXPLICIT' or not 1<=len(lines)<=512:
        raise ValueError('bounded explicit environment package lock required')
    packages=json.loads(source_bytes)['packages']
    expected={p['name']:p for p in packages}
    if len(expected)!=len(packages):
        raise ValueError('duplicate package names in private environment pins')
    by_url={p['url']:p for p in packages}
    if len(by_url)!=len(packages) or len(lines)!=len(packages):
        raise ValueError('explicit lock and SHA256 package pins differ')
    seen=set()
    for line in lines:
        url,md5=urldefrag(line)
        row=by_url.get(url)
        if url in seen or row is None or row.get('md5')!=md5 or len(row.get('sha256',''))!=64:
            raise ValueError('explicit URL/MD5 lock disagrees with SHA256 package pins')
        if not url.startswith(('https://conda.anaconda.org/conda-forge/', 'https://conda.anaconda.org/projectchrono/')):
            raise ValueError('private package URL is not an explicit approved source')
        seen.add(url)
    if not {'python','pychrono'}<=set(expected):
        raise ValueError('locked Python and PyChrono packages required')
    return expected,dict(lock_sha256=sha256(lock_bytes).hexdigest(), package_pins_sha256=sha256(source_bytes).hexdigest())


def _matching_environment(prefix, expected):
    """Check exact package receipts and critical Python/Chrono installed files.

    This is an installation integrity check, not a claim that every dependency
    was independently reproduced or that any train model is physically valid.
    """
    prefix=Path(prefix)
    if prefix.is_symlink() or not prefix.is_dir():
        raise ValueError('existing private environment is not an ordinary directory; leaving it unchanged')
    metadata=prefix/'conda-meta'
    records={}
    for path in sorted(metadata.glob('*.json')):
        if path.is_symlink() or path.stat().st_size>16*1024*1024:
            raise ValueError('invalid installed package receipt; leaving environment unchanged')
        row=json.loads(path.read_bytes())
        if row.get('name') in records:
            raise ValueError('duplicate installed package receipt; leaving environment unchanged')
        records[row.get('name')]=row
        if len(records)>512:
            raise ValueError('installed package count exceeds lock budget')
    if set(records)!=set(expected):
        raise ValueError('existing private environment package inventory differs; leaving it unchanged')
    for name,row in records.items():
        if any(row.get(k)!=expected[name].get(k) for k in ('version','build','url','sha256','md5')):
            raise ValueError('existing private environment package differs: '+name+'; leaving it unchanged')
    critical={}
    size=0
    for name in ('python','pychrono'):
        for row in records[name].get('paths_data',{}).get('paths',[]):
            rel=row.get('_path','')
            selected=(name=='python' and rel=='bin/python3.12') or (name=='pychrono' and
                (rel=='lib/libChrono_core.so' or '/pychrono/' in rel and rel.endswith(('.py','.so'))))
            if not selected:
                continue
            path=prefix/rel
            if Path(rel).is_absolute() or '..' in Path(rel).parts or path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(prefix.resolve()):
                raise ValueError('critical private runtime path invalid; leaving environment unchanged')
            size+=path.stat().st_size
            if size>2*1024*1024*1024:
                raise ValueError('critical runtime verification exceeds two GiB budget')
            digest=sha256(path.read_bytes()).hexdigest()
            if digest!=row.get('sha256_in_prefix',row.get('sha256')):
                raise ValueError('critical private runtime bytes differ: '+rel+'; leaving environment unchanged')
            critical[rel]=digest
    if 'bin/python3.12' not in critical or not any('/pychrono/_core' in p and p.endswith('.so') for p in critical):
        raise ValueError('critical Python/PyChrono integrity receipts missing; leaving environment unchanged')
    if not (prefix/'bin/python').is_file() or not os.access(prefix/'bin/python',os.X_OK):
        raise ValueError('private environment Python unavailable; leaving it unchanged')
    return dict(package_count=len(records),critical_runtime_sha256=critical,
                integrity_scope='Exact lock/package receipts and critical Python/Chrono installed-file hashes')


def ensure_chrono(root, micromamba, log_output, *, timeout_s=1000):
    """Create/reuse the fixed private locked environment, without user rc files.

    Existing mismatches and partial installs are retained and refused; nothing
    is deleted or repaired in place. Download/create logs stay with the job.
    """
    if type(timeout_s) not in (int,float) or not 1<=timeout_s<=1000:
        raise ValueError('bounded private environment setup timeout required')
    root=Path(root).resolve(); log_output=Path(log_output)
    expected,pins=_locked_packages(root)
    prefix=root/'build/trip-dynamics/environment/chrono'
    root_prefix=root/'build/trip-dynamics/environment/mamba-root'
    sources_before=dict(pins)
    created=False
    command=None
    if prefix.is_symlink() or root_prefix.is_symlink() or any(p.is_symlink() for p in prefix.parents):
        raise ValueError('ordinary private environment paths required')
    if not prefix.exists():
        micromamba=Path(micromamba)
        if micromamba.is_symlink() or not micromamba.is_file() or not os.access(micromamba,os.X_OK):
            raise ValueError('pinned private micromamba executable required')
        log_output.mkdir(parents=True,exist_ok=True)
        command=[str(micromamba),'create','--no-rc','--no-env','--root-prefix',str(root_prefix),
                 '--prefix',str(prefix),'--file',str(root/'engineering/trip_dynamics/environment-linux-64.lock'),'--yes']
        environment={k:v for k,v in os.environ.items() if not k.startswith(('MAMBA_','CONDA_','PYTHON'))}
        with (log_output/'chrono-setup-stdout.txt').open('xb') as stdout, (log_output/'chrono-setup-stderr.txt').open('xb') as stderr:
            process=subprocess.run(command,cwd=root,env=environment,stdout=stdout,stderr=stderr,timeout=timeout_s)
        if process.returncode:
            raise RuntimeError('locked Chrono creation failed; partial environment and setup logs retained')
        created=True
    state=_matching_environment(prefix,expected)
    _,after=_locked_packages(root)
    if after!=sources_before:
        raise ValueError('private environment lock/source pins changed during setup')
    return dict(schema='osr-private-chrono-setup/1',prefix=str(prefix),created=created,reused=not created,
                command=command,**pins,**state,global_environment_modified=False,
                code_aster_installed=False,physical_accepted=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    tools=install(args.output)
    tools['chrono']=ensure_chrono(args.source_root,tools['micromamba'],args.output/'logs')
    print(json.dumps(tools, indent=2))
