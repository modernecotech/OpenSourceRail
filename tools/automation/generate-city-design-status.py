#!/usr/bin/env python3
"""Source-bound city system inventory; available artifacts never imply release.

This is a common reporting/default-workflow adapter, not another CAD authority.
It reads each city's own configuration and generated registers. In particular it
does not transfer Baghdad ground, train loads or research pilots to other cities.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
import gzip
import json
import os
from pathlib import Path
import tempfile
import tomllib
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "osr-city-design-system/1"
DOMAINS = {
    "requirements-site": ("Requirements, alignment and site", ("alignment", "mapping", "survey", "water", "clearance", "access"), "Adopt survey, ownership, utilities, ground, flood, wind and seismic investigations; open maps are screening inputs."),
    "civil": ("Foundations, supports, decks and track", ("civil-works", "connected-build/civil.json", "connected-build/span-layout.json", "detail/slab-reference.svg"), "Complete load combinations, resistance, connections, construction stages and site-specific ground verification."),
    "stations": ("Stations, access and services", ("station-product-map.json", "station-cluster-summary.json", "connected-build/stations.json", "connected-build/station-products.json", "connected-build/ifc", "connected-build/cad", "federation"), "Complete placed structures, egress, accessibility, fire, services and connection acceptance."),
    "mechanical": ("Rolling stock and mechanical assemblies", ("detail",), "Close complete train geometry, bogies, brakes, couplers, doors, fatigue, crash applicability and manufacturing drawings."),
    "electrical": ("Traction, battery and electrical", ("energy", "connected-build/energy.json", "connected-build/battery-envelope-sensitivity.json"), "Freeze exact chemistry, supplier ratings, protection, thermal/fire design, harnesses and measured duty."),
    "thermal-fluid": ("Cooling, HVAC, drainage and fluids", ("connected-build/energy.json", "detail/register.json"), "Qualify whole-car HVAC, cooling and fluids against local environment and measured supplier maps."),
    "software": ("Software, signalling, control and communications", ("detail/register.json", "connected-build/energy-control.json", "simulation"), "Allocate requirements and interfaces to deployed versions; execute fault, integration, SIL/HIL and applicable independent assurance."),
    "factories": ("Factories, tooling and local manufacture", ("factory", "connected-build/industrialisation-programme.json", "connected-build/procurement-evidence.json", "connected-build/suppliers.json", "connected-build/logistics.json"), "Freeze British manufacture case by case, supplier configurations, quotations, process capability, cranes, tooling and factory acceptance."),
    "operations": ("Service, stabling and maintenance", ("sumo", "stabling", "depot-scope", "connected-build/movement-profiles.json"), "Accept timetable, fleet duty, charging, depot capacity, rescue, maintenance and degraded operation."),
    "integration": ("Coupled train, track, structures and energy", ("connected-build", "project-twin"), "Run exact-revision coupled dynamics, loads, power, heat and protocol tests with convergence and adverse controls."),
    "delivery-finance": ("Delivery programme and finance", ("delivery", "finance", "factory", "programme-recalculation/summary.json", "coupled-programme/summary.json"), "Obtain funding commitments, contracts, current quotations, approved calendar, land and programme acceptance."),
    "quality": ("Manufacturing QA and physical acceptance", ("detail/register.json", "civil-works/review-register.json", "connected-build/remaining-work.json"), "Execute serial/revision-specific inspections, calibrated tests, authenticated evidence and independent engineering release."),
}
VISUAL_SUFFIXES = {".png", ".jpg", ".jpeg", ".svg", ".gif", ".mp4", ".webm", ".ifc", ".fcstd", ".step", ".stp"}


def visual(path: Path) -> bool:
    return path.suffix.lower() in VISUAL_SUFFIXES or any(path.name.lower().endswith(ext) for ext in (".step.gz", ".stp.gz", ".ifc.gz"))


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def encoded(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("city artifacts must remain within the repository")
    return resolved.relative_to(root.resolve()).as_posix()


def receipt_status(path: Path, design: Path, root: Path) -> dict:
    """Check declared identities, never infer freshness from an mtime or pass flag."""
    try:
        value = json.loads(path.read_bytes())
    except (ValueError, UnicodeError):
        return {"state": "unreadable", "checked": 0, "mismatches": ["invalid JSON"]}
    if not isinstance(value, dict):
        return {"state": "unbound", "checked": 0, "mismatches": []}
    checked = 0
    mismatches = []
    design_bound = False
    design_name = relative(design, root)
    expected = value.get("design_sha256")
    if expected is not None:
        checked += 1
        design_bound = True
        if expected != digest(design):
            mismatches.append(design_name)
    aliases = value.get("source_paths", {})
    if not isinstance(aliases, dict):
        aliases = {}
    for field in ("sources_sha256", "source_sha256", "inputs_sha256", "input_sha256", "outputs_sha256", "output_sha256", "files_sha256"):
        claims = value.get(field)
        if not isinstance(claims, dict):
            continue
        for name, expected in claims.items():
            if not isinstance(name, str) or not isinstance(expected, str) or len(expected) != 64:
                continue
            actual_name = aliases.get(name, name)
            if not isinstance(actual_name, str):
                mismatches.append(name + " (invalid receipt path alias)")
                continue
            p = Path(actual_name)
            if p.is_absolute() or ".." in p.parts:
                mismatches.append(name + " (unsafe receipt path)")
                continue
            # Existing city receipts use either repository-relative or local paths.
            target, fallback = ((path.parent / p, root / p) if field in {"outputs_sha256", "output_sha256", "files_sha256"} else (root / p, path.parent / p))
            if not target.is_file():
                target = fallback
            if not target.resolve().is_relative_to(root.resolve()):
                mismatches.append(name + " (outside repository)")
                continue
            checked += 1
            if target.resolve() == design.resolve():
                design_bound = True
            if not target.is_file() or digest(target) != expected:
                mismatches.append(name)
    return {"state": "stale" if mismatches else "design-bound" if design_bound else "receipt-consistent" if checked else "unbound",
            "checked": checked, "mismatches": sorted(set(mismatches))}


def research_context(slug: str, selected_families: set[str], root: Path) -> tuple[dict | None, set[Path]]:
    """Link the named Baghdad pilot context without adopting it as a city design.

    Check small sealed metadata and its source snapshot, not the 25 MB portable
    bundle on every city build. Full raw/native integrity remains the assembly
    publication verifier's responsibility and is explicitly linked to its seal.
    """
    if slug != "baghdad":
        return None, set()
    folder = root / "docs/design-engine/assembly-design"
    used = set()
    context = {"state": "unavailable", "prototype_id": None, "epoch": None, "pilots": [],
               "completed_variants": None, "native_exhibits": 0, "source_mismatches": [],
               "engineering_complete": False, "manufacturing_release": False,
               "applicability": "Named Baghdad six-car provisional component research only; route, ground, duty and production acceptance remain open.",
               "verification_scope": "Small manifest-bound metadata and qualified source hashes; full raw evidence and CAD payload checks require the linked assembly publication verifier."}
    names = ("manifest.json", "progress.json", "prototype.json", "qualification.json", "baseline.json.gz")
    missing = [name for name in names if not (folder / name).is_file()]
    if missing:
        context["missing"] = missing
        return context, used
    try:
        for name in names:
            used.add(folder / name)
        manifest = json.loads((folder / "manifest.json").read_bytes())
        sealed = manifest["files_sha256"]
        for name in names[1:]:
            if digest(folder / name) != sealed.get(name):
                raise ValueError("research metadata seal differs: " + name)
        progress = json.loads((folder / "progress.json").read_bytes())
        prototype = json.loads((folder / "prototype.json").read_bytes())
        qualification = json.loads((folder / "qualification.json").read_bytes())
        with gzip.open(folder / "baseline.json.gz", "rb") as stream:
            raw = stream.read(20_000_001)
        if len(raw) > 20_000_000:
            raise ValueError("research baseline exceeds metadata bound")
        baseline = json.loads(raw)
        for record in (manifest, progress, prototype, qualification, baseline):
            if any(record.get(flag) is not False for flag in ("design_complete", "manufacturing_release", "physical_release", "physical_validation")):
                raise ValueError("research release or completeness boundary differs")
        context.update(prototype_id=prototype.get("id"), epoch=manifest.get("epoch"),
                       manifest=relative(folder / "manifest.json", root), index=relative(folder / "index.html", root),
                       qualification=relative(folder / "qualification.json", root))
        if (prototype.get("id") != "BAGHDAD-PROTOTYPE-6C-2026-10-19" or prototype.get("architecture") != "baghdad-six-car"
                or prototype.get("family") != "metro-6car" or selected_families != {"metro-6car"}
                or baseline.get("prototype") != prototype or baseline.get("policy", {}).get("architecture") != prototype["architecture"]):
            context["state"] = "inapplicable-prototype"
            return context, used
        if sha256(encoded(baseline)).hexdigest() != manifest.get("epoch") or progress.get("epoch") != manifest.get("epoch"):
            raise ValueError("research epoch differs")
        if sha256(encoded(progress)).hexdigest() != manifest.get("progress_digest"):
            raise ValueError("research progress seal differs")
        hashes = baseline.get("source_sha256")
        if not hashes or qualification.get("sources") != hashes or progress.get("source_sha256") != hashes:
            raise ValueError("research qualification source identities differ")
        if qualification.get("passed") is not True or qualification.get("returncode") != 0:
            raise ValueError("research qualification did not pass")
        for name, expected in hashes.items():
            p = Path(name)
            if p.is_absolute() or ".." in p.parts or not (root / p).resolve().is_relative_to(root.resolve()):
                raise ValueError("unsafe qualified research source")
            if not (root / p).is_file() or digest(root / p) != expected:
                context["source_mismatches"].append(name)
        context["state"] = "stale-source-context" if context["source_mismatches"] else "source-current-provisional-research"
        context["completed_variants"] = progress.get("counts", {}).get("completed_trials")
        for diagnostic, entries in ((False, progress.get("selected", [])), (True, progress.get("diagnostics", []))):
            for entry in entries:
                kind = entry["kind"]
                if kind not in {"bearing-seat", "structural-bay", "service-cassette"}:
                    raise ValueError("unrecognised research pilot")
                prefix = ("diagnostics/" if diagnostic else "models/") + kind + "/"
                metadata = {}
                for name in ("result.json", "native-result.json"):
                    path = folder / prefix / name
                    used.add(path)
                    if digest(path) != sealed.get(prefix + name):
                        raise ValueError("research pilot metadata seal differs")
                    metadata[name] = json.loads(path.read_bytes())
                native = metadata["native-result.json"]
                result = metadata["result.json"]
                if native.get("child") != entry["key"]:
                    raise ValueError("research native child identity differs")
                if not diagnostic and (result.get("failed_checks") or native.get("state") != "passed"):
                    raise ValueError("failed research exhibit promoted to representative")
                links = {}
                for label, name in (("CAD", "model.FCStd"), ("STEP", "model.step.gz"), ("IFC", "assembly.ifc.gz"),
                                    ("image", "overview.png"), ("BOM", "manufacturing-bom.csv"), ("checks", "result.json"),
                                    ("native", "native-result.json"), ("QA", "qa-plan.json")):
                    full = prefix + name
                    if full in sealed and (folder / full).is_file():
                        links[label] = {"path": relative(folder / full, root), "manifest_sha256": sealed[full]}
                context["pilots"].append({"kind": kind, "candidate": entry["key"], "diagnostic": diagnostic,
                    "state": "excluded-diagnostic" if diagnostic else "held-research-representative",
                    "native_state": native.get("state"), "failed_checks": result.get("failed_checks", []),
                    "held_checks": result.get("held_checks", []), "links": links, "engineering_complete": False})
        context["native_exhibits"] = sum(p["native_state"] == "passed" for p in context["pilots"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        context["state"] = "invalid-research-context"
        context["reason"] = str(error)
    return context, used


def build(design: Path, root: Path = ROOT) -> dict:
    root = root.resolve()
    design = design.resolve()
    relative(design, root)
    value = tomllib.loads(design.read_text())
    city = value.get("city", {})
    slug = city.get("slug")
    if not isinstance(slug, str) or not slug or Path(slug).name != slug or slug in {".", ".."}:
        raise ValueError("a safe city.slug is required")
    engineering = design.parent / "engineering"
    source_paths = {design}
    for candidate in (design.parent / (slug + ".toml"), design.parent / (slug + ".corridor.geojson"), design.parent / "alignment-policy.toml"):
        if candidate.is_file():
            source_paths.add(candidate)
    records = []
    register = engineering / "detail/register.json"
    software = []
    register_freshness = {"state": "missing", "checked": 0, "mismatches": []}
    if register.is_file():
        data = json.loads(register.read_bytes())
        source_paths.add(register)
        register_freshness = receipt_status(register, design, root)
        for part in data.get("parts", []):
            records.append({"id": part["id"], "title": part.get("title"), "group": part.get("group"),
                            "definition": relative(register, root), "definition_sha256": digest(register),
                            "basis": part.get("basis"), "quantity_network_reference": part.get("quantity_network_reference"),
                            "supplier_part_number": part.get("supplier_part_number"),
                            "procurement_route": part.get("procurement_route"),
                            "acceptance_required": part.get("acceptance"), "engineering_complete": False,
                            "state": "stale-reference" if register_freshness["state"] == "stale" else "provisional-reference"})
        software = data.get("software_allocations", [])
    systems = []
    all_artifacts = {}
    for identity, (title, locations, hold) in DOMAINS.items():
        paths = set()
        missing = []
        for location in locations:
            p = engineering / location
            if p.is_dir():
                paths.update(x for x in p.rglob("*") if x.is_file() and (visual(x) or x.name in {"summary.json", "manifest.json", "compact-summary.json", "register.json", "remaining-work.json", "README.md"}))
            elif p.is_file():
                paths.add(p)
            else:
                missing.append("engineering/" + location)
        artifacts = []
        for path in sorted(paths):
            name = relative(path, root)
            source_paths.add(path)
            if name not in all_artifacts:
                entry = {"path": name, "sha256": digest(path), "bytes": path.stat().st_size,
                         "type": "geometry-or-visual" if visual(path) else "report"}
                if path.suffix.lower() == ".json":
                    entry["receipt"] = receipt_status(path, design, root)
                all_artifacts[name] = entry
            artifacts.append(name)
        states = [all_artifacts[p].get("receipt", {}).get("state") for p in artifacts]
        systems.append({"id": identity, "title": title, "state": "stale-evidence" if "stale" in states else "provisional-evidence" if artifacts else "missing-evidence",
                        "artifacts": artifacts, "missing_outputs": missing, "engineering_complete": False,
                        "mandatory_open_gate": hold})
    # All city-specific CAD/images/video files are discoverable, including new
    # adapters whose folder names are not yet in the system map.
    if engineering.is_dir():
        for path in sorted(engineering.rglob("*")):
            if not path.is_file() or not visual(path) or "design-system" in path.relative_to(engineering).parts:
                continue
            name = relative(path, root)
            if name not in all_artifacts:
                source_paths.add(path)
                all_artifacts[name] = {"path": name, "sha256": digest(path), "bytes": path.stat().st_size, "type": "geometry-or-visual"}
    research, research_sources = research_context(slug, {line["rolling_stock"] for line in value.get("lines", []) if "rolling_stock" in line}, root)
    source_paths.update(p for p in research_sources if p.is_file())
    generator = Path(__file__).resolve()
    source_hashes = {relative(p, root): digest(p) for p in sorted(source_paths)}
    return {"schema": SCHEMA, "city": slug, "country": city.get("country"),
            "configuration": {"design": relative(design, root), "design_sha256": digest(design), "bbox": city.get("bbox"),
                              "population": city.get("population"), "climate": value.get("climate", {}),
                              "rolling_stock_families": sorted({line["rolling_stock"] for line in value.get("lines", []) if "rolling_stock" in line}),
                              "line_count": len(value.get("lines", [])), "station_count": len(value.get("stations", [])),
                              "route_length_m": sum(line.get("length_m", 0) for line in value.get("lines", [])),
                              "architecture_policy": "Use this city's own selected families, duty and site inputs. Research geometry from another city is not adopted."},
            "workflow_policy": {"version": 1, "default": True,
                                "sequence": ["bind-city-inputs", "generate-current-alignment", "generate-physical-and-system-packages", "execute-applicable-tests", "verify-exact-source-receipts", "publish-provisional-coverage", "close-independent-acceptance-gates"],
                                "unknown_inputs": "hold; never substitute another city's site or loads",
                                "failed_checks": "exclude exact candidate and invalidate descendants",
                                "external_release": "Requires an appointed authority and authenticated, applicable acceptance evidence."},
            "sources_sha256": source_hashes, "generator_sha256": digest(generator),
            "systems": systems, "parts": records, "software_allocations": software, "external_research": research,
            "part_register_receipt": register_freshness,
            "artifacts": sorted(all_artifacts.values(), key=lambda entry: entry["path"]),
            "counts": {"system_domains": len(systems), "registered_parts": len(records), "software_allocations": len(software),
                       "artifacts": len(all_artifacts), "stale_system_domains": sum(x["state"] == "stale-evidence" for x in systems),
                       "accepted_complete_parts": 0, "accepted_complete_systems": 0},
            "design_complete": False, "engineering_release": False, "manufacturing_release": False, "physical_release": False,
            "scope": "Source-bound inventory and provisional design coverage. A generated file or matching receipt does not establish engineering completion."}


def render(report: dict, output: Path, root: Path = ROOT) -> str:
    def href(name):
        return escape(quote(os.path.relpath(root / name, output), safe="/._-"), quote=True)
    def link(name):
        return '<a href="' + href(name) + '">' + escape(name) + '</a>'
    rows = []
    for system in report["systems"]:
        links = "<br>".join(link(p) for p in system["artifacts"])
        rows.append("<tr><td>" + escape(system["title"]) + "</td><td>" + escape(system["state"]) + "</td><td>" + links + "</td><td>" + escape(system["mandatory_open_gate"]) + "</td></tr>")
    visuals = [a for a in report["artifacts"] if a["type"] == "geometry-or-visual"]
    images = [a for a in visuals if Path(a["path"]).suffix.lower() in {".png", ".jpg", ".jpeg"}]
    priority = ("qgis", "population-access", "network-visualizer", "qa-gates")
    images.sort(key=lambda a: (next((i for i, word in enumerate(priority) if word in a["path"]), len(priority)), a["path"]))
    previews = ''.join('<figure><a href="' + href(a["path"]) + '"><img loading="lazy" src="' + href(a["path"]) + '" alt="' + escape(Path(a["path"]).name, quote=True) + '" style="max-width:100%;max-height:500px"></a><figcaption>' + escape(Path(a["path"]).name) + '</figcaption></figure>' for a in images[:4])
    research_html = ""
    research = report.get("external_research")
    if research:
        research_html = '<h2>Source-bound component research</h2><p>' + escape(research["state"]) + '. ' + escape(research["applicability"]) + '</p>'
        if research.get("index"):
            research_html += '<p>' + link(research["index"]) + ' | ' + link(research["manifest"]) + '</p>'
        research_html += '<p>' + str(research["completed_variants"]) + ' completed variants; ' + str(research["native_exhibits"]) + ' native geometry exhibits. Native correspondence is not engineering acceptance.</p>'
        for pilot in research["pilots"]:
            research_html += '<h3>' + escape(pilot["kind"]) + ' — ' + escape(pilot["state"]) + '</h3><p>' + ' | '.join(link(v["path"]) for v in pilot["links"].values()) + '</p>'
            image = pilot["links"].get("image")
            if image:
                research_html += '<a href="' + href(image["path"]) + '"><img loading="lazy" style="max-width:100%;max-height:450px" src="' + href(image["path"]) + '" alt="' + escape(pilot["kind"], quote=True) + ' provisional research geometry"></a>'
            research_html += '<p>Known failed checks: ' + escape(', '.join(pilot["failed_checks"]) or 'none recorded in this scoped result') + '. Unresolved checks: ' + str(len(pilot["held_checks"])) + '.</p>'
        if research["source_mismatches"]:
            research_html += '<p>Stale source inputs: ' + escape(', '.join(research["source_mismatches"])) + '</p>'
    parts = "".join("<tr><td>" + escape(str(p["id"])) + "</td><td>" + escape(str(p["title"])) + "</td><td>" + escape(p["state"]) + "</td><td>" + escape(str(p["acceptance_required"])) + "</td></tr>" for p in report["parts"])
    counts = report["counts"]
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>' + escape(report["city"]) + ' design system</title>'
            '<style>body{font:16px system-ui;max-width:1400px;margin:2em auto;padding:1em}table{border-collapse:collapse;width:100%}td,th{border:1px solid #aaa;padding:.5em;text-align:left;vertical-align:top}a{overflow-wrap:anywhere}.notice{background:#fff2cc;padding:1em}</style>'
            '<h1>' + escape(report["city"]) + ' — current design system</h1><p class="notice">Provisional design and simulation inventory. Engineering, manufacturing and physical release remain open. No complete railway or manufacturing release is claimed.</p>'
            '<p>' + str(counts["registered_parts"]) + ' registered parts; ' + str(counts["software_allocations"]) + ' software allocations; ' + str(counts["system_domains"]) + ' system domains. ' + str(counts["accepted_complete_systems"]) + ' accepted complete systems.</p>'
            '<p>Configuration: ' + link(report["configuration"]["design"]) + '. <a href="summary.json">Exact hashes and full coverage</a>.</p>'
            '<p>Matching hashes establish source consistency only. Stale receipts require regeneration; unbound evidence requires an applicable receipt. City-specific ground, duty, supplier and physical acceptance gates remain open.</p>'
            + research_html + '<table><tr><th>System</th><th>Evidence state</th><th>Actual outputs</th><th>Next acceptance gate</th></tr>' + ''.join(rows) + '</table>'
            '<h2>Geometry, images and sequence media</h2><p>Presence does not establish motion, collision or physical validation.</p>' + previews + '<ul>' + ''.join('<li>' + link(a["path"]) + '</li>' for a in visuals) + '</ul>'
            '<h2>Authoritative city component register</h2><table><tr><th>ID</th><th>Component</th><th>State</th><th>Required acceptance</th></tr>' + parts + '</table></html>\n')


def generate(design: Path, root: Path = ROOT, *, verify: bool = False) -> dict:
    output = design.resolve().parent / "engineering/design-system"
    report = build(design, root)
    products = {output / "summary.json": encoded(report), output / "index.html": render(report, output, root).encode()}
    for path, content in products.items():
        if verify:
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError("stale city design system: " + str(path))
        else:
            atomic(path, content)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    report = generate(args.design, verify=args.verify)
    print(json.dumps({"city": report["city"], "counts": report["counts"], "engineering_release": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
