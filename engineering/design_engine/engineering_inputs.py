"""Typed engineering input templates and explicit partial-block boundaries."""

from copy import deepcopy
import json


def qualification_template(kind, contract, scope):
    if kind == "foundation":
        from .foundation_response import input_template

        return input_template(contract, scope)
    from .civil_qualification import input_templates

    if kind in {"site", "prestress"}:
        return input_templates(contract, scope)[kind + "_input"]
    if kind != "manufacturing":
        raise ValueError("supported qualification draft kind required")
    identifier = contract["parts"][0]["id"]
    return dict(
        schema="osr-manufacturing-plan/1",
        part_rules=[
            dict(
                physical_id=identifier,
                stock_bounds_m=[None] * 3,
                minimum_wall_m=None,
                basis_reference=None,
            )
        ],
        tool_envelopes=[
            dict(
                physical_id=identifier,
                bounds_m=[[None] * 3, [None] * 3],
                keepout_part_ids=[],
                basis_reference=None,
            )
        ],
        removal_paths=[
            dict(
                physical_id=identifier,
                bounds_m=[[None] * 3, [None] * 3],
                translation_m=[None] * 3,
                keepout_part_ids=[],
                basis_reference=None,
            )
        ],
        tolerance_stacks=[
            dict(
                physical_id=identifier,
                nominal_clearance_m=None,
                required_clearance_m=None,
                contributors=[dict(physical_id=identifier, plus_minus_m=None)],
                basis_reference=None,
            )
        ],
        tooling=[
            dict(
                id=None,
                kind=None,
                count=None,
                physical_part_ids=[identifier],
                basis_reference=None,
            )
        ],
    )


def draft_structure(value, template, path="input", depth=0):
    """Strict structural fields, finite values and bounded future records."""
    import math

    if depth > 48:
        raise ValueError("qualification draft nesting exceeds limit")
    if value is None:
        return
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite qualification draft value")
    if isinstance(template, dict):
        if not isinstance(value, dict) or set(value) != set(template):
            raise ValueError("exact qualification fields required: " + path)
        for key in value:
            draft_structure(value[key], template[key], path + "." + key, depth + 1)
    elif isinstance(template, list):
        if not isinstance(value, list) or len(value) > 1024:
            raise ValueError("bounded qualification list required: " + path)
        if template:
            exemplar = template[0]
        elif path.endswith(".route_station_constraints"):
            exemplar = dict(
                id=None,
                kind=None,
                source=dict(reference=None, sha256=None, basis=None),
                available=dict(
                    value=None,
                    unit=None,
                    source=dict(reference=None, sha256=None, basis=None),
                ),
                required=dict(
                    value=None,
                    unit=None,
                    source=dict(reference=None, sha256=None, basis=None),
                ),
                uncertainty=dict(
                    value=None,
                    unit=None,
                    source=dict(reference=None, sha256=None, basis=None),
                ),
            )
        elif path.endswith(".observations"):
            exemplar = dict(id=None, description=None, position_m=[None] * 3)
        else:
            exemplar = None
        for index, row in enumerate(value):
            draft_structure(row, exemplar, path + f"[{index}]", depth + 1)
    elif isinstance(value, (dict, list)):
        # Optional prestress losses use the same source-qualified scalar shape.
        if path.endswith((".creep_loss", ".shrinkage_loss", ".relaxation_loss")):
            draft_structure(
                value,
                dict(
                    value=None,
                    unit=None,
                    source=dict(reference=None, sha256=None, basis=None),
                ),
                path,
                depth + 1,
            )
        elif path.endswith(
            (".coverage_bounds_m", ".design_origin_in_crs_m", ".design_axes_in_crs")
        ) and isinstance(value, list):
            for index, row in enumerate(value):
                if isinstance(row, list):
                    for item in row:
                        draft_structure(item, None, path, depth + 1)
                else:
                    draft_structure(row, None, path, depth + 1)
        else:
            raise ValueError("scalar qualification value required: " + path)


def draft_missing(value, path="input"):
    if path.endswith(
        (".identity", ".creep_loss", ".shrinkage_loss", ".relaxation_loss")
    ):
        return []
    if value is None or value == "" or value == []:
        return [path]
    if isinstance(value, dict):
        return [
            p
            for key, row in value.items()
            for p in draft_missing(row, path + "." + key)
        ]
    if isinstance(value, list):
        return [
            p
            for i, row in enumerate(value)
            for p in draft_missing(row, path + f"[{i}]")
        ]
    return []


def effective_input(kind, contract, scope, value):
    """Keep complete entered blocks; blanks never become inferred properties."""
    draft_structure(value, qualification_template(kind, contract, scope))
    if not isinstance(value, dict):
        raise ValueError("structured engineering inputs required")
    output = deepcopy(value)
    if kind == "manufacturing":
        keys = (
            "part_rules",
            "tool_envelopes",
            "removal_paths",
            "tolerance_stacks",
            "tooling",
        )
        for key in keys:
            output[key] = [row for row in (output[key] or []) if not draft_missing(row)]
        present = any(output[key] for key in keys)
    else:
        if output["identity"] != scope:
            raise ValueError("engineering input belongs to another exact scope")
        from .contracts import fingerprint

        if output["contract_sha256"] != fingerprint(contract):
            raise ValueError("engineering input belongs to another physical definition")
        if kind in {"prestress", "foundation"}:
            return None if draft_missing(output) else output
        keys = (
            "survey",
            "layers",
            "groundwater",
            "utilities",
            "calibration",
            "route_station_constraints",
        )
        for key in keys:
            if draft_missing(output[key]):
                output[key] = None
        present = any(output[key] for key in keys)
    return output if present else None


def decode_input(text):
    if not isinstance(text, str) or len(text.encode()) > 4 * 1024**2:
        raise ValueError("bounded manufactured definition JSON text required")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate definition field: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("nonfinite definition value: " + value)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
