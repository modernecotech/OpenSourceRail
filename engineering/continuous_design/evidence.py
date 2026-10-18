"""Explicit evidence levels; integrity is separate from rerunning any physics."""
import math

LEVELS = ("analytical_screening", "native_geometry", "numerical_confirmation",
          "numerical_robustness", "physical_correlation")


def label(kind, result):
    if "verification" in result:
        return result
    levels = {level: dict(state="not_run", checks=[]) for level in LEVELS}
    keys = list(result.get("checks", {}))
    if kind in ("mechanical-detail", "civil-detail", "integration-coupling"):
        level = "analytical_screening"
    elif kind in ("mechanical-interface", "civil-bay"):
        level = "native_geometry"
    elif kind in ("mechanical-cleat", "civil-steel-beam"):
        level = "numerical_robustness"
        for lower in LEVELS[:3]:
            levels[lower] = dict(state="passed" if result["study_pass"] else "partial", checks=keys,
                scope=result.get("scope"))
    elif kind.startswith("software-"):
        level = "executable_verification"
    else:
        level = "source_artifact_integrity"
    levels[level] = dict(state="passed" if result["study_pass"] else "failed", checks=keys, scope=result.get("scope"))
    result["verification"] = dict(evaluated_level=level, levels=levels,
        scope=result.get("scope"), independent_physics_rerun=False)
    return result


def margins(checks):
    values = []
    for check in checks:
        value, limit = check.get("value"), check.get("limit")
        if (check.get("state") not in {"pass", "fail"} or type(value) not in (int, float)
                or type(limit) not in (int, float) or not math.isfinite(value) or not math.isfinite(limit) or limit == 0):
            continue
        distance = abs(limit - value) / max(abs(limit), abs(value), 1e-30)
        values.append(dict(id=check["id"], signed_normalised_distance=distance if check["state"] == "pass" else -distance,
            value=value, limit=limit, units=check.get("units"), accepted_basis=False))
    return sorted(values, key=lambda row: row["signed_normalised_distance"])
