"""Deterministic compact evidence transport; never a replacement for raw solvers.

The raw package is verified before export. Its original receipt is retained
unchanged, while a separate receipt names exactly what was kept and omitted.
No remote raw-object storage is configured by this helper.
"""
from pathlib import Path, PurePosixPath
from hashlib import sha256
import gzip
import io
import json
import tarfile
from .common import encoded, identity, digest
from . import ROOT, FLAGS

MAX_BYTES = 256*1024*1024
SMALL_EXTENSIONS = {'.json','.geo','.pro','.py','.log','.txt','.inp','.dat','.sta','.cvg','.toml','.csv','.md','.f90','.c','.cpp','.rs'}


def _safe(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or str(p)!=name or '\\' in name:
        raise ValueError('Unsafe archive path')
    return name


def _files(folder):
    result={}
    for p in Path(folder).rglob('*'):
        if p.is_symlink():raise ValueError('Evidence packages cannot contain symbolic links')
        if p.is_file():result[_safe(p.relative_to(folder).as_posix())]=p
    return result


def _raw_verified(packet,root):
    files=_files(packet)
    if 'manifest.json' not in files:raise ValueError('Original immutable manifest required')
    m=json.loads(files['manifest.json'].read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Original manifest identity differs')
    if any(m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('Research archive cannot grant release')
    actual={n:digest(p) for n,p in files.items() if n!='manifest.json'}
    if actual!=m['files_sha256']:raise ValueError('Original raw package differs from receipt')
    for n,h in m['source_sha256'].items():
        if digest(Path(root)/_safe(n))!=h:raise ValueError('Original method source differs')
    # Invoke the motor-specific result/identity checks in addition to complete
    # generic receipt checks. Other small packets retain the generic checks.
    if m.get('schema')=='osr-native-primary-package/1':
        from .station_motor import verify
        verify(packet,root)
    elif m.get('schema')=='osr-native-full-primary-package/1':
        from .long_motor import verify
        verify(packet,root)
    return m,files


def export(packet,archive,root=ROOT,*,include_all=False,max_bytes=MAX_BYTES):
    """Verify and export to a fresh tar.gz; return its compact receipt.

    ``include_all`` retains complete small body/braking packages. Otherwise
    native mesh, factorisation, field and binary files stay in the local raw
    directory and are indexed by their original SHA-256. max_bytes bounds
    uncompressed retained bytes as well as the compressed archive.
    """
    packet=Path(packet).resolve();archive=Path(archive);root=Path(root).resolve()
    if archive.exists():raise ValueError('Preserve existing immutable archive')
    if type(max_bytes) is not int or not 0<max_bytes<=MAX_BYTES:raise ValueError('Archive budget must be positive and at most 256 MiB')
    original,files=_raw_verified(packet,root)
    retained={n:p for n,p in files.items() if n=='manifest.json' or include_all or p.suffix.lower() in SMALL_EXTENSIONS}
    payload={}
    total=0
    for n,p in sorted(retained.items()):
        total+=p.stat().st_size
        if total>max_bytes:raise ValueError('Retained evidence exceeds archive budget')
        payload['raw/'+n]=p.read_bytes()
    for n,h in sorted(original['source_sha256'].items()):
        p=root/_safe(n);total+=p.stat().st_size
        if total>max_bytes:raise ValueError('Retained evidence exceeds archive budget')
        value=p.read_bytes()
        if sha256(value).hexdigest()!=h:raise ValueError('Source changed during archival')
        payload['sources/'+n]=value
    omitted={n:h for n,h in original['files_sha256'].items() if n not in retained}
    compact=dict(schema='osr-compact-native-evidence/1',original_manifest_id=original['manifest_id'],
        original_manifest_sha256=digest(packet/'manifest.json'),source_sha256=original['source_sha256'],
        files_sha256={n:sha256(b).hexdigest() for n,b in sorted(payload.items())},
        omitted_raw_files_sha256=omitted,retained_raw_payload_complete=not omitted,
        local_raw_package_at_export=str(packet),remote_raw_storage=None,
        full_native_verifier_available_from_compact_alone=False,
        verification_scope='Retained bytes, original receipt, omission index and included method sources; not omitted solver outputs or physical qualification',
        uncompressed_retained_bytes=total,include_all=include_all,**FLAGS)
    compact['compact_manifest_id']=identity(compact)
    payload['compact-manifest.json']=encoded(compact)
    if total+len(payload['compact-manifest.json'])>max_bytes:raise ValueError('Archive receipt exceeds retained-byte budget')
    archive.parent.mkdir(parents=True,exist_ok=True)
    # gzip header mtime/name and tar owner/time/mode are fixed: equal inputs
    # produce exactly equal archives, independent of their destination name.
    try:
        with archive.open('xb') as raw:
            with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as gz:
                with tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as tar:
                    for n,b in sorted(payload.items()):
                        info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o644;info.uid=info.gid=info.mtime=0
                        tar.addfile(info,io.BytesIO(b))
        if archive.stat().st_size>max_bytes:raise ValueError('Compressed archive exceeds budget')
        verify(archive,root)
    except BaseException:
        archive.unlink(missing_ok=True)
        raise
    return compact


def verify(archive,root=None,*,max_bytes=MAX_BYTES):
    """Check the exact retained set without extracting archive members."""
    if type(max_bytes) is not int or not 0<max_bytes<=MAX_BYTES:raise ValueError('Invalid verification byte budget')
    payload={};total=0
    with tarfile.open(archive,'r:gz') as tar:
        for item in tar:
            _safe(item.name)
            if not item.isfile() or item.name in payload:raise ValueError('Only unique ordinary evidence files permitted')
            total+=item.size
            if total>max_bytes:raise ValueError('Archive exceeds decompressed budget')
            payload[item.name]=tar.extractfile(item).read()
    if 'compact-manifest.json' not in payload:raise ValueError('Compact manifest missing')
    m=json.loads(payload.pop('compact-manifest.json'))
    if m['schema']!='osr-compact-native-evidence/1' or m['compact_manifest_id']!=identity({k:v for k,v in m.items() if k!='compact_manifest_id'}):raise ValueError('Compact receipt identity differs')
    if any(m.get(k) is not v for k,v in FLAGS.items()) or m['remote_raw_storage'] is not None or m['full_native_verifier_available_from_compact_alone'] is not False:raise ValueError('Compact evidence cannot grant release or imply raw availability')
    if {n:sha256(b).hexdigest() for n,b in payload.items()}!=m['files_sha256']:raise ValueError('Retained bytes differ')
    original_raw=payload['raw/manifest.json'];original=json.loads(original_raw)
    if sha256(original_raw).hexdigest()!=m['original_manifest_sha256'] or original['manifest_id']!=m['original_manifest_id'] or original['manifest_id']!=identity({k:v for k,v in original.items() if k!='manifest_id'}):raise ValueError('Original receipt differs')
    retained={n[4:]:sha256(b).hexdigest() for n,b in payload.items() if n.startswith('raw/') and n!='raw/manifest.json'}
    omitted=m['omitted_raw_files_sha256']
    if set(retained)&set(omitted) or {**retained,**omitted}!=original['files_sha256']:raise ValueError('Retained/omitted partition differs from original receipt')
    if m['retained_raw_payload_complete']!= (not omitted) or m['source_sha256']!=original['source_sha256']:raise ValueError('Completeness or source claim differs')
    sources={n[8:]:sha256(b).hexdigest() for n,b in payload.items() if n.startswith('sources/')}
    if sources!=m['source_sha256'] or any(not n.startswith(('raw/','sources/')) for n in payload):raise ValueError('Source bytes or archive paths differ')
    if root is not None and any(digest(Path(root)/_safe(n))!=h for n,h in sources.items()):raise ValueError('Current source differs from archived method')
    return dict(verified=True,compact_manifest_id=m['compact_manifest_id'],original_manifest_id=m['original_manifest_id'],retained_raw_payload_complete=m['retained_raw_payload_complete'],omitted_raw_file_count=len(omitted),remote_raw_storage=None,full_native_verifier_available_from_compact_alone=False,**FLAGS)
