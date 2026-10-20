"""Separate exact design/provenance identity from solver round-off agreement.

These tolerances govern reproduction, not engineering acceptance. Geometry,
configuration hashes, source hashes, decisions and unlisted values remain exact.
"""
from __future__ import annotations
import json
import math
import re

RULES = (
    (r"(?:review\.)?(?:minimum_static_contact_n|static_reaction_balance_n)$", 1e-7, 1e-12),
    (r"(?:review\.)?carbody_dynamics\[\d+\]\.(?:cg_m|cg_change_m)\[\d+\]$", 1e-12, 1e-13),
    (r"(?:review\.)?carbody_dynamics\[\d+\]\.inertia_kg_m2\[\d+\]\[\d+\]$", 1e-8, 1e-12),
)


def differences(actual, expected, path="", *, rules=RULES):
    """Return changed paths; tolerate only finite floats at registered paths."""
    if type(actual) is not type(expected):return [path or '$']
    if isinstance(actual, dict):
        if actual.keys()!=expected.keys():return [path or '$']
        return [p for key in actual for p in differences(actual[key],expected[key],f'{path}.{key}' if path else key,rules=rules)]
    if isinstance(actual,list):
        if len(actual)!=len(expected):return [path or '$']
        return [p for i,(a,b) in enumerate(zip(actual,expected)) for p in differences(a,b,f'{path}[{i}]',rules=rules)]
    if isinstance(actual,float):
        if not math.isfinite(actual) or not math.isfinite(expected):return [path or '$']
        for pattern,absolute,relative in rules:
            if re.fullmatch(pattern,path):
                return [] if math.isclose(actual,expected,abs_tol=absolute,rel_tol=relative) else [path]
    return [] if actual==expected else [path or '$']


def require_equivalent(actual, expected, label):
    changed=differences(actual,expected)
    if changed:raise ValueError(label+' differs at '+', '.join(changed[:8]))


def require_html_equivalent(actual, expected):
    marker='<script id="data" type="application/json">'
    def split(value):
        start=value.index(marker)+len(marker);end=value.index('</script>',start)
        return value[:start],json.loads(value[start:end].replace('<\\/','</')),value[end:]
    a,b=split(actual),split(expected)
    if a[0]!=b[0] or a[2]!=b[2]:raise ValueError('published HTML source differs')
    require_equivalent(a[1],b[1],'published HTML data')
