"""Command line entry point for offline sourcing review.

This interface writes only local append-only sourcing records and fresh review
packets. Procurement drafts stay disabled and no physical approval is made.
"""
import argparse
from copy import deepcopy
from datetime import date
import gzip
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

from . import catalogue, inputs, publication
from .database import Store
from .model import encoded, identity
from .requirements import extract_requirements, validate_requirements

ROOT = Path(__file__).resolve().parents[2]
RECORD_KINDS = ("source", "product", "offer", "fx", "benchmark", "process",
                "requirement", "assessment", "rfq", "overlay", "run", "redesign")


def default_database_path(environ=None, home=None):
    """Use per-user state, never a SQLite file inside the source checkout."""
    environ = os.environ if environ is None else environ
    state = environ.get("XDG_STATE_HOME")
    if not state:
        state = Path.home() if home is None else Path(home)
        state = Path(state) / ".local" / "state"
    path = Path(state).expanduser() / "opensourcerail" / "sourcing" / "sourcing.sqlite3"
    return path.resolve()


def default_raw_cache_path(environ=None, home=None):
    """Raw official-feed bytes live in per-user data, outside the checkout."""
    environ = os.environ if environ is None else environ
    data = environ.get("XDG_DATA_HOME")
    if not data:
        data = Path.home() if home is None else Path(home)
        data = Path(data) / ".local" / "share"
    return (Path(data).expanduser() / "opensourcerail" / "sourcing" / "raw-feeds").resolve()


def _emit(value, stream=None):
    stream = sys.stdout if stream is None else stream
    stream.write(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def _parser():
    parser = argparse.ArgumentParser(
        prog="osr source",
        description="Offline candidate-bound sourcing review; not procurement or physical acceptance.")
    parser.add_argument("--database", "--db", type=Path, default=None,
                        help="SQLite path (default: XDG_STATE_HOME/opensourcerail/sourcing/sourcing.sqlite3)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create the local append-only sourcing database")

    refresh = sub.add_parser("refresh", help="Fetch the declared official feeds into an outside-checkout raw cache")
    refresh.add_argument("--cache-dir", type=Path,
                         help="Raw feed cache directory (default: XDG_DATA_HOME/opensourcerail/sourcing/raw-feeds)")

    seed = sub.add_parser("seed", help="Append the bundled offline catalogue observations")
    seed.add_argument("--path", action="append", type=Path, dest="paths",
                      help="Use an explicit seed JSON file; repeat for a combined seed")

    run = sub.add_parser("run", help="Evaluate one typed input and publish a closed review packet")
    run.add_argument("--input", required=True, type=Path, help="Typed BOM JSON, packet directory, or tar.gz")
    run.add_argument("--member", help="Exact JSON member in a tar.gz input")
    run.add_argument("--as-of", required=True, help="Explicit estimate date (YYYY-MM-DD)")
    run.add_argument("--output", required=True, type=Path, help="Fresh publication directory")
    run.add_argument("--bindings", type=Path, help="JSON list of exact revision-bound product mappings")
    run.add_argument("--max-requirements", type=int,
                     help="Evaluate only the first N priority-sorted requirements; retain the rest as pending")
    run.add_argument("--category-budget", action="append", default=[], metavar="CATEGORY=N",
                     help="Per-category requirement budget; repeat for a balanced bounded evaluation")
    run.add_argument("--target-currency", default="USD", help="ISO target currency (default: USD)")

    verify = sub.add_parser("verify", help="Verify a sourcing packet and replay its saved inputs")
    verify.add_argument("publication", type=Path)

    study = sub.add_parser("study", help="Run bounded comparative material studies")
    study_sub = study.add_subparsers(dest="study_command", required=True)
    laminate = study_sub.add_parser("laminate", help="Compare declared 10 m² laminate material hypotheses")
    laminate.add_argument("--input", required=True, type=Path, help="Typed whole-cell source packet")
    laminate.add_argument("--member", required=True, help="Exact federated BOM JSON member")
    laminate.add_argument("--as-of", required=True, help="Explicit estimate date (YYYY-MM-DD)")
    laminate.add_argument("--output", required=True, type=Path, help="Fresh directory for separate study packets")
    laminate.add_argument("--max-requirements", type=int,
                          help="Evaluate at most N priority-sorted groups in each proposal")
    laminate.add_argument("--category-budget", action="append", default=[], metavar="CATEGORY=N",
                          help="Per-category requirement budget; repeat for a balanced bounded evaluation")
    laminate.add_argument("--product-observation", action="append", default=[], metavar="PRODUCT_KEY=RECORD_ID",
                          help="Select an exact immutable product observation when a key has multiple revisions")
    laminate.add_argument("--target-currency", default="USD")

    estimate = sub.add_parser("estimate", help="Create a source-linked fabrication cost screen")
    estimate_sub = estimate.add_subparsers(dest="estimate_command", required=True)
    fabrication = estimate_sub.add_parser("fabrication", help="Estimate material + labour hours + explicit uplift")
    fabrication.add_argument("--input", required=True, type=Path,
                             help="Exact typed digital-twin input packet or JSON")
    fabrication.add_argument("--member", help="Exact JSON member in a tar.gz input")
    fabrication.add_argument("--recipe", required=True, type=Path,
                             help="Recipe JSON with exact benchmark IDs and declared quantities")
    fabrication.add_argument("--output", required=True, type=Path,
                             help="Fresh JSON output path")
    takeoff_estimate = estimate_sub.add_parser("takeoff", help="Apply an explicit recipe to an exact material takeoff roll-up")
    takeoff_estimate.add_argument("--takeoff", required=True, type=Path,
                                  help="Sealed candidate-bound material takeoff JSON or .json.gz")
    takeoff_estimate.add_argument("--recipe", required=True, type=Path,
                                  help="Recipe JSON with exact benchmarks and target roll-up")
    takeoff_estimate.add_argument("--output", required=True, type=Path,
                                  help="Fresh JSON output path")
    gfrp = estimate_sub.add_parser("gfrp-laminate", help="Screen local labour against sourced 10 m² GFRP material studies")
    gfrp.add_argument("--packet-root", required=True, type=Path,
                      help="Directory containing the exact solid, sandwich and higher-fibre laminate packets")
    gfrp.add_argument("--output", required=True, type=Path,
                      help="Fresh source-bound JSON output path")

    takeoff = sub.add_parser("takeoff", help="Build traceable stock material quantity roll-ups")
    takeoff_sub = takeoff.add_subparsers(dest="takeoff_command", required=True)
    material = takeoff_sub.add_parser("material", help="Roll up candidate-bound stock mass and geometry")
    material.add_argument("--input", required=True, type=Path,
                          help="Federated railway BOM JSON or source archive")
    material.add_argument("--member", help="Exact JSON member in a tar.gz input")
    material.add_argument("--as-of", required=True, help="Benchmark cutoff date (YYYY-MM-DD)")
    material.add_argument("--output", required=True, type=Path,
                          help="Fresh JSON or .json.gz takeoff output")

    packages = sub.add_parser("procurement-bom", help="Group located candidate stock into traceable draft quote packages")
    packages.add_argument("--input", required=True, type=Path,
                          help="Exact federated BOM JSON, sealed sourcing input, or source archive")
    packages.add_argument("--member", help="Exact JSON member in a tar.gz input")
    packages.add_argument("--output", required=True, type=Path,
                          help="Fresh JSON or .json.gz procurement package BOM output")
    packages.add_argument("--regional-cost-reference", type=Path,
                          help="Optional exact regional-cost packet; links its group estimates to concrete span packages")

    sub.add_parser("status", help="Show database record counts and recent evaluation summaries")
    show = sub.add_parser("show", help="Show a run summary and its bounded evidence counts")
    show.add_argument("run_id")

    rfq = sub.add_parser("rfq", help="Export disabled RFQ drafts for review")
    rfq_sub = rfq.add_subparsers(dest="rfq_command", required=True)
    export = rfq_sub.add_parser("export", help="Write local disabled RFQ draft JSON; sends no messages")
    export.add_argument("run_id")
    export.add_argument("--output", required=True, type=Path)

    serve = sub.add_parser("serve", help="Serve the local read-only Workbench on loopback")
    serve.add_argument("--port", type=int, default=8774)

    return parser


def _latest_runs(store, limit=5):
    found = []
    for row in store.connection.execute(
            "SELECT record_id FROM records WHERE kind='run' ORDER BY rowid DESC LIMIT ?", (limit * 4,)):
        result = store.get(row[0], "run")
        # workflow.evaluate also retains an internal evidence row of kind=run;
        # only the publication-layer run carries the input/request epoch.
        if result.get("input_payload_id"):
            found.append(result)
            if len(found) == limit:
                break
    return found


def _parse_category_budgets(values, max_requirements=None):
    """Parse repeated CATEGORY=N options without silently replacing a category."""
    if values and max_requirements is not None:
        raise ValueError("Use either --max-requirements or --category-budget, not both")
    result = {}
    for value in values or ():
        if not isinstance(value, str) or "=" not in value:
            raise ValueError("Category budget must have the form CATEGORY=N")
        category, count = value.split("=", 1)
        if (not category or category != category.strip() or any(char.isspace() for char in category) or
                category in result):
            raise ValueError("Distinct nonempty category names required")
        if re.fullmatch(r"[0-9]+", count) is None or int(count) < 1:
            raise ValueError("Positive integer category budgets required")
        result[category] = int(count)
    return result or None


def _parse_product_observations(values):
    """Keep material studies bound to a selected immutable catalogue revision."""
    result = {}
    for value in values or ():
        if not isinstance(value, str) or "=" not in value:
            raise ValueError("Product observation must have the form PRODUCT_KEY=RECORD_ID")
        key, record_id = value.split("=", 1)
        if (not key or key != key.strip() or key in result or
                re.fullmatch(r"[0-9a-f]{64}", record_id) is None):
            raise ValueError("Distinct product keys and exact immutable record IDs required")
        result[key] = record_id
    return result or None


def _status(store, database):
    counts = {kind: 0 for kind in RECORD_KINDS}
    counts.update({row[0]: row[1] for row in store.connection.execute(
        "SELECT kind, COUNT(*) FROM records GROUP BY kind")})
    counts["run"] = store.connection.execute(
        "SELECT COUNT(*) FROM records WHERE kind='run' AND json_extract(payload, '$.input_payload_id') IS NOT NULL").fetchone()[0]
    recent = []
    for run in _latest_runs(store):
        recent.append(publication.summary(store, run))
    return dict(schema="osr-sourcing-cli-status/1", database=str(database),
                database_read_only=True, counts=counts, recent_runs=recent,
                complete_installed_cost=None, complete_whole_life_cost=None,
                physical_qualification=None, supplier_communications_sent=0,
                note="Coverage follows the supplied typed input; vehicle-only input is not a whole-infrastructure BOM.")


def _show(store, run_id):
    run = store.get(run_id, "run")
    summary = publication.summary(store, run)
    details = publication.details(store, run)
    return dict(schema="osr-sourcing-run-review/1", summary=summary,
                evidence_counts={key: len(value) for key, value in details.items() if isinstance(value, list)},
                overlay_coverage=details["overlay"].get("coverage"),
                rfq_draft_status=dict(count=len(details["RFQ_drafts"]), enabled=False,
                                      supplier_emails_sent=0, procurement_authorized=False),
                complete_installed_cost=None, complete_whole_life_cost=None,
                physical_qualification=None)


def _write_rfq_export(store, run_id, output):
    run = store.get(run_id, "run")
    details = publication.details(store, run)
    drafts = details["RFQ_drafts"]
    payload = dict(schema="osr-sourcing-rfq-export/1", candidate_id=run["candidate_id"],
                   evaluation_id=run["record_id"], estimate_date=run["estimate_date"],
                   drafts=drafts, enabled=False, send_supplier_emails=False,
                   procurement_authorized=False, supplier_communications_sent=0,
                   physical_qualification=None)
    payload["export_id"] = identity(payload)
    path = Path(output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents silent replacement of a previously reviewed draft.
    with path.open("x", encoding="utf-8") as stream:
        stream.write(encoded(payload).decode("utf-8") + "\n")
    return dict(path=str(path), export_id=payload["export_id"], draft_count=len(drafts),
                enabled=False, send_supplier_emails=False)


def _run_laminate_study(store, *, input_path, member, as_of, output,
                        max_requirements=None, max_requirements_by_category=None,
                        target_currency="USD", product_observations=None):
    from . import studies

    source_input = inputs.load_twin(input_path, member=member)
    parent_requirements = extract_requirements(source_input["payload"])
    parent_candidate_id = validate_requirements(parent_requirements)
    source_input_id = source_input["payload_id"]
    proposals = studies.laminate_study_requirements(
        store, parent_candidate_id=parent_candidate_id, source_input_id=source_input_id,
        product_observations=product_observations)
    if not isinstance(proposals, list) or not proposals:
        raise ValueError("Laminate study must return an explicit nonempty proposal list")
    for proposal in proposals:
        if (proposal.get("schema") != "osr-sourcing-declared-requirements/1" or
                proposal.get("parent_candidate_id") != parent_candidate_id or
                proposal.get("source_input_id") != source_input_id or
                validate_requirements(proposal.get("requirements")) != proposal.get("candidate_id")):
            raise ValueError("Laminate study proposal candidate/source binding differs")

    destination = Path(output).expanduser().resolve()
    if destination.exists() or destination.is_symlink():
        raise ValueError("Fresh study packet set directory required")
    destination.mkdir(parents=True)

    request = dict(as_of=as_of, target_currency=target_currency)
    if max_requirements is not None:
        request["max_requirements"] = max_requirements
    if max_requirements_by_category is not None:
        request["max_requirements_by_category"] = max_requirements_by_category
    entries = []
    for proposal in proposals:
        recipe = proposal["proposal"]["recipe"]
        study_input = dict(schema="osr-sourcing-twin-input/1", payload=proposal,
                           payload_id=identity(proposal),
                           origin=dict(source_input["origin"], study="laminate-material-10m2",
                                       parent_source_input_id=source_input_id))
        # Process provenance is part of the source epoch used by replay.
        store.put(proposal["process"])
        result = publication.execute(store, deepcopy(study_input), request, root=ROOT)
        packet = destination / recipe
        manifest = publication.publish(store, result, study_input, request, packet, root=ROOT)
        summary = publication.summary(store, result)
        entries.append(dict(recipe=recipe, candidate_id=proposal["candidate_id"],
                            packet=str(packet), publication_id=manifest["publication_id"],
                            run_id=result["record_id"], summary=summary["summary"],
                            limitations=proposal.get("limitations", [])))
    return dict(schema="osr-laminate-study-set/1", study_basis="10 m² material comparison",
                parent_candidate_id=parent_candidate_id, source_input_id=source_input_id,
                studies=entries, selected_reference_changed=False,
                roof_cad_takeoff=False, complete_vehicle_bom=False,
                complete_installed_cost=None, physical_qualification=None)


def _estimate_fabrication(store, *, input_path, member, recipe_path, output_path):
    from .fabrication import domestic_fabrication_estimate

    direct = inputs.read_json(input_path) if member is None else None
    if (isinstance(direct, dict) and direct.get("schema") == "osr-sourcing-twin-input/1" and
            direct.get("payload_id") == identity(direct.get("payload"))):
        source_input = direct
    else:
        source_input = inputs.load_twin(input_path, member=member)
    requirement_rows = extract_requirements(source_input["payload"])
    candidate_id = validate_requirements(requirement_rows)
    recipe = inputs.read_json(recipe_path)
    required = {"schema", "estimate_key", "output_quantity", "output_unit", "currency",
                "benchmark_ids", "material_lines", "labour_lines"}
    optional = {"candidate_id", "input_id", "uplift_fraction"}
    if (not isinstance(recipe, dict) or recipe.get("schema") != "osr-domestic-fabrication-recipe/1" or
            required - recipe.keys() or recipe.keys() - required - optional):
        raise ValueError("Domestic fabrication recipe schema/fields differ")
    if recipe.get("candidate_id") not in (None, candidate_id):
        raise ValueError("Recipe candidate identity differs from the digital-twin input")
    if recipe.get("input_id") not in (None, source_input["payload_id"]):
        raise ValueError("Recipe source-input identity differs from the digital-twin input")
    if not isinstance(recipe["benchmark_ids"], dict):
        raise ValueError("Exact benchmark key-to-record mapping required")
    selected = {}
    for key, benchmark_id in recipe["benchmark_ids"].items():
        benchmark = store.get(benchmark_id, "benchmark")
        if benchmark.get("benchmark_key") != key:
            raise ValueError("Exact benchmark key and record ID differ")
        selected[benchmark_id] = benchmark
    material_lines = []
    for row in recipe["material_lines"]:
        if not isinstance(row, dict) or row.get("benchmark_key") not in recipe["benchmark_ids"]:
            raise ValueError("Every material line must name an exact sourced benchmark key")
        material_lines.append(dict(row, benchmark_id=recipe["benchmark_ids"][row["benchmark_key"]]))
    labour_lines = []
    for row in recipe["labour_lines"]:
        if not isinstance(row, dict) or row.get("benchmark_key") not in recipe["benchmark_ids"]:
            raise ValueError("Every labour line must name an exact sourced benchmark key")
        labour_lines.append(dict(row, benchmark_id=recipe["benchmark_ids"][row["benchmark_key"]]))
    process = domestic_fabrication_estimate(
        estimate_key=recipe["estimate_key"], candidate_id=candidate_id,
        input_id=source_input["payload_id"], output_quantity=recipe["output_quantity"],
        output_unit=recipe["output_unit"], currency=recipe["currency"],
        material_lines=material_lines, labour_lines=labour_lines,
        uplift_fraction=recipe.get("uplift_fraction", "0.20"), benchmarks=selected)
    source_hashes = publication.sources(root=ROOT)
    source_hashes["engineering/sourcing/cli.py"] = inputs.digest(ROOT / "engineering/sourcing/cli.py")
    payload = dict(schema="osr-domestic-fabrication-estimate/1",
                   source_input_id=source_input["payload_id"],
                   candidate_id=candidate_id, input_origin=source_input["origin"],
                   recipe_id=identity(recipe), source_sha256=source_hashes,
                   estimate=process, source_seed_required=True,
                   candidate_takeoff_mapped=False, complete_installed_cost=None,
                   physical_qualification=None)
    payload["estimate_packet_id"] = identity(payload)
    path = Path(output_path).expanduser().resolve()
    if path.exists() or path.is_symlink():
        raise ValueError("Fresh fabrication estimate output path required")
    path.parent.mkdir(parents=True, exist_ok=True)
    store.put(process)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(encoded(payload).decode("utf-8") + "\n")
    return dict(output=str(path), estimate_packet_id=payload["estimate_packet_id"],
                process_record_id=process["record_id"], candidate_id=candidate_id,
                currency=process["currency"], estimated_unit_cost=process["estimated_unit_cost"],
                candidate_takeoff_mapped=False, complete_installed_cost=None,
                physical_qualification=None)


def _estimate_takeoff(store, *, takeoff_path, recipe_path, output_path):
    from .fabrication import domestic_fabrication_takeoff_estimate

    takeoff = inputs.read_json(takeoff_path)
    if (not isinstance(takeoff, dict) or
            takeoff.get("schema") != "osr-engineering-material-takeoff/1" or
            not isinstance(takeoff.get("takeoff_id"), str) or
            takeoff["takeoff_id"] != identity({key: value for key, value in takeoff.items()
                                                if key != "takeoff_id"})):
        raise ValueError("Exact sealed candidate-bound material takeoff required")
    recipe = inputs.read_json(recipe_path)
    required = {"schema", "estimate_key", "output_quantity", "output_unit", "currency",
                "benchmark_ids", "material_lines", "labour_lines", "target_rollup"}
    optional = {"candidate_id", "input_id", "uplift_fraction"}
    if (not isinstance(recipe, dict) or recipe.get("schema") != "osr-domestic-fabrication-recipe/1" or
            required - recipe.keys() or recipe.keys() - required - optional):
        raise ValueError("Takeoff fabrication recipe schema/fields differ")
    for key, takeoff_key in (("candidate_id", "candidate_id"), ("input_id", "source_input_id")):
        if recipe.get(key) not in (None, takeoff.get(takeoff_key)):
            raise ValueError("Recipe " + key + " differs from exact takeoff identity")
    if recipe["output_unit"] != "m3":
        raise ValueError("Current geometry takeoff costing requires a declared per-m3 recipe")
    if not isinstance(recipe["benchmark_ids"], dict):
        raise ValueError("Exact benchmark key-to-record mapping required")
    selected = {}
    for key, benchmark_id in recipe["benchmark_ids"].items():
        benchmark = store.get(benchmark_id, "benchmark")
        if benchmark.get("benchmark_key") != key:
            raise ValueError("Exact benchmark key and record ID differ")
        selected[benchmark_id] = benchmark
    material_lines = []
    for row in recipe["material_lines"]:
        if not isinstance(row, dict) or row.get("benchmark_key") not in recipe["benchmark_ids"]:
            raise ValueError("Every material line must name an exact sourced benchmark key")
        material_lines.append(dict(row, benchmark_id=recipe["benchmark_ids"][row["benchmark_key"]]))
    labour_lines = []
    for row in recipe["labour_lines"]:
        if not isinstance(row, dict) or row.get("benchmark_key") not in recipe["benchmark_ids"]:
            raise ValueError("Every labour line must name an exact sourced benchmark key")
        labour_lines.append(dict(row, benchmark_id=recipe["benchmark_ids"][row["benchmark_key"]]))
    process = domestic_fabrication_takeoff_estimate(
        estimate_key=recipe["estimate_key"], takeoff=takeoff,
        target_rollup=recipe["target_rollup"],
        recipe_output_quantity=recipe["output_quantity"],
        currency=recipe["currency"], material_lines=material_lines,
        labour_lines=labour_lines, benchmarks=selected,
        uplift_fraction=recipe.get("uplift_fraction", "0.20"))

    source_names = (
        "engineering/sourcing/cli.py", "engineering/sourcing/fabrication.py",
        "engineering/sourcing/takeoff.py", "engineering/sourcing/model.py",
        "engineering/sourcing/inputs.py", "engineering/sourcing/catalogue.py",
        "engineering/sourcing/database.py", "engineering/sourcing/requirements.py",
        "engineering/sourcing/data/supplier-catalogue.json",
        "engineering/sourcing/data/public-feeds.json",
        "engineering/station_rail/common.py",
    )
    source_hashes = {name: inputs.digest(ROOT / name) for name in source_names}
    source_hashes["takeoff_file"] = inputs.digest(takeoff_path)
    source_hashes["recipe_file"] = inputs.digest(recipe_path)
    payload = dict(schema="osr-domestic-fabrication-takeoff-estimate/1",
                   candidate_id=takeoff["candidate_id"],
                   source_input_id=takeoff["source_input_id"],
                   takeoff_id=takeoff["takeoff_id"],
                   recipe_id=identity(recipe), source_sha256=source_hashes,
                   estimate=process, candidate_takeoff_mapped=True,
                   complete_procurement_cost=None, complete_installed_cost=None,
                   whole_life_cost=None, physical_qualification=None,
                   engineering_accepted=False, procurement_approved=False,
                   selected_reference_changed=False, unknown_is_zero=False)
    payload["estimate_packet_id"] = identity(payload)
    path = Path(output_path).expanduser().resolve()
    if path.exists() or path.is_symlink():
        raise ValueError("Fresh takeoff estimate output path required")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(encoded(payload).decode("utf-8") + "\n")
    store.put(process)
    return dict(output=str(path), estimate_packet_id=payload["estimate_packet_id"],
                process_record_id=process["record_id"], candidate_id=payload["candidate_id"],
                takeoff_id=payload["takeoff_id"], currency=process["currency"],
                estimated_total=process["estimated_total"],
                estimated_unit_cost=process["estimated_unit_cost"],
                mapped_group_count=process["candidate_takeoff_group_count"],
                mapped_occurrence_count=process["candidate_takeoff_occurrence_count"],
                candidate_takeoff_mapped=True, complete_installed_cost=None,
                physical_qualification=None)


def _material_takeoff(*, input_path, member, as_of, output_path):
    from .takeoff import material_takeoff

    twin_input = inputs.load_twin(input_path, member=member)
    result = material_takeoff(twin_input, catalogue_records=catalogue.load_catalogue(), as_of=as_of)
    source_hashes = publication.sources(root=ROOT)
    source_hashes["engineering/sourcing/cli.py"] = inputs.digest(ROOT / "engineering/sourcing/cli.py")
    for name in ("engineering/sourcing/data/supplier-catalogue.json",
                 "engineering/sourcing/data/public-feeds.json"):
        source_hashes[name] = inputs.digest(ROOT / name)
    result["source_sha256"] = source_hashes
    result.pop("takeoff_id", None)
    result["takeoff_id"] = identity(result)

    path = Path(output_path).expanduser().resolve()
    if path.exists() or path.is_symlink():
        raise ValueError("Fresh material takeoff output path required")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = encoded(result) + b"\n"
    with path.open("xb") as stream:
        stream.write(gzip.compress(raw, mtime=0) if path.name.endswith(".gz") else raw)
    raw_references = [row["raw_commodity_reference"] for row in result["material_rollups"]
                      if row["raw_commodity_reference"] is not None]
    return dict(output=str(path), takeoff_id=result["takeoff_id"],
                candidate_id=result["candidate_id"], evaluation_id=result["evaluation_id"],
                source_input_id=result["source_input_id"],
                manufacturing_group_count=result["input_provenance"]["manufacturing_group_count"],
                engineering_occurrence_count=result["input_provenance"]["located_occurrence_count"],
                unlocated_account_count=result["input_provenance"]["unlocated_account_count"],
                summary=result["summary"], raw_commodity_references=raw_references,
                complete_installed_cost=None, physical_qualification=None)


def main(argv=None):
    parser = _parser()
    args = parser.parse_args(argv)
    database = (args.database or default_database_path()).expanduser().resolve()

    try:
        category_budgets = None
        if args.command in {"run", "study"}:
            category_budgets = _parse_category_budgets(
                args.category_budget, args.max_requirements)
        if args.command == "serve":
            from .workbench import serve
            serve(database, port=args.port)
            return 0

        if args.command == "takeoff":
            if args.takeoff_command != "material":
                parser.error("unsupported sourcing takeoff")
            _emit(_material_takeoff(input_path=args.input, member=args.member,
                as_of=args.as_of, output_path=args.output))
            return 0

        if args.command == "procurement-bom":
            from .procurement_bom import build_procurement_bom, load_twin_input, source_hashes, write_packet
            from .catalogue import load_catalogue
            twin_input = load_twin_input(args.input, member=args.member)
            source_file = args.input.expanduser().resolve()
            regional_reference = None
            concrete_estimates = []
            source_evidence_hashes = {}
            source_registry = [row for row in load_catalogue() if row["kind"] == "source"]
            for relative in ("engineering/sourcing/data/supplier-catalogue.json",
                             "engineering/sourcing/data/public-feeds.json"):
                source_evidence_hashes[relative] = inputs.digest(ROOT / relative)
            if args.regional_cost_reference is not None:
                regional_path = args.regional_cost_reference.expanduser().resolve()
                regional_reference = inputs.read_json(regional_path)
                source_evidence_hashes[regional_path.relative_to(ROOT).as_posix()
                                       if regional_path.is_relative_to(ROOT) else regional_path.name] = inputs.digest(regional_path)
                for row in regional_reference.get("baghdad_concrete_takeoff_estimates", []):
                    hours = str(row.get("labour_hours_per_nominal_m3"))
                    estimate_path = regional_path.parent / ("baghdad-concrete-takeoff-" + hours + "h.json")
                    estimate_packet = inputs.read_json(estimate_path)
                    if estimate_packet.get("estimate_packet_id") != row.get("estimate_packet_id"):
                        raise ValueError("Regional cost index and concrete estimate packet identity differ")
                    concrete_estimates.append((hours, estimate_packet))
                    source_evidence_hashes[estimate_path.relative_to(ROOT).as_posix()
                                           if estimate_path.is_relative_to(ROOT) else estimate_path.name] = inputs.digest(estimate_path)
            packet = build_procurement_bom(
                twin_input,
                source_file_sha256=inputs.digest(source_file),
                source_file_name=source_file.name,
                source_code_hashes={**source_hashes(),
                                    "engineering/sourcing/cli.py": inputs.digest(ROOT / "engineering/sourcing/cli.py")},
                source_evidence_hashes=source_evidence_hashes,
                regional_cost_reference=regional_reference,
                concrete_estimate_packets=concrete_estimates,
                domestic_source_records=source_registry,
            )
            output_path = write_packet(packet, args.output)
            _emit({
                "output": str(output_path),
                "packet_id": packet["packet_id"],
                "candidate_id": packet["candidate_id"],
                "evaluation_id": packet["evaluation_id"],
                "source_input_id": packet["source_input_id"],
                "located_occurrence_count": packet["located_stock_occurrence_count"],
                "draft_package_count": packet["draft_package_count"],
                "unlocated_obligation_count": packet["unlocated_obligation_count"],
                "material_purchasing_line_count": packet["material_purchasing_line_count"],
                "material_demand_groups_preserved": packet["material_demand_groups_preserved"],
                "material_demand_occurrences_preserved": packet["material_demand_occurrences_preserved"],
                "source_registry_record_count": packet["source_registry_record_count"],
                "commercial_order_quantities_known": False,
                "unmapped_located_occurrence_count": len(packet["unmapped_located_occurrence_ids"]),
                "packages_with_domestic_cost_estimates": packet["packages_with_domestic_cost_estimates"],
                "domestic_cost_estimate_scenario_count": packet["domestic_cost_estimate_scenario_count"],
                "complete_installed_bom": False,
                "physical_qualification": None,
            })
            return 0

        if args.command == "refresh":
            cache = (args.cache_dir or default_raw_cache_path()).expanduser().resolve()
            if cache.is_relative_to(ROOT):
                raise ValueError("Raw feed cache must be outside the repository checkout")
            from .refresh import refresh_public_feeds
            with Store(database) as store:
                result = refresh_public_feeds(store, cache_dir=cache)
            _emit(dict(cache_directory=str(cache), network_refresh_was_explicit=True,
                       automatic_source_updates=False, committed_raw_vendor_files=False,
                       refresh=result))
            return 0

        if args.command == "verify":
            _emit(publication.verify(args.publication, root=ROOT))
            return 0

        if args.command == "study":
            if args.study_command != "laminate":
                parser.error("unsupported sourcing study")
            date.fromisoformat(args.as_of)
            with Store(database) as store:
                _emit(_run_laminate_study(
                    store, input_path=args.input, member=args.member, as_of=args.as_of,
                    output=args.output, max_requirements=args.max_requirements,
                    max_requirements_by_category=category_budgets,
                    target_currency=args.target_currency,
                    product_observations=_parse_product_observations(args.product_observation)))
            return 0

        if args.command == "estimate":
            if args.estimate_command == "gfrp-laminate":
                from .iraq_gfrp_cost_scenarios import _build
                payload = _build(catalogue.load_catalogue(), args.packet_root.expanduser().resolve())
                output_path = args.output.expanduser().resolve()
                if output_path.exists() or output_path.is_symlink():
                    raise ValueError("Fresh GFRP cost-screen output path required: " + str(output_path))
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(encoded(payload) + b"\n")
                _emit(dict(output=str(output_path), packet_id=payload["packet_id"],
                           scenarios=sum(len(row["scenarios"]) for row in payload["studies"]),
                           regional_scenarios=sum(len(row["regional_scenarios"]) for row in payload["studies"]),
                           regional_governorate_count=len(payload["basis"]["regional_governorates"]),
                           complete_fabrication_cost_iqd=None, physical_qualification=None))
                return 0
            if not database.is_file():
                raise ValueError("Initialize and seed the sourcing database before estimating")
            with Store(database) as store:
                if args.estimate_command == "fabrication":
                    result = _estimate_fabrication(store, input_path=args.input,
                        member=args.member, recipe_path=args.recipe, output_path=args.output)
                elif args.estimate_command == "takeoff":
                    result = _estimate_takeoff(store, takeoff_path=args.takeoff,
                        recipe_path=args.recipe, output_path=args.output)
                else:
                    parser.error("unsupported sourcing estimate")
                _emit(result)
            return 0

        if args.command == "init":
            with Store(database):
                pass
            _emit(dict(initialized=True, database=str(database), outside_checkout=not database.is_relative_to(ROOT),
                       physical_qualification=None))
            return 0

        if args.command in {"status", "show"} and not database.is_file():
            if args.command == "status":
                counts = {kind: 0 for kind in RECORD_KINDS}
                _emit(dict(schema="osr-sourcing-cli-status/1", database=str(database),
                           database_read_only=True, counts=counts, recent_runs=[],
                           complete_installed_cost=None, complete_whole_life_cost=None,
                           physical_qualification=None,
                           note="Database is not initialized. Coverage is limited to any later supplied typed input."))
                return 0
            raise ValueError("Sourcing database does not exist; initialize it or select the correct --database")

        with Store(database, readonly=args.command in {"status", "show", "rfq"}) as store:
            if args.command == "seed":
                _emit(catalogue.seed(store, args.paths))
            elif args.command == "run":
                # Date validation is also performed by downstream pricing; check
                # here so malformed dates fail before any run records are added.
                date.fromisoformat(args.as_of)
                twin_input = inputs.load_twin(args.input, member=args.member)
                request = dict(as_of=args.as_of, target_currency=args.target_currency)
                if args.bindings is not None:
                    request["bindings"] = inputs.read_json(args.bindings)
                if args.max_requirements is not None:
                    request["max_requirements"] = args.max_requirements
                if category_budgets is not None:
                    request["max_requirements_by_category"] = category_budgets
                # Preserve the original input envelope for publication even when
                # an evaluator applies an internal priority order to requirements.
                result = publication.execute(store, deepcopy(twin_input), request, root=ROOT)
                manifest = publication.publish(store, result, twin_input, request, args.output, root=ROOT)
                _emit(dict(manifest=manifest, summary=publication.summary(store, result),
                           input_origin=twin_input["origin"],
                           input_scope=twin_input["input_scope"],
                           vehicle_only_input_is_not_infrastructure_coverage=True))
            elif args.command == "status":
                _emit(_status(store, database))
            elif args.command == "show":
                _emit(_show(store, args.run_id))
            elif args.command == "rfq":
                _emit(_write_rfq_export(store, args.run_id, args.output))
            else:
                parser.error("unsupported sourcing command")
        return 0
    except (OSError, sqlite3.Error, KeyError, ValueError) as error:
        parser.exit(2, f"osr sourcing: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
