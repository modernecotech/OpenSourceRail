"""Immutable checksummed multipart archives and safe streaming retrieval."""
from __future__ import annotations
import gzip
import hashlib
import io
from pathlib import Path
import shutil
import tarfile

from .contracts import encoded,identity,load,sha,ROOT


class PartWriter:
    def __init__(self,output,maximum):
        self.output=output;self.maximum=maximum;self.current=None;self.size=0;self.paths=[]
    def write(self,data):
        view=memoryview(data);original=len(view)
        while view:
            if self.current is None or self.size==self.maximum:
                if self.current:self.current.close()
                path=self.output/f'part-{len(self.paths)+1:04d}.tar.gz.part'
                self.paths.append(path);self.current=path.open('xb');self.size=0
            count=min(len(view),self.maximum-self.size)
            self.current.write(view[:count]);view=view[count:];self.size+=count
        return original
    def flush(self):
        if self.current:self.current.flush()
    def close(self):
        if self.current:self.current.close()


class PartReader(io.RawIOBase):
    def __init__(self,paths):self.paths=iter(paths);self.current=None
    def readable(self):return True
    def readinto(self,buffer):
        target=memoryview(buffer);total=0
        while total<len(target):
            if self.current is None:
                path=next(self.paths,None)
                if path is None:break
                self.current=path.open('rb')
            n=self.current.readinto(target[total:])
            if not n:self.current.close();self.current=None;continue
            total+=n
        return total
    def close(self):
        if self.current:self.current.close()
        super().close()


def safe(root,relative):
    path=Path(relative)
    if path.is_absolute() or '..' in path.parts or not (root/path).resolve().is_relative_to(root.resolve()):
        raise ValueError('archive path escapes its controlled root')
    return root/path


def pack(source,output,maximum=50*1024**2):
    if output.exists() or not source.is_dir() or not 1024<=maximum<=50*1024**2:
        raise ValueError('archive requires a source directory, new output and bounded part size')
    if output.resolve().is_relative_to(source.resolve()):raise ValueError('archive output cannot be inside source')
    files={}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():raise ValueError('archive cannot contain symlinks')
        if path.is_file():files[path.relative_to(source).as_posix()]=dict(sha256=sha(path),bytes=path.stat().st_size)
    output.mkdir(parents=True)
    writer=PartWriter(output,maximum)
    try:
        with gzip.GzipFile(filename='',fileobj=writer,mode='wb',mtime=0,compresslevel=1) as compressed:
            with tarfile.open(fileobj=compressed,mode='w|') as archive:
                for relative,receipt in files.items():
                    path=source/relative
                    if sha(path)!=receipt['sha256']:raise ValueError('source changed while packing')
                    info=tarfile.TarInfo(relative);info.size=receipt['bytes'];info.mode=0o644;info.mtime=0
                    with path.open('rb') as stream:archive.addfile(info,stream)
    finally:writer.close()
    index=dict(schema='osr-civil-artifact-store/1',version=identity(files),files=files,
               parts=[dict(name=p.name,sha256=sha(p),bytes=p.stat().st_size) for p in writer.paths])
    (output/'index.json').write_bytes(encoded(index))
    return index


def restore(store,destination):
    index=load(store/'index.json')
    if index['schema']!='osr-civil-artifact-store/1' or index['version']!=identity(index['files']):
        raise ValueError('archive identity differs from its member inventory')
    if destination.exists():raise ValueError('restore destination must be new')
    if destination.resolve().is_relative_to(ROOT) and not destination.resolve().is_relative_to(ROOT/'build'):
        raise ValueError('retrieval inside repository belongs under build/')
    paths=[]
    for part in index['parts']:
        path=safe(store,part['name'])
        if not path.is_file() or path.stat().st_size!=part['bytes'] or sha(path)!=part['sha256']:
            raise ValueError('archive part integrity failure')
        paths.append(path)
    destination.mkdir(parents=True);seen=set()
    try:
        with io.BufferedReader(PartReader(paths)) as joined, tarfile.open(fileobj=joined,mode='r|gz') as archive:
            for member in archive:
                if not member.isfile() or member.name not in index['files'] or member.name in seen:
                    raise ValueError('unexpected, duplicate or nonregular archive member')
                receipt=index['files'][member.name]
                if member.size!=receipt['bytes']:raise ValueError('archive member size mismatch')
                target=safe(destination,member.name);target.parent.mkdir(parents=True,exist_ok=True)
                source=archive.extractfile(member)
                if source is None:raise ValueError('archive member missing data')
                with source, target.open('xb') as output:shutil.copyfileobj(source,output)
                if sha(target)!=receipt['sha256']:raise ValueError('archive member hash mismatch')
                seen.add(member.name)
        if seen!=set(index['files']):raise ValueError('archive incomplete')
    except Exception:
        shutil.rmtree(destination)
        raise
    return dict(version=index['version'],files_restored=len(seen),integrity_verified=True)
