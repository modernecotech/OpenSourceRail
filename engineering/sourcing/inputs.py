"""Read portable twin inputs without executing archived source or native solvers."""
from pathlib import Path, PurePosixPath
import gzip
import hashlib
import io
import json
import tarfile
from engineering.station_rail.common import identity as native_identity
from .model import identity, is_id

MAX_JSON_BYTES = 192 * 1024 ** 2
MAX_ARCHIVE_BYTES = 256 * 1024 ** 2
MAX_TAR_BYTES = 1024 * 1024 ** 2
MAX_TAR_FILES = 256


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def decode_json(raw, *, compressed=False):
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("Compressed/source input exceeds JSON byte budget")
    if compressed:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_JSON_BYTES + 1)
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("Decompressed twin input exceeds byte budget")
    def no_duplicates(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError("Duplicate JSON object key")
            value[key] = item
        return value
    def no_constants(value):
        raise ValueError("Non-finite JSON numeric constant: " + value)
    return json.loads(raw, object_pairs_hook=no_duplicates, parse_constant=no_constants)


def read_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("Bounded regular JSON input required")
    return decode_json(path.read_bytes(), compressed=path.name.endswith(".gz"))


def _sealed(value, key):
    if not is_id(value.get(key)) or native_identity({k: v for k, v in value.items() if k != key}) != value[key]:
        raise ValueError("Source packet identity differs: " + key)


def _tar_subset(path, selected):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("Bounded regular twin archive required")
    result = {}
    seen = set()
    total = 0
    with tarfile.open(path, "r:gz") as tar:
        for item in tar:
            name = PurePosixPath(item.name)
            if (not item.isfile() or name.is_absolute() or ".." in name.parts or
                    "\\" in item.name or item.name in seen or item.size < 0):
                raise ValueError("Unsafe or duplicate twin archive member")
            seen.add(item.name)
            total += item.size
            if total > MAX_TAR_BYTES or len(seen) > MAX_TAR_FILES:
                raise ValueError("Twin archive inventory budget exceeded")
            if item.name in selected:
                if item.size > MAX_JSON_BYTES:
                    raise ValueError("Twin member exceeds input budget")
                with tar.extractfile(item) as stream:
                    result[item.name] = stream.read(MAX_JSON_BYTES + 1)
                if len(result[item.name]) != item.size:
                    raise ValueError("Truncated twin input member")
    if set(result) != set(selected):
        raise ValueError("Required exact twin input members missing")
    return result


def _origin(path):
    path = Path(path).resolve()
    root = Path(__file__).resolve().parents[2]
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        relative = None
    return dict(display_name=path.name, repository_relative_path=relative,
                source_blob_sha256=digest(path), developer_absolute_path_required=False)


def load_twin(path, *, member=None):
    """Return payload plus provenance, not an engineering acceptance result.

    A frame publication provides exact registry occurrences and its integrated
    candidate binding. A default export remains a subtotal/account namespace.
    Other whole-cell BOM archives can be supplied with an explicit JSON member.
    """
    path = Path(path).resolve()
    if path.is_dir():
        descriptor = read_json(path / "manifest.json")
        if descriptor.get("schema") != "osr-frame-cell-publication/1":
            raise ValueError("Unsupported packet; supply its explicit BOM JSON/archive member")
        _sealed(descriptor, "publication_id")
        if set(descriptor["files"]) != {"frame-cell.tar.gz", "summary.json"}:
            raise ValueError("Unexpected source frame publication inventory")
        for name, expected in descriptor["files"].items():
            item = path / name
            if item.is_symlink() or not item.is_file() or item.stat().st_size != expected["bytes"] or digest(item) != expected["sha256"]:
                raise ValueError("Source publication payload/hash differs")
        parts = _tar_subset(path / "frame-cell.tar.gz", {"manifest.json", "equipment.json.gz"})
        package = decode_json(parts["manifest.json"])
        _sealed(package, "package_id")
        if package.get("execution") != "completed":
            raise ValueError("Completed source packet required")
        expected = package["files"]["equipment.json.gz"]
        actual = parts["equipment.json.gz"]
        if len(actual) != expected["bytes"] or hashlib.sha256(actual).hexdigest() != expected["sha256"]:
            raise ValueError("Equipment member differs from source packet manifest")
        equipment = decode_json(actual, compressed=True)
        _sealed(equipment, "evaluation_id")
        summary = read_json(path / "summary.json")
        for key in ("candidate_id", "body_candidate_id", "evaluation_id", "package_id"):
            if summary[key] != package[key]:
                raise ValueError("Frame publication candidate/package summary differs")
        vehicle = equipment["vehicle"]
        if vehicle["candidate_id"] != package["body_candidate_id"] or equipment["candidate_id"] != vehicle["candidate_id"]:
            raise ValueError("Mixed source equipment/body candidate")
        payload = dict(candidate_id=package["candidate_id"], body_candidate_id=vehicle["candidate_id"],
                       vehicle=vehicle, source_package_id=package["package_id"],
                       source_publication_id=descriptor["publication_id"])
        origin = dict(_origin(path / "frame-cell.tar.gz"), publication_id=descriptor["publication_id"],
                      package_id=package["package_id"], member="equipment.json.gz",
                      member_sha256=hashlib.sha256(actual).hexdigest(),
                      native_solver_recomputed=False, operating_map_admitted=False)
    elif member is not None:
        parts = _tar_subset(path, {member})
        payload = decode_json(parts[member], compressed=member.endswith(".gz"))
        origin = dict(_origin(path), member=member, member_sha256=hashlib.sha256(parts[member]).hexdigest())
    else:
        payload = read_json(path)
        origin = _origin(path)
    return dict(schema="osr-sourcing-twin-input/1", payload=payload, payload_id=identity(payload),
                origin=origin, input_scope="integrity-and-typed-inventory; no engineering approval",
                physical_qualification=None)
