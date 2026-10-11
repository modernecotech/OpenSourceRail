"""Strict data, time and retained-evidence primitives for local factory tools."""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib
import math
from pathlib import Path
from osr_mech.engineering_definition import fingerprint,load_definition

ROOT=Path(__file__).resolve().parents[2]


def finite(value,name,minimum=None):
    if type(value) not in (int,float) or not math.isfinite(value) or (minimum is not None and value<minimum):
        raise ValueError('invalid '+name)
    return float(value)


def timestamp(value):
    if not isinstance(value,str):raise ValueError('timezone-aware ISO timestamp required')
    try:result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as error:raise ValueError('timezone-aware ISO timestamp required') from error
    if result.tzinfo is None:raise ValueError('timezone-aware ISO timestamp required')
    return result.astimezone(timezone.utc)


def artifact(ref,root=ROOT,*,kind=None):
    required={'path','sha256','kind','revision','approved_by'}
    if not isinstance(ref,dict) or set(ref)!=required or not ref['revision'] or not ref['approved_by']:
        raise ValueError('retained artifact revision and approval identity required')
    if ref['kind'] not in ('drawing','procedure','material','measurement','calibration','record') or (kind is not None and ref['kind']!=kind):
        raise ValueError('incompatible or synthetic evidence kind')
    path=Path(ref['path']);base=Path(root).resolve();resolved=(base/path).resolve()
    if path.is_absolute() or '..' in path.parts or not resolved.is_relative_to(base) or not resolved.is_file():
        raise ValueError('retained evidence must be inside its controlled root')
    if hashlib.sha256(resolved.read_bytes()).hexdigest()!=ref['sha256']:raise ValueError('retained evidence checksum changed')
    return ref
