"""Deterministic, lossless supporting-archive parts and receipt-bound reads."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import zipfile

PRIMARY = 'Baghdad-Proposal-Supporting-Data.zip'
TEXT = {'.json','.csv','.toml','.md','.py','.rs','.ifc','.xml','.geojson',
        '.html','.js','.svg','.txt','.pdf','.gpkg'}


def archive_name(index):
    return PRIMARY if index == 1 else f'Baghdad-Proposal-Supporting-Data-part-{index:03d}.zip'


def write_parts(directory, members, as_of, maximum):
    """Measure real compressed entries, then partition without dropping inputs."""
    stamp=tuple(int(v) for v in as_of.split('-'))+(0,0,0)
    def write(path, names):
        with zipfile.ZipFile(path,'w') as archive:
            for name in names:
                source=members[name]
                entry=zipfile.ZipInfo(name,date_time=stamp)
                entry.compress_type=zipfile.ZIP_LZMA if source.suffix.lower() in TEXT else zipfile.ZIP_DEFLATED
                entry.external_attr=0o100644<<16
                archive.writestr(entry,source.read_bytes(),compresslevel=9)
    with tempfile.TemporaryDirectory(dir=directory,prefix='.proposal-archives-') as folder:
        temporary=Path(folder)
        measured=temporary/'measured.zip'
        write(measured,sorted(members))
        groups=[[]];size=22
        with zipfile.ZipFile(measured) as archive:
            for entry in archive.infolist():
                # Local and central headers, UTF-8 names, ZIP64/codec margins.
                cost=entry.compress_size+128+2*len(entry.filename.encode('utf-8'))
                if cost+22>maximum:
                    raise ValueError('One compressed evidence member exceeds archive limit: '+entry.filename)
                if groups[-1] and size+cost>maximum:
                    groups.append([]);size=22
                groups[-1].append(entry.filename);size+=cost
        result={}
        for index,names in enumerate(groups,1):
            name=archive_name(index);part=temporary/name
            write(part,names)
            if part.stat().st_size>maximum:raise ValueError('Supporting archive exceeds limit: '+name)
            result[name]=names
        # Publish only after every part has successfully materialised.
        for name in result:(temporary/name).replace(directory/name)
        for old in directory.glob('Baghdad-Proposal-Supporting-Data*.zip'):
            if old.name not in result:old.unlink()
    return result


def part_inventory(manifest):
    return manifest.get('supporting_archives',{PRIMARY:manifest.get('archive_members',[])})


def read_members(root, directory, manifest, names):
    """Verify all requested bytes before the caller restores any local input."""
    legacy='supporting_archives' not in manifest and 'archive_members' not in manifest
    inventory={PRIMARY:names} if legacy else part_inventory(manifest)
    locations={}
    for part,members in inventory.items():
        if Path(part).name!=part or not part.endswith('.zip'):raise ValueError('Unsafe archive part name')
        for member in members:
            if member in locations:raise ValueError('Duplicate archive members across parts')
            locations[member]=part
    data={}
    needed={locations[name] for name in names}
    for part in sorted(needed):
        path=directory/part;receipt=manifest['outputs'][path.relative_to(root).as_posix()]
        raw=path.read_bytes()
        if len(raw)!=receipt['bytes'] or hashlib.sha256(raw).hexdigest()!=receipt['sha256']:
            raise ValueError('Proposal archive differs from its publication receipt')
        with zipfile.ZipFile(path) as archive:
            entries=archive.namelist()
            if len(entries)!=len(set(entries)):raise ValueError('Duplicate archive members')
            if not legacy and set(entries)!=set(inventory[part]):raise ValueError('Archive inventory mismatch')
            for name in names:
                if locations[name]==part:data[name]=archive.read(name)
    return data
