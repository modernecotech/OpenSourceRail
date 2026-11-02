"""Independently replay a caller-pinned topology cost baseline.

A self-sealed ledger proves internal identity, not authenticity. The expected
baseline ID must come from an independent trusted reference, such as a reviewed
commit. This analytical replay does not admit a native evaluator or qualify the
railway. Original and replay tool contexts remain separate.
"""
import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import topology_system_cost as canonical

PRODUCER = 'engineering/design_search/topology_baseline_integrity.py'
BASELINE = 'docs/design-engine/civil-topology/baseline.json.gz'
MAX_COMPRESSED = 64 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, installed_mass_complete=False,
             physical_journey_completed=False, service_qualified=False)


def _sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _pairs(rows):
    value = {}
    for key, item in rows:
        if key in value:
            raise ValueError('Duplicate JSON key')
        value[key] = item
    return value


def _snapshot(path):
    """Bounded ordinary file; no symlink ancestors or changing input bytes."""
    path = Path(path).absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError('Symlink baseline or ancestor refused')
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_COMPRESSED:
        raise ValueError('Bounded ordinary compressed baseline required')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as source:
        opened = source.fileno()
        actual = os.fstat(opened)
        signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if signature(before) != signature(actual):
            raise ValueError('Baseline changed before reading')
        raw = source.read(MAX_COMPRESSED + 1)
        if len(raw) > MAX_COMPRESSED or signature(actual) != signature(os.fstat(opened)):
            raise ValueError('Baseline changed during reading')
    if signature(actual) != signature(path.stat()):
        raise ValueError('Baseline changed after reading')
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as source:
        expanded = source.read(MAX_EXPANDED + 1)
    if len(expanded) > MAX_EXPANDED:
        raise ValueError('Expanded baseline exceeds budget')
    try:
        value = json.loads(expanded, object_pairs_hook=_pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError('Malformed baseline JSON') from error
    if not isinstance(value, dict):
        raise ValueError('Baseline JSON object required')
    return raw, value


def verify_record(baseline, *, expected_baseline_id, root=ROOT):
    """Recompute every field except the original tool epoch and its own seal.

    The externally expected ID is a trust input, not an independently verified
    signature. An attacker controlling both the input and that ID can select a
    different input, but still cannot make altered costs reproduce without also
    changing the checked source/model epoch.
    """
    if not _sha(expected_baseline_id) or not isinstance(baseline, dict):
        raise ValueError('Caller-pinned baseline identity required')
    saved = deepcopy(baseline)
    if (saved.get('baseline_id') != expected_baseline_id
            or expected_baseline_id != identity({k: v for k, v in saved.items() if k != 'baseline_id'})):
        raise ValueError('Baseline differs from caller-pinned identity')
    producer_before = digest(Path(__file__))
    root = Path(root).resolve()
    canonical.validate_baseline(saved, root, require_current_tools=False)
    original_tools = deepcopy(saved['tool_context'])
    fresh = canonical.make_baseline(root, saved['load_context'])
    canonical.validate_baseline(saved, root, require_current_tools=False)
    if (baseline.get('baseline_id') != expected_baseline_id
            or identity({k: v for k, v in baseline.items() if k != 'baseline_id'}) != expected_baseline_id
            or identity({k: v for k, v in saved.items() if k != 'baseline_id'}) != expected_baseline_id):
        raise ValueError('Baseline changed during analytical replay')
    ignored = {'baseline_id', 'tool_context'}
    preserved = {k: v for k, v in saved.items() if k not in ignored}
    reproduced = {k: v for k, v in fresh.items() if k not in ignored}
    preserved_id = identity(preserved)
    if preserved_id != identity(reproduced):
        differing = sorted(k for k in set(preserved) | set(reproduced)
            if k not in preserved or k not in reproduced or identity(preserved[k]) != identity(reproduced[k]))
        raise ValueError('Canonical baseline semantic replay differs: ' + ', '.join(differing))
    if digest(Path(__file__)) != producer_before:
        raise ValueError('Integrity verifier source changed during replay')
    result = dict(schema='osr-topology-baseline-integrity/1', verified=True,
        expected_baseline_id=expected_baseline_id, replay_baseline_id=fresh['baseline_id'],
        source_epoch_id=identity(saved['source_sha256']), load_context_id=saved['load_context_id'],
        selected_vehicle_candidate_id=saved['selected']['candidate_id'],
        selected_vehicle_evaluation_id=saved['selected']['vehicle_evaluation_id'],
        selection_id=saved['selected']['selection_id'],
        canonical_system_cost_estimate_id=saved['canonical_system_cost_estimate_id'],
        canonical_vehicle_cost_estimate_id=saved['canonical_vehicle_cost_estimate_id'],
        semantic_baseline_id=preserved_id, recorded_tool_context=original_tools,
        replay_tool_context=deepcopy(fresh['tool_context']),
        original_runtime_independently_attested=False, caller_identity_independently_attested=False,
        caller_pinned_identity_required=True, native_evaluator_reuse=False,
        canonical_cost_fields_recomputed=True, full_semantic_baseline_recomputed=True,
        scope='Exact fresh analytical baseline replay except recorded tool context and its dependent identity; no physical qualification',
        producer_sha256=producer_before, **FLAGS)
    result['verification_id'] = identity(result)
    return result


def verify(path=None, *, expected_baseline_id, root=ROOT):
    path = Path(root) / BASELINE if path is None else Path(path)
    raw, baseline = _snapshot(path)
    report = verify_record(baseline, expected_baseline_id=expected_baseline_id, root=root)
    if _snapshot(path)[0] != raw:
        raise ValueError('Baseline file changed during verification')
    report.pop('verification_id')
    report['baseline_file_sha256'] = sha256(raw).hexdigest()
    report['verification_id'] = identity(report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--expected-baseline-id', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        result = verify(args.baseline, expected_baseline_id=args.expected_baseline_id, root=args.root)
    except (ValueError, OSError, EOFError, KeyError, TypeError) as error:
        parser.exit(2, str(error) + '\n')
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
