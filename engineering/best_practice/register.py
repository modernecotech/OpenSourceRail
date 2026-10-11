"""Deterministic research coverage, source provenance and open verification plans.

The checker assesses document completeness, never engineering conformity.
Network discovery is a reviewed authoring activity, not an unattended CI input.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import tomllib
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DATA = Path("engineering/best_practice/data")
FIELDS = ("design", "materials", "assembly", "inspection", "maintenance",
          "verification", "open_questions")
SOURCE_KINDS = {"standard-scope", "regulatory-scope", "manufacturer-practice", "method"}
# OSR research refresh policies in calendar days, not ISO requirements.
REFRESH_DAYS = {"regulatory-scope": 90, "manufacturer-practice": 180,
                "standard-scope": 365, "method": 730}
OUTPUTS = {
    "coverage.json": Path("engineering/best_practice/coverage.json"),
    "component-guidance.csv": Path("engineering/best_practice/component-guidance.csv"),
    "verification-plan.json": Path("engineering/best_practice/verification-plan.json"),
    "handbook.md": Path("docs/best-practice/handbook.md"),
}


def contained(root: Path, relative: str | Path) -> Path:
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"source path must be repository relative: {relative}")
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"source path escapes repository: {relative}")
    return target


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(root: Path, relative: str | Path):
    return json.loads(contained(root, relative).read_text(), object_pairs_hook=_unique_pairs)


def text_list(value, label):
    if not isinstance(value, list) or not value or any(
        not isinstance(s, str) or not s.strip() for s in value
    ) or len(set(value)) != len(value):
        raise ValueError(f"{label} requires unique nonempty text entries")


def keyed(rows, label):
    result = {}
    for row in rows:
        identifier = row.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in result:
            raise ValueError(f"duplicate/invalid {label} ID: {identifier}")
        result[identifier] = row
    return result


def inventory(root: Path, scope: dict) -> list[dict]:
    """Read definitions, including optional zero-quantity train items and variants."""
    items = []
    train = load(root, scope["catalogue_paths"]["train"])
    for collection, kind in (("product_items", "train-product"), ("assemblies", "train-assembly")):
        for row in train[collection]:
            items.append(dict(id=row["id"], kind=kind, title=row["title"],
                              definition_status=row["maturity"],
                              applicability=[dict(family=train["family"],
                                  quantity=row["quantity_per_trainset"],
                                  unit=row.get("unit", "assembly"))],
                              source=scope["catalogue_paths"]["train"]))
    civil = load(root, scope["catalogue_paths"]["civil"])
    for row in civil["type_register"]:
        items.append(dict(id=row["type_id"], kind="civil-type", title=row["disposition"],
                          definition_status=row["status"], asset_class=row["asset_class"],
                          applicability=[dict(package=row["package_id"],
                                              occurrences=row["occurrence_count"])],
                          source=scope["catalogue_paths"]["civil"]))
    station = load(root, scope["catalogue_paths"]["station"])
    station_rows = {}
    seen_variants = set()
    for variant in station["variants"]:
        name = variant["archetype"]
        if name in seen_variants:
            raise ValueError(f"duplicate station variant: {name}")
        seen_variants.add(name)
        items.append(dict(id="station:" + name, kind="station-system", title=name,
                          definition_status=station["assumption_status"],
                          applicability=[dict(variant=name, consist=variant["consist"])],
                          source=scope["catalogue_paths"]["station"]))
        for collection, kind in (("product_items", "station-product"), ("assemblies", "station-assembly")):
            local = set()
            for row in variant[collection]:
                identifier = row["id"]
                if identifier in local:
                    raise ValueError(f"duplicate station definition: {name}/{identifier}")
                local.add(identifier)
                entry = station_rows.setdefault(identifier, dict(id=identifier, kind=kind,
                    title=row["title"], definition_status="variant-specific-reference-definition",
                    applicability=[], source=scope["catalogue_paths"]["station"]))
                if entry["kind"] != kind:
                    raise ValueError(f"station ID reused across product/assembly: {identifier}")
                entry["applicability"].append(dict(variant=name, title=row["title"],
                    quantity=row.get("quantity_per_station", row.get("quantity")), unit=row.get("unit")))
    items.extend(station_rows.values())
    workspace = tomllib.loads(contained(root, scope["workspace_path"]).read_text())
    for member in workspace["workspace"]["members"]:
        path = Path(member) / "Cargo.toml"
        package = tomllib.loads(contained(root, path).read_text())["package"]
        items.append(dict(id="software:" + package["name"], kind="software-package",
                          title=package.get("description", package["name"]),
                          definition_status="software-source-target-labels-are-not-achieved-integrity",
                          applicability=[dict(member=member)], source=str(path)))
    keyed(items, "catalogue")
    template_names = {p.name for p in (root / "lib/templates").iterdir()
                      if p.suffix in (".toml", ".json")}
    included = scope["template_assignments"]
    excluded = scope["template_exclusions"]
    if set(included) & set(excluded):
        raise ValueError("template is both included and excluded")
    missing = template_names - set(included) - set(excluded)
    stale = (set(included) | set(excluded)) - template_names
    if missing or stale:
        raise ValueError(f"template scope drift: unclassified={sorted(missing)}, missing files={sorted(stale)}")
    if any(not isinstance(reason, str) or not reason.strip() for reason in excluded.values()):
        raise ValueError("template exclusions require an explicit reason")
    for name in sorted(included):
        items.append(dict(id="template:" + name, kind="subsystem-template", title=name,
                          definition_status="planning-template-project-applicability-open",
                          applicability=[], source="lib/templates/" + name))
    return sorted(items, key=lambda row: row["id"])


def validate(sources_document, practices_document, scope, items, as_of: date):
    if sources_document.get("schema") != "osr-best-practice-sources/1":
        raise ValueError("unknown source schema")
    if sources_document.get("third_party_designs_redistributed") is not False:
        raise ValueError("source register must not claim redistribution authority")
    if practices_document.get("schema") != "osr-best-practices/1" or scope.get("schema") != "osr-best-practice-scope/1":
        raise ValueError("unknown practice/scope schema")
    for flag in ("engineering_accepted", "physical_validation"):
        if practices_document.get(flag) is not False:
            raise ValueError(f"research register cannot establish {flag}")
    sources = keyed(sources_document["sources"], "source")
    practices = keyed(practices_document["practices"], "practice")
    common = practices_document["common_practices"]
    text_list(common, "common practices")
    if not set(common) <= set(practices):
        raise ValueError("unknown common practice")
    refresh = []
    for identifier, source in sources.items():
        for field in ("publisher", "title", "finding", "limitation"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError(f"source {identifier} missing {field}")
        url = urlsplit(source["url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError(f"source {identifier} requires a public HTTPS reference")
        if source["kind"] not in SOURCE_KINDS:
            raise ValueError(f"unknown source kind: {identifier}")
        if source.get("full_clause_review") is not False:
            raise ValueError(f"public-scope register cannot assert full clause review: {identifier}")
        reviewed = date.fromisoformat(source["reviewed_on"])
        if reviewed > as_of:
            raise ValueError(f"source review after assessment date: {identifier}")
        age = (as_of - reviewed).days
        if age > REFRESH_DAYS[source["kind"]]:
            refresh.append(dict(source_id=identifier, age_days=age,
                                policy_days=REFRESH_DAYS[source["kind"]]))
    for identifier, practice in practices.items():
        for field in ("title", "domain", "owner_role"):
            if not isinstance(practice.get(field), str) or not practice[field].strip():
                raise ValueError(f"practice {identifier} missing {field}")
        if practice.get("status") != "recommended-practice-project-adoption-open":
            raise ValueError(f"practice status implies unsupported acceptance: {identifier}")
        for field in (*FIELDS, "source_ids"):
            text_list(practice.get(field), f"practice {identifier}/{field}")
        if not set(practice["source_ids"]) <= set(sources):
            raise ValueError(f"unknown source in practice: {identifier}")
    by_item = keyed(items, "inventory")
    assignments = dict(scope["assignments"])
    assignments.update({"template:" + name: ids for name, ids in scope["template_assignments"].items()})
    assignments.update({"software:" + name: ids for name, ids in scope["software_assignments"].items()})
    if set(by_item) != set(assignments):
        raise ValueError(f"catalogue coverage drift: unmapped={sorted(set(by_item)-set(assignments))}, "
                         f"stale mappings={sorted(set(assignments)-set(by_item))}")
    used = set(common)
    for identifier, ids in assignments.items():
        text_list(ids, f"assignment {identifier}")
        if not set(ids) <= set(practices):
            raise ValueError(f"unknown practice assigned to {identifier}")
        if not set(ids) - set(common):
            raise ValueError(f"specialist practice missing for {identifier}")
        used.update(ids)
    if used != set(practices):
        raise ValueError(f"unallocated practices: {sorted(set(practices)-used)}")
    future = keyed(scope["future_scopes"], "future scope")
    for row in future.values():
        text_list(row["source_ids"], f"future scope {row['id']}")
        if not set(row["source_ids"]) <= set(sources) or not row.get("reason") or "open" not in row.get("status", ""):
            raise ValueError(f"invalid future scope: {row['id']}")
    return sources, practices, assignments, refresh


def assurance_links(root: Path, practices: dict) -> dict:
    links = load(root, DATA / "assurance-links.json")
    if links.get("schema") != "osr-best-practice-assurance-links/1":
        raise ValueError("unknown assurance link schema")
    authority = tomllib.loads(contained(root, links["authority_path"]).read_text())
    controls = keyed(authority["controls"], "standards control")
    if set(links["practice_control_ids"]) != set(practices):
        raise ValueError("practice-to-assurance coverage drift")
    for identifier, ids in links["practice_control_ids"].items():
        text_list(ids, "assurance links for " + identifier)
        if not set(ids) <= set(controls):
            raise ValueError("unknown existing assurance control for " + identifier)
    return links


def source_hashes(root: Path, scope: dict, items: list[dict], links: dict):
    paths = set(scope["catalogue_paths"].values())
    paths.update("lib/templates/" + name for name in (*scope["template_assignments"], *scope["template_exclusions"]))
    paths.update(str(p.relative_to(root)) for p in (root / DATA).glob("*.json"))
    paths.update(str(p.relative_to(root)) for p in (root / "engineering/best_practice").glob("*.py"))
    paths.update(("tools/automation/best-practice.py", "docs/standards/OSR-BP-001.md",
                  "docs/best-practice/research-plan.md", "docs/standards/OSR-ENG-001.md",
                  "docs/standards/OSR-ENG-002.md", "docs/standards/OSR-MFG-001.md"))
    paths.update(item["source"] for item in items)
    paths.update((scope["workspace_path"], links["authority_path"]))
    return {name: hashlib.sha256(contained(root, name).read_bytes()).hexdigest() for name in sorted(paths)}


def canonical(value) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def build(root: Path = ROOT, as_of: date = date(2026, 10, 11)) -> dict[str, str]:
    sources_document = load(root, DATA / "sources.json")
    practices_document = load(root, DATA / "practices.json")
    scope = load(root, DATA / "scope.json")
    items = inventory(root, scope)
    sources, practices, assignments, refresh = validate(sources_document, practices_document, scope, items, as_of)
    links = assurance_links(root, practices)
    counts = dict(sorted(Counter(item["kind"] for item in items).items()))
    common = practices_document["common_practices"]
    station_variants = sorted({a["variant"] for item in items if item["kind"].startswith("station-")
                               for a in item["applicability"]})
    coverage = dict(schema="osr-best-practice-coverage/1", assessed_on=as_of.isoformat(),
        scope=scope["boundary"], inventory_count=len(items), inventory_by_kind=counts,
        mapped_count=len(assignments), unmapped_ids=[], practice_count=len(practices), source_count=len(sources),
        station_variants=station_variants, template_exclusions=scope["template_exclusions"],
        source_refresh_required=refresh, source_sha256=source_hashes(root, scope, items, links),
        assurance_control_authority=links["authority_path"],
        practice_control_ids=links["practice_control_ids"],
        documentation_coverage_complete=True, research_refresh_current=not refresh,
        engineering_accepted=False, production_released=False, physical_validation=False,
        all_possible_rail_components_covered=False, future_scopes=scope["future_scopes"])
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["id", "kind", "title", "definition_status", "source",
        "applicability_json", "specialist_practices", "common_practices", "source_ids", "assurance_control_ids", "evidence_status"])
    writer.writeheader()
    for item in items:
        ids = list(dict.fromkeys(common + assignments[item["id"]]))
        refs = sorted({ref for identifier in ids for ref in practices[identifier]["source_ids"]})
        writer.writerow({k: item[k] for k in ("id", "kind", "title", "definition_status", "source")} | dict(
            applicability_json=json.dumps(item["applicability"], ensure_ascii=False, separators=(",", ":")),
            specialist_practices=";".join(assignments[item["id"]]), common_practices=";".join(common),
            source_ids=";".join(refs),
            assurance_control_ids=";".join(sorted({control for identifier in ids
                for control in links["practice_control_ids"][identifier]})),
            evidence_status="project-adoption-and-physical-evidence-open"))
    # Refer to each card's verification tasks once; avoid duplicating identical prose per part.
    plan = dict(schema="osr-best-practice-verification-plan/1", assessed_on=as_of.isoformat(),
        interpretation="Unperformed planning tasks, not test results or accepted requirements. Resolve applicability, "
            "complete clauses, limits, configuration, procedures and authority before execution.",
        task_definitions=[dict(id=identifier + "/V" + str(index), practice_id=identifier,
            owner_role=practice["owner_role"], task=task,
            assurance_control_ids=links["practice_control_ids"][identifier], acceptance_criteria=None,
            adopted_standard_clauses=[], procedure=None, result=None, evidence=[], status="open-unperformed")
            for identifier, practice in practices.items() for index, task in enumerate(practice["verification"], 1)],
        allocations=[dict(item_id=item["id"], specialist_practices=assignments[item["id"]],
            common_practices=common, project_configuration=None, adoption_status="open",
            variant_applicability=item["applicability"]) for item in items],
        research_backlog=[dict(practice_id=identifier, owner_role=p["owner_role"],
            questions=p["open_questions"], status="open") for identifier, p in practices.items()],
        future_scopes=scope["future_scopes"], engineering_accepted=False, physical_validation=False)
    lines = ["# OpenSourceRail best-practice handbook", "",
        f"Research baseline {as_of.isoformat()} · generated from the reviewed open register.", "",
        f"{len(practices)} practice cards, {len(sources)} primary references and {len(items)} explicitly mapped definitions. "
        "Coverage means guidance exists for the scoped inventory. Project adoption, production release and physical qualification remain open.", "",
        "The design, materials, assembly, inspection and maintenance guidance below is original OSR synthesis. "
        "References support the method or application context; public standard scopes and supplier examples do not establish clause conformity or product performance.", "",
        "Use [OSR-BP-001](../standards/OSR-BP-001.md) and the [research plan](research-plan.md). "
        "The [component mapping](../../engineering/best_practice/component-guidance.csv), "
        "[coverage audit](../../engineering/best_practice/coverage.json) and "
        "[open verification plan](../../engineering/best_practice/verification-plan.json) are generated together.", "",
        "## Scope and coverage", "", "| Definition kind | Mapped |", "|---|---:|"]
    lines += [f"| {kind} | {count} |" for kind, count in counts.items()]
    lines += ["", "Station variants: " + ", ".join(station_variants) + ".", "",
        "Optional zero-quantity train products are retained as configuration alternatives; "
        "they are not counted as installed. Civil coordination envelopes retain their interface status. "
        "Station applicability records preserve titles and quantities across variants. "
        "A kit mapping does not decompose its individual bolts, terminals, seals or consumables. "
        "Software source titles may contain SIL/GoA targets; they are not achieved integrity claims. "
        "Common lifecycle cards require applicability review; physical material/tool checks do not automatically apply to pure software.", "",
        "## Practice index", "", "| Practice | Domain | Responsible role |", "|---|---|---|"]
    lines += [f"| [{p['title']}](#{p['id']}) | {p['domain']} | {p['owner_role']} |" for p in practices.values()]
    for identifier, p in practices.items():
        mapped = sum(identifier in assignments[item["id"]] or identifier in common for item in items)
        refs = ", ".join(f"[{sources[s]['publisher']}: {sources[s]['title']}]({sources[s]['url']})" for s in p["source_ids"])
        lines += ["", f'<a id="{identifier}"></a>', "", "## " + p["title"], "",
            f"Responsible role: {p['owner_role']}. Applied to {mapped} scoped definitions. Status: recommended; project adoption open.", ""]
        lines += ["Existing assurance objectives: " + ", ".join(links["practice_control_ids"][identifier]) +
            ". Use the [Digital Standards Thread](../certification/digital-standards-adherence.md) for applicability, clause adoption and evidence decisions.", ""]
        for field in FIELDS:
            label = "Open evidence and decisions" if field == "open_questions" else field.capitalize()
            lines += [f"**{label}:** " + ". ".join(p[field]) + ".", ""]
        lines += ["Basis: " + refs + "."]
    lines += ["", "## Source limitations and refresh", "",
        "All references were reviewed on the date recorded below. ISO/IEC/EN entries are public-scope discovery, "
        "with complete adopted clause review open. Regulatory scope depends on project jurisdiction and system type. "
        "Manufacturer examples contribute methods; no proprietary design, guaranteed improvement or accepted supplier specification is redistributed.", "",
        "Refresh policies are OSR research rules: regulatory sources 90 days, manufacturer examples 180 days, "
        "standard scopes 365 days, method references 730 days. Checks use an explicit assessment date; "
        "a source overdue for review stays visible in the audit."]
    for s in sources.values():
        lines += ["", f"- [{s['publisher']}: {s['title']}]({s['url']}) "
            f"({s['kind']}; reviewed {s['reviewed_on']}). {s['finding']} {s['limitation']}"]
    lines += ["", "## Expansion boundaries", ""]
    lines += [f"- **{r['id']}** ({r['status']}): {r['reason']}" for r in scope["future_scopes"]]
    return {"coverage.json": canonical(coverage), "component-guidance.csv": output.getvalue(),
            "verification-plan.json": canonical(plan), "handbook.md": "\n".join(lines) + "\n"}


def check(root: Path = ROOT, as_of: date = date(2026, 10, 11)) -> dict:
    expected = build(root, as_of)
    coverage = json.loads(expected["coverage.json"])
    if coverage["source_refresh_required"]:
        raise ValueError("source refresh required: " + ", ".join(r["source_id"] for r in coverage["source_refresh_required"]))
    stale = [str(path) for name, path in OUTPUTS.items()
             if not contained(root, path).exists() or contained(root, path).read_bytes() != expected[name].encode()]
    if stale:
        raise ValueError("stale generated best-practice outputs: " + ", ".join(stale))
    return coverage
