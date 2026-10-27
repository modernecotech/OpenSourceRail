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
        current = root / path
        if any(part.is_symlink() for part in (current,*current.parents) if part!=root and part.is_relative_to(root)):
            raise ValueError('Ordinary retained source required: ' + name)
        if path.suffix == '.py':
            actual = _producer_digest(str(root), source_revision, name)
            if actual != expected:raise ValueError('Retained producer ancestry differs: ' + name)
        else:
            if not current.is_file() or sha256(current.read_bytes()).hexdigest() != expected:
                raise ValueError('Retained live input differs: ' + name)
            live[name] = expected
    return dict(source_revision=source_revision,
                ancestry_source_sha256=dict(sorted(bindings.items())),
                source_sha256={**dict(sorted(live.items())), CODE: sha256(Path(__file__).read_bytes()).hexdigest()})
