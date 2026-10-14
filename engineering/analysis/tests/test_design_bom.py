"""Real physical adapters must retain their installed inventory in review exports."""

from copy import deepcopy
import csv
import json
import os

import pytest

from engineering.design_engine.adapters import compile_candidate
from engineering.design_engine.bom import candidate_bill
from engineering.design_engine.contracts import SCHEMA, fingerprint, identity
from engineering.design_engine.export import export, verify_export
from engineering.design_engine.publication import digest
from engineering.design_engine.registry import get
from engineering.design_engine.runtime import request, review_package
from engineering.design_engine.store import Store, write_new

PROBLEMS = [
    "clipped-side-bay",
    "viaduct-bay",
    "battery-installation",
    "roof-hvac",
    "full-train",
]


def scope():
    return identity(
        dict(
            schema=SCHEMA,
            city="samawah",
            project="bom-test",
            environment="simulation",
            configuration_revision="research-1",
            baseline_sha256=None,
            run_id=None,
            asset_id=None,
            part_id=None,
        )
    )


@pytest.fixture(scope="module")
def candidates():
    result = {}
    for name in PROBLEMS:
        charter = get(name)
        values = {
            key: row.get("choices", row.get("bounds"))[0]
            for key, row in charter["variables"].items()
        }
        result[name] = compile_candidate(charter, scope(), values)
    return result


@pytest.mark.parametrize("name", PROBLEMS)
def test_real_compilers_export_all_physical_instances_and_unknown_allocations(
    name, candidates, tmp_path
):
    candidate = candidates[name]
    charter = get(name)
    bill = candidate_bill(candidate, adapter=charter["adapter"])
    definition = candidate["definition"]
    model = definition.get("contract", definition.get("model"))
    physical = model.get("parts", model.get("instances"))
    source = {part["id"]: part for part in physical}
    assert len(bill["parts"]) == len(source) > 0
    assert {row["physical_id"] for row in bill["parts"]} == set(source)
    assert sum(row["quantity"] for row in bill["parts"]) == len(source)
    assert bill["complete_installed_mass_kg"] is None
    assert bill["complete_installed_kit"] is False
    assert (
        bill["unresolved_allocations"]
        == definition["installed_register"]["unresolved_allocations"]
    )
    assert bill["unresolved_allocations"]
    for row in bill["parts"]:
        part = source[row["physical_id"]]
        props = part["properties"].get("design", part["properties"])
        assert row["revision"] == part["revision"]
        assert row["part_id"] == part.get("part_id", part["id"])
        assert row["material"] == part.get("material")
        assert row["defined_mass_kg"] == props["mass_kg"]
        assert row["cg_m"] == props["cg_m"]
        assert row["inertia_tensor_kg_m2"] == props["inertia_tensor_kg_m2"]
    assert bill["defined_mass_kg"] == pytest.approx(
        candidate["metrics"]["defined_mass_kg"]
    )
    req = request(name, scope(), candidates=[candidate["variables"]])
    summary = dict(candidates=[candidate], conditional_shortlist=[candidate["id"]])
    review = review_package(req, summary)
    assert review["bill"] == [bill]
    store = Store(tmp_path / "jobs")
    job = store.create(req)
    attempt = store.begin(job["id"], os.getpid())
    write_new(attempt / "comparison.json", summary)
    manifest = dict(
        schema="osr-design-attempt/1",
        request_sha256=fingerprint(req),
        artifacts={"comparison.json": digest(attempt / "comparison.json")},
        physical_release=False,
    )
    write_new(attempt / "manifest.json", manifest)
    store.finish(job["id"], "completed", None, manifest)
    destination = tmp_path / "review"
    export(store, job["id"], destination)
    receipt = verify_export(destination)
    packed = json.loads((destination / "bill-of-materials.json").read_text())
    assert packed["candidates"] == [bill]
    with (destination / "bill-of-materials.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(source)
    assert {row["physical_id"] for row in rows} == set(source)
    assert all(
        row["quantity"] == "1" and row["installed_kit_complete"] == "false"
        for row in rows
    )
    assert "engineering/design_engine/bom.py" in receipt["package_source_sha256"]
    assert (destination / "sources/engineering/design_engine/bom.py").is_file()


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-register",
        "empty-inventory",
        "missing-model",
        "duplicate",
        "quantity",
        "physical-quantity",
        "part-id",
        "material",
        "revision",
        "mass",
        "cg",
        "inertia",
        "catalogue",
        "unresolved",
        "stale",
        "missing-property",
        "nan",
    ],
)
def test_malformed_or_disagreeing_physical_inventory_cannot_become_empty_or_zero(
    mutation, candidates
):
    candidate = deepcopy(candidates["full-train"])
    definition = candidate["definition"]
    model = definition["model"]
    register = definition["installed_register"]
    row = register["parts"][0]
    if mutation == "missing-register":
        del definition["installed_register"]
    elif mutation == "empty-inventory":
        model["instances"] = []
        register["parts"] = []
    elif mutation == "missing-model":
        del definition["model"]
    elif mutation == "duplicate":
        register["parts"][1]["physical_id"] = row["physical_id"]
    elif mutation == "quantity":
        row["quantity"] = 0
    elif mutation == "physical-quantity":
        model["instances"][0]["quantity"] = 2
    elif mutation == "part-id":
        row["part_id"] = "different-part"
    elif mutation == "material":
        row["material"] = "invented-material"
    elif mutation == "revision":
        row["revision"] = "another-revision"
    elif mutation == "mass":
        row["defined_mass_kg"] = 0
    elif mutation == "cg":
        row["cg_m"] = [1, 2, 3]
    elif mutation == "inertia":
        row["inertia_tensor_kg_m2"] = None
    elif mutation == "catalogue":
        register["catalogue_quantities"] = {}
    elif mutation == "unresolved":
        register["unresolved_allocations"] = []
    elif mutation == "stale":
        register["physical_definition_sha256"] = "wrong"
    elif mutation == "missing-property":
        del model["instances"][0]["properties"]["design"]["mass_kg"]
    elif mutation == "nan":
        model["instances"][0]["properties"]["design"]["mass_kg"] = float("nan")
    if mutation != "stale" and "model" in definition and mutation != "nan":
        register["physical_definition_sha256"] = fingerprint(model)
    with pytest.raises(ValueError):
        candidate_bill(candidate, adapter="vehicle")


def test_explicit_unknown_mass_material_and_properties_stay_unknown(candidates):
    candidate = deepcopy(candidates["full-train"])
    definition = candidate["definition"]
    model = definition["model"]
    row = definition["installed_register"]["parts"][0]
    props = model["instances"][0]["properties"]["design"]
    for key in ("mass_kg", "cg_m", "inertia_tensor_kg_m2"):
        props[key] = None
    row.update(defined_mass_kg=None, cg_m=None, inertia_tensor_kg_m2=None)
    definition["installed_register"]["physical_definition_sha256"] = fingerprint(model)
    bill = candidate_bill(candidate, adapter="vehicle")
    assert bill["defined_mass_kg"] is None
    assert bill["parts"][0]["material"] is None
    assert bill["parts"][0]["defined_mass_kg"] is None
    assert bill["complete_installed_mass_kg"] is None


def test_study_adapter_is_explicitly_nonphysical_and_cannot_mask_missing_vehicle(
    candidates,
):
    candidate = compile_candidate(
        get("civil-campaign"), scope(), {"profile": "reference"}
    )
    bill = candidate_bill(candidate, adapter="civil")
    assert bill["state"] == "not-applicable"
    assert bill["parts"] == []
    assert bill["physical_instance_count"] is None
    assert bill["defined_mass_kg"] is None
    damaged = deepcopy(candidates["full-train"])
    del damaged["definition"]["model"]
    with pytest.raises(ValueError):
        candidate_bill(damaged, adapter="civil")
