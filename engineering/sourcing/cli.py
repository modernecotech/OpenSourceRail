"""Command line entry point for offline sourcing review.

This interface writes only local append-only sourcing records and fresh review
packets. Procurement drafts stay disabled and no physical approval is made.
"""
import argparse
from copy import deepcopy
from datetime import date
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
    laminate.add_argument("--target-currency", default="USD")

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
                        target_currency="USD"):
    from . import studies

    source_input = inputs.load_twin(input_path, member=member)
    parent_requirements = extract_requirements(source_input["payload"])
    parent_candidate_id = validate_requirements(parent_requirements)
    source_input_id = source_input["payload_id"]
    proposals = studies.laminate_study_requirements(
        store, parent_candidate_id=parent_candidate_id, source_input_id=source_input_id)
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
                    target_currency=args.target_currency))
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
