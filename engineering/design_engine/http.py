"""Allowlisted Workbench design APIs; no browser-to-shell command surface."""

from __future__ import annotations
import json
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlsplit

from .contracts import load, identity
from .registry import ROOT, problems, dependencies
from .runtime import Manager, request, comparison, toolchain, preflight
from .review import ReviewStore, REQUIRED

LOCK = threading.Lock()


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
        if path == "problems":
            registered = list(problems().values())
            payload = dict(
                problems=registered,
                preflight={p["id"]: preflight(p) for p in registered},
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
            payload = dict(records=ReviewStore(store).list(city, environment))
        elif path == "cost-objectives":
            from datetime import date
            from .economics import installed_objectives

            payload = installed_objectives(
                ReviewStore(store).list(city, environment),
                place=query.get("place", [city])[0],
                currency=query.get("currency", ["USD"])[0],
                as_of=query.get("as_of", [date.today().isoformat()])[0],
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
        if path == "jobs":
            if set(data) - {
                "problem",
                "identity",
                "candidates",
                "refine",
                "shortlist",
                "budget",
                "seed",
                "search",
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
                )
            )
        elif path.startswith("jobs/"):
            fields = path.split("/")
            if set(data) != {"identity"}:
                raise ValueError("job action accepts only its scoped identity")
            if len(fields) != 3 or fields[2] not in {"cancel", "resume", "export"}:
                raise ValueError("unsupported design job action")
            job = store.get(fields[1])
            if job["city"] != city or job["environment"] != environment:
                raise PermissionError("job belongs to another city/environment")
            for key in ("project", "configuration_revision", "baseline_sha256"):
                if scope[key] != job["request"]["identity"][key]:
                    raise PermissionError(
                        "job belongs to another project/revision/baseline"
                    )
            if fields[2] == "cancel":
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

            if set(data) != {"identity", "job", "candidate", "proposed"}:
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
            payload = definition_diff(
                candidate["definition"]["contract"], data["proposed"]
            )
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
            if set(data) != {"identity", "kind", "payload", "idempotency_key"}:
                raise ValueError("controlled record submission required")
            payload = ReviewStore(store).submit(
                city,
                environment,
                data["kind"],
                data["payload"],
                actor["username"],
                data["idempotency_key"],
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
            if set(data) != {"identity", "record", "revision"}:
                raise ValueError("review exact record and revision only")
            payload = ReviewStore(store).verify(
                data["record"],
                data["revision"],
                actor,
                city=city,
                environment=environment,
                evidence_root=handler.evidence_root,
            )
        else:
            raise ValueError("unknown design action")
        handler._send_json(200, payload)
    except PermissionError as error:
        handler._send_json(403, dict(error=str(error)))
    except (ValueError, OSError, KeyError, TypeError) as error:
        handler._send_json(400, dict(error=str(error), physical_release=False))
