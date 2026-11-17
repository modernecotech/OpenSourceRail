"""Verify the completed v0.7 coupled research at its original source epoch.

This is byte integrity, not a current-evaluator replay or physical acceptance.
"""
from hashlib import sha256
import json
from pathlib import Path
import tarfile

from . import ROOT
from .common import identity
from .publication import digest

PACKET = Path('docs/design-engine/coupled-railway-v07')
ARCHIVE = Path('docs/archives/coupled-railway-v07-source-epoch/sources.tar.gz')
SOURCE_COMMIT = 'e4e73bfdda720c608816aa76a78148855ab8443b'
MANIFEST_ID = 'bebd7f952031f211156ddaea5f3393229ac88ad18a1347cffca1ebd17255814e'
FLAGS = ('physical_accepted', 'engineering_accepted', 'manufacturing_release',
         'operating_release', 'configuration_adopted')


def verify(root=ROOT):
    root = Path(root).resolve()
    base = root / PACKET
    manifest_path = base / 'manifest.json'
    manifest = json.loads(manifest_path.read_bytes())
    if (manifest.get('schema') != 'osr-coupled-railway-publication/2'
            or manifest.get('manifest_id') != MANIFEST_ID
            or identity({k: v for k, v in manifest.items() if k != 'manifest_id'}) != MANIFEST_ID
            or any(manifest.get(flag) is not False for flag in FLAGS)):
        raise ValueError('Retained v0.7 coupled manifest or disposition differs')
    sources = manifest.get('source_sha256')
    files = manifest.get('files_sha256')
    if (not isinstance(sources, dict) or len(sources) != 66
            or not isinstance(files, dict) or len(files) != 49):
        raise ValueError('Retained v0.7 coupled source or payload inventory differs')
    actual = {p.relative_to(base).as_posix(): digest(p)
              for p in base.rglob('*') if p.is_file() and p != manifest_path}
    if actual != files:
        raise ValueError('Retained v0.7 coupled payload differs')
    archive_path = root / ARCHIVE
    with tarfile.open(archive_path, 'r:gz') as archive:
        members = archive.getmembers()
        if (len(members) != len(sources)
                or sum(member.size for member in members) > 8 * 1024 * 1024
                or any(not member.isfile() or Path(member.name).is_absolute()
                       or '..' in Path(member.name).parts for member in members)
                or len({member.name for member in members}) != len(members)):
            raise ValueError('Retained v0.7 coupled source archive inventory differs')
        source_hashes = {member.name: sha256(archive.extractfile(member).read()).hexdigest()
                         for member in members}
    if source_hashes != sources:
        raise ValueError('Retained v0.7 coupled source bytes differ')
    dependencies = {str(PACKET / name): value for name, value in files.items()}
    dependencies.update({str(PACKET / 'manifest.json'): digest(manifest_path),
                         str(ARCHIVE): digest(archive_path),
                         'engineering/station_rail/retained_v07_coupled.py':
                         digest(root / 'engineering/station_rail/retained_v07_coupled.py')})
    return {'verified': True, 'source_commit': SOURCE_COMMIT,
            'original_manifest_id': MANIFEST_ID, 'original_source_count': len(sources),
            'numerical_reexecuted': False, 'current_evaluator_admission': False,
            'physical_accepted': False, 'dependency_sha256': dependencies}
