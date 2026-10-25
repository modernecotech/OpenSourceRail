"""Fast source/payload checks for startup, explicitly separate from engineering."""
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re


def _digest(path):
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _ordinary(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != name:
        raise ValueError('ordinary relative receipt path required')
    result = root/path
    if result.is_symlink() or result.resolve() != result or not result.is_file():
        raise ValueError('missing or linked receipt file: '+name)
    return result


def primary_integrity(root, *, source_provider=None):
    """Check the publication envelope; do not rebuild native engineering studies.

    A held packet does not prevent access to tools needed to investigate it.
    This result must never be labelled an engineering or physical acceptance.
    """
    root = Path(root).resolve(); folder = root/'docs/design-engine/ferrite-maglev/reference'
    issues = []; source_count = payload_count = 0
    try:
        receipt = _ordinary(root, 'docs/design-engine/ferrite-maglev/reference/manifest.json')
        if receipt.stat().st_size > 16*1024*1024:
            raise ValueError('bounded primary receipt required')
        manifest = json.loads(receipt.read_bytes())
        if not isinstance(manifest, dict):
            raise ValueError('primary receipt object required')
        if manifest.get('schema') != 'osr-primary-infrastructure-publication/1' or manifest.get('family') != 'ferrite-pm-maglev-study':
            raise ValueError('not the current primary publication schema')
        for name in ('design_complete', 'physical_validation', 'manufacturing_release', 'physical_release'):
            if manifest.get(name) is not False:
                raise ValueError('research packet cannot assert '+name)
        expected, payload = manifest['source_sha256'], manifest['files_sha256']
        for mapping in (expected, payload):
            if not isinstance(mapping, dict) or not mapping or not all(
                    isinstance(name, str) and isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest)
                    for name, digest in mapping.items()):
                raise ValueError('explicit source and payload SHA256 mappings required')
        source_count = len(expected)
        if source_provider is None:
            from engineering.ferrite_maglev import model
            if root == model.ROOT.resolve():
                source_provider = model.sources
        if source_provider is not None:
            live = source_provider()
            issues += ['source differs: '+name for name in sorted(set(expected)|set(live)) if expected.get(name) != live.get(name)]
        else:
            for name, digest in expected.items():
                if _digest(_ordinary(root, name)) != digest:
                    issues.append('source differs: '+name)
        payload_count = len(payload)
        actual = {p.name for p in folder.iterdir() if p.is_file()}
        if actual != set(payload)|{'manifest.json'}:
            issues.append('primary payload inventory differs')
        for name, digest in payload.items():
            if _digest(_ordinary(folder, name)) != digest:
                issues.append('payload differs: '+name)
    except (OSError, ValueError, TypeError, KeyError) as error:
        issues.append(str(error))
    return dict(state='held' if issues else 'current', scope='source-and-payload-integrity-only',
                source_files=source_count, payload_files=payload_count,
                issue_count=len(issues), issues=issues[:20],
                numerical_verification_executed=False, engineering_accepted=False,
                physical_accepted=False,
                explanation='Opening the Workbench checks receipt integrity. Numerical reproduction is an explicit separate action.')
