#!/usr/bin/env python3
"""Package verified, committed digital studies; never authorise physical release."""
import argparse
from hashlib import sha1,sha256
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import gzip

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import delivery,iteration,model


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    manifest=delivery.verify();iteration.verify()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=subprocess.check_output(['git','ls-tree','-rz','--full-tree','HEAD'],cwd=ROOT)
    tracked={}
    for item in raw.split(b'\0'):
        if item:
            meta,name=item.split(b'\t',1);mode,kind,digest=meta.split()
            if kind==b'blob' and mode in (b'100644',b'100755'):tracked[name.decode()]=digest.decode()
    paths=set(manifest['source_sha256'])
    paths.update(('README.md','LICENSE.md','OpenSourceRail-Book.pdf','docs/ARCHITECTURE.md','docs/ROADMAP.md',
                  'engineering/ferrite_maglev/README.md','engineering/ferrite_maglev/city-index.md',
                  'tools/automation/package-maglev-release.py'))
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'LICENSES').rglob('*') if p.is_file())
    for folder in ('reference','native','beam-only','system-development','baghdad-reference','coupled','iterative'):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'docs/design-engine/ferrite-maglev'/folder).rglob('*') if p.is_file())
    files={};total=0
    for name in sorted(paths):
        path=ROOT/name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or '..' in Path(name).parts:raise ValueError('unsafe release member')
        if path.stat().st_size>64*1024*1024:raise ValueError('oversized member: '+name)
        data=path.read_bytes();total+=len(data)
        if total>512*1024*1024:raise ValueError('release package exceeds bound')
        git_hash=sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if tracked.get(name)!=git_hash:raise ValueError('release member differs from committed source: '+name)
        files[name]=data
    record=dict(schema='osr-software-study-release/1',version=model.RELEASE_VERSION,commit=commit,
        scope='Source-bound digital research studies, not a manufacturing or operating release. This evidence bundle is a selected source subset; obtain full source from the Git tag.',
        source_sha256=manifest['source_sha256'],files_sha256={n:sha256(d).hexdigest() for n,d in files.items()},
        accepted_engineering_items=0,**model.FLAGS)
    files['RELEASE-MANIFEST.json']=delivery.encoded(record)
    prefix='OpenSourceRail-v'+model.RELEASE_VERSION
    output=args.output.resolve()
    if output.exists() and any(output.iterdir()):raise ValueError('choose a new empty release output')
    output.mkdir(parents=True,exist_ok=True)
    archive=output/(prefix+'-design-studies.tar.gz')
    with archive.open('wb') as target,gzip.GzipFile(filename='',mode='wb',fileobj=target,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w|') as tar:
        for name,data in sorted(files.items()):
            info=tarfile.TarInfo(prefix+'/'+name);info.size=len(data);info.mode=0o644;info.mtime=0
            tar.addfile(info,io.BytesIO(data))
    (output/'RELEASE-MANIFEST.json').write_bytes(files['RELEASE-MANIFEST.json'])
    (output/'OpenSourceRail-Book.pdf').write_bytes((ROOT/'OpenSourceRail-Book.pdf').read_bytes())
    sums=''.join(sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(output.iterdir()))
    (output/'SHA256SUMS').write_text(sums)
    print(json.dumps(dict(version=model.RELEASE_VERSION,commit=commit,members=len(files),uncompressed_bytes=total,
        archive_bytes=archive.stat().st_size,output=str(output),physical_release=False),indent=2))


if __name__=='__main__':main()
