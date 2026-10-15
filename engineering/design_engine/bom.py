"""Validated, per-instance quantities from the compiled installed register.

The physical definition supplies correspondence, revisions and coordinate frames;
the installed register supplies quantities. Missing allocations stay separate from
the represented inventory and never acquire an assumed quantity or mass.
"""

from collections import Counter
from copy import deepcopy
import math

from osr_mech.engineering_definition import _transform
from osr_mech.vehicle_mass_properties import inertia_tensor

from .contracts import fingerprint

PROPERTY_UNITS = dict(mass="kg", cg="m", inertia="kg m2")
INERTIA_REFERENCE = "own centre of gravity"
NONPHYSICAL_ADAPTERS = {
    "civil": "study",
    "city-options": "catalogue_entries",
    "engineering-change": "catalogue_entries",
}


def _identifier(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("BOM requires a nonempty " + label)
    return value


def _number(value, label):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError("BOM requires a finite " + label)


def _properties(properties):
    for key in ("mass_kg", "cg_m", "inertia_tensor_kg_m2"):
        if key not in properties:
            raise ValueError("BOM physical properties omit " + key)
    mass = properties["mass_kg"]
    if mass is not None:
        _number(mass, "mass")
        if mass < 0:
            raise ValueError("BOM mass cannot be negative")
    cg = properties["cg_m"]
    if cg is not None:
        if not isinstance(cg, list) or len(cg) != 3:
            raise ValueError("BOM CG must have three coordinates")
        for value in cg:
            _number(value, "CG coordinate")
    tensor = properties["inertia_tensor_kg_m2"]
    if tensor is not None:
        if (
            not isinstance(tensor, list)
            or len(tensor) != 3
            or any(not isinstance(row, list) or len(row) != 3 for row in tensor)
        ):
            raise ValueError("BOM inertia must be a three by three tensor")
        inertia_tensor(tensor, "BOM inertia")


def _frame(model, physical_key, part, row, properties):
    """SI properties follow the controlled schema, about each part's own CG.

    Representation parts already use assembly axes; shared-model instances use
    local axes. Placement is validated but never applied a second time here.
    """
    expected_schema = (
        {"osr-engineering-representations/1", "osr-generated-solid-definition/1"}
        if physical_key == "parts" else {"osr-shared-engineering/1"}
    )
    if model.get("schema") not in expected_schema:
        raise ValueError("BOM requires a controlled SI property/frame schema")
    frame = "assembly" if physical_key == "parts" else "instance-local; placement maps to assembly"
    placement = part.get("placement" if physical_key == "parts" else "transform")
    if placement is not None:
        try:
            _transform(placement)
            import numpy as np

            rotation = np.asarray(placement["rotation"])
            if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-10, rtol=0):
                raise ValueError("placement cannot scale or shear the property axes")
        except (ValueError, TypeError, KeyError) as error:
            raise ValueError("BOM requires a proper SI placement transform") from error
    elif properties["cg_m"] is not None or properties["inertia_tensor_kg_m2"] is not None:
        raise ValueError("BOM known CG/inertia requires an explicit coordinate transform")
    else:
        frame = "instance-local; assembly placement unknown" if physical_key == "instances" else frame
    geometry = part.get("manufacturing", part.get("geometry"))
    if isinstance(geometry, dict) and geometry.get("units", "m") != "m":
        raise ValueError("BOM geometry must use metres")
    for key, expected in (("property_units", PROPERTY_UNITS),
                          ("property_frame", frame), ("inertia_reference", INERTIA_REFERENCE)):
        for declared in (row, properties):
            if key in declared and declared[key] != expected:
                raise ValueError("BOM property units/frame correspondence differs: " + key)
    if "placement" in row and row["placement"] != placement:
        raise ValueError("BOM property units/frame correspondence differs: placement")
    return frame, placement


def review_bill(candidate, *, adapter):
    """Retain explicitly failed compilations without inventing an empty inventory."""
    if (not candidate.get("definition") and candidate.get("error")
            and candidate.get("definition_sha256") is None
            and candidate.get("evidence_state") in {"failed", "outside-domain"}):
        return dict(candidate=_identifier(candidate.get("id"), "candidate ID"),
                    state="not-compiled", basis=candidate["error"], parts=[],
                    physical_instance_count=None, defined_mass_kg=None,
                    complete_installed_mass_kg=None, incomplete_installed_inventory=True,
                    complete_installed_kit=False, unresolved_allocations=None,
                    production_released=False)
    return candidate_bill(candidate, adapter=adapter)


def candidate_bill(candidate, *, adapter):
    """Return checked per-instance inventory, or an explicit nonphysical scope.

    Unknown values remain ``None``. Malformed/missing physical inventories raise;
    they cannot become a successful empty BOM. No installed-kit closure is inferred.
    """
    identifier = _identifier(candidate.get("id"), "candidate ID")
    definition = candidate.get("definition")
    if not isinstance(definition, dict):
        raise ValueError("BOM requires the candidate definition")
    present = [key for key in ("contract", "model") if key in definition]
    if not present:
        key = NONPHYSICAL_ADAPTERS.get(adapter)
        if (
            key is None
            or not isinstance(definition.get(key), (dict, list))
            or not definition[key]
        ):
            raise ValueError("physical candidate has no installed physical definition")
        register = definition.get("installed_register")
        if not isinstance(register, dict) or register.get("parts") != []:
            raise ValueError("nonphysical candidate has an invalid installed register")
        return dict(
            candidate=identifier,
            state="not-applicable",
            basis="adapter supplies a study/catalogue, not a compiled physical assembly",
            parts=[],
            physical_instance_count=None,
            defined_mass_kg=None,
            complete_installed_mass_kg=None,
            incomplete_installed_inventory=True,
            complete_installed_kit=False,
            unresolved_allocations=None,
            production_released=False,
        )
    if len(present) != 1 or not isinstance(definition[present[0]], dict):
        raise ValueError("BOM requires one unambiguous physical definition")
    model = definition[present[0]]
    physical_keys = [key for key in ("parts", "instances") if key in model]
    if len(physical_keys) != 1:
        raise ValueError("BOM requires one explicit physical inventory")
    physical = model[physical_keys[0]]
    if not isinstance(physical, list) or not physical:
        raise ValueError("physical candidate cannot have an empty BOM")
    register = definition.get("installed_register")
    if (
        not isinstance(register, dict)
        or register.get("schema") != "osr-installed-variant-register/1"
    ):
        raise ValueError("BOM requires a supported installed register")
    if register.get("physical_definition_sha256") != fingerprint(model):
        raise ValueError("stale BOM physical definition")
    rows = register.get("parts")
    if not isinstance(rows, list) or len(rows) != len(physical):
        raise ValueError("BOM installed/physical instance counts differ")
    source = {}
    for part in physical:
        if not isinstance(part, dict):
            raise ValueError("malformed BOM physical instance")
        part_id = _identifier(part.get("id"), "physical ID")
        if part_id in source:
            raise ValueError("duplicate BOM physical ID")
        source[part_id] = part
    seen, output = set(), []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("malformed installed BOM row")
        physical_id = _identifier(row.get("physical_id"), "installed physical ID")
        if physical_id not in source or physical_id in seen:
            raise ValueError("BOM physical/installed ID correspondence differs")
        seen.add(physical_id)
        part = source[physical_id]
        part_id = _identifier(part.get("part_id", physical_id), "part ID")
        revision = _identifier(part.get("revision"), "physical revision")
        if (
            row.get("part_id") != part_id
            or "material" not in row
            or row["material"] != part.get("material")
        ):
            raise ValueError("BOM part/material correspondence differs")
        if "revision" in row and row["revision"] != revision:
            raise ValueError("BOM revision correspondence differs")
        if row.get("production_released") is not False:
            raise ValueError("BOM numerical correspondence cannot release production")
        if (
            type(row.get("quantity")) is not int
            or row["quantity"] != 1
            or row.get("unit") != "ea"
        ):
            raise ValueError("BOM must count every physical instance exactly once")
        if physical_keys[0] == "instances" and (
            type(part.get("quantity")) is not int
            or part["quantity"] != 1
            or part.get("unit") != "ea"
        ):
            raise ValueError(
                "physical assembly quantities must identify individual instances"
            )
        properties = part.get("properties")
        if not isinstance(properties, dict):
            raise ValueError("BOM physical instance has no properties")
        if "design" in properties:
            properties = properties["design"]
        if not isinstance(properties, dict):
            raise ValueError("BOM physical instance has no defined design properties")
        _properties(properties)
        frame, placement = _frame(model, physical_keys[0], part, row, properties)
        for installed_key, physical_key in (
            ("defined_mass_kg", "mass_kg"),
            ("cg_m", "cg_m"),
            ("inertia_tensor_kg_m2", "inertia_tensor_kg_m2"),
        ):
            if installed_key not in row or fingerprint(
                row[installed_key]
            ) != fingerprint(properties[physical_key]):
                raise ValueError("BOM mass/CG/inertia correspondence differs")
        geometry = part.get("manufacturing", part.get("geometry"))
        if "manufacturing" not in row or fingerprint(
            row["manufacturing"]
        ) != fingerprint(geometry):
            raise ValueError("BOM manufacturing correspondence differs")
        output.append(
            dict(
                deepcopy(row),
                revision=revision,
                placement=deepcopy(placement),
                property_frame=frame,
                property_units=deepcopy(PROPERTY_UNITS),
                inertia_reference=INERTIA_REFERENCE,
            )
        )
    counts = dict(sorted(Counter(row["part_id"] for row in output).items()))
    if register.get("catalogue_quantities") != counts:
        raise ValueError("BOM catalogue quantities differ from physical instances")
    missing = model.get(
        "unresolved_part_allocations", definition.get("coverage", {}).get("rows", [])
    )
    if (
        not isinstance(missing, list)
        or register.get("unresolved_allocations") != missing
    ):
        raise ValueError("BOM unresolved allocations differ from compiled definition")
    if (
        type(register.get("complete_installed_kit")) is not bool
        or register["complete_installed_kit"]
    ):
        raise ValueError("BOM cannot infer complete installed-kit qualification")
    masses = [row["defined_mass_kg"] for row in output]
    return dict(
        candidate=identifier,
        state="represented-inventory-reconciled",
        physical_definition_sha256=register["physical_definition_sha256"],
        parts=output,
        physical_instance_count=len(output),
        catalogue_quantities=counts,
        defined_mass_kg=(
            math.fsum(masses) if all(value is not None for value in masses) else None
        ),
        complete_installed_mass_kg=None,
        incomplete_installed_inventory=True,
        complete_installed_kit=False,
        unresolved_allocations=deepcopy(missing),
        tooling=deepcopy(register.get("tooling")),
        production_released=False,
        physical_release=False,
    )
