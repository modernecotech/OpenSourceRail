"""Explicit fixture-root selection for retained research software tests.

Tests use their own checkout unless a caller deliberately supplies an absolute
evidence root. An override must contain the requested fixtures and the same
producer sources; it cannot silently borrow a different checkout's evaluators.
This helper does not authenticate measurements or qualify physical equipment.
"""
from hashlib import sha256
import os
from pathlib import Path


def evidence_root(checkout_root, *, required, sources, environ=None,
                  variable='OSR_EVIDENCE_ROOT'):
    checkout = Path(checkout_root).resolve()
    environment = os.environ if environ is None else environ
    if variable not in environment:
        return checkout
    supplied = environment[variable]
    if variable != 'OSR_EVIDENCE_ROOT' and 'OSR_EVIDENCE_ROOT' in environment:
        if Path(environment['OSR_EVIDENCE_ROOT']).resolve() != Path(supplied).resolve():
            raise ValueError('Conflicting explicit research evidence roots')
    if not supplied or not Path(supplied).is_absolute():
        raise ValueError(variable + ' must explicitly name an absolute fixture root')
    root = Path(supplied).resolve()
    if not root.is_dir() or not required or not sources:
        raise ValueError(variable + ' requires an existing root, fixtures and source provenance')

    def ordinary(folder, name):
        relative = Path(name)
        path = folder / relative
        if relative.is_absolute() or '..' in relative.parts or not path.is_file():
            raise ValueError(variable + ' fixture/source missing or invalid: ' + str(name))
        if not path.resolve().is_relative_to(folder):
            raise ValueError(variable + ' fixture/source escapes its declared root: ' + str(name))
        return path

    for name in required:
        ordinary(root, name)
    for name in sources:
        fixture = ordinary(root, name)
        producer = ordinary(checkout, name)
        if sha256(fixture.read_bytes()).digest() != sha256(producer.read_bytes()).digest():
            raise ValueError(variable + ' source provenance differs from this checkout: ' + str(name))
    return root
