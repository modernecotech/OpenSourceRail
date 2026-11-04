"""Small, source-traced reference libraries; no automatic engineering approval.

Apache-2.0 executable implementation. Imported records retain their own declared
licenses; a permission declaration is not an independent legal determination.
"""
from copy import deepcopy
from hashlib import sha256
from math import isfinite, fsum, prod
from pathlib import Path
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[2]
KINDS = ("functional-patterns", "physical-solutions", "production-methods")
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             movement_authority=False)
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_BYTES = 2 * 1024 * 1024
OWNED_BRIDGE_SHA256 = "4b10c685df322b87d7ac245331e6c5752e6a96bebd9787a8a2b4868ccf7b59ca"


def encoded(value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    if len(raw) > MAX_BYTES:
        raise ValueError("Bounded reference record required")
    return raw


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _seal(value, key):
    value = deepcopy(value)
    value[key] = identity(value)
    return value


def _checked(value, key):
    if not isinstance(value, dict) or value.get(key) != identity({k: v for k, v in value.items() if k != key}):
        raise ValueError("Reference identity differs: " + key)
    return deepcopy(value)


def _repo_file(root, uri):
    relative = Path(uri.removeprefix("repo:"))
    if not uri.startswith("repo:") or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Ordinary repository-relative source required")
    root = Path(root).resolve(); target = root / relative
    if not target.is_file() or any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError("Ordinary source file required")
    if target.stat().st_size > MAX_BYTES:
        raise ValueError("Source exceeds reference byte budget")
    return target


def make_record(kind, *, name, origin, rights, evidence, interfaces=(),
                behavior_fixtures=(), geometry_candidates=(), material_candidates=(),
                process_candidates=(), related_record_ids=(), unresolved_tasks=(),
                artifact_bytes=None, root=None):
    """Create an immutable record. Unknown rights/source authenticity stay explicit."""
    origin = deepcopy(origin)
    if kind not in KINDS or not isinstance(name, str) or not name:
        raise ValueError("Named reference library kind required")
    if not SHA.fullmatch(str(origin.get("artifact_sha256", ""))) or not origin.get("uri"):
        raise ValueError("Origin URI and artifact SHA-256 required")
    if origin.get("source_class") not in ("A", "B", "C", "unknown"):
        raise ValueError("Explicit source class required")
    if origin.get("source_kind") not in ("owned-source", "authorized-observation", "reported-observation", "published-reference", "mesh", "cad", "assumption"):
        raise ValueError("Explicit source kind required")
    verified = False
    if artifact_bytes is not None:
        if not isinstance(artifact_bytes, bytes) or len(artifact_bytes) > MAX_BYTES:
            raise ValueError("Bounded artifact bytes required")
        if sha256(artifact_bytes).hexdigest() != origin["artifact_sha256"]:
            raise ValueError("Artifact bytes differ from declared origin")
        verified = True
    if origin["uri"].startswith("repo:") and root is not None:
        if sha256(_repo_file(root, origin["uri"]).read_bytes()).hexdigest() != origin["artifact_sha256"]:
            raise ValueError("Repository source differs from declared origin")
        verified = True
    value = dict(schema="osr-outline-reference/1", kind=kind, name=name,
        origin=origin, source_bytes_verified_at_import=verified, rights=deepcopy(rights),
        evidence=list(deepcopy(evidence)), interface_contracts=list(deepcopy(interfaces)),
        behavior_fixtures=list(deepcopy(behavior_fixtures)), geometry_candidates=list(deepcopy(geometry_candidates)),
        material_candidates=list(deepcopy(material_candidates)), process_candidates=list(deepcopy(process_candidates)),
        related_record_ids=list(related_record_ids), unresolved_tasks=list(unresolved_tasks),
        implementation_reuse_allowed=False, authorization_verification="declaration-only",
        physical_measurement_implied=False, **FLAGS)
    value["implementation_reuse_allowed"] = _reuse_allowed(value)
    return validate_record(_seal(value, "record_id"), root=root)


def _reuse_allowed(value):
    rights = value["rights"]
    return (rights.get("permitted_use") == "implementation"
        and rights.get("authorization", {}).get("status") == "authorized"
        and "implementation" in rights.get("authorization", {}).get("scope", [])
        and rights.get("spdx") not in (None, "", "unknown")
        and value.get("source_bytes_verified_at_import") is True)


def validate_record(record, *, root=None):
    value = _checked(record, "record_id")
    if value.get("schema") != "osr-outline-reference/1" or value.get("kind") not in KINDS:
        raise ValueError("Reference schema/kind differs")
    if any(value.get(k) is not False for k in FLAGS) or value.get("physical_measurement_implied") is not False:
        raise ValueError("Reference evidence cannot grant physical acceptance")
    origin = value["origin"]; rights = value["rights"]
    if (not value.get("name") or not origin.get("uri")
            or origin.get("source_class") not in ("A", "B", "C", "unknown")
            or origin.get("source_kind") not in ("owned-source", "authorized-observation", "reported-observation", "published-reference", "mesh", "cad", "assumption")):
        raise ValueError("Explicit named source provenance required")
    if not SHA.fullmatch(str(origin.get("artifact_sha256", ""))):
        raise ValueError("Origin artifact digest required")
    if rights.get("permitted_use") not in ("unknown", "reference-only", "implementation", "prohibited"):
        raise ValueError("Declared permitted use required")
    auth = rights.get("authorization", {})
    if auth.get("status") not in ("authorized", "unknown", "prohibited") or not isinstance(auth.get("scope", []), list):
        raise ValueError("Explicit authorization declaration required")
    if auth.get("status") == "authorized" and not auth.get("basis"):
        raise ValueError("Authorization basis required")
    if value.get("implementation_reuse_allowed") is not _reuse_allowed(value):
        raise ValueError("Unknown/restricted evidence cannot become implementation permission")
    if not isinstance(value.get("evidence"), list) or not value["evidence"]:
        raise ValueError("Evidence observations required")
    for row in value["evidence"]:
        if row.get("kind") not in ("source-inspection", "software-observation", "calculated-geometry", "physical-measurement", "assumption", "synthetic-fixture"):
            raise ValueError("Observation must distinguish measurement and assumption")
        if not row.get("claim") or row.get("uncertainty") is None:
            raise ValueError("Claim and explicit uncertainty required")
        if row["kind"] == "physical-measurement" and not (row.get("instrument") and row.get("unit") and row.get("measurement_artifact_sha256")):
            raise ValueError("Physical measurement needs instrument, unit and source artifact")
    for fixture in value["behavior_fixtures"]:
        if fixture.get("method") not in ("source-derived", "offline-python-owned-source", "imported-observation", "synthetic"):
            raise ValueError("Fixture method must identify what was actually executed")
        if fixture.get("rea_executed") is not False:
            raise ValueError("This adapter does not establish execution of REA")
    if root is not None and origin.get("uri", "").startswith("repo:"):
        if sha256(_repo_file(root, origin["uri"]).read_bytes()).hexdigest() != origin["artifact_sha256"]:
            raise ValueError("Current source differs from immutable reference")
    return value


def new_library():
    return _seal(dict(schema="osr-outline-reference-library/1", records={k: [] for k in KINDS}, **FLAGS), "library_id")


def validate(library, *, root=None):
    value = _checked(library, "library_id")
    if value.get("schema") != "osr-outline-reference-library/1" or set(value.get("records", {})) != set(KINDS):
        raise ValueError("Three connected reference libraries required")
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError("Library cannot release physical work")
    records = [validate_record(r, root=root) for kind in KINDS for r in value["records"][kind]]
    ids = {r["record_id"] for r in records}
    if len(ids) != len(records):
        raise ValueError("Duplicate immutable reference")
    for kind in KINDS:
        for record in value["records"][kind]:
            if record["kind"] != kind or not set(record["related_record_ids"]) <= ids:
                raise ValueError("Broken cross-library reference")
    return value


def register(library, record, *, root=None):
    value = validate(library, root=root); record = validate_record(record, root=root)
    value.pop("library_id")
    value["records"][record["kind"]].append(record)
    value["records"][record["kind"]].sort(key=lambda r: r["record_id"])
    return validate(_seal(value, "library_id"), root=root)


def export_library(library, output=None, *, root=None):
    value = validate(library, root=root)
    if output is None:
        return value
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError("Fresh immutable library output required")
    output.mkdir(parents=True)
    (output / "library.json").write_bytes(encoded(value))
    manifest = _seal(dict(schema="osr-outline-reference-export/1", library_id=value["library_id"],
        files={"library.json": sha256(encoded(value)).hexdigest()}, **FLAGS), "manifest_id")
    (output / "manifest.json").write_bytes(encoded(manifest))
    return manifest


def recover_box_ascii_stl(raw, *, units, uncertainty_m):
    """Recover only a closed oriented axis-aligned box; reject arbitrary meshes."""
    if units not in ("m", "mm", "cm") or not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ValueError("Bounded ASCII STL and explicit supported units required")
    if type(uncertainty_m) not in (int, float) or not isfinite(uncertainty_m) or uncertainty_m < 0:
        raise ValueError("Finite nonnegative geometric uncertainty required")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as e:
        raise ValueError("ASCII STL only; binary/other geometry needs an external adapter") from e
    tokens = text.split(); triangles = []; current = []
    if not tokens or tokens[0] != "solid" or "endsolid" not in tokens:
        raise ValueError("ASCII STL solid required")
    for line in text.splitlines():
        fields = line.strip().split()
        if not fields:
            continue
        if fields[0] == "vertex":
            if len(fields) != 4:
                raise ValueError("Three finite coordinates required")
            vertex = tuple(float(x) * {"m": 1, "mm": .001, "cm": .01}[units] for x in fields[1:])
            if not all(isfinite(x) for x in vertex):
                raise ValueError("Finite mesh coordinates required")
            current.append(vertex)
        elif fields[0] == "endfacet":
            if len(current) != 3:
                raise ValueError("Triangular facets required")
            triangles.append(tuple(current)); current = []
        elif fields[0] not in ("solid", "endsolid", "facet", "outer", "endloop"):
            raise ValueError("Unexpected ASCII STL content")
    if current or len(triangles) != 12:
        raise ValueError("Only twelve-triangle box fixtures are recoverable here")
    vertices = set(v for t in triangles for v in t)
    if len(vertices) != 8:
        raise ValueError("Eight exact box corners required")
    low = [min(v[i] for v in vertices) for i in range(3)]
    high = [max(v[i] for v in vertices) for i in range(3)]
    dimensions = [high[i] - low[i] for i in range(3)]
    if min(dimensions) < 1e-9 or max(dimensions) > 1e6 or any(v[i] not in (low[i], high[i]) for v in vertices for i in range(3)):
        raise ValueError("Mesh is outside the axis-aligned box domain")
    directed = {}; faces = set(); volumes = []
    for tri in triangles:
        key = frozenset(tri)
        if len(key) != 3 or key in faces or not any(len({v[i] for v in tri}) == 1 for i in range(3)):
            raise ValueError("Distinct nondegenerate box-plane triangles required")
        faces.add(key)
        p, q, r = tri
        local_p, local_q, local_r = [tuple(v[i]-low[i] for i in range(3)) for v in tri]
        cross = (local_q[1]*local_r[2]-local_q[2]*local_r[1], local_q[2]*local_r[0]-local_q[0]*local_r[2], local_q[0]*local_r[1]-local_q[1]*local_r[0])
        volumes.append(fsum(local_p[i]*cross[i] for i in range(3))/6)
        for start, end in ((p, q), (q, r), (r, p)):
            directed[(start, end)] = directed.get((start, end), 0) + 1
    if any(count != 1 or directed.get((end, start)) != 1 for (start, end), count in directed.items()):
        raise ValueError("Closed consistently oriented two-manifold mesh required")
    expected = prod(dimensions); volume = abs(fsum(volumes))
    if abs(volume-expected) > max(expected*1e-9, 1e-15):
        raise ValueError("Mesh volume does not match the primitive")
    result = dict(schema="osr-outline-box-recovery/1", input_sha256=sha256(raw).hexdigest(), input_units=units,
        uncertainty_m=uncertainty_m, primitive="axis-aligned-box", origin_m=low, dimensions_m=dimensions,
        volume_m3=volume, bounding_box_volume_m3=expected, watertight=True, consistently_oriented=True,
        fixture_domain="exact twelve-triangle axis-aligned box only", method="bounded-python-geometric-reconstruction",
        topology_and_volume_verified=True, CAD_export_executed=False, physical_material=None,
        arbitrary_organic_reconstruction=False, **FLAGS)
    return _seal(result, "geometry_evaluation_id")


def owned_pilot(root=ROOT):
    """Actually call the existing offline draft bridge; never send a transaction."""
    root = Path(root).resolve(); source = "services/integration/osr_integration/reference_cell.py"
    raw = _repo_file(root, "repo:"+source).read_bytes()
    if sha256(raw).hexdigest() != OWNED_BRIDGE_SHA256:
        raise ValueError("Owned pilot source changed; review its new behavior before execution")
    spec = importlib.util.spec_from_file_location("osr_outline_owned_bridge", root/source)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    candidate = identity({"owned-software-fixture": 1})
    report = dict(candidate_id=candidate, body_candidate_id="fixture-body",
        manufacturing=dict(candidate_id=candidate, ERPNext=dict(external_transactions_performed=False,
            production_orders=[], items=[dict(name="fixture-disabled", disabled=1)])),
        bundle=dict(candidate_id=candidate, mass_registry_revision_id="fixture-registry"),
        civil=dict(construction_sequence=[]))
    observed = module.delivery_drafts(deepcopy(report))
    tampered = deepcopy(report); tampered["manufacturing"]["ERPNext"]["items"][0]["disabled"] = 0
    try:
        module.delivery_drafts(tampered)
    except ValueError as error:
        rejected = str(error)
    else:
        raise ValueError("Owned pilot unexpectedly accepted live items")
    mixed = deepcopy(report); mixed["manufacturing"]["candidate_id"] = "another-candidate"
    try:
        module.delivery_drafts(mixed)
    except ValueError as error:
        mixed_rejected = str(error)
    else:
        raise ValueError("Owned pilot unexpectedly accepted mixed candidate identities")
    origin = dict(uri="repo:"+source, artifact_sha256=sha256(raw).hexdigest(), source_kind="owned-source", source_class="B", version="source-digest")
    rights = dict(spdx="Apache-2.0", permitted_use="implementation", authorization=dict(status="authorized",
        basis="Owned OpenSourceRail software, repository LICENSES path mapping", scope=["analysis", "implementation"]))
    fixtures = [dict(name="disabled-draft", input=report, observed=observed, expected=dict(live_movement_authority=False, active_orders_mutated=False),
        method="offline-python-owned-source", rea_executed=False), dict(name="active-item-refusal", input=tampered,
        observed_error=rejected, method="offline-python-owned-source", rea_executed=False),
        dict(name="mixed-candidate-refusal", input=mixed, observed_error=mixed_rejected, method="offline-python-owned-source", rea_executed=False)]
    pattern = make_record("functional-patterns", name="Candidate-bound disabled delivery handoff", origin=origin,
        rights=rights, evidence=[dict(kind="software-observation", claim="Existing Python bridge returns drafts and rejects active items and mixed candidate identities", uncertainty="Only three local synthetic software fixtures; no external system or physical plant observed")],
        interfaces=[dict(name="delivery_drafts", input="candidate-bound report", output="disabled ERP draft and source/evaluation identity", hardware_access=False)],
        behavior_fixtures=fixtures, unresolved_tasks=["Live interface qualification, permissions and physical commissioning remain separate"], root=root)
    proto = _repo_file(root, "repo:crates/osr-proto/src/lib.rs").read_bytes()
    software = make_record("functional-patterns", name="Track-state protocol representation reference", origin=dict(uri="repo:crates/osr-proto/src/lib.rs",
        artifact_sha256=sha256(proto).hexdigest(), source_kind="owned-source", source_class="B", version="source-digest"),
        rights=rights, evidence=[dict(kind="source-inspection", claim="Rust wire structs use postcard; the proto schema remains normative", uncertainty="Source-informed contract only; no Rust binary or REA execution")],
        interfaces=[dict(name="track-state-log", schema="crates/osr-core/proto/track_state.proto", wire_format="postcard-development", protobuf_wire_compatibility_proven=False)],
        related_record_ids=[pattern["record_id"]], unresolved_tasks=["Actual cross-language binary fixtures and protocol version compatibility"], root=root)
    mesh = box_fixture_bytes(); geometry = recover_box_ascii_stl(mesh, units="mm", uncertainty_m=0)
    physical = make_record("physical-solutions", name="Owned rectangular plate geometry pattern",
        origin=dict(uri="artifact:owned-100x60x4-mm-plate", artifact_sha256=sha256(mesh).hexdigest(), source_kind="mesh", source_class="C", version="owned-fixture/1"),
        rights=dict(spdx="CERN-OHL-S-2.0", permitted_use="implementation", authorization=dict(status="authorized",
            basis="Owned generated geometric fixture under repository hardware path mapping", scope=["analysis", "implementation"])),
        evidence=[dict(kind="calculated-geometry", claim="Twelve triangles form a watertight oriented box with matching volume", uncertainty="Exact digital fixture; zero physical measurement or tolerance evidence")],
        geometry_candidates=[geometry], material_candidates=[dict(material=None, status="unassigned")],
        related_record_ids=[pattern["record_id"]], unresolved_tasks=["Actual material, loads, attachments, tolerances and physical validation"], artifact_bytes=mesh)
    production = make_record("production-methods", name="Disabled draft and human release workflow", origin=origin, rights=rights,
        evidence=[dict(kind="source-inspection", claim="Delivery creates change-review records without mutating released production orders", uncertainty="Workflow pattern only; no released manufacturing process")],
        process_candidates=[dict(method="candidate-bound draft BOM then human change-control", physical_process_qualified=False)],
        related_record_ids=[pattern["record_id"], software["record_id"], physical["record_id"]], unresolved_tasks=["Measured process capability, QA and approved released revisions"], root=root)
    library = new_library()
    for record in (pattern, software, physical, production):
        library = register(library, record, root=root)
    return dict(library=library, pilot_method="owned-source-inspection-and-offline-python-behavior",
        source_sha256={name: sha256(_repo_file(root, "repo:"+name).read_bytes()).hexdigest() for name in (
            source, "crates/osr-proto/src/lib.rs", "crates/osr-core/proto/track_state.proto",
            "engineering/station_rail/common.py", "Cargo.toml", "LICENSES/README.md")},
        rea_executed=False, rust_binary_executed=False, physical_plant_observed=False,
        native_jobs=0, external_transactions_performed=False, **FLAGS)


def box_fixture_bytes():
    """Owned digital geometry fixture; dimensions carry no measured tolerance."""
    vertices = [(0,0,0),(100,0,0),(100,60,0),(0,60,0),(0,0,4),(100,0,4),(100,60,4),(0,60,4)]
    faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
             (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    lines = ["solid owned_plate"]
    for face in faces:
        lines.extend(["facet normal 0 0 0", "outer loop"])
        lines.extend("vertex %g %g %g" % vertices[i] for i in face)
        lines.extend(["endloop", "endfacet"])
    return ("\n".join([*lines, "endsolid owned_plate"]) + "\n").encode()
