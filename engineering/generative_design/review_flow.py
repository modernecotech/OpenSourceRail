"""Compact, source-aware review of configurations, screens and open packages.

This projection contains summaries rather than copied engineering payloads.
Historical integrity and current applicability are distinct visible properties.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from . import architecture_campaign, campaign, queue_campaign, review
from .coverage import ROOT, local, sha

DOCS = ROOT / "docs/design-engine"


def read(path):
    from .evidence_store import read_json

    return read_json(Path(path))


def web_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(DOCS):
        raise ValueError("review evidence must be published under docs/design-engine")
    return "../" + path.relative_to(DOCS).as_posix()


def gate_labels(value):
    if isinstance(value, dict):
        return [
            f'{k}: {v.get("basis",v)}' if isinstance(v, dict) else f"{k}: {v}"
            for k, v in value.items()
        ]
    return [
        (
            f'{v.get("id","qualification")}: {v.get("requirement",v.get("basis",v))}'
            if isinstance(v, dict)
            else str(v)
        )
        for v in value or []
    ]


def failed_checks(value):
    rows = (
        value.items()
        if isinstance(value, dict)
        else [(r.get("id", "unknown-check"), r) for r in value or []]
    )
    return [
        str(name)
        for name, row in rows
        if row.get("status", row.get("state")) == "failed"
    ]


def candidate_row(
    candidate,
    *,
    packet,
    family,
    case,
    source,
    package_ids=(),
    selected=False,
    proposed=False,
):
    failures = failed_checks(candidate.get("checks", {}))
    gates = gate_labels(candidate.get("remaining_gates", []))
    checks = candidate.get("checks", {})
    check_rows = (
        checks.items()
        if isinstance(checks, dict)
        else [(r.get("id", "unknown-check"), r) for r in checks]
    )
    gates = list(
        dict.fromkeys(
            gates
            + [
                f'{name}: {row.get("basis","Qualification not established")}'
                for name, row in check_rows
                if row.get("status", row.get("state")) == "unknown"
            ]
        )
    )
    if any(
        candidate.get(key) is True
        for key in (
            "design_complete",
            "engineering_design_complete",
            "manufacturing_release",
            "physical_release",
        )
    ):
        raise ValueError("provisional review cannot conceal a release claim")
    metrics = candidate.get("metrics", {})
    compatibility = candidate.get("existing_configuration_compatible")
    if selected and proposed or selected and compatibility is False:
        raise ValueError(
            "source-changing proposal cannot be labelled source-compatible selection"
        )
    screen = next(
        (
            candidate[k]
            for k in (
                "conditional_stress_and_geometry_pass",
                "conditional_screen_feasible",
                "conditional_feasible",
            )
            if k in candidate
        ),
        None,
    )
    if screen is True and failures:
        raise ValueError("failed known check cannot be presented as a passing screen")
    return dict(
        id=f'{packet}:{case}:{family}:{candidate["id"]}',
        candidate_id=candidate["id"],
        packet=packet,
        case=case,
        family=family,
        source=source,
        packages=sorted(set(package_ids)),
        variables=candidate.get("variables", {}),
        metrics={
            k: v
            for k, v in metrics.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        },
        screen=(
            "failed"
            if failures or screen is False
            else "local-pass" if screen is True else "unknown"
        ),
        failed_checks=failures,
        unknown_gates=gates,
        selected_local=bool(selected),
        proposed_configuration=bool(proposed),
        source_configuration_compatible=compatibility,
        material_acceptance="unaccepted",
        connection_acceptance="unqualified",
        manufacturing_release=False,
        next_action=(
            "Resolve the source-envelope/configuration change and its dependent interfaces."
            if compatibility is False
            else (
                "Repair failed predicates and rerun the affected configuration."
                if failures
                else "Supply controlled inputs, complete discipline and connection checks, then obtain inspection and independent acceptance."
            )
        ),
    )


def packet_info(identifier, folder, verifier, *, current=False):
    verified = verifier(folder, current=False)
    if not verified.get("integrity_verified"):
        raise ValueError("packet integrity did not verify")
    applicable = False
    if current:
        try:
            applicable = bool(
                verifier(folder, current=True).get("current_sources_checked")
            )
        except ValueError as error:
            if "source revision" not in str(error) and "source" not in str(error):
                raise
    return dict(
        id=identifier,
        label=folder.name,
        source=web_path(folder / "snapshot.json"),
        integrity_verified=True,
        applicability="current-at-generation" if applicable else "historical",
        numerical_recomputation_by_review=False,
        physical_release=False,
    )


def additional_queued_rows(queued, closure):
    """Keep distinct declared rows, including fixed audits and failed schedules."""
    cases = []
    rows = []
    package_by_id = {p["id"]: p for p in closure["packages"]}
    for lane in ("civil", "factory", "integration"):
        report = read(queued / lane / "report.json")
        for package in report["packages"]:
            identity = package["work_package_id"]
            case = f"queued-{identity}"
            source = web_path(queued / lane / "report.json")
            cases.append(
                dict(
                    id=case,
                    packet="queued",
                    architecture=(
                        "metro-6car-planning"
                        if identity == "BASIS-CONFIGURATION"
                        else "package-specific-unadopted"
                    ),
                    label=f'{identity}: {package_by_id[identity]["title"]}',
                    input_status="unaccepted",
                    full_definition=False,
                    source=source,
                    geometry="Package-specific bounded submodels; source basis retained with each investigation",
                    connections="All original package gates remain mandatory; numerical records do not establish complete interfaces",
                )
            )
            for investigation in package["investigations"]:
                entries = []
                for key in ("candidates", "finite_cases", "resource_bounds"):
                    entries.extend(
                        (key, index, entry)
                        for index, entry in enumerate(investigation.get(key, []))
                    )
                for variant in investigation.get("variants", []):
                    entries.extend(
                        (f'variant-{variant.get("archetype","case")}', index, entry)
                        for index, entry in enumerate(variant.get("candidates", []))
                    )
                if not entries:
                    entries = [("fixed-reference", 0, investigation)]
                for collection, index, entry in entries:
                    candidate = dict(entry)
                    candidate.setdefault(
                        "id", f'{investigation["id"]}/{collection}-{index+1}'
                    )
                    candidate.setdefault(
                        "variables",
                        {
                            k: v
                            for k, v in entry.items()
                            if isinstance(v, (str, bool))
                            and k not in {"id", "basis", "method"}
                        },
                    )
                    candidate.setdefault(
                        "metrics",
                        {k: v for k, v in entry.items() if type(v) in (int, float)},
                    )
                    candidate.setdefault("remaining_gates", package["unresolved_gates"])
                    row = candidate_row(
                        candidate,
                        packet="queued",
                        family=investigation["id"],
                        case=case,
                        source=source,
                        package_ids=[identity],
                    )
                    row["record_kind"] = collection
                    row["basis"] = investigation.get(
                        "basis",
                        investigation.get(
                            "method", "See source for declared input/method scope"
                        ),
                    )
                    rows.append(row)
    integrated = read(queued / "integration/report.json")
    for entry in integrated["all_beam_responses"]:
        candidate = dict(
            id=entry["candidate_id"],
            variables=entry["variables"],
            metrics={k: v for k, v in entry.items() if type(v) in (int, float)},
            remaining_gates=integrated["packages"][0]["unresolved_gates"],
            checks={
                "isolated_zero_tension_predicate": dict(
                    status=(
                        "passed" if entry["zero_tension_planning_screen"] else "failed"
                    ),
                    basis="Sampled zero-tension predicate only; complete stress, geometry, resistance and loading qualification remain open",
                )
            },
            physical_release=False,
        )
        candidate["metrics"]["minimum_service_compression_pa"] = entry[
            "minimum_sampled_service_compression_pa"
        ]
        row = candidate_row(
            candidate,
            packet="queued",
            family="six-car-envelope-response",
            case="queued-BASIS-CONFIGURATION",
            source=web_path(queued / "integration/report.json"),
            package_ids=["BASIS-CONFIGURATION"],
        )
        row["record_kind"] = "sampled-stress-response"
        rows.append(row)
    return cases, rows


def build(*, architecture=None):
    packets = []
    cases = []
    rows = []
    classic = DOCS / "generative-campaign"
    queued = DOCS / "queued-systems"
    architecture = Path(architecture or DOCS / "architecture-feedback").resolve()
    packets.append(packet_info("initial", classic, review.verify_snapshot))
    packets.append(
        packet_info(
            "queued",
            queued,
            lambda p, **kw: queue_campaign.verify(p, snapshot=True, **kw),
        )
    )
    packets.append(
        packet_info(
            "architecture",
            architecture,
            lambda p, **kw: architecture_campaign.verify(p, snapshot=True, **kw),
            current=True,
        )
    )
    if architecture != DOCS / "architecture-feedback":
        packets.append(
            packet_info(
                "architecture-history",
                DOCS / "architecture-feedback",
                lambda p, **kw: architecture_campaign.verify(p, snapshot=True, **kw),
            )
        )
    for lane in ("civil", "mechanical"):
        report = read(classic / lane / "search.json")
        case = "legacy-three-car" if lane == "civil" else "connection-fixture"
        cases.append(
            dict(
                id=case,
                packet="initial",
                architecture="LM3" if lane == "civil" else "fixture-only",
                label=(
                    "Retained three-car load diagnostic"
                    if lane == "civil"
                    else "Standalone connection/fixture research"
                ),
                input_status="unaccepted",
                full_definition=False,
                source=web_path(classic / lane / "search.json"),
                geometry=(
                    "Prismatic beam and straight tendons"
                    if lane == "civil"
                    else "Locator/bolt/plate primitives"
                ),
                connections=(
                    "End zones, reinforcement and bearing/lift joints unqualified"
                    if lane == "civil"
                    else "Preload, resistance and complete machine/process integration unqualified"
                ),
            )
        )
        for candidate in report["candidates"]:
            rows.append(
                candidate_row(
                    candidate,
                    packet="initial",
                    family=lane,
                    case=case,
                    source=web_path(classic / lane / "search.json"),
                    selected=candidate["id"] in report["selected_candidate_ids"],
                )
            )
    mechanical = read(queued / "mechanical/report.json")
    families = {}
    for package in mechanical["packages"]:
        for investigation in package["investigations"]:
            entry = families.setdefault(
                investigation["id"], dict(investigation=investigation, packages=[])
            )
            if entry["investigation"] != investigation:
                raise ValueError("reused family has inconsistent definitions")
            entry["packages"].append(package["work_package_id"])
    cases.append(
        dict(
            id="lm3-system-submodels",
            packet="queued",
            architecture="LM3",
            label="LM3 component submodels",
            input_status="unaccepted",
            full_definition=False,
            source=web_path(queued / "mechanical/report.json"),
            geometry="Source product/PDR envelopes and proposed repairs",
            connections="Join, tolerance, retention and manufacturing qualification remain open",
        )
    )
    for family, entry in families.items():
        investigation = entry["investigation"]
        for candidate in investigation["candidates"]:
            rows.append(
                candidate_row(
                    candidate,
                    packet="queued",
                    family=family,
                    case="lm3-system-submodels",
                    source=web_path(queued / "mechanical/report.json"),
                    package_ids=entry["packages"],
                    selected=candidate["id"] in investigation["selected_candidate_ids"],
                    proposed=candidate["id"] in investigation["proposed_candidate_ids"],
                )
            )
    report = read(architecture / "report.json")
    for record in report["cases"]:
        case = record["case"]
        cases.append(
            dict(
                id=case["id"],
                packet="architecture",
                architecture=case["architecture_id"],
                label=case["id"],
                train_mass_kg=case["total_mass_kg"],
                train_length_m=case["train_length_m"],
                axles=len(case["axles"]),
                platform_length_m=record["platform"][
                    "complete_module_platform_length_m"
                ],
                force_sensitivity_multiplier=report["basis"][
                    "force_sensitivity_multiplier"
                ],
                input_status="unaccepted",
                full_definition=False,
                source=web_path(architecture / record["civil_report"]),
                geometry="Explicit proposed train/axle cells, section and straight tendons",
                connections="Body/joint, rail, bearing, end-zone, reinforcement, tooling and foundation acceptance open",
                required_gates=record["required_gates"],
            )
        )
        study = read(architecture / record["civil_report"])
        for candidate in study["candidates"]:
            rows.append(
                candidate_row(
                    candidate,
                    packet="architecture",
                    family="civil",
                    case=case["id"],
                    source=web_path(architecture / record["civil_report"]),
                    selected=candidate["id"] in study["selected_candidate_ids"],
                )
            )
    closure = read(queued / "report.json")
    extra_cases, extra_rows = additional_queued_rows(queued, closure)
    cases.extend(extra_cases)
    rows.extend(extra_rows)
    packages = [
        dict(
            id=p["id"],
            title=p["title"],
            domain=p["domain"],
            owner=p["owner_agent_role"],
            dependencies=p["dependencies"],
            required_gates=p["required_gates"],
            unresolved_gates=p["unresolved_gates"],
            source_products=sorted(
                {i for source in p["authoritative_sources"] for i in source["ids"]}
            ),
            missing_artifacts=len(
                p["manufacturing_evidence"]["missing_or_unissued_artifact_ids"]
            ),
            next_action="Complete the listed controlled inputs, discipline/interface work and actual production/inspection evidence.",
            design_complete=False,
            manufacturing_release=False,
        )
        for p in closure["packages"]
    ]
    if len(packages) != 63 or len({p["id"] for p in packages}) != 63:
        raise ValueError("review must retain exact 63 package identities")
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("duplicate review candidate identity")
    return dict(
        schema="osr-campaign-review/1",
        packets=packets,
        cases=cases,
        candidates=rows,
        packages=packages,
        counts=dict(
            candidates=len(rows),
            packages=len(packages),
            screens=dict(Counter(r["screen"] for r in rows)),
        ),
        manufacturing_audit=closure["manufacturing_evidence_counts"],
        applicability_rule="Current means source applicability was checked when this static review was generated. Reverify after source changes; integrity checks do not recompute physics.",
        counting_rule="Rows include bounded alternatives, fixed-reference audits, resource bounds and sampled responses; they are not counts of completed components or unique physical designs.",
        all_systems_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )


def pack_data(data):
    """Intern repeated geometry/gate definitions and metric field names for UI."""
    result = {k: v for k, v in data.items() if k != "candidates"}
    result["schema"] = "osr-campaign-review-compact/1"
    tables = {
        name: []
        for name in (
            "variables",
            "gates",
            "metric_keys",
            "failures",
            "actions",
            "sources",
        )
    }
    indexes = {name: {} for name in tables}

    def intern(name, value):
        key = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if key not in indexes[name]:
            indexes[name][key] = len(tables[name])
            tables[name].append(value)
        return indexes[name][key]

    result["columns"] = [
        "candidate_id",
        "packet",
        "case",
        "family",
        "screen",
        "selected_local",
        "proposed_configuration",
        "source_configuration_compatible",
        "packages",
        "variables_ref",
        "gates_ref",
        "metric_keys_ref",
        "metric_values",
        "failures_ref",
        "action_ref",
        "source_ref",
        "record_kind",
        "basis",
    ]
    result["records"] = []
    for row in data["candidates"]:
        if (
            row["manufacturing_release"] is not False
            or row["material_acceptance"] != "unaccepted"
            or row["connection_acceptance"] != "unqualified"
        ):
            raise ValueError(
                "compact review defaults must not conceal different acceptance states"
            )
        keys = sorted(row["metrics"])
        values = [
            row["candidate_id"],
            row["packet"],
            row["case"],
            row["family"],
            row["screen"],
            row["selected_local"],
            row["proposed_configuration"],
            row["source_configuration_compatible"],
            row["packages"],
            intern("variables", row["variables"]),
            intern("gates", row["unknown_gates"]),
            intern("metric_keys", keys),
            [row["metrics"][k] for k in keys],
            intern("failures", row["failed_checks"]),
            intern("actions", row["next_action"]),
            intern("sources", row["source"]),
            row.get("record_kind", "bounded-candidate"),
            row.get("basis"),
        ]
        if (
            row["id"]
            != f'{row["packet"]}:{row["case"]}:{row["family"]}:{row["candidate_id"]}'
        ):
            raise ValueError("compact review candidate identity differs")
        result["records"].append(values)
    result["tables"] = tables
    return result


def write(output, *, architecture=None):
    output = Path(output).resolve()
    if not output.is_relative_to(
        DOCS / "campaign-review"
    ) and not output.is_relative_to(ROOT / "build"):
        raise ValueError("review output must be under campaign-review or ignored build")
    result = build(architecture=architecture)
    output.mkdir(parents=True, exist_ok=True)
    (output / "data.json").write_text(
        json.dumps(
            pack_data(result), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        + "\n"
    )
    return result["counts"]
