"""Optional REA observation interchange and bounded plans; never runs REA.

Apache-2.0. Tool metadata is an explicitly dated upstream observation, not an
installed-tool claim. Third-party licenses do not license the analyzed target.
"""
from copy import deepcopy
from pathlib import Path
import json

from . import reference_library as library

UPSTREAM = dict(
    rea=dict(name="REA", repository="https://github.com/morluto/rea", version="6.8.0",
        commit="71f680d7c1aa7a45ba0325fe87b104744b0c105f", spdx="MIT",
        package_sha256="2606aa5fc71de499bbe9e57c9115d2acd0eee69644abe37ff377f5a4b3c7d9f8",
        license_sha256="798f9e4d18e49b30bf2f12696c8ced73dc4e1413da375a333d01281543a1ea8b",
        observed_on="2026-11-04", method="Read upstream README/package/LICENSE and pinned raw bytes; no installation or REA execution"),
    open3d=dict(name="Open3D", version="0.19.0", spdx="MIT",
        repository="https://github.com/isl-org/Open3D", docs="https://www.open3d.org/docs/release/tutorial/geometry/mesh.html",
        license_sha256="e5439bd70250da5f17b3435ff9efb05e96e7f9fdc34248d3355b0026baadaa41"),
    stl2step_blinkingsun=dict(name="BlinkingSun/stl2step", repository="https://github.com/BlinkingSun/stl2step",
        commit="6ffe1e5fbd8c1816efe547b9ad151f4d21c92919", spdx="MIT",
        license_sha256="d95ac4593367c177b1fbb8714d5572a97544b9ac3ee542ddf9ff7131f0c93660",
        dependency_terms="OpenCASCADE LGPL-2.1-with-exception; separate dependency terms apply"),
    stl2step_nickpagz=dict(name="nickpagz/stl2step", repository="https://github.com/nickpagz/stl2step",
        commit="ae32fab1f8d081b125d6ad8727c11bf5a0947fd4", spdx="Apache-2.0",
        method="Source-informed build123d feature-tree workflow; not the similarly named PyPI AGPL project"),
    freecad=dict(name="FreeCAD", repository="https://github.com/FreeCAD/FreeCAD",
        spdx="unknown", license_document="https://github.com/FreeCAD/FreeCAD/blob/main/LICENSE",
        license_observation="Upstream main LICENSE contains LGPL-2.1 text; exact installed distribution and dependency terms require verification",
        version=None, installed_version_verified=False))


def capabilities():
    return dict(upstream=deepcopy(UPSTREAM), automatic_installation=False,
        rea_executed=False, external_tool_execution=False,
        normalized_schema="osr-rea-normalized-observation/1",
        scope="OpenSourceRail normalized interchange, not a claim of native REA export-schema compatibility",
        **library.FLAGS)


def plan_task(target, *, purpose="interface-analysis", cpu_seconds=30,
              memory_mb=512, maximum_artifact_bytes=library.MAX_BYTES):
    """Return a reviewable data plan, with no command strings or execution."""
    target = deepcopy(target)
    library.encoded(target)
    if purpose not in ("interface-analysis", "behavior-fixtures", "geometry-reconstruction"):
        raise ValueError("Supported bounded reference task required")
    if (type(cpu_seconds) is not int or not 1 <= cpu_seconds <= 60
            or type(memory_mb) is not int or not 64 <= memory_mb <= 1024
            or type(maximum_artifact_bytes) is not int or not 1 <= maximum_artifact_bytes <= library.MAX_BYTES):
        raise ValueError("Bounded reference-task resources required")
    origin = target.get("origin", {})
    if not origin.get("uri") or not library.SHA.fullmatch(str(origin.get("artifact_sha256", ""))):
        raise ValueError("Exact target artifact required")
    auth = target.get("rights", {}).get("authorization", {})
    permitted = target.get("rights", {}).get("permitted_use")
    authorized = auth.get("status") == "authorized" and auth.get("basis") and "analysis" in auth.get("scope", [])
    allowed = bool(authorized and permitted not in (None, "unknown", "prohibited"))
    source_first = target.get("source_available") is True
    mode = ("source-first" if source_first else "mesh-inspection" if purpose == "geometry-reconstruction" else "optional-rea-observation")
    value = dict(schema="osr-outline-reference-task/1", target=target, purpose=purpose,
        state="ready-for-authorized-local-analysis" if allowed else "authorization-or-permitted-use-required",
        method=mode, budget=dict(cpu_seconds=cpu_seconds, memory_mb=memory_mb,
            maximum_artifact_bytes=maximum_artifact_bytes, maximum_targets=1),
        required_artifacts=["Exact input digest and units/schema", "Observed behavior or mesh-quality report",
            "Uncertainty, failed cases, source versions and derived-pattern tests"],
        tool_requirements=[] if source_first else ["Explicit installed tool/version/binary digest and applicable licenses"],
        commands=[], automatic_execution=False, source_first_preferred=True,
        operating_plant_access=False, external_messages_sent=False, rea_executed=False,
        authorization_verification="declaration-only; no OS sandbox or independent legal review implied",
        **library.FLAGS)
    value["task_id"] = library.identity(value)
    return value


def import_rea(observation, *, root=None, artifact_bytes=None, rights_declaration=None):
    """Import only our bounded normalized envelope; do not invent tool execution."""
    if isinstance(observation, (str, bytes)):
        if len(observation) > library.MAX_BYTES:
            raise ValueError("Bounded normalized observation required")
        observation = json.loads(observation)
    value = deepcopy(observation); library.encoded(value)
    if not isinstance(value, dict):
        raise ValueError("Normalized observation object required")
    if value.get("schema") != "osr-rea-normalized-observation/1":
        raise ValueError("Normalize upstream output explicitly before importing")
    if any(value.get(k, False) is not False for k in library.FLAGS):
        raise ValueError("REA observations cannot establish physical qualification")
    tool = value.get("tool", {})
    if tool.get("name") != "REA" or not isinstance(tool.get("version"), str) or not tool["version"]:
        raise ValueError("Declared upstream tool name/version required")
    evidence = value.get("observations", [])
    if any(row.get("kind") == "physical-measurement" for row in evidence):
        raise ValueError("Software REA observations are not physical measurements")
    fixtures = [dict(row, method="imported-observation", rea_executed=False)
                for row in value.get("behavior_fixtures", [])]
    origin = deepcopy(value["origin"])
    origin["upstream_origin"] = deepcopy(value["origin"])
    origin["upstream_rights"] = deepcopy(value["rights"])
    origin["source_kind"] = "reported-observation"
    origin["source_class"] = "C"
    origin["upstream_tool"] = tool
    origin["normalized_report_sha256"] = library.identity(value)
    origin["upstream_execution_reported"] = value.get("upstream_execution_reported", False)
    # A tool report cannot authorize itself. A separate caller declaration is
    # required before any implementation reuse; retain the original claims.
    rights = (dict(spdx="unknown", permitted_use="unknown", authorization=dict(status="unknown", scope=[]))
              if rights_declaration is None else deepcopy(rights_declaration))
    return library.make_record(value.get("kind", "functional-patterns"), name=value["name"],
        origin=origin, rights=rights, evidence=evidence,
        interfaces=value.get("interface_contracts", []), behavior_fixtures=fixtures,
        geometry_candidates=value.get("geometry_candidates", []), material_candidates=value.get("material_candidates", []),
        process_candidates=value.get("process_candidates", []),
        related_record_ids=value.get("related_record_ids", []),
        unresolved_tasks=value.get("unresolved_tasks", []) + ["Independent behavior replay and any physical validation remain separate"],
        artifact_bytes=artifact_bytes, root=root)


def geometry_recipe(record, *, tool="open3d"):
    record = library.validate_record(record)
    if tool not in ("open3d", "stl2step_blinkingsun", "stl2step_nickpagz", "freecad"):
        raise ValueError("Explicit geometry-tool identity required")
    operations = dict(open3d=["Inspect triangle/point-cloud geometry", "Check manifold, orientation and self-intersection", "Measure distances and volume only within the declared domain"],
        stl2step_blinkingsun=["Pin exact engine and OCCT dependencies", "Declare input STL units", "Retain RESULT, topology/volume checks and faceted fallback disposition"],
        stl2step_nickpagz=["Pin exact source and build123d dependencies", "Produce editable feature recipe", "Retain dimensions, volume, opening and feature verification"],
        freecad=["Pin existing FreeCAD version and source input", "Build or reopen explicit solids", "Reopen STEP and compare geometry, units and quantities"])
    value = dict(schema="osr-outline-geometry-recipe/1", reference_record_id=record["record_id"], tool=deepcopy(UPSTREAM[tool]),
        state="planning-only", operations=operations[tool], commands=[], installation_performed=False,
        implementation_reuse_allowed=record["implementation_reuse_allowed"],
        execution_performed=False, input_units_required=True,
        required_checks=["Input hash and units", "Watertight/manifold/orientation/self-intersection disposition",
            "Dimensions, volume, tolerances, retained openings and independent CAD reopening",
            "Materials, joints, manufacture and physical verification remain separate"],
        freeform_or_organic_recovery_proven=False, **library.FLAGS)
    value["recipe_id"] = library.identity(value)
    return value
