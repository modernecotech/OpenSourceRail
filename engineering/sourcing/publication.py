"""Reproducible sourcing packets, with immutable observations and exact replay.

Archived source is retained for inspection, never imported or executed. Prices
are historical observations; replay does not fetch today's replacement prices.
"""
from copy import deepcopy
from decimal import localcontext, ROUND_HALF_EVEN
from pathlib import Path
import gzip
import hashlib
import io
import json
import tarfile
import tempfile
from .model import FLAGS, encoded, identity, record, validate_record
from .database import Store
from .inputs import digest, read_json, MAX_JSON_BYTES
from .requirements import extract_requirements, validate_requirements
from .requirements import PRIORITIES
from . import workflow, erp

ROOT = Path(__file__).resolve().parents[2]
BASE_KINDS = {"source", "product", "offer", "fx", "benchmark", "process"}
FILES = {"input.json.gz", "catalogue.json.gz", "request.json", "result.json.gz",
         "records.json.gz", "erp-drafts.json.gz", "summary.json", "sources.tar.gz"}
MAX_FILES_BYTES = 256 * 1024 ** 2


def sources(root=ROOT):
    root = Path(root)
    names = []
    for folder in ("engineering/sourcing", "engineering/component_registry"):
        for path in (root / folder).rglob("*.py"):
            relative = path.relative_to(root).as_posix()
            if "tests" not in path.parts and path.name not in {"cli.py", "__main__.py", "workbench.py"}:
                names.append(relative)
    names += ["engineering/station_rail/common.py", "engineering/station_rail/__init__.py",
              "engineering/reference_cell/__init__.py", "engineering/reference_cell/economics.py",
              "engineering/reference_cell/manufacturing.py"]
    return {name: digest(root / name) for name in sorted(set(names))}


def _source_archive(epoch, root=ROOT):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as tar:
        for name, expected in sorted(epoch.items()):
            raw = (Path(root) / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != expected:
                raise ValueError("Sourcing implementation changed during source snapshot")
            info = tarfile.TarInfo(name); info.size = len(raw); info.mode = 0o644; info.mtime = 0
            tar.addfile(info, io.BytesIO(raw))
    return gzip.compress(stream.getvalue(), mtime=0)


def _write(path, value):
    raw = encoded(value) + b"\n"
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("Sourcing publication JSON budget exceeded")
    Path(path).write_bytes(gzip.compress(raw, mtime=0) if str(path).endswith(".gz") else raw)


def base_snapshot(store, *, required_process_ids=()):
    """Snapshot shared source observations and only the processes this BOM uses.

    A long-lived append-only store can contain processes from earlier candidate
    studies. Including those unrelated records in every later publication makes
    the packet depend on work that its candidate never consumed.
    """
    required_process_ids = set(required_process_ids)
    if any(not isinstance(value, str) or len(value) != 64 for value in required_process_ids):
        raise ValueError("Exact required process record IDs must be supplied")
    values = [value for value in store.all() if value["kind"] in BASE_KINDS and
              (value["kind"] != "process" or value["record_id"] in required_process_ids)]
    included_process_ids = {value["record_id"] for value in values if value["kind"] == "process"}
    if included_process_ids != required_process_ids:
        raise ValueError("Source requirements refer to missing or unrelated process records")
    result = dict(schema="osr-sourcing-input-catalogue/1", records=values)
    result["snapshot_id"] = identity(result)
    return result


def _requirements(twin_input):
    if twin_input.get("schema") != "osr-sourcing-twin-input/1" or twin_input.get("payload_id") != identity(twin_input.get("payload")):
        raise ValueError("Sourcing input envelope differs")
    payload = twin_input["payload"]
    if isinstance(payload, dict) and payload.get("schema") == "osr-sourcing-declared-requirements/1":
        values = payload["requirements"]
        validate_requirements(values)
        if any(value["namespace"] in {"component_registry", "twin-scene", "station-account"} for value in values):
            raise ValueError("Canonical BOM namespaces require the actual typed input, not a declared count list")
        if payload.get("candidate_id") != values[0]["candidate_id"]:
            raise ValueError("Declared requirements candidate differs")
        return values
    return extract_requirements(payload)


def execute(store, twin_input, request, *, root=ROOT):
    """One source/data/request epoch; the caller supplies a calendar estimate date."""
    allowed = {"as_of", "target_currency", "max_fx_age_days", "max_price_age_days",
               "bindings", "max_requirements", "max_requirements_by_category",
               "service_context", "years", "discount_rate"}
    if set(request) - allowed:
        raise ValueError("Unsupported sourcing evaluation request")
    if not request.get("as_of"):
        raise ValueError("Explicit estimate date required")
    before = sources(root)
    # Declared study inputs expose their requirement list by reference. Sorting
    # must not mutate the immutable, payload-hashed input envelope.
    requirements = deepcopy(_requirements(twin_input))
    required_process_ids = {row["process_id"] for row in requirements if row.get("process_id") is not None}
    catalogue = base_snapshot(store, required_process_ids=required_process_ids)
    requirements.sort(key=lambda value: (value.get("priority", 15), value["record_id"]))
    maximum = request.get("max_requirements")
    by_category = request.get("max_requirements_by_category")
    if maximum is not None and by_category is not None:
        raise ValueError("Choose one explicit total or per-category evaluation budget")
    if maximum is not None and (type(maximum) is not int or maximum < 1):
        raise ValueError("Positive explicit requirement budget required")
    if by_category is not None:
        categories = {name for name, _ in PRIORITIES} | {"other"}
        if (not isinstance(by_category, dict) or not by_category or
                set(by_category) - categories or
                any(type(value) is not int or not 1 <= value <= 100000 for value in by_category.values())):
            raise ValueError("Explicit positive bounded per-category requirement budgets required")
        counts = {name: 0 for name in by_category}
        selected, pending = [], []
        for requirement in requirements:
            category = requirement["category"]
            if category in by_category and counts[category] < by_category[category]:
                selected.append(requirement)
                counts[category] += 1
            else:
                pending.append(requirement)
    else:
        selected = requirements if maximum is None else requirements[:maximum]
        pending = [] if maximum is None else requirements[maximum:]
    input_physical_scope_count = len({(value["namespace"], path) for value in requirements for path in (value.get("physical_scopes") or [])})
    input_engineering_occurrence_count = len({(value["namespace"], path) for value in requirements for path in value["occurrence_ids"]})
    input_source_groups = [value for value in requirements if value.get("source_manufacturing_group_id")]
    input_unlocated_account_count = sum(value.get("scope_kind") == "installed-account" for value in requirements)
    arguments = {key: deepcopy(value) for key, value in request.items()
                 if key not in {"max_requirements", "max_requirements_by_category"}}
    with localcontext() as context:
        context.prec = 28; context.rounding = ROUND_HALF_EVEN
        result = workflow.evaluate(store, selected, **arguments)
    fields = {key: deepcopy(value) for key, value in result.items() if key not in {"schema", "kind", "record_id"}}
    fields.update(workflow_run_id=result["record_id"], input_payload_id=twin_input["payload_id"],
                  catalogue_snapshot_id=catalogue["snapshot_id"], request_id=identity(request),
                  source_sha256=before, input_requirement_count=len(requirements),
                  input_physical_scope_count=input_physical_scope_count,
                  input_engineering_occurrence_count=input_engineering_occurrence_count,
                  input_source_manufacturing_group_count=len(input_source_groups),
                  input_source_manufacturing_group_occurrence_count=sum(value.get("engineering_occurrence_count", len(value["occurrence_ids"])) for value in input_source_groups),
                  input_unlocated_account_count=input_unlocated_account_count,
                  evaluated_requirement_count=len(selected), pending_requirement_ids=[value["record_id"] for value in pending],
                  decimal_context=dict(precision=28, rounding="ROUND_HALF_EVEN"))
    fields["summary"].update(
        input_requirement_count=len(requirements),
        input_physical_scope_count=input_physical_scope_count,
        input_engineering_occurrence_count=input_engineering_occurrence_count,
        input_source_manufacturing_group_count=len(input_source_groups),
        input_source_manufacturing_group_occurrence_count=sum(value.get("engineering_occurrence_count", len(value["occurrence_ids"])) for value in input_source_groups),
        input_unlocated_account_count=input_unlocated_account_count)
    result = record("run", **fields)
    if before != sources(root):
        raise ValueError("Sourcing implementation changed during evaluation")
    store.put(result)
    return result


def details(store, result):
    validate_record(result, "run")
    groups = {"requirements": "requirement_ids", "technical_assessments": "technical_assessment_ids",
              "price_assessments": "price_assessment_ids", "RFQ_drafts": "rfq_ids", "redesign_tasks": "redesign_ids"}
    value = {name: [store.get(key) for key in result[field]] for name, field in groups.items()}
    value["overlay"] = store.get(result["overlay_id"], "overlay")
    value["run"] = result
    return value


def summary(store, result):
    backlog = result.get("backlog", [])
    cost_ranked = sum(row.get("sensitivity", {}).get("cost_sensitivity_score") is not None for row in backlog)
    mass_ranked = sum(row.get("sensitivity", {}).get("mass_sensitivity_score_kg") is not None for row in backlog)
    sensitive = sum(row.get("sensitivity", {}).get("cost_sensitivity_score") is not None or
                    row.get("sensitivity", {}).get("mass_sensitivity_score_kg") is not None for row in backlog)
    blockers = sum(row.get("sensitivity", {}).get("safety_or_design_blocker") is True for row in backlog)
    value = dict(schema="osr-sourcing-review-summary/1", run_id=result["record_id"],
                 candidate_id=result["candidate_id"], estimate_date=result["estimate_date"], currency=result["currency"],
                 summary=result["summary"], input_requirement_count=result["input_requirement_count"],
                 input_physical_scope_count=result["input_physical_scope_count"],
                 input_engineering_occurrence_count=result["input_engineering_occurrence_count"],
                 input_source_manufacturing_group_count=result["input_source_manufacturing_group_count"],
                 input_source_manufacturing_group_occurrence_count=result["input_source_manufacturing_group_occurrence_count"],
                 input_unlocated_account_count=result["input_unlocated_account_count"],
                 evaluated_requirement_count=result["evaluated_requirement_count"], pending_requirement_count=len(result["pending_requirement_ids"]),
                 backlog_first_30=backlog[:30], sensitivity_rankable_requirement_count=sensitive,
                 cost_sensitivity_rankable_requirement_count=cost_ranked,
                 mass_sensitivity_rankable_requirement_count=mass_ranked,
                 safety_or_design_blocker_requirement_count=blockers, integrated_winner=None,
                 complete_installed_cost=None, complete_whole_life_cost=None,
                 physical_qualification=None, supplier_communications_sent=0, **FLAGS)
    value["summary_id"] = identity(value)
    return value


def publish(store, result, twin_input, request, output, *, root=ROOT):
    """Write a fresh closed packet; never overwrite an earlier price observation."""
    validate_record(result, "run")
    folder = Path(output)
    if folder.exists() or folder.is_symlink():
        raise ValueError("Fresh sourcing publication directory required")
    if result.get("source_sha256") != sources(root) or result.get("request_id") != identity(request):
        raise ValueError("Sourcing result source/request epoch differs")
    data = details(store, result)
    required_process_ids = {row["process_id"] for row in data["requirements"]
                            if row.get("process_id") is not None}
    catalogue = base_snapshot(store, required_process_ids=required_process_ids)
    if result["catalogue_snapshot_id"] != catalogue["snapshot_id"]:
        raise ValueError("Catalogue changed after sourcing evaluation")
    drafts = erp.delivery_drafts(data["requirements"], data["technical_assessments"])
    folder.mkdir(parents=True)
    try:
        for name, value in (("input.json.gz", twin_input), ("catalogue.json.gz", catalogue),
                            ("request.json", request), ("result.json.gz", result),
                            ("records.json.gz", data), ("erp-drafts.json.gz", drafts),
                            ("summary.json", summary(store, result))):
            _write(folder / name, value)
        (folder / "sources.tar.gz").write_bytes(_source_archive(result["source_sha256"], root))
        files = {name: dict(bytes=(folder/name).stat().st_size, sha256=digest(folder/name)) for name in sorted(FILES)}
        if sum(value["bytes"] for value in files.values()) > MAX_FILES_BYTES:
            raise ValueError("Sourcing publication storage budget exceeded")
        manifest = dict(schema="osr-sourcing-publication/1", execution="completed", run_id=result["record_id"],
                        candidate_id=result["candidate_id"], source_sha256=result["source_sha256"],
                        files=files, source_observations_replaced_during_replay=False,
                        selection_purpose="sourcing-and-next-experiment-review", physical_qualification=None,
                        complete_installed_cost=None, complete_whole_life_cost=None, **FLAGS)
        manifest["publication_id"] = identity(manifest)
        _write(folder / "manifest.json", manifest)
    except BaseException as error:
        _write(folder / "failed-publication.json", dict(execution="failed", reason=type(error).__name__+": "+str(error), physical_qualification=None))
        raise
    return manifest


def verify(output, *, root=ROOT):
    folder = Path(output)
    if folder.is_symlink() or {p.name for p in folder.iterdir()} != FILES | {"manifest.json"}:
        raise ValueError("Exact closed sourcing publication inventory required")
    if any(p.is_symlink() or not p.is_file() for p in folder.iterdir()):
        raise ValueError("Regular publication files required")
    manifest = read_json(folder / "manifest.json")
    if manifest.get("publication_id") != identity({k:v for k,v in manifest.items() if k != "publication_id"}):
        raise ValueError("Sourcing publication identity differs")
    if manifest.get("schema") != "osr-sourcing-publication/1" or manifest.get("execution") != "completed" or manifest.get("source_sha256") != sources(root):
        raise ValueError("Current sourcing implementation differs from publication")
    if any(manifest.get(key) is not expected for key, expected in FLAGS.items()):
        raise ValueError("Unsupported sourcing publication release claim")
    if (manifest.get("physical_qualification") is not None or manifest.get("complete_installed_cost") is not None or
            manifest.get("complete_whole_life_cost") is not None or
            manifest.get("selection_purpose") != "sourcing-and-next-experiment-review" or
            manifest.get("source_observations_replaced_during_replay") is not False):
        raise ValueError("Unsupported sourcing completion claim")
    if set(manifest["files"]) != FILES:
        raise ValueError("Sourcing publication descriptor inventory differs")
    if any(type(item.get("bytes")) is not int or item["bytes"] < 0 for item in manifest["files"].values()) or sum(item["bytes"] for item in manifest["files"].values()) > MAX_FILES_BYTES:
        raise ValueError("Sourcing publication storage budget exceeded")
    for name, expected in manifest["files"].items():
        path = folder / name
        if path.stat().st_size != expected["bytes"] or digest(path) != expected["sha256"]:
            raise ValueError("Sourcing publication payload differs")
    if (folder / "sources.tar.gz").read_bytes() != _source_archive(manifest["source_sha256"], root):
        raise ValueError("Archived sourcing implementation differs")
    catalogue = read_json(folder / "catalogue.json.gz")
    if catalogue.get("snapshot_id") != identity({k:v for k,v in catalogue.items() if k != "snapshot_id"}):
        raise ValueError("Historical observation snapshot differs")
    if any(value["kind"] not in BASE_KINDS for value in catalogue["records"]):
        raise ValueError("Evaluation outputs cannot masquerade as input observations")
    request = read_json(folder / "request.json")
    twin_input = read_json(folder / "input.json.gz")
    saved = read_json(folder / "result.json.gz")
    with tempfile.TemporaryDirectory(prefix="osr-sourcing-replay-") as temp:
        with Store(Path(temp) / "replay.sqlite") as store:
            store.insert_many(catalogue["records"])
            actual = execute(store, twin_input, request, root=root)
            if encoded(actual) != encoded(saved):
                raise ValueError("Actual sourcing workflow replay differs")
            if encoded(details(store, actual)) != encoded(read_json(folder / "records.json.gz")):
                raise ValueError("Price, RFQ or redesign evidence differs")
            if encoded(summary(store, actual)) != encoded(read_json(folder / "summary.json")):
                raise ValueError("Sourcing publication summary differs")
            data = details(store, actual)
            if encoded(erp.delivery_drafts(data["requirements"], data["technical_assessments"])) != encoded(read_json(folder / "erp-drafts.json.gz")):
                raise ValueError("Disabled business drafts differ")
    if manifest["run_id"] != actual["record_id"] or manifest["candidate_id"] != actual["candidate_id"]:
        raise ValueError("Sourcing publication candidate/run binding differs")
    return dict(verified=True, semantic_replay_executed=True, publication_id=manifest["publication_id"],
                run_id=actual["record_id"], candidate_id=actual["candidate_id"],
                evaluated_requirement_count=actual["evaluated_requirement_count"],
                supplier_communications_sent=0, physical_qualification=None, **FLAGS)
