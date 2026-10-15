"""Allowlisted Workbench design APIs; no browser-to-shell command surface."""

from __future__ import annotations
import json
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlsplit

from .contracts import load, identity
from .registry import ROOT, problems, dependencies
from .runtime import Manager, request, comparison, toolchain, preflight
from .review import ReviewStore, REQUIRED, normalize_record_scope

LOCK = threading.Lock()


from .engineering_inputs import (
    qualification_template,
    draft_structure as _draft_structure,
    draft_missing as _draft_missing,
)


def qualification_draft(store, job, candidate, data, scope, actor):
    from copy import deepcopy
    import shutil
    import tempfile
    from .contracts import fingerprint
    from .civil_qualification import (
        assess_site,
        foundation_geometry,
        prestress_assessment,
    )
    from .manufacturing_rules import evaluate
    from .store import write_new

    adapter = job["request"]["problem"]["adapter"]
    if scope != job["request"]["identity"]:
        raise PermissionError(
            "qualification draft requires the exact original job identity"
        )
    if job["request"]["dependencies"] != dependencies(adapter) or job["request"][
        "toolchain"
    ] != toolchain(adapter):
        raise ValueError(
            "qualification draft requires current job sources and toolchain"
        )
    contract = candidate.get("definition", {}).get("contract")
    if not contract or data["contract_sha256"] != fingerprint(contract):
        raise ValueError(
            "qualification draft requires the exact physical candidate hash"
        )
    kind = data["kind"]
    proposed = decode_definition(data["input_json"])
    template = qualification_template(kind, contract, scope)
    _draft_structure(proposed, template)
    if not isinstance(proposed, dict):
        raise ValueError("structured qualification draft required")
    if kind != "manufacturing":
        if proposed["identity"] != scope or proposed["contract_sha256"] != fingerprint(
            contract
        ):
            raise PermissionError(
                "qualification inputs belong to another identity or physical contract"
            )
    missing = _draft_missing(proposed)
    if kind == "site":
        partial = deepcopy(proposed)
        for name in (
            "survey",
            "layers",
            "groundwater",
            "utilities",
            "calibration",
            "route_station_constraints",
        ):
            if _draft_missing(partial[name]):
                partial[name] = None
        result = assess_site(
            partial,
            context=scope,
            contract=contract,
            required_depth_m=foundation_geometry(contract)[
                "minimum_investigation_depth_m"
            ],
        )
    elif kind == "foundation":
        from .foundation_response import assess_foundation_response

        result = assess_foundation_response(
            contract, None if missing else proposed, context=scope
        )
    elif kind == "prestress":
        trace = load(
            ROOT / "engineering/industrialisation/vehicle-civil-load-trace.json"
        )
        result = prestress_assessment(
            contract, trace, None if missing else proposed, context=scope
        )
    else:
        partial = deepcopy(proposed)
        for name in (
            "part_rules",
            "tool_envelopes",
            "removal_paths",
            "tolerance_stacks",
            "tooling",
        ):
            partial[name] = [
                row for row in (partial[name] or []) if not _draft_missing(row)
            ]
        amended = deepcopy(contract)
        amended["manufacturing_plan"] = partial
        result = evaluate(amended)
    if job["request"]["dependencies"] != dependencies(adapter):
        raise ValueError("job sources changed during qualification validation")
    payload = dict(
        schema="osr-qualification-input-draft/1",
        identity=scope,
        job=job["id"],
        candidate=candidate["id"],
        kind=kind,
        contract_sha256=fingerprint(contract),
        input_sha256=fingerprint(proposed),
        draft_sha256=fingerprint(dict(request=data, actor=actor["username"])),
        actor=actor["username"],
        missing_fields=missing,
        assessment=result,
        state="draft",
        baseline_modified=False,
        physical_release=False,
        independent_acceptance=False,
        source_files_verified=False,
    )
    folder = (
        store.root / "planning-drafts" / ("qualification-" + payload["draft_sha256"])
    )
    with LOCK:
        if not folder.exists():
            folder.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            staged = Path(tempfile.mkdtemp(prefix=".qualification-", dir=folder.parent))
            try:
                write_new(staged / "request.json", data)
                write_new(staged / "assessment.json", payload)
                staged.rename(folder)
            finally:
                shutil.rmtree(staged, ignore_errors=True)
        else:
            payload = load(folder / "assessment.json")
    store.event(
        job["id"],
        dict(
            kind="qualification-draft-checked",
            actor=actor["username"],
            draft_sha256=payload["draft_sha256"],
            physical_release=False,
        ),
    )
    return payload


from .engineering_inputs import decode_input as decode_definition


def manager(handler):
    with LOCK:
        if not hasattr(handler.server, "design_manager"):
            handler.server.design_manager = Manager(
                handler.database_path.parent / "design-engine"
            )
    return handler.server.design_manager


def scoped(handler, city, environment, *, write=False):
    if city not in handler.project_twins._cities or environment not in {
        "simulation",
        "physical",
        "training",
    }:
        raise ValueError("known city and explicit environment required")
    actor = handler._actor()
    if actor is None:
        raise PermissionError("authenticated account required")
    if "*" not in actor.get("city_scopes", []) and city not in actor.get(
        "city_scopes", []
    ):
        raise PermissionError("account cannot access this city")
    if write and (
        handler.headers.get("Origin") != "http://" + handler.headers.get("Host", "")
        or not handler._valid_csrf(actor)
    ):
        raise PermissionError("same-origin request and valid CSRF token required")
    return actor


def query_scope(query, city, environment):
    def value(name, default=None):
        return query.get(name, [default])[0] or None

    return identity(
        dict(
            schema="osr-design-identity/1",
            city=city,
            environment=environment,
            project=value("project", city),
            configuration_revision=value("revision", "unselected"),
            baseline_sha256=value("baseline_sha256"),
            run_id=value("run_id"),
            asset_id=value("asset_id"),
            part_id=value("part_id"),
        )
    )


def query_applicability(query):
    return {
        key: query.get(key, [None])[0] or None
        for key in (
            "candidate_id",
            "physical_part_id",
            "material_batch",
            "definition_sha256",
        )
    }


def get(handler):
    url = urlsplit(handler.path)
    path = url.path.removeprefix("/api/design/").strip("/")
    query = parse_qs(url.query)
    city = query.get("city", [handler.bootstrap["city"]])[0]
    environment = query.get("environment", ["simulation"])[0]
    try:
        actor = scoped(handler, city, environment)
        service = manager(handler)
        store = service.store
        selected_scope = query_scope(query, city, environment)
        if path == "problems":
            registered = list(problems().values())
            payload = dict(
                problems=registered,
                preflight={p["id"]: preflight(p) for p in registered},
                operations={
                    p["id"]: {
                        operation: preflight(p, operation=operation)
                        for operation in ("screen", "optimise", "confirm", "iterate")
                    }
                    for p in registered
                },
            )
        elif path == "preflight":
            from .registry import get as get_problem

            payload = preflight(
                get_problem(query["problem"][0]), operation=query["operation"][0]
            )
        elif path == "parts":
            payload = load(ROOT / "engineering/design_engine/data/potential-parts.json")
        elif path == "review-schema":
            payload = dict(
                kinds={kind: sorted(fields) for kind, fields in REQUIRED.items()},
                accounts_configured=handler.user_store is not None,
                verification_grants_physical_release=False,
            )
        elif path == "verification-matrix":
            from .qualification import matrix

            payload = matrix()
        elif path == "records":
            records = ReviewStore(store).list(city, environment)
            payload = dict(
                records=[r for r in records if r["identity"] == selected_scope],
                legacy_unscoped=[r for r in records if r["identity"] is None],
                identity=selected_scope,
            )
        elif path == "cost-objectives":
            from datetime import date
            from .economics import installed_objectives

            payload = installed_objectives(
                ReviewStore(store).list(city, environment),
                place=query.get("place", [city])[0],
                currency=query.get("currency", ["USD"])[0],
                as_of=query.get("as_of", [date.today().isoformat()])[0],
                identity=selected_scope,
                applicability=query_applicability(query),
            )
        elif path == "input-revisions":
            from .input_revisions import InputRevisions

            payload = dict(
                revisions=InputRevisions(store).list(selected_scope),
                identity=selected_scope,
            )
        elif path == "jobs":
            jobs = store.list(city, environment)
            for job in jobs:
                adapter = job["request"]["problem"]["adapter"]
                job["source_state"] = (
                    "current"
                    if job["request"]["dependencies"] == dependencies(adapter)
                    and job["request"]["toolchain"] == toolchain(adapter)
                    else "stale"
                )
                job.pop("pid", None)
                job.pop("process_start", None)
            payload = dict(jobs=jobs)
        elif path == "work-queue":
            from .ownership import projection
            from workbench_city import city_summary
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "projection_ops", ROOT / "tools/automation/ops-core-server.py"
            )
            ops = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ops)
            with ops.connect(handler.database_path) as con:
                state = ops.load_state(con, city)
            info = city_summary(
                ROOT,
                city,
                handler.project_twins._cities[city]["design_path"],
                handler.bootstrap["city"],
                environment if environment != "training" else "simulation",
            )
            payload = projection(
                city,
                environment,
                jobs=store.list(city, environment),
                twin_jobs=handler.project_twins.jobs(city),
                railway_records=state,
                erp_routes=info["erp"]["routes"],
                telemetry=info.get("supervision"),
            )
        elif path.startswith("jobs/"):
            identifier = path.split("/")[1]
            job = store.get(identifier)
            if job["city"] != city or job["environment"] != environment:
                raise PermissionError("job belongs to another city/environment")
            if path.endswith("/comparison"):
                payload = comparison(store, identifier)
                adapter = job["request"]["problem"]["adapter"]
                payload["source_state"] = (
                    "current"
                    if job["request"]["dependencies"] == dependencies(adapter)
                    and job["request"]["toolchain"] == toolchain(adapter)
                    else "stale"
                )
            elif path.endswith("/definition"):
                report = comparison(store, identifier)
                candidate_id = query.get("candidate", [""])[0]
                candidate = next(
                    (r for r in report["candidates"] if r["id"] == candidate_id), None
                )
                if candidate is None or "contract" not in candidate.get(
                    "definition", {}
                ):
                    raise ValueError("candidate has no manufactured definition")
                payload = candidate["definition"]["contract"]
            elif path.endswith("/artifacts"):
                from .publication import digest

                root = store.root / "runs" / identifier
                payload = dict(
                    job=identifier,
                    artifacts=[
                        dict(
                            name=p.relative_to(root).as_posix(),
                            bytes=p.stat().st_size,
                            sha256=digest(p),
                        )
                        for p in sorted(root.rglob("*"))
                        if p.is_file() and not p.is_symlink()
                    ],
                    execution_state=job["status"],
                    physical_release=False,
                )
            elif path.endswith("/artifact"):
                from .delivery import controlled_file, send_file

                send_file(
                    handler,
                    controlled_file(
                        store.root / "runs" / identifier, query.get("file", [""])[0]
                    ),
                )
                return
            elif path.endswith("/download"):
                import re
                from .delivery import controlled_file, send_file

                export_id = query.get("export", [""])[0]
                if not re.fullmatch(re.escape(identifier) + r"-[a-f0-9]{8}", export_id):
                    raise ValueError("exact job review export required")
                folder = store.root / "downloads" / export_id
                receipt = load(folder / "download.json")
                name = query.get("file", [""])[0]
                expected = next(
                    (r for r in receipt["chunks"] if r["name"] == name), None
                )
                if not expected:
                    raise ValueError("unknown review chunk")
                path_to_send = controlled_file(folder, name)
                from .publication import digest

                if digest(path_to_send) != expected["sha256"]:
                    raise ValueError("review download changed")
                send_file(handler, path_to_send)
                return
            else:
                job.pop("pid", None)
                job.pop("process_start", None)
                payload = job
        else:
            raise ValueError("unknown design API read")
        handler._send_json(200, payload)
    except PermissionError as error:
        handler._send_json(403, dict(error=str(error)))
    except (ValueError, OSError, KeyError, TypeError) as error:
        handler._send_json(400, dict(error=str(error), physical_release=False))


def post(handler):
    path = urlsplit(handler.path).path.removeprefix("/api/design/").strip("/")
    try:
        length = int(handler.headers.get("Content-Length", "0"))
        maximum = 4 * 1024**2 if path == "definition-diff" else 256 * 1024
        if not 0 < length <= maximum:
            raise ValueError("bounded nonempty design request required")
        data = handler._read_json()
        if not isinstance(data, dict):
            raise ValueError("structured design request required")
        scope = identity(data.get("identity", {}))
        city = scope.get("city")
        environment = scope.get("environment")
        actor = scoped(handler, city, environment, write=True)
        allowed = (
            {"admin", "planner"}
            if (
                path == "jobs"
                or path.startswith("jobs/")
                or path in {"definition-diff", "production-plan"}
            )
            else {
                "admin",
                "planner",
                "maintainer",
                "inspector",
                "approver",
                "document_controller",
            }
        )
        if not set(actor.get("roles", [])) & allowed:
            raise PermissionError(
                "authenticated account role cannot perform this design action"
            )
        service = manager(handler)
        store = service.store
        if path.startswith("input-revisions/"):
            from .input_revisions import InputRevisions

            fields = path.split("/")
            if len(fields) != 3 or fields[2] not in {"review", "run"}:
                raise ValueError("controlled input revision action required")
            revisions = InputRevisions(store)
            retained = revisions.get(fields[1])
            if retained["identity"] != scope:
                raise PermissionError(
                    "input revision belongs to another exact identity"
                )
            if fields[2] == "review":
                if handler.user_store is None:
                    raise PermissionError(
                        "configure named accounts before independent input review"
                    )
                if set(data) != {"identity", "revision", "rationale"}:
                    raise ValueError(
                        "exact input proposal revision and review rationale required"
                    )
                payload = revisions.review(
                    fields[1], data["revision"], scope, actor, data["rationale"]
                )
            else:
                if not set(actor.get("roles", [])) & {"planner", "admin"}:
                    raise PermissionError(
                        "authenticated planner required to run revised inputs"
                    )
                required = {"identity", "search", "refine", "budget"}
                if not required <= set(data) or set(data) - required - {"recursive"}:
                    raise ValueError(
                        "explicit revised run search, confirmation and budget required"
                    )
                snapshot = revisions.snapshot(fields[1])
                parent = store.verify_request(snapshot["parent_job"])
                from .recursive_workflow import TUNING

                inherited = parent["request"].get("recursive")
                recursive = data["recursive"] if "recursive" in data else (
                    {key: value for key, value in inherited.items() if key in TUNING}
                    if inherited is not None else None
                )
                req = request(
                    snapshot["problem_id"],
                    snapshot["target_identity"],
                    parent["request"]["candidates"],
                    search=data["search"],
                    refine=data["refine"],
                    budget=data["budget"],
                    reviewed_inputs=snapshot,
                    recursive=recursive,
                )
                revisions.validate_job(req)
                from .contracts import fingerprint

                submission = fingerprint(
                    dict(input_revision=fields[1], request=req, actor=actor["username"])
                )
                payload = dict(
                    job=service.start(req, idempotency_key=submission),
                    child_identity=snapshot["target_identity"],
                    baseline_modified=False,
                    physical_release=False,
                )
        elif path == "jobs":
            if set(data) - {
                "problem",
                "identity",
                "candidates",
                "refine",
                "shortlist",
                "budget",
                "seed",
                "search",
                "interactions",
                "recursive",
            }:
                raise ValueError("unknown job fields")
            payload = service.start(
                request(
                    data["problem"],
                    scope,
                    data.get("candidates"),
                    refine=data.get("refine", False),
                    shortlist=data.get("shortlist", 3),
                    budget=data.get("budget"),
                    seed=data.get("seed", 11),
                    search=data.get("search"),
                    interactions=data.get("interactions"),
                    recursive=data.get("recursive"),
                )
            )
        elif path.startswith("jobs/"):
            fields = path.split("/")
            qualification = len(fields) == 3 and fields[2] == "qualification-draft"
            input_proposal = len(fields) == 3 and fields[2] == "input-revisions"
            if not qualification and not input_proposal and set(data) != {"identity"}:
                raise ValueError("job action accepts only its scoped identity")
            if len(fields) != 3 or fields[2] not in {
                "cancel",
                "resume",
                "export",
                "qualification-draft",
                "input-revisions",
            }:
                raise ValueError("unsupported design job action")
            job = store.get(fields[1])
            if job["city"] != city or job["environment"] != environment:
                raise PermissionError("job belongs to another city/environment")
            for key in ("project", "configuration_revision", "baseline_sha256"):
                if scope[key] != job["request"]["identity"][key]:
                    raise PermissionError(
                        "job belongs to another project/revision/baseline"
                    )
            if input_proposal:
                from .input_revisions import InputRevisions

                report = comparison(store, job["id"])
                candidate = next(
                    (r for r in report["candidates"] if r["id"] == data["candidate"]),
                    None,
                )
                if candidate is None:
                    raise ValueError("unknown parent candidate")
                payload = InputRevisions(store).propose(
                    job,
                    candidate,
                    data,
                    scope,
                    actor,
                    evidence_root=handler.evidence_root,
                )
            elif qualification:
                if set(data) != {
                    "identity",
                    "candidate",
                    "contract_sha256",
                    "kind",
                    "input_json",
                }:
                    raise ValueError(
                        "exact candidate, kind and bounded input JSON draft required"
                    )
                if job["status"] != "completed":
                    raise ValueError(
                        "qualification draft requires a completed candidate artifact"
                    )
                report = comparison(store, job["id"])
                candidate = next(
                    (r for r in report["candidates"] if r["id"] == data["candidate"]),
                    None,
                )
                if candidate is None:
                    raise ValueError("unknown physical candidate")
                payload = qualification_draft(store, job, candidate, data, scope, actor)
            elif fields[2] == "cancel":
                payload = store.cancel(fields[1])
            elif fields[2] == "resume":
                payload = service.resume(fields[1])
            else:
                from .export import export
                import uuid

                destination = (
                    store.root / "exports" / (fields[1] + "-" + uuid.uuid4().hex[:8])
                )
                payload = export(store, fields[1], destination)
                payload["local_output"] = str(destination)
                from .delivery import bundle
                from .contracts import canonical

                download_folder = store.root / "downloads" / destination.name
                receipt = bundle(destination, download_folder)
                (download_folder / "download.json").write_bytes(
                    canonical(receipt) + b"\n"
                )
                payload["download"] = dict(export_id=destination.name, **receipt)
        elif path == "definition-diff":
            from .exchange import definition_diff

            if set(data) not in (
                {"identity", "job", "candidate", "proposed"},
                {"identity", "job", "candidate", "proposed_json"},
            ):
                raise ValueError(
                    "exact source candidate and proposed physical definition required"
                )
            job = store.get(data["job"])
            if job["city"] != city or job["environment"] != environment:
                raise PermissionError("definition is outside the selected scope")
            for key in ("project", "configuration_revision", "baseline_sha256"):
                if scope[key] != job["request"]["identity"][key]:
                    raise PermissionError(
                        "definition belongs to another project/revision/baseline"
                    )
            report = comparison(store, data["job"])
            candidate = next(
                (r for r in report["candidates"] if r["id"] == data["candidate"]), None
            )
            if candidate is None or "contract" not in candidate.get("definition", {}):
                raise ValueError(
                    "candidate has no editable manufactured representation"
                )
            proposed = (
                decode_definition(data["proposed_json"])
                if "proposed_json" in data
                else data["proposed"]
            )
            payload = definition_diff(candidate["definition"]["contract"], proposed)
            store.event(
                job["id"],
                dict(
                    kind="definition-diff-prepared",
                    actor=actor["username"],
                    original=payload["original_sha256"],
                    proposed=payload["proposed_sha256"],
                    baseline_overwrite_permitted=False,
                ),
            )
        elif path == "records":
            if set(data) - {
                "identity",
                "kind",
                "payload",
                "idempotency_key",
                "applicability",
            } or not {"identity", "kind", "payload", "idempotency_key"} <= set(data):
                raise ValueError("controlled record submission required")
            payload = ReviewStore(store).submit(
                city,
                environment,
                data["kind"],
                data["payload"],
                actor["username"],
                data["idempotency_key"],
                identity=scope,
                applicability=data.get("applicability"),
            )
        elif path == "production-plan":
            from .economics import schedule
            from .store import write_new
            from .contracts import fingerprint

            if set(data) != {"identity", "tasks", "resources"}:
                raise ValueError("explicit tasks and resources required")
            payload = schedule(data["tasks"], data["resources"])
            payload.update(identity=scope, actor=actor["username"])
            folder = store.root / "planning-drafts" / fingerprint(data)
            folder.mkdir(parents=True, exist_ok=True)
            if not (folder / "request.json").exists():
                write_new(folder / "request.json", data)
                write_new(folder / "schedule.json", payload)
            payload["draft_sha256"] = fingerprint(data)
        elif path == "records/verify":
            if handler.user_store is None:
                raise PermissionError(
                    "configure named authenticated accounts before independent record verification"
                )
            if set(data) - {"identity", "record", "revision", "applicability"} or not {
                "identity",
                "record",
                "revision",
            } <= set(data):
                raise ValueError("review exact record and revision only")
            payload = ReviewStore(store).verify(
                data["record"],
                data["revision"],
                actor,
                city=city,
                environment=environment,
                evidence_root=handler.evidence_root,
                identity=scope,
                applicability=data.get("applicability"),
            )
        else:
            raise ValueError("unknown design action")
        handler._send_json(200, payload)
    except PermissionError as error:
        handler._send_json(403, dict(error=str(error)))
    except (ValueError, OSError, KeyError, TypeError) as error:
        handler._send_json(400, dict(error=str(error), physical_release=False))
