"""Fail-closed verifier for the declared v0.6 digital closure gates.

The verifier checks that all campaign work IDs are represented, that a closure
claim is backed by in-tree content hashes and a separate review record, and
that physical/manufacturing/operating acceptance is not inferred from software
closure. It validates record integrity, not engineering semantics.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import tomllib


CAMPAIGN = 'campaigns/v06-design-integration-closure.toml'
STATUS = 'docs/design-engine/v06-design-closure/status.json'
STATUS_SCHEMA = 'osr-v06-design-closure-status/1'
VALID_STATES = {'open', 'partial', 'closed'}
RELEASE_FLAGS = ('physical_accepted', 'engineering_accepted', 'manufacturing_release',
                 'operating_release', 'movement_authority')


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'JSON object required: {path}')
    return value


def _recorded_file(root: Path, row: dict, label: str) -> str:
    relative = row.get('path')
    expected = row.get('sha256')
    if (not isinstance(relative, str) or not relative or '\\' in relative
            or PurePosixPath(relative).is_absolute() or '..' in PurePosixPath(relative).parts
            or PurePosixPath(relative).as_posix() != relative):
        raise ValueError(f'unsafe {label} path')
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'ordinary in-tree {label} file required: {relative}')
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f'symlink in {label} path: {relative}')
        current = current.parent
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    actual = digest.hexdigest()
    if expected != actual:
        raise ValueError(f'{label} content hash mismatch: {relative}')
    return actual


def inspect(root: str | Path, *, campaign_path: str = CAMPAIGN,
            status_path: str = STATUS) -> dict:
    """Validate closure ledger structure and return a release-readiness report."""
    root = Path(root).resolve()
    campaign_file = root / campaign_path
    status_file = root / status_path
    if campaign_file.is_symlink() or not campaign_file.is_file():
        raise ValueError('closure campaign is absent or not an ordinary file')
    if status_file.is_symlink() or not status_file.is_file():
        raise ValueError('closure status record is absent or not an ordinary file')
    campaign_bytes = campaign_file.read_bytes()
    campaign = tomllib.loads(campaign_bytes.decode('utf-8'))
    status = _read_json(status_file)
    if campaign.get('schema') != 'osr-design-integration-closure-program/1':
        raise ValueError('unexpected v0.6 closure campaign schema')
    if status.get('schema') != STATUS_SCHEMA:
        raise ValueError('unexpected v0.6 closure status schema')
    if status.get('campaign_path') != campaign_path:
        raise ValueError('closure status points to a different campaign')
    campaign_digest = sha256(campaign_bytes)
    if status.get('campaign_sha256') != campaign_digest:
        raise ValueError('closure status is stale for the declared campaign')

    work = campaign.get('work', [])
    if not isinstance(work, list):
        raise ValueError('closure campaign work list required')
    required_rows = [row for row in work if isinstance(row, dict) and row.get('required') is True]
    required_ids = [row.get('id') for row in required_rows]
    if any(not isinstance(value, str) or not value for value in required_ids):
        raise ValueError('each required campaign item needs a nonempty ID')
    if len(required_ids) != len(set(required_ids)):
        raise ValueError('duplicate required campaign work ID')
    required = set(required_ids)
    records = status.get('gates')
    controls_publication = campaign.get('release_unpublished_until_required_work_closed')
    if type(controls_publication) is not bool:
        raise ValueError('Explicit software-publication control required')
    publication = campaign.get('software_publication', {})
    if controls_publication is False and (
            publication.get('control_superseded') is not True
            or publication.get('engineering_findings_remain_open') is not True
            or not publication.get('published_release')
            or not publication.get('published_source_commit')
            or not publication.get('published_release_url')):
        raise ValueError('Superseded software-publication control needs its published source and retained engineering findings')
    if (not required or not isinstance(records, dict) or set(records) != required):
        raise ValueError('closure ledger must cover each and only each required campaign work ID')

    open_gates = []
    for gate_id in sorted(required):
        row = records[gate_id]
        if not isinstance(row, dict) or row.get('state') not in VALID_STATES:
            raise ValueError(f'invalid closure state for {gate_id}')
        evidence = row.get('evidence')
        if not isinstance(evidence, list):
            raise ValueError(f'evidence list required for {gate_id}')
        for item in evidence:
            _recorded_file(root, item, f'{gate_id} evidence')
        if row['state'] == 'closed':
            if not evidence:
                raise ValueError(f'closed gate needs source-bound evidence: {gate_id}')
            review = row.get('independent_review')
            if not isinstance(review, dict) or review.get('state') != 'accepted':
                raise ValueError(f'closed gate needs an independent accepted review: {gate_id}')
            reviewer = review.get('reviewer')
            if not isinstance(reviewer, str) or not reviewer.strip():
                raise ValueError(f'closed gate reviewer identity required: {gate_id}')
            _recorded_file(root, review, f'{gate_id} independent review')
        else:
            blocker = row.get('blocker')
            if not isinstance(blocker, str) or not blocker.strip():
                raise ValueError(f'open gate needs a visible blocker: {gate_id}')
            open_gates.append(dict(id=gate_id, state=row['state'], blocker=blocker))

    flags = status.get('release_flags')
    if not isinstance(flags, dict) or any(flags.get(name) is not False for name in RELEASE_FLAGS):
        raise ValueError('software closure cannot assert physical or operational acceptance')
    review = status.get('release_review')
    if not isinstance(review, dict):
        raise ValueError('release review record required')
    all_closed = not open_gates
    release_reviewed = review.get('state') == 'accepted'
    if release_reviewed:
        if not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip():
            raise ValueError('independent release reviewer identity required')
        _recorded_file(root, review, 'independent release review')
    elif not isinstance(review.get('blocker'), str) or not review['blocker'].strip():
        raise ValueError('pending release review needs a visible blocker')
    ready = all_closed and release_reviewed
    if status.get('release_ready') is not ready:
        raise ValueError('release_ready does not match the verified gate and review state')
    return dict(schema='osr-v06-release-readiness/1', campaign_sha256=campaign_digest,
                required_gate_count=len(required), closed_gate_count=len(required)-len(open_gates),
                open_gates=open_gates, release_ready=ready,
                engineering_design_complete=ready,
                controls_software_publication=controls_publication,
                published_software_release=publication.get('published_release'),
                release_flags={name: False for name in RELEASE_FLAGS})


def require_ready(root: str | Path) -> dict:
    report = inspect(root)
    if not report['release_ready']:
        ids = ', '.join(item['id'] for item in report['open_gates']) or 'independent release review'
        raise ValueError(f'v0.6 engineering design closure remains incomplete: {ids}')
    return report
