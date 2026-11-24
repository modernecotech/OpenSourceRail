"""Authenticate retained producer ancestry without substituting live input data.

Historical Python producer bytes are checked against an explicit local Git
revision. Non-Python inputs used by today's evaluator must match the live files.
This module never fetches Git objects or treats an old producer as current code.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import re
import subprocess

CODE = 'engineering/research_ancestry.py'

# These v0.5 inputs moved byte-for-byte out of the repository root. A retained
# receipt still names its original path. Resolve only the exact archived digest
# so a different input cannot acquire the old source identity by path aliasing.
RELOCATED_V05_INPUTS = {
    ('lib/templates/infrastructure.toml', '0bebf8fbfd6b4dd05e53394171caadcc90b5d28154e31a8aa61794a57c898d12'):
        'engineering/maglev_research/infrastructure-policy-v05.toml',
    ('ferrite-maglev-study.toml', 'a1effd80c4a5390b3c615b5833258e88ed1e687cfad065c65260b8149ae50839'):
        'engineering/maglev_research/inputs/ferrite-maglev-study.toml',
    ('OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx', 'ddadab05460950f13f99f8134fafb5303f0103a6e914aa57181917008d092b9a'):
        'engineering/maglev_research/inputs/OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx',
    ('OpenSourceRail maglev station concept.png', '0f795d8c20890279ec6ef1075a882e61827f26db26c02c14f375948ed5275d37'):
        'engineering/maglev_research/inputs/OpenSourceRail maglev station concept.png',
    ('Vertical spiral escape chute concept.png', 'b784a542c1fec9d2172f07ca917df7f6a2f5d9b48bf0a7aa4e7ac89e9e4c91b5'):
        'engineering/maglev_research/inputs/Vertical spiral escape chute concept.png',
}


def live_input_path(root, name, expected):
    """Resolve an ordinary current file or the exact byte-identical v0.5 move."""
    root = Path(root).resolve()
    path = Path(name)
    if path.is_absolute() or not path.parts or '..' in path.parts or not re.fullmatch('[a-f0-9]{64}', expected):
        raise ValueError('Ordinary source path and SHA256 required')
    direct = root / path
    selected = direct if direct.is_file() or direct.is_symlink() else root / RELOCATED_V05_INPUTS.get((name, expected), name)
    if any(part.is_symlink() for part in (selected, *selected.parents) if part != root and part.is_relative_to(root)):
        raise ValueError('Ordinary retained source required (symlink): ' + name)
    return selected


@lru_cache(maxsize=1024)
def _producer_digest(root, revision, name):
    result = subprocess.run(['git', 'show', revision + ':' + name], cwd=root,
                            capture_output=True, check=False)
    if result.returncode:
        raise ValueError('Retained producer ancestry unavailable locally: ' + revision + ':' + name)
    return sha256(result.stdout).hexdigest()


def verify(root, bindings, *, source_revision):
    """Return separate archived ancestry and live inputs for an exact source pin."""
    root = Path(root).resolve()
    if not isinstance(source_revision, str) or not re.fullmatch('[a-f0-9]{40}', source_revision):
        raise ValueError('Explicit full retained source revision required')
    live = {}
    if not isinstance(bindings, dict):raise ValueError('Explicit retained source mapping required')
    for name, expected in bindings.items():
        if not isinstance(name,str) or not isinstance(expected,str):raise ValueError('Ordinary source path and SHA256 required')
        path = Path(name)
        if path.is_absolute() or not path.parts or '..' in path.parts or not re.fullmatch('[a-f0-9]{64}', expected):
            raise ValueError('Ordinary source path and SHA256 required')
        if path.suffix == '.py':
            actual = _producer_digest(str(root), source_revision, name)
            if actual != expected:raise ValueError('Retained producer ancestry differs: ' + name)
        else:
            current = live_input_path(root, name, expected)
            if not current.is_file() or sha256(current.read_bytes()).hexdigest() != expected:
                raise ValueError('Retained live input differs: ' + name)
            live[name] = expected
    return dict(source_revision=source_revision,
                ancestry_source_sha256=dict(sorted(bindings.items())),
                source_sha256={**dict(sorted(live.items())), CODE: sha256(Path(__file__).read_bytes()).hexdigest()})
