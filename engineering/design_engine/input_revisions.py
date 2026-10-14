"""Independently reviewed research inputs create new, immutable design runs.

File integrity, permission to use an input in a numerical study, and physical
acceptance are separate facts. This module grants neither physical acceptance
nor permission to overwrite the source candidate or adopted baseline.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil
import uuid

from .contracts import canonical, fingerprint, identity, problem_fingerprint
from .engineering_inputs import effective_input, decode_input
from .publication import digest
from .registry import dependencies, get
from .review import ReviewStore, record_applicability, _decoded_record
from .store import now, write_new

KINDS = {"manufacturing", "site", "prestress", "foundation"}


def _actor(actor, city, *, review=False):
    roles = {"admin", "approver"} if review else {"admin", "planner"}
    if (
        not isinstance(actor, dict)
        or not actor.get("username")
        or not roles.intersection(actor.get("roles", []))
    ):
        raise PermissionError(
            "authenticated research input reviewer required"
            if review
            else "authenticated design planner required"
        )
    if city not in actor.get("city_scopes", []) and "*" not in actor.get(
        "city_scopes", []
    ):
        raise PermissionError("account is outside this city")


def _current(job):
    from .runtime import toolchain

    req = job["request"]
    adapter = req["problem"]["adapter"]
    if req["dependencies"] != dependencies(adapter) or req["toolchain"] != toolchain(
        adapter
    ):
        raise ValueError("input revision requires current source and toolchain")


def _source_uses(value):
    """Find every actually used source, without treating free prose as proof."""
    sha, references = set(), set()
    if isinstance(value, dict):
        for key, entry in value.items():
            if key == "source" and isinstance(entry, dict):
                if entry.get("sha256"):
                    sha.add(entry["sha256"])
            elif key == "basis_reference" and entry:
                references.add(entry)
            else:
                a, b = _source_uses(entry)
                sha.update(a)
                references.update(b)
    elif isinstance(value, list):
        for entry in value:
            a, b = _source_uses(entry)
            sha.update(a)
            references.update(b)
    return sha, references


class InputRevisions:
    def __init__(self, store):
        self.store = store
        ReviewStore(store)
        with store.connect() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS design_input_revisions(
                    id TEXT PRIMARY KEY, parent_job TEXT NOT NULL, creator TEXT NOT NULL,
                    created TEXT NOT NULL, identity TEXT NOT NULL, target_identity TEXT NOT NULL,
                    proposal TEXT NOT NULL, proposal_sha256 TEXT NOT NULL,
                    state TEXT NOT NULL, review TEXT
                );
                CREATE TABLE IF NOT EXISTS design_input_events(
                    sequence INTEGER PRIMARY KEY, revision TEXT NOT NULL,
                    time TEXT NOT NULL, actor TEXT NOT NULL, payload TEXT NOT NULL
                );
            """)

    def _event(self, con, identifier, actor, event):
        con.execute(
            "INSERT INTO design_input_events(revision,time,actor,payload) VALUES(?,?,?,?)",
            (identifier, now(), actor, canonical(event).decode()),
        )

    def get(self, identifier):
        if not isinstance(identifier, str) or not re.fullmatch(
            r"inputs-[a-f0-9]{16}", identifier
        ):
            raise ValueError("controlled input revision ID required")
        with self.store.connect() as con:
            raw = con.execute(
                "SELECT * FROM design_input_revisions WHERE id=?", (identifier,)
            ).fetchone()
        if raw is None:
            raise ValueError("unknown input revision")
        row = dict(raw)
        for key in ("identity", "target_identity", "proposal", "review"):
            row[key] = json.loads(row[key]) if row[key] else None
        path = self.store.root / "input-revisions" / identifier / "proposal.json"
        if (
            load_equal(path, row["proposal"]) is not True
            or fingerprint(row["proposal"]) != row["proposal_sha256"]
        ):
            raise ValueError("input proposal content changed")
        if row["review"] is not None and not load_equal(
            path.with_name("review.json"), row["review"]
        ):
            raise ValueError("input review content changed")
        for record in row["proposal"]["records"]:
            source = path.parent / "sources" / record["evidence"]["sha256"]
            if (
                source.is_symlink()
                or not source.is_file()
                or digest(source) != record["evidence"]["sha256"]
            ):
                raise ValueError("immutable reviewed source snapshot changed")
        row.update(physical_release=False, baseline_modified=False)
        return row

    def list(self, scope):
        scope = identity(scope)
        with self.store.connect() as con:
            identifiers = [
                r[0]
                for r in con.execute(
                    "SELECT id FROM design_input_revisions WHERE identity=? ORDER BY created DESC LIMIT 200",
                    (canonical(scope).decode(),),
                )
            ]
        return [self.get(identifier) for identifier in identifiers]

    def _records(self, bindings, scope, candidate, contract, *, evidence_root):
        if not isinstance(bindings, list) or not 1 <= len(bindings) <= 64:
            raise ValueError("one or more exact verified evidence bindings required")
        known, seen = [], set()
        physical = {r["id"] for r in contract["parts"]}
        definition_sha = fingerprint(contract)
        root = Path(evidence_root).resolve()
        for binding in bindings:
            if (
                not isinstance(binding, dict)
                or set(binding) != {"id", "revision", "applicability"}
                or binding["id"] in seen
            ):
                raise ValueError(
                    "distinct exact record ID, revision and applicability required"
                )
            seen.add(binding["id"])
            with self.store.connect() as con:
                raw = con.execute(
                    "SELECT * FROM review_records WHERE id=?", (binding["id"],)
                ).fetchone()
            if raw is None:
                raise ValueError("unknown source evidence record")
            record = _decoded_record(dict(raw))
            app = binding["applicability"]
            if (
                app.get("candidate_id") != candidate["id"]
                or app.get("definition_sha256") != definition_sha
            ):
                raise ValueError(
                    "source record must explicitly target this candidate and definition"
                )
            if (
                app.get("physical_part_id") is not None
                and app["physical_part_id"] not in physical
            ):
                raise ValueError("source record refers to an absent physical part")
            if record["revision"] != binding["revision"]:
                raise ValueError("source evidence revision changed")
            check = record_applicability(record, scope, app)
            if not check["eligible"]:
                raise ValueError(
                    "inapplicable source evidence: " + "; ".join(check["reasons"])
                )
            reference = record["payload"].get("source_reference") or record[
                "payload"
            ].get("identity_reference")
            if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
                raise ValueError("retained source document required")
            name = Path(reference["path"])
            path = root / name
            if (
                name.is_absolute()
                or ".." in name.parts
                or path.is_symlink()
                or not path.resolve().is_relative_to(root)
                or not path.is_file()
                or digest(path) != reference["sha256"]
            ):
                raise ValueError("retained source evidence changed or is unavailable")
            known.append(
                dict(
                    id=record["id"],
                    revision=record["revision"],
                    kind=record["kind"],
                    identity=record["identity"],
                    applicability=record["applicability"],
                    evidence=reference,
                )
            )
        return known

    def propose(self, parent_job, candidate, data, scope, actor, *, evidence_root):
        scope = deepcopy(identity(scope))
        _actor(actor, scope["city"])
        _current(parent_job)
        if scope != parent_job["request"]["identity"]:
            raise PermissionError("input revision requires the exact parent identity")
        if data.get("identity") != scope:
            raise PermissionError("submitted input identity differs from its parent")
        if (
            scope["baseline_sha256"] is None
            or scope["configuration_revision"] == "unselected"
        ):
            raise ValueError(
                "choose a known research baseline and revision before binding engineering evidence"
            )
        if set(data) != {
            "identity",
            "candidate",
            "drafts",
            "records",
            "configuration_revision",
            "rationale",
            "policy",
        }:
            raise ValueError(
                "exact parent, drafts, source bindings, new revision, rationale and policy required"
            )
        if data["candidate"] != candidate["id"]:
            raise ValueError("input revision targets another candidate")
        revision = data["configuration_revision"]
        if (
            not isinstance(revision, str)
            or not 1 <= len(revision) <= 160
            or revision == scope["configuration_revision"]
        ):
            raise ValueError("distinct named configuration revision required")
        if (
            not isinstance(data["rationale"], str)
            or not data["rationale"].strip()
            or len(data["rationale"]) > 8000
        ):
            raise ValueError("bounded input-change rationale required")
        if data["policy"] not in {"exact-definition", "retained-physical-ids"}:
            raise ValueError("explicit engineering input applicability policy required")
        contract = candidate.get("definition", {}).get("contract")
        if not contract:
            raise ValueError(
                "reviewed engineering inputs require an actual manufacturing contract"
            )
        records = self._records(
            data["records"], scope, candidate, contract, evidence_root=evidence_root
        )
        available_sha = {r["evidence"]["sha256"] for r in records}
        available_refs = {
            v
            for r in records
            for v in (r["id"], r["evidence"]["path"], r["evidence"]["sha256"])
        }
        draft_ids = data["drafts"]
        if (
            not isinstance(draft_ids, list)
            or not 1 <= len(draft_ids) <= 4
            or len(set(draft_ids)) != len(draft_ids)
        ):
            raise ValueError("one to four distinct retained input drafts required")
        inputs, original = {}, []
        for sha in draft_ids:
            if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{64}", sha):
                raise ValueError("exact retained draft hash required")
            folder = self.store.root / "planning-drafts" / ("qualification-" + sha)
            from .contracts import load

            submitted, assessment = load(folder / "request.json"), load(
                folder / "assessment.json"
            )
            if (
                assessment["draft_sha256"] != sha
                or fingerprint(dict(request=submitted, actor=assessment["actor"]))
                != sha
            ):
                raise ValueError("input draft content changed")
            if (
                submitted["identity"] != scope
                or submitted["candidate"] != candidate["id"]
                or submitted["contract_sha256"] != fingerprint(contract)
            ):
                raise ValueError("input draft is outside the parent scope")
            kind = submitted["kind"]
            if kind not in KINDS or kind in inputs:
                raise ValueError(
                    "one draft per applicable engineering input kind required"
                )
            # Retained JSON text is decoded with the same duplicate/nonfinite guard.
            entered = decode_input(submitted["input_json"])
            if fingerprint(entered) != assessment["input_sha256"]:
                raise ValueError("input assessment refers to altered source values")
            effective = effective_input(kind, contract, scope, entered)
            if effective is None:
                raise ValueError(
                    "blank input templates cannot become reviewed engineering inputs"
                )
            if kind != "manufacturing" and data["policy"] != "exact-definition":
                raise ValueError(
                    "site and prestress records require their exact physical definition"
                )
            sha_uses, reference_uses = _source_uses(effective)
            if not sha_uses <= available_sha or not reference_uses <= available_refs:
                raise ValueError(
                    "each applied source must bind an applicable verified retained document"
                )
            if not sha_uses and not reference_uses:
                raise ValueError("reviewed inputs cannot omit their source evidence")
            inputs[kind] = effective
            original.append(dict(sha256=sha, assessment_sha256=fingerprint(assessment)))
        inherited = parent_job["request"].get("reviewed_inputs")
        if inherited:
            inputs = {**deepcopy(inherited["inputs"]), **inputs}
        if (
            any(key in inputs for key in ("site", "prestress", "foundation"))
            and data["policy"] != "exact-definition"
        ):
            raise ValueError(
                "inherited site/prestress inputs cannot acquire broader geometry applicability"
            )
        target = {**scope, "configuration_revision": revision, "run_id": None}
        proposal = dict(
            schema="osr-reviewed-input-proposal/1",
            parent_job=parent_job["id"],
            parent_request_sha256=fingerprint(parent_job["request"]),
            parent_candidate=candidate["id"],
            parent_definition_sha256=fingerprint(contract),
            parent_geometry_sha256=geometry_fingerprint(contract),
            base_problem_sha256=problem_fingerprint(
                get(parent_job["request"]["problem"]["id"])
            ),
            problem_id=parent_job["request"]["problem"]["id"],
            source_identity=scope,
            target_identity=target,
            inputs=inputs,
            draft_references=original,
            records=records,
            policy=data["policy"],
            rationale=data["rationale"],
            creator=actor["username"],
            invalidated=[
                "geometry",
                "BOM",
                "mass-cg-inertia",
                "screens",
                "fault-holdout-confirmation",
                "cost-objectives",
                "CAD-drawings",
                "inspection-applicability",
                "optimisation",
            ],
            physical_release=False,
            production_released=False,
            baseline_modified=False,
        )
        identifier = "inputs-" + uuid.uuid4().hex[:16]
        sha = fingerprint(proposal)
        with self.store.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            prior = con.execute(
                "SELECT id,proposal_sha256 FROM design_input_revisions WHERE target_identity=?",
                (canonical(target).decode(),),
            ).fetchone()
            if prior is not None:
                if prior["proposal_sha256"] == sha:
                    return self.get(prior["id"])
                raise ValueError(
                    "this target revision already has an immutable input proposal"
                )
            write_new(
                self.store.root / "input-revisions" / identifier / "proposal.json",
                proposal,
            )
            for record in records:
                source = Path(evidence_root).resolve() / record["evidence"]["path"]
                destination = (
                    self.store.root
                    / "input-revisions"
                    / identifier
                    / "sources"
                    / record["evidence"]["sha256"]
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    shutil.copyfile(source, destination)
                if digest(destination) != record["evidence"]["sha256"]:
                    raise ValueError(
                        "source document changed during immutable input snapshot"
                    )
            con.execute(
                "INSERT INTO design_input_revisions VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    identifier,
                    parent_job["id"],
                    actor["username"],
                    now(),
                    canonical(scope).decode(),
                    canonical(target).decode(),
                    canonical(proposal).decode(),
                    sha,
                    "proposed",
                    None,
                ),
            )
            self._event(
                con, identifier, actor["username"], dict(kind="proposed", sha256=sha)
            )
        return self.get(identifier)

    def review(self, identifier, expected_sha, scope, actor, rationale):
        scope = identity(scope)
        _actor(actor, scope["city"], review=True)
        if (
            not isinstance(rationale, str)
            or not rationale.strip()
            or len(rationale) > 8000
        ):
            raise ValueError("bounded independent input-use rationale required")
        row = self.get(identifier)
        if row["identity"] != scope:
            raise PermissionError("review refers to another exact identity")
        if row["creator"] == actor["username"]:
            raise PermissionError(
                "input proposal author cannot review their own proposal"
            )
        _current(self.store.verify_request(row["parent_job"]))
        decision = dict(
            schema="osr-research-input-review/1",
            proposal_sha256=expected_sha,
            reviewer=actor["username"],
            reviewed_at=now(),
            rationale=rationale,
            permitted_use="new numerical research revision only",
            technical_acceptance=False,
            physical_release=False,
        )
        with self.store.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            current = con.execute(
                "SELECT state,proposal_sha256 FROM design_input_revisions WHERE id=?",
                (identifier,),
            ).fetchone()
            if (
                current["state"] != "proposed"
                or current["proposal_sha256"] != expected_sha
            ):
                if (
                    current["state"] == "reviewed-input"
                    and current["proposal_sha256"] == expected_sha
                ):
                    retained = self.get(identifier)
                    if (
                        retained["review"]["reviewer"] == actor["username"]
                        and retained["review"]["rationale"] == rationale
                    ):
                        return retained
                raise ValueError("input review needs the exact unreviewed proposal")
            write_new(
                self.store.root / "input-revisions" / identifier / "review.json",
                decision,
            )
            con.execute(
                "UPDATE design_input_revisions SET state='reviewed-input',review=? WHERE id=?",
                (canonical(decision).decode(), identifier),
            )
            self._event(
                con,
                identifier,
                actor["username"],
                dict(kind="reviewed-for-research", proposal_sha256=expected_sha),
            )
        return self.get(identifier)

    def snapshot(self, identifier):
        row = self.get(identifier)
        if (
            row["state"] != "reviewed-input"
            or not row["review"]
            or row["review"]["proposal_sha256"] != row["proposal_sha256"]
        ):
            raise ValueError("independent input-use review required before a new run")
        proposal = row["proposal"]
        return {
            **deepcopy(proposal),
            "schema": "osr-reviewed-job-inputs/1",
            "id": identifier,
            "proposal_sha256": row["proposal_sha256"],
            "review_sha256": fingerprint(row["review"]),
        }

    def validate_job(self, request, _seen=None):
        snapshot = request.get("reviewed_inputs")
        expected_problem = get(request["problem"]["id"])
        expected_problem["budget"] = request["problem"]["budget"]
        if snapshot is not None:
            expected_problem["revision"] += (
                "+inputs-" + snapshot["proposal_sha256"][:16]
            )
        if fingerprint(expected_problem) != fingerprint(request["problem"]):
            raise ValueError(
                "job altered its controlled functional problem or mandatory checks"
            )
        if snapshot is None:
            return None
        seen = set() if _seen is None else set(_seen)
        if snapshot["id"] in seen or len(seen) >= 32:
            raise ValueError("reviewed input lineage is cyclic or exceeds its bound")
        seen.add(snapshot["id"])
        expected = self.snapshot(snapshot["id"])
        if (
            fingerprint(snapshot) != fingerprint(expected)
            or request["identity"] != expected["target_identity"]
        ):
            raise ValueError(
                "job changed the reviewed immutable inputs or target scope"
            )
        parent = self.store.verify_request(expected["parent_job"])
        _current(parent)
        if fingerprint(parent["request"]) != expected["parent_request_sha256"]:
            raise ValueError("input revision lineage changed")
        self.validate_job(parent["request"], seen)
        return snapshot

    def source_directories(self, request):
        """Validated immutable proposal/review/document directories for export."""
        self.validate_job(request)
        directories = []
        seen = set()
        while request.get("reviewed_inputs"):
            snapshot = request["reviewed_inputs"]
            if snapshot["id"] in seen or len(seen) >= 32:
                raise ValueError("input source lineage is cyclic or too deep")
            seen.add(snapshot["id"])
            directories.append(self.store.root / "input-revisions" / snapshot["id"])
            request = self.store.verify_request(snapshot["parent_job"])["request"]
        return directories


def load_equal(path, value):
    from .contracts import load

    return fingerprint(load(path)) == fingerprint(value)


def geometry_fingerprint(contract):
    # Manufacturing constraints are reviewed separately from the unchanged
    # physical definition. Every physical/material/analysis field still binds.
    return fingerprint(
        {key: value for key, value in contract.items() if key != "manufacturing_plan"}
    )


def apply_reviewed_inputs(definition, snapshot, scope):
    """Apply reviewed facts before rebuilding all derived registers and checks."""
    if snapshot is None:
        return
    contract = definition.get("contract")
    if contract is None:
        raise ValueError(
            "reviewed inputs cannot attach to an unrepresented physical assembly"
        )
    if (
        snapshot["policy"] == "exact-definition"
        and geometry_fingerprint(contract) != snapshot["parent_geometry_sha256"]
    ):
        raise ValueError("reviewed inputs are outside their exact physical definition")
    inputs = deepcopy(snapshot["inputs"])
    if "manufacturing" in inputs:
        contract["manufacturing_plan"] = inputs["manufacturing"]
    # Civil facts remain explicitly bound to their source definition. The target
    # is a new revision of that same geometry; this is no geometric extrapolation.
    for key in ("site", "prestress", "foundation"):
        if key in inputs:
            inputs[key]["identity"] = deepcopy(scope)
            inputs[key]["contract_sha256"] = fingerprint(contract)
    definition["reviewed_engineering_inputs"] = inputs
    definition["input_lineage"] = dict(
        id=snapshot["id"],
        proposal_sha256=snapshot["proposal_sha256"],
        parent_candidate=snapshot["parent_candidate"],
        source_definition_sha256=snapshot["parent_definition_sha256"],
        invalidated=deepcopy(snapshot["invalidated"]),
        physical_release=False,
    )
