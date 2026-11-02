"""Reuse one validated summary without sharing separately exposed records."""
from copy import deepcopy

import pytest

from engineering.component_registry import make_occurrence, make_part, make_registry, summary
from engineering.component_registry import registry as registry_module
from engineering.sourced_case import encoded, equipment, identity


def typed_vehicle():
    functions = list(equipment.DEFAULT_SELECTIONS)
    parts = [make_part("DISPOSABLE-"+name.upper()+"-TEST", "T1", [name],
        dict(kind="envelope", dimensions_m=[1., .4, .4], net_volume_m3=None), None,
        dict(calculated_kg=None, lower_bound_kg=20., upper_bound_kg=30., evidence_state="bounded-estimate"),
        dict(method="unqualified-test-envelope")) for name in functions]
    occurrences = []
    for car in range(6):
        for i, part in enumerate(parts):
            pose = [[1.,0.,0.,17.5*car+2.*i], [0.,1.,0.,0.], [0.,0.,1.,.5], [0.,0.,0.,1.]]
            occurrences.append(make_occurrence(f"car-{car+1}/equipment-{i}", part, transform=pose))
    registry = make_registry("DISPOSABLE equipment-interface fixture", parts, occurrences, functions)
    value = dict(candidate_id=registry["candidate_id"], registry=registry, summary=summary(registry),
        requirements=dict(cars=6), unresolved=[], source_sha256={})
    value["evaluation_id"] = identity(value)
    return value


@pytest.fixture(scope="module")
def vehicle():
    return typed_vehicle()


def test_one_summary_is_computed_while_registry_validation_remains_active(vehicle, monkeypatch):
    original_input = encoded(vehicle)
    summaries = []
    validations = []
    real_summary = equipment.summary
    real_validate = registry_module.validate_registry

    def count_summary(registry):
        summaries.append(registry["candidate_id"])
        return real_summary(registry)

    def count_validation(registry):
        validations.append(registry["candidate_id"])
        return real_validate(registry)

    monkeypatch.setattr(equipment, "summary", count_summary)
    monkeypatch.setattr(registry_module, "validate_registry", count_validation)
    result = equipment.substitute(vehicle)
    assert encoded(vehicle) == original_input
    assert result["candidate_id"] == "c5c242947d2a73d71653e60e17e89ae4a1d14cb4ed4933802b37afd96bbf5060"
    assert summaries == [result["candidate_id"]]
    assert result["candidate_id"] in validations
    assert vehicle["candidate_id"] in validations
    assert result["summary"] == result["vehicle"]["summary"]
    assert result["summary"]["registry_id"] == result["vehicle"]["registry"]["registry_id"]
    assert result["mass_change_bounds_kg"] == [
        result["summary"]["mass_lower_bound_kg"]-vehicle["summary"]["mass_upper_bound_kg"],
        result["summary"]["mass_upper_bound_kg"]-vehicle["summary"]["mass_lower_bound_kg"]]
    assert all(result[key] is False for key in equipment.FLAGS)
    assert result["evaluation_id"] == identity({k:v for k,v in result.items() if k!="evaluation_id"})


def test_exposed_summary_records_keep_independent_nested_mutability(vehicle):
    result = equipment.substitute(vehicle)
    outer = result["summary"]
    inner = result["vehicle"]["summary"]
    assert outer == inner and outer is not inner
    names = list(inner["functional_coverage"])
    inner_before = deepcopy(inner)
    outer["functional_coverage"][names[0]]["occurrences"] = -1
    assert inner == inner_before
    outer_before = deepcopy(outer)
    inner["functional_coverage"][names[-1]]["occurrences"] = -2
    assert outer == outer_before


def test_input_registry_tampering_is_still_rejected(vehicle):
    bad = deepcopy(vehicle)
    bad["registry"]["occurrences"][0]["part_revision_id"] = "0"*64
    bad["evaluation_id"] = identity({k:v for k,v in bad.items() if k!="evaluation_id"})
    with pytest.raises(ValueError, match="Registry schema/revision identity differs"):
        equipment.substitute(bad)
