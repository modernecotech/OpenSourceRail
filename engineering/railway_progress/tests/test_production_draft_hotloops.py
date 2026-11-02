"""Preserve complete draft exports while avoiding repeated bookkeeping work."""
from collections import Counter
from hashlib import sha256

import pytest

from engineering.railway_progress import alternatives, encoded, identity, production
from engineering.railway_progress.tests.test_alternatives import vehicle as base_vehicle


@pytest.fixture(scope="module")
def inputs(base_vehicle):
    alternative = alternatives.evaluate(base_vehicle)
    candidate_id = identity(dict(body=base_vehicle["candidate_id"], alternative=alternative["candidate_id"]))
    civil = dict(candidate_id=candidate_id, body_candidate_id=base_vehicle["candidate_id"],
        alternative_candidate_id=alternative["candidate_id"], construction_sequence=[])
    civil["evaluation_id"] = identity(civil)
    return base_vehicle, civil, alternative, candidate_id


@pytest.fixture(scope="module")
def result(inputs):
    return production.compile(*inputs)


def test_complete_production_and_draft_exports_match_pre_optimisation_reference(result):
    # Captured from commit 6122ab1094 for the existing typed two-part fixture.
    # This covers ordering, rates, quantities, flags and every nested draft.
    assert sha256(encoded(result)).hexdigest() == "ce070277fb8f74e2aeeda8c14bf3291e42a29376eb8fde998161740a901fbbd1"
    drafts = result["ERPNext_drafts"]
    assert sha256(encoded(drafts)).hexdigest() == "24d7c45b02402cb36a835f7ecfa8efd8d82a2983e926e1bcc1e379aeeb8d7ca1"
    assert drafts["export_id"] == "8d655aea11b13d835e52bee1f7afc85655e62a8b296599045bc83dec5da59f59"


def test_repeated_occurrences_remain_one_item_with_the_complete_rfq_quantity(inputs, result):
    vehicle, _, alternative, _ = inputs
    counts = Counter(o["part_definition_id"] for o in vehicle["registry"]["occurrences"])
    assert sorted(counts.values()) == [6, 18]
    expected = {"vehicle/"+key: count for key, count in counts.items()}
    expected.update({"launch/"+part["part_id"]: part["count"] for part in alternative["inventory"]})
    drafts = result["ERPNext_drafts"]
    source_by_code = {item["item_code"]: item["source_key"] for item in drafts["item_drafts"]}
    actual = {source_by_code[rfq["items"][0]["item_code"]]: rfq["items"][0]["qty"]
        for rfq in drafts["rfq_drafts"]}
    assert actual == expected
    assert len(source_by_code) == len(expected) == len(drafts["routing_drafts"])
    assert drafts["quantity_reconciliation"]["all_counts_reconciled"]


def test_quantity_union_is_performed_once_without_changing_any_export(inputs, result, monkeypatch):
    class CountedCounter(Counter):
        unions = 0

        def __or__(self, other):
            type(self).unions += 1
            return super().__or__(other)

    monkeypatch.setattr(production, "Counter", CountedCounter)
    actual = production.compile(*inputs)
    assert CountedCounter.unions == 1
    assert encoded(actual) == encoded(result)


def test_item_code_hash_prefix_collisions_are_still_rejected(inputs, result, monkeypatch):
    vehicle, _, alternative, candidate_id = inputs
    parts = {part["physical_definition_id"]: part for part in vehicle["registry"]["parts"]}
    counts = Counter(o["part_definition_id"] for o in vehicle["registry"]["occurrences"])
    first_revision = parts[sorted(parts)[0]]["revision_id"]
    first_launch_part = alternative["inventory"][0]
    real_identity = production.identity

    def colliding_identity(value):
        if isinstance(value, str) and value.startswith(("vehicle/", "launch/")):
            return "c"*64
        if value is first_launch_part:
            return first_revision
        return real_identity(value)

    monkeypatch.setattr(production, "identity", colliding_identity)
    with pytest.raises(ValueError, match="Draft item-code collision"):
        production._drafts(vehicle, alternative, candidate_id, parts, counts, result["routings"])
