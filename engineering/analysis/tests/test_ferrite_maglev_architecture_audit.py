"""Retired adapters cannot quietly re-enter source or compressed publications."""
import gzip
import pytest
from engineering.ferrite_maglev import architecture_audit,model


def test_current_tree_contains_only_current_vehicle_sources():
    assert architecture_audit.verify(model.ROOT)['current_only']


def test_old_identity_in_plain_or_compressed_evidence_is_rejected(tmp_path):
    for suffix in ('.py','.json.gz'):
        p=tmp_path/('receipt'+suffix)
        raw=('configuration='+architecture_audit.TOKENS[0]).encode()
        p.write_bytes(gzip.compress(raw) if suffix.endswith('.gz') else raw)
        assert architecture_audit.scan([p])==[str(p)]


def test_geographic_comparisons_and_accessibility_terms_are_permitted(tmp_path):
    p=tmp_path/'requirements.md';p.write_text('Accessible wheelchair entry. Compare urban rail coverage with London and Paris.')
    assert not architecture_audit.scan([p])
