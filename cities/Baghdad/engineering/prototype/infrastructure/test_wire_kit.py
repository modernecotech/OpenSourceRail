import csv
from io import StringIO
import json

import pytest

from cities.Baghdad.engineering.prototype.infrastructure import wire_kit as kit


FIXTURE = (kit.HERE / "wire-practice.csv").read_bytes()


def make(raw):
    return kit.build(raw, "COUPON-A", "PRACTICE-0.5MM2")


def records(raw):
    return list(csv.DictReader(StringIO(raw.decode())))


def test_coupon_preserves_cut_allowances_pin_pairs_and_open_checks():
    out = make(FIXTURE)
    assert out == make(FIXTURE)
    manifest = json.loads(out["wire-kit.json"])
    assert manifest["wire_count"] == 2 and manifest["total_cut_mm"] == 460
    assert not manifest["fabrication_released"] and not manifest["energisation_authorised"]
    labels = records(out["wire-cut-labels.csv"])
    assert [(r["wire_id"], r["cut_mm"]) for r in labels] == [("C01", "210"), ("C02", "250")]
    for row in records(out["continuity-traveller.csv"]):
        assert row["kit_evaluation_id"] == manifest["kit_evaluation_id"]
        assert row["observed_from"] == row["continuity_reading_and_unit"] == row["disposition"] == ""
    for name, sha in manifest["artifact_sha256"].items():
        assert kit.digest(out[name]) == sha


@pytest.mark.parametrize("field,value,match", [
    ("from_pin", "1", "repeats a terminal"), ("wire_id", "c01", "repeats a wire"),
    ("service_slack_mm", "TBD", "needs a value"), ("from_end_allowance_mm", "-1", "whole-millimetre"),
    ("scope", "invented", "unknown interface"), ("data_class", "supplier-proposal", "mixed data"),
    ("candidate_id", "OTHER", "different candidate"), ("drawing_revision", "B", "drawing revision"),
    ("packet_evaluation_id", "old", "packet"), ("wire_spec", "other", "wire specification"),
])
def test_incomplete_mixed_and_ambiguous_returns_are_rejected(field, value, match):
    rows = records(FIXTURE)
    rows[1][field] = value
    with pytest.raises(ValueError, match=match):
        make(kit.csv_bytes(kit.FIELDS, rows))
