"""Federate source specifications, executable design variants and the reference twin.

Specification coverage, a calculated design model, and a physically correlated
operating twin are distinct outcomes. Missing design detail stays a named task.
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import csv
import gzip
import hashlib
import html
import io
import json
from pathlib import Path
import platform
import threading

from . import coverage, design_scenario

ROOT = coverage.ROOT
SCHEMA = "osr-federated-design-thread/1"
FLAGS = dict(design_complete=False, manufacturing_release=False,
             physical_release=False, physical_validation=False)
LANES = ("mechanical", "civil", "software-factory")
_BUILD_LOCK = threading.RLock()
OUTPUTS = {
    "specifications.json.gz", "reference-twin.json.gz", "mechanical.json.gz",
    "civil.json.gz", "software-factory.json.gz", "open-requests.json.gz",
    "telemetry-contract.json", "summary.json", "index.html", "components.csv",
    "coupling.json.gz",
}


def runtime_code_sources():
    paths = {Path(__file__), ROOT / "osr", ROOT / "tools/automation/design-digital-thread.py"}
    for relative in ("engineering/generative_design", "engineering/twin_design",
                     "engineering/civil_exploration", "engineering/factory_examples",
                     "engineering/industrialisation", "engineering/assurance",
                     "engineering/design_engine",
                     "design/component-catalogue/src/osr_mech"):
        paths.update((ROOT / relative).rglob("*.py"))
    return {p.relative_to(ROOT).as_posix(): coverage.sha(p) for p in sorted(paths)}


# Python retains imported code even when its file changes. Enforce a fresh
# interpreter after any executable-source edit rather than attaching new hashes
# to an older in-memory implementation.
_IMPORTED_CODE_SOURCES = runtime_code_sources()


def freeze_sources(plan):
    code = runtime_code_sources()
    if code != _IMPORTED_CODE_SOURCES:
        raise ValueError("executable sources changed; start a fresh Python process")
    sources = dict(plan["source_hashes"])
    merge_sources(sources, code)
    # The retained reference supplies dependency names only, never trusted values
    # or old digests. Capture current bytes before executing the new model.
    reference_path = ROOT / "engineering/models/digital-twins/best-practice/reference-twin.json"
    reference = json.loads(reference_path.read_text())
    merge_sources(sources, {reference_path.relative_to(ROOT).as_posix(): coverage.sha(reference_path)})
    for name in reference["review"]["source_sha256"]:
        merge_sources(sources, {name: coverage.sha(coverage.local(name))})
    for relative in ("engineering/generative_design/data", "engineering/twin_design/data",
                     "engineering/factory_examples/data"):
        for path in sorted((ROOT / relative).rglob("*.json")):
            merge_sources(sources, {path.relative_to(ROOT).as_posix(): coverage.sha(path)})
    for name in (
        "design/component-catalogue/catalog/buildable-trainset/supplier-anchors.json",
        "docs/civil/baghdad-qualification.md", "docs/civil/station-construction-method.md",
        "docs/commercial/baghdad-uk-factory-suppliers-2026-10-15.md",
    ):
        merge_sources(sources, {name: coverage.sha(coverage.local(name))})
    return sources


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def _pointer(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def _records(value, pointer=""):
    if isinstance(value, dict):
        if (isinstance(value.get("family"), str)
                and "assemblies" in value and "product_items" in value):
            # The trainset manifest identifies its family by a scalar field,
            # rather than an id member. Preserve the actual complete record.
            yield value["family"], pointer, value
        for key in ("id", "product_id", "type_id", "drawing_id"):
            if isinstance(value.get(key), str):
                yield value[key], pointer, value
        for key, child in value.items():
            yield from _records(child, pointer + "/" + _pointer(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _records(child, pointer + "/" + str(index))


def attributes(value, pointer="", inherited_unit=None):
    """Preserve terminal source fields, including nulls and empty collections.

    These are source attributes, not a claim that each is a fabricated part or
    an accepted design value. Units are inferred only from explicit key suffixes.
    """
    key = pointer.rsplit("/", 1)[-1]
    units = (("_kg_m3", "kg/m3"), ("_n_m2", "N/m2"), ("_n_m", "N/m"),
             ("_mm", "mm"), ("_m", "m"), ("_kg", "kg"), ("_n", "N"),
             ("_w", "W"), ("_v", "V"), ("_s", "s"))
    unit = next((u for suffix, u in units if key.endswith(suffix)), inherited_unit)
    if isinstance(value, (dict, list)) and value:
        children = value.items() if isinstance(value, dict) else enumerate(value)
        for key, child in children:
            yield from attributes(child, pointer + "/" + _pointer(key),
                                  unit if isinstance(value, list) else None)
        return
    yield dict(pointer=pointer or "/", value=value, unit=unit,
               state="unknown" if value is None else "source-record-unaccepted")


def specification_graph(plan=None):
    """Join every exact controlled item to its actual records and release work."""
    plan = plan or design_scenario.plan()
    documents, indices = {}, {}
    for name in plan["source_hashes"]:
        if name.endswith(".json"):
            document = json.loads(coverage.local(name).read_text())
            documents[name] = document
            by_id = {}
            for identity, pointer, record in _records(document):
                by_id.setdefault(identity, {})[pointer] = record
            indices[name] = by_id
    defaults = documents["design/component-catalogue/catalog/buildable-trainset/default-product-specifications.json"]
    default_map = {r["product_id"]: r for r in defaults["defaults"]}
    manufacturing_map = {r["product_id"]: r for r in plan["manufacturing_audit"]["products"]}
    items, packages, links, requests = {}, [], [], []
    for package in plan["work_packages"]:
        package_id = "package:" + package["id"]
        package_row = {key: package[key] for key in (
            "id", "title", "domain", "owner_role", "dependencies",
            "required_gates", "original_completion_predicate", "interfaces",
            "drawing_definitions", "production_artifact_requests",
            "inspection_characteristics", "supplier_configuration_requests",
            "completion_artifacts", "external_actions")}
        package_row["node_id"] = package_id
        packages.append(package_row)
        for component in package["components"]:
            name, identity = component["source"], component["id"]
            item_id = "item:" + digest([name, identity])[:24]
            links.append(dict(parent_id=package_id, child_id=item_id,
                              relation="assigned-controlled-item"))
            if item_id not in items:
                records = [dict(pointer=p, record=r) for p, r in
                           sorted(indices.get(name, {}).get(identity, {}).items())]
                fields = [dict(source_pointer=r["pointer"], **a)
                          for r in records for a in attributes(r["record"])]
                items[item_id] = dict(
                    id=item_id, catalogue_id=identity, title=component["title"],
                    source=name, source_sha256=plan["source_hashes"][name],
                    source_records=records, attributes=fields,
                    candidate_default=default_map.get(identity), package_ids=[],
                    production_definition=manufacturing_map.get(identity),
                    required_detail_sections=[
                        "Function and configuration-specific loads/duty",
                        "Dimensioned geometry, connections and assembly/removal envelopes",
                        "Material, finish and qualified process allowables",
                        "Datum scheme, tolerances and interface allocation",
                        "Manufacturing route, tooling and configured equipment limits",
                        "Inspection characteristics, acceptance limits and traceable results",
                        "Verification, maintenance, spares and exact-revision acceptance"],
                    specification_state="source-definition-partial",
                    detailed_specification_complete=False,
                    **FLAGS)
                if not records:
                    requests.append(dict(id="resolve:" + item_id, item_id=item_id,
                        kind="source-record-resolution", owner_role=package["owner_role"],
                        required=f"Resolve exact record {identity} in {name}; source inventory assignment alone supplies no specification.",
                        state="open"))
            items[item_id]["package_ids"].append(package["id"])
        # Every actual required artifact/inspection remains attached to its item
        # and package. Generic headings do not become completed specifications.
        for kind, rows in (("production-artifact", package["production_artifact_requests"]),
                           ("inspection-result", package["inspection_characteristics"]),
                           ("supplier-configuration", package["supplier_configuration_requests"])):
            for row in rows:
                requests.append(dict(id=f"{package['id']}:{kind}:{row.get('id', row.get('artifact_id', row.get('product_id')))}",
                    package_id=package["id"], kind=kind,
                    owner_role=package["owner_role"], requirement=row, state="open"))
        requests.append(dict(id="detail:" + package["id"], package_id=package["id"],
            kind="complete-design-definition", owner_role=package["owner_role"],
            required=package["completion_artifacts"],
            gates=package["required_gates"], state="open"))
    by_catalogue = {}
    for item in items.values():
        by_catalogue.setdefault(item["catalogue_id"], []).append(item["id"])
    # Exact catalogue assembly children are relationships, never guessed matches.
    for item in items.values():
        for record in item["source_records"]:
            for child in record["record"].get("children", []):
                if isinstance(child, str):
                    for target in by_catalogue.get(child, []):
                        if target != item["id"]:
                            links.append(dict(parent_id=item["id"], child_id=target,
                                              relation="declared-catalogue-child"))
    links = sorted({(r["parent_id"], r["child_id"], r["relation"]): r
                    for r in links}.values(), key=lambda r: (r["parent_id"], r["child_id"], r["relation"]))
    return dict(schema="osr-source-specification-graph/1", packages=packages,
        items=sorted(items.values(), key=lambda r: r["id"]), relationships=links,
        open_requests=requests, source_files=plan["source_hashes"],
        count_semantics="Source attributes are terminal stored values, not manufactured parts; item allocation does not establish completed design coverage.",
        **FLAGS)


def _lane(name):
    from importlib import import_module
    return import_module("engineering.generative_design.twin_" + name.replace("-", "_")).build()


def normalize_lane(packet):
    """Turn variant-local engineering labels into unique physical-study instances."""
    packet = deepcopy(packet)
    for system in packet["systems"]:
        for variant in system["variants"]:
            prefix = f"{packet['domain']}/{system['id']}/{variant['id']}/"
            mapping = {part["id"]: prefix + part["id"] for part in variant["parts"]}
            if len(mapping) != len(variant["parts"]):
                raise ValueError("duplicate local part identity")
            for part in variant["parts"]:
                old_id, parent = part["id"], part.get("parent_id")
                part["local_id"], part["id"] = old_id, mapping[old_id]
                part["parent_id"] = mapping.get(parent, parent)
            if "configuration_id" in variant:
                variant["producer_configuration_id"] = variant["configuration_id"]
            variant["configuration_sha256"] = variant_revision(packet, system, variant)
            variant["configuration_id"] = "variant-" + variant["configuration_sha256"][:24]
    return packet


def variant_revision(packet, system, variant):
    return digest(dict(system_configuration_id=system["configuration_id"],
        parameters=variant["parameters"], parts=variant["parts"],
        source_files=packet["source_files"]))


def merge_sources(target, incoming):
    """A conflicting frozen revision is an error, never last-writer-wins."""
    for name, sha in incoming.items():
        coverage.local(name)
        if name in target and target[name] != sha:
            raise ValueError("conflicting source revisions: " + name)
        target[name] = sha


def _validate_lane(packet):
    if packet.get("schema") != "osr-domain-design-twin/1" or not packet.get("source_files"):
        raise ValueError("source-bound domain twin required")
    system_ids = set()
    for system in packet["systems"]:
        if not system.get("id") or system["id"] in system_ids or not system.get("configuration_id"):
            raise ValueError("unique system and explicit configuration required")
        system_ids.add(system["id"])
        variant_ids = set()
        for variant in system["variants"]:
            if not variant.get("id") or variant["id"] in variant_ids:
                raise ValueError("unique variant IDs required")
            variant_ids.add(variant["id"])
            if not variant.get("configuration_id") or not variant.get("configuration_sha256"):
                raise ValueError("revision-bound variant configuration required")
            if variant["configuration_sha256"] != variant_revision(packet, system, variant):
                raise ValueError("variant configuration hash differs from parameters and parts")
            if variant["configuration_id"] != "variant-" + variant["configuration_sha256"][:24]:
                raise ValueError("variant configuration identity differs from revision")
            if any(variant.get(key, False) is not False for key in FLAGS):
                raise ValueError("variant cannot grant engineering or physical release")
            parts = variant["parts"]
            ids = {p["id"] for p in parts}
            if len(ids) != len(parts):
                raise ValueError("duplicate component instance")
            parents = {}
            for part in parts:
                for key in ("title", "specifications", "material", "manufacturing", "inspection"):
                    if key not in part:
                        raise ValueError("incomplete part definition: " + key)
                parent = part.get("parent_id")
                if parent is not None and parent not in ids | {system["id"], variant["id"]}:
                    raise ValueError("unresolved part parent")
                parents[part["id"]] = parent
            for identity in parents:
                trail, current = set(), identity
                while current in parents:
                    if current in trail:
                        raise ValueError("cyclic assembly")
                    trail.add(current)
                    current = parents[current]
            checks = variant["checks"]
            if not checks or len({c["id"] for c in checks}) != len(checks):
                raise ValueError("unique nonempty variant checks required")
            if any(c.get("state") not in {"pass", "fail", "unknown"} for c in checks):
                raise ValueError("explicit check states required")
    encoded(packet)


def coupled_studies(mechanical):
    """Recalculate affected civil parents for two actual frame generations.

    This is deliberately a gross-mass addition sensitivity with no removal
    credit. Failed mechanical proposals remain diagnostic, never adopted loads.
    """
    from . import civil_detail
    rows = []
    for system in mechanical["systems"]:
        architecture = system["configuration_id"]
        variants = [v for v in system["variants"] if v["id"] in
                    {"connected-seed", "connected-feedback-2"}]
        for original in civil_detail.contexts():
            if original["architecture_id"] != architecture:
                continue
            for variant in variants:
                mass = variant["objectives"]["modeled_plate_and_RHS_mass_kg"]
                cars = 3 if architecture == "LM3" else 6
                context = civil_detail.coupled_context(original, mass * cars)
                variables = civil_detail.seed(context)
                attempts, seen, parent = [], set(), None
                # Three evaluations at most; every successor comes from actual
                # failure feedback. No identical-input retry earns progress.
                for generation in range(3):
                    identity = digest(variables)
                    if identity in seen:
                        break
                    seen.add(identity)
                    assessed = civil_detail.assess(variables, context)
                    attempts.append(dict(id=assessed["id"], parent_id=parent,
                        generation=generation, assessment=assessed))
                    proposals = civil_detail.propose(assessed, context)
                    changed = next((p for p in proposals if digest(p) not in seen), None)
                    if changed is None:
                        break
                    parent, variables = assessed["id"], changed
                rows.append(dict(id="coupling-" + digest([architecture, original["id"], variant["id"]])[:20],
                    architecture_id=architecture, mechanical_system_id=system["id"],
                    mechanical_variant_id=variant["id"],
                    mechanical_configuration_sha256=variant["configuration_sha256"],
                    source_mechanical_has_failed_checks=any(c["state"] == "fail" for c in variant["checks"]),
                    cars=cars, modeled_member_mass_per_car_kg=mass,
                    gross_added_train_mass_kg=mass * cars,
                    removed_mass_kg=None, net_mass_change_kg=None,
                    complete_vehicle_mass_known=False,
                    base_civil_context_id=original["id"], civil_context=context,
                    attempts=attempts, adopted=False,
                    termination="three-evaluation-budget-or-no-new-failure-directed-proposal", **FLAGS))
    return dict(schema="osr-design-thread-parent-coupling/1", records=rows,
        basis="Known member steel added to existing train as an explicit sensitivity; omitted fastener/weld/accessory and removed frame masses are unknown. Proportional axle scaling retains original distribution. One-way static transfer only; no coupled vehicle-structure dynamic convergence.",
        **FLAGS)


def reset_numerical_caches():
    """A new source/input campaign cannot inherit an old context/response cache."""
    from . import architecture_civil, civil, civil_detail, integration
    cleared = []
    for module in (civil, integration, architecture_civil, civil_detail):
        for name, value in vars(module).items():
            reset = getattr(value, "cache_clear", None)
            if callable(reset):
                reset()
                cleared.append(module.__name__ + "." + name)
    return cleared


def build(*, concurrency=3):
    # Clearing shared numerical caches must precede the lane workers, and cannot
    # race another federated campaign in this process. Code edits require a new
    # Python process; data revisions may run as fresh campaigns here.
    with _BUILD_LOCK:
        return _build(concurrency=concurrency)


def _build(*, concurrency):
    if type(concurrency) is not int or not 1 <= concurrency <= 3:
        raise ValueError("concurrency must be 1..3")
    reset_numerical_caches()
    plan = design_scenario.plan()
    frozen_sources = freeze_sources(plan)
    specs = specification_graph(plan)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        packets = [normalize_lane(p) for p in pool.map(_lane, LANES)]
    for packet in packets:
        _validate_lane(packet)
    coupling = coupled_studies(packets[0])
    from engineering.twin_design.compiler import compile_design
    from .digital_thread_telemetry import contract
    reference = compile_design()
    sources = dict(specs["source_files"])
    merge_sources(sources, reference["review"]["source_sha256"])
    for packet in packets:
        merge_sources(sources, packet["source_files"])
    # Bind the full executable lane code as well as its controlled input maps.
    for path in sorted(Path(__file__).parent.glob("*.py")):
        merge_sources(sources, {path.relative_to(ROOT).as_posix(): coverage.sha(path)})
    for relative in ("tools/automation/design-digital-thread.py", "osr"):
        merge_sources(sources, {relative: coverage.sha(coverage.local(relative))})
    for relative, sha in sources.items():
        if relative in frozen_sources and frozen_sources[relative] != sha:
            raise ValueError("source changed during twin execution: " + relative)
        if coverage.sha(coverage.local(relative)) != sha:
            raise ValueError("source changed during twin execution: " + relative)
    # Retain the complete pre-execution dependency fence. Undeclared new
    # dependencies cannot be backdated into it by a post-execution source map.
    missing_frozen = set(sources) - set(frozen_sources)
    if missing_frozen:
        raise ValueError("missing pre-execution source binding: " + ", ".join(sorted(missing_frozen)))
    for name, sha in frozen_sources.items():
        if coverage.sha(coverage.local(name)) != sha:
            raise ValueError("source changed during twin execution: " + name)
    merge_sources(sources, frozen_sources)
    requests = list(specs["open_requests"])
    for packet in packets:
        requests.extend(dict(row, domain=packet["domain"]) for row in packet["open_requests"])
    # Keep lack of physical association distinct from complete digital geometry.
    requests.append(dict(id="physical-correlation", kind="physical-twin-correlation", state="open",
        owner_role="configuration-integrator", required=[
            "Serial-numbered installed asset to model-instance association",
            "Calibrated, revision-bound observations and a declared uncertainty budget",
            "Independent validation over nominal, degraded and adverse conditions",
            "Configuration-specific acceptance by the appointed project authority"]))
    for request in requests:
        request.setdefault("kind", "discipline-detail-or-evidence")
        request.setdefault("state", "open")
        request.setdefault("owner_role", {
            "mechanical": "mechanical-designer", "civil": "civil-designer",
            "software-factory": "manufacturing-and-software-integrator",
        }.get(request.get("domain"), "configuration-integrator"))
        request["request_id"] = "request-" + digest(request)[:24]
    summary = dict(schema=SCHEMA,
        source_qualified_items=len(specs["items"]), work_packages=len(specs["packages"]),
        source_attributes=sum(len(r["attributes"]) for r in specs["items"]),
        source_records_resolved=sum(bool(r["source_records"]) for r in specs["items"]),
        reference_instances=reference["review"]["instance_count"],
        reference_interfaces=reference["review"]["interface_count"],
        remaining_reference_allocations=reference["review"]["remaining_allocations"],
        domain_systems=sum(len(p["systems"]) for p in packets),
        design_variants=sum(len(s["variants"]) for p in packets for s in p["systems"]),
        variant_part_records=sum(len(v["parts"]) for p in packets for s in p["systems"] for v in s["variants"]),
        check_states=dict(Counter(c["state"] for p in packets for s in p["systems"] for v in s["variants"] for c in v["checks"])),
        coupled_parent_sensitivities=len(coupling["records"]),
        coupled_civil_evaluations=sum(len(r["attempts"]) for r in coupling["records"]),
        open_requests=len(requests), completed_specifications=0,
        runtime="Three deterministic numerical lane adapters; specialist AI agents developed and reviewed their source separately.",
        scope="Federated engineering design twin with partial detailed models; physical correlation and full railway specification remain open.",
        **FLAGS)
    result = dict(schema=SCHEMA, source_files=dict(sorted(sources.items())),
        environment=dict(python=platform.python_version(), implementation=platform.python_implementation(),
                         numpy=__import__("numpy").__version__),
        specifications=specs, reference_twin=reference,
        domains={name: packet for name, packet in zip(LANES, packets)},
        coupling=coupling,
        telemetry_contract=contract(reference), open_requests=requests, summary=summary, **FLAGS)
    validate(result)
    return result


def validate(result):
    if result.get("schema") != SCHEMA or any(result.get(k) is not False for k in FLAGS):
        raise ValueError("digital thread cannot authenticate engineering or physical release")
    expected = {(c["source"], c["id"]) for p in design_scenario.plan()["work_packages"] for c in p["components"]}
    rows = result["specifications"]["items"]
    if len({r["id"] for r in rows}) != len(rows) or {(r["source"], r["catalogue_id"]) for r in rows} != expected:
        raise ValueError("exact controlled inventory coverage required")
    if any(r.get("detailed_specification_complete") is not False for r in rows):
        raise ValueError("source record presence cannot complete a specification")
    nodes = {r["node_id"] for r in result["specifications"]["packages"]} | {r["id"] for r in rows}
    for edge in result["specifications"]["relationships"]:
        if edge["parent_id"] not in nodes or edge["child_id"] not in nodes:
            raise ValueError("unresolved specification relationship")
    if set(result["domains"]) != set(LANES):
        raise ValueError("all domain lanes required")
    for packet in result["domains"].values():
        _validate_lane(packet)
    validate_coupling(result)
    part_ids = [part["id"] for p in result["domains"].values() for s in p["systems"]
                for v in s["variants"] for part in v["parts"]]
    if len(part_ids) != len(set(part_ids)):
        raise ValueError("part instances must be unique across all variants")
    request_ids = [r["request_id"] for r in result["open_requests"]]
    if len(request_ids) != len(set(request_ids)):
        raise ValueError("evidence requests require unique controlled identities")
    for key in FLAGS:
        if result["summary"].get(key) is not False:
            raise ValueError("summary cannot grant release")
    encoded(result)
    return True


def validate_coupling(result):
    from . import civil_detail
    mechanical = {s["id"]: s for s in result["domains"]["mechanical"]["systems"]}
    originals = {c["id"]: c for c in civil_detail.contexts()}
    expected = {(s["id"], v["id"], c["id"]) for s in mechanical.values()
        for v in s["variants"] if v["id"] in {"connected-seed", "connected-feedback-2"}
        for c in originals.values() if c["architecture_id"] == s["configuration_id"]}
    records = result["coupling"]["records"]
    actual = [(r["mechanical_system_id"], r["mechanical_variant_id"], r["base_civil_context_id"]) for r in records]
    if len(set(actual)) != len(actual) or set(actual) != expected:
        raise ValueError("complete unique coupling context coverage required")
    for row in records:
        system = mechanical[row["mechanical_system_id"]]
        variant = next(v for v in system["variants"] if v["id"] == row["mechanical_variant_id"])
        mass = variant["objectives"]["modeled_plate_and_RHS_mass_kg"]
        cars = 3 if system["configuration_id"] == "LM3" else 6
        if (row["mechanical_configuration_sha256"] != variant["configuration_sha256"]
                or row["architecture_id"] != system["configuration_id"]
                or row["modeled_member_mass_per_car_kg"] != mass
                or row["cars"] != cars or row["gross_added_train_mass_kg"] != mass * cars
                or row["removed_mass_kg"] is not None or row["net_mass_change_kg"] is not None
                or row["adopted"] is not False):
            raise ValueError("coupling differs from exact mechanical revision and gross mass")
        context = civil_detail.coupled_context(originals[row["base_civil_context_id"]], mass * cars)
        if row["civil_context"] != context:
            raise ValueError("coupling civil context differs from controlled recalculation")
        attempts = row["attempts"]
        if not 1 <= len(attempts) <= 3:
            raise ValueError("bounded nonempty coupling evaluations required")
        seen = set()
        for index, attempt in enumerate(attempts):
            assessed = attempt["assessment"]
            variables = assessed["variables"]
            if (attempt["id"] in seen or attempt["generation"] != index
                    or attempt["id"] != assessed["id"]
                    or attempt["parent_id"] != (attempts[index - 1]["id"] if index else None)):
                raise ValueError("coupling candidate ancestry differs")
            seen.add(attempt["id"])
            if assessed != civil_detail.assess(variables, context):
                raise ValueError("coupling assessment differs from recalculation")
            if index and variables not in civil_detail.propose(attempts[index - 1]["assessment"], context):
                raise ValueError("coupling child does not follow actual failed checks")
            if not index and variables != civil_detail.seed(context):
                raise ValueError("coupling initial variables differ")


def component_csv(result):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["item_id", "catalogue_id", "title", "source", "package_ids", "source_fields", "specification_state"])
    for item in result["specifications"]["items"]:
        # Prevent a supplier-controlled source title becoming a spreadsheet formula.
        def safe(v):
            v = str(v)
            return "'" + v if v.startswith(("=", "+", "-", "@")) else v
        writer.writerow(map(safe, [item["id"], item["catalogue_id"], item["title"], item["source"],
            ";".join(item["package_ids"]), len(item["attributes"]), item["specification_state"]]))
    return stream.getvalue().encode()


def review_html(result):
    rows = []
    for item in result["specifications"]["items"]:
        rows.append(dict(title=item["catalogue_id"] + " · " + item["title"], domain="source specification", data=item))
    for domain, packet in result["domains"].items():
        for system in packet["systems"]:
            rows.append(dict(title=system["title"], domain=domain, data=system))
    for study in result["coupling"]["records"]:
        rows.append(dict(title=study["architecture_id"] + " · " + study["base_civil_context_id"] + " · " + study["mechanical_variant_id"],
                         domain="parent coupling", data=study))
    data = encoded(rows).decode().replace("<", "\\u003c")
    summary = html.escape(json.dumps(result["summary"], indent=2))
    return ('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenSourceRail Baghdad engineering twin</title><style>
body{font:16px system-ui;margin:0;background:#eff4f5;color:#17323b}main{max-width:1200px;margin:auto;padding:28px}
h1{font-size:2rem}aside{background:#fff0cd;padding:16px;border-left:5px solid #a26600}input,select{font:inherit;padding:10px;margin:8px 12px 16px 0;max-width:90%}
details{background:white;margin:8px 0;padding:12px;border-radius:5px}summary{cursor:pointer;font-weight:600}pre{overflow:auto;max-height:65vh;white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}
.tag{font-weight:400;color:#526870}a{color:#005b7b}#count{margin:8px 0}</style><main>
<h1>Baghdad engineering twin and component specifications</h1>
<p>Explore the controlled component records and calculated mechanical, civil, software and factory alternatives. Expand a system to inspect its variants, parts, interfaces and checks.</p>
<aside>Provisional engineering models. Source coverage and passing numerical checks do not establish a complete railway design, issued fabrication specifications or a physically correlated operating twin. Missing values and failed checks remain visible.</aside>
<p><a href="components.csv">Component register</a> · <a href="summary.json">Execution summary</a> · <a href="open-requests.json.gz">Outstanding evidence and detail</a> · <a href="manifest.json">Source and output hashes</a></p>
<details><summary>Coverage and execution counts</summary><pre>''' + summary + '''</pre></details>
<label>Find a component or specification <input id="search" type="search" placeholder="bearing, weld, HVAC, LM3…"></label>
<label>Domain <select id="domain"><option value="">All</option></select></label><p id="count" role="status"></p><section id="results"></section>
<script type="application/json" id="data">''' + data + '''</script><script>
const rows=JSON.parse(document.getElementById('data').textContent),select=document.getElementById('domain');
for(const domain of [...new Set(rows.map(r=>r.domain))]){const o=document.createElement('option');o.value=domain;o.textContent=domain;select.append(o)}
const index=rows.map(r=>({...r,text:JSON.stringify(r.data).toLowerCase()}));
function render(){const q=document.getElementById('search').value.toLowerCase(),d=select.value,filtered=index.filter(r=>(!d||r.domain===d)&&(!q||r.text.includes(q)));const target=document.getElementById('results');target.replaceChildren();document.getElementById('count').textContent=filtered.length+' records';
for(const row of filtered){const detail=document.createElement('details'),summary=document.createElement('summary'),tag=document.createElement('span');summary.textContent=row.title+' ';tag.className='tag';tag.textContent='('+row.domain+')';summary.append(tag);detail.append(summary);detail.addEventListener('toggle',()=>{if(detail.open&&!detail.querySelector('pre')){const pre=document.createElement('pre');pre.textContent=JSON.stringify(row.data,null,2);detail.append(pre)}});target.append(detail)}}
document.getElementById('search').addEventListener('input',render);select.addEventListener('change',render);render();</script></main></html>''').encode()


def _output_bytes(result):
    outputs = {"summary.json": encoded(result["summary"]),
               "telemetry-contract.json": encoded(result["telemetry_contract"]),
               "components.csv": component_csv(result), "index.html": review_html(result)}
    packets = {"specifications": result["specifications"], "reference-twin": result["reference_twin"],
               "open-requests": result["open_requests"], "coupling": result["coupling"], **result["domains"]}
    for name, packet in packets.items():
        outputs[name + ".json.gz"] = gzip.compress(encoded(packet), mtime=0)
    assert set(outputs) == OUTPUTS
    return outputs


def run(output, *, concurrency=3):
    output = Path(output)
    if output.exists():
        raise ValueError("use a fresh digital-thread output directory")
    result = build(concurrency=concurrency)
    output.mkdir(parents=True)
    files = _output_bytes(result)
    for name, data in files.items():
        (output / name).write_bytes(data)
    manifest = dict(schema=SCHEMA, source_files=result["source_files"],
        environment=result["environment"], concurrency=concurrency,
        outputs={name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
        **FLAGS)
    (output / "manifest.json").write_bytes(encoded(manifest))
    return result["summary"]


def verify(output, *, current=True, replay=False):
    output = Path(output)
    manifest = json.loads((output / "manifest.json").read_text())
    if manifest.get("schema") != SCHEMA or set(manifest.get("outputs", {})) != OUTPUTS:
        raise ValueError("exact digital-thread member set required")
    if {p.name for p in output.iterdir()} != OUTPUTS | {"manifest.json"}:
        raise ValueError("unexpected or missing digital-thread member")
    if any(manifest.get(k) is not False for k in FLAGS):
        raise ValueError("manifest cannot grant release")
    for name, sha in manifest["outputs"].items():
        path = output / name
        if path.is_symlink() or not path.is_file() or coverage.sha(path) != sha:
            raise ValueError("changed output: " + name)
    if current:
        for name, sha in manifest["source_files"].items():
            if coverage.sha(coverage.local(name)) != sha:
                raise ValueError("changed source: " + name)
    if replay:
        if not current:
            raise ValueError("historical integrity does not establish current replay")
        result = build(concurrency=manifest["concurrency"])
        if result["environment"] != manifest["environment"]:
            raise ValueError("replay environment differs")
        for name, data in _output_bytes(result).items():
            if (output / name).read_bytes() != data:
                raise ValueError("replayed output differs: " + name)
        if result["source_files"] != manifest["source_files"]:
            raise ValueError("source member set differs")
    summary = json.loads((output / "summary.json").read_text())
    if any(summary.get(k) is not False for k in FLAGS):
        raise ValueError("summary cannot grant release")
    return dict(integrity_verified=True, current_sources_checked=current,
                numerical_replay_verified=replay, summary=summary)
