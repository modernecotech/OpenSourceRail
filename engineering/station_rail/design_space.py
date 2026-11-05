"""Integrity adapter for the retired fixed-service design-space comparison.

The original generator and numerical tests live at the exact retained Git
commit. Active design work requires an explicit candidate campaign, service
requirements and station geometry. This adapter cannot manufacture a new motor
layout by replaying the former implicit 900 m recipe under changed producers.
"""
from pathlib import Path
from hashlib import sha256
from . import ROOT
from .retired_station_reference import RetiredReferenceHold

PRODUCER='engineering/station_rail/design_space.py'
SPEC='campaigns/v06-expanded-design-space.toml'
OUTPUT='docs/design-engine/v06-design-space'
_LOADED_SHA=sha256(Path(__file__).read_bytes()).hexdigest()


def _retired_recipe():
    raise RetiredReferenceHold(
        'The fixed-service expanded design-space recipe is retired. '
        'Use an explicit candidate campaign with service requirements and station layout. '
        'Reproduce the original comparison only in the pinned 3bf38a501d09fa3a3c2dd6f4731be11828d04f55 checkout; '
        'design space verify checks preserved bytes, not current numerical admission.')


def parent(root=ROOT):
    """Do not materialize an old implicit parent as a current design default."""
    return _retired_recipe()


def assemble(root=ROOT):
    return _retired_recipe()


def build(root=ROOT,output=None,*,native_dirs=None):
    # Refuse before creating outputs or attaching any native result.
    return _retired_recipe()


def verify(root=ROOT,output=None):
    """Strict old-packet integrity only; the original numerical replay is separate."""
    from . import retired_station_reference as retired
    root=Path(root).resolve();expected=root/OUTPUT
    if output is not None and Path(output).resolve()!=expected:
        raise RetiredReferenceHold('Only the exact pinned retired design-space packet is admitted for byte verification')
    source=retired._path(root,PRODUCER)
    if sha256(source.read_bytes()).hexdigest()!=_LOADED_SHA:
        raise RetiredReferenceHold('Executing retired design-space adapter differs from source root')
    result=retired.verify(root)
    return dict(schema='osr-retired-design-space-verification/1',verified=True,retired=True,
        manifest_id=result['retired_manifest_ids']['v06-design-space'],
        reference_commit=result['reference_commit'],retention_id=result['retention_id'],
        verification_scope='Exact retired packet and pinned Git source bytes only',
        dependency_sha256={**result['dependency_sha256'],PRODUCER:_LOADED_SHA},
        **{k:False for k in ('current_evaluator_admission','numerical_reexecuted',
            'physical_equivalence_proven','physical_accepted','engineering_accepted',
            'configuration_adopted','manufacturing_release','operating_release')})
