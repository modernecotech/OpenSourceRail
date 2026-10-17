"""Content-addressed, lossless research evidence with explicit legacy projections.

A projection preserves the byte hash of every original file and its original seal.
Large JSON containers form a shared immutable DAG, so repeated candidate evidence
is stored once. References are storage records, never engineering acceptance.
"""

from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import gzip
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile

from .coverage import ROOT

STORE = ROOT / "docs/design-engine/evidence-store"
MANIFEST = "projection.json"
REFERENCE_SCHEMA = "osr-evidence-reference/1"
PROJECTION_SCHEMA = "osr-evidence-projection/1"
NODE_SCHEMA = "osr-evidence-node/1"
HASH = re.compile(r"^[0-9a-f]{64}$")
THRESHOLD = 2048


def digest(data):
    return sha256(data).hexdigest()


def pretty(value):
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def compact(value):
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


ENCODINGS = {
    "json-pretty-sorted-2-newline": (2, True, True),
    "json-pretty-utf8-sorted-2-newline": (2, False, True),
    "json-compact-utf8-sorted-newline": (None, False, True),
    "json-compact-sorted-newline": (None, True, True),
    "json-compact-utf8-sorted": (None, False, False),
    "json-compact-sorted": (None, True, False),
}


def serialize(value, encoding):
    indent, ascii_only, newline = ENCODINGS[encoding]
    options = dict(sort_keys=True, allow_nan=False, ensure_ascii=ascii_only)
    if indent is None:
        options["separators"] = (",", ":")
    else:
        options["indent"] = indent
    return (json.dumps(value, **options) + ("\n" if newline else "")).encode()


def _safe_name(name):
    if not isinstance(name, str):
        raise ValueError("unsafe evidence member path")
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError("unsafe evidence member path")
    return name


def _under(path, folder):
    path, folder = Path(path).absolute(), Path(folder).resolve()
    if not path.resolve().is_relative_to(folder):
        raise ValueError("evidence path leaves controlled folder")
    return path


class ObjectStore:
    def __init__(self, folder=STORE):
        self.folder = Path(folder).resolve()
        self.nodes = {}
        self.values = {}
        self.visiting = set()
        self.reachable = set()
        self.encoded = {}

    def path(self, key, kind):
        if (
            not isinstance(key, str)
            or not HASH.fullmatch(key)
            or kind not in {"json", "blob"}
        ):
            raise ValueError("invalid evidence object reference")
        legacy = _under(
            self.folder / "sha256" / key[:2] / (key + "." + kind), self.folder
        )
        if kind == "json" and not (legacy.exists() or legacy.is_symlink()):
            return _under(legacy.with_suffix(".json.gz"), self.folder)
        return legacy

    def put(self, data, kind):
        if kind == "json":
            # The address hashes the actual deterministic compressed bytes.
            data = gzip.compress(data, compresslevel=9, mtime=0)
        key = digest(data)
        target = self.path(key, kind)
        if target.exists():
            if target.is_symlink() or target.read_bytes() != data:
                raise ValueError("immutable evidence object differs: " + key)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation prevents replacement of a concurrent object.
            try:
                with target.open("xb") as stream:
                    stream.write(data)
            except FileExistsError:
                if target.read_bytes() != data:
                    raise ValueError("immutable evidence object differs: " + key)
        return key

    def get(self, key, kind):
        path = self.path(key, kind)
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing evidence object: " + key)
        data = path.read_bytes()
        if digest(data) != key:
            raise ValueError("evidence object hash differs: " + key)
        self.reachable.add((key, kind))
        if path.suffix == ".gz":
            try:
                return gzip.decompress(data)
            except (OSError, EOFError) as error:
                raise ValueError("invalid compressed evidence object") from error
        return data

    def encode(self, value):
        semantic = compact(value)
        signature = digest(semantic)
        if signature in self.encoded:
            return self.encoded[signature]

        def slot(item):
            if isinstance(item, (dict, list)) and len(compact(item)) >= THRESHOLD:
                return {"ref": self.encode(item)}
            return {"value": item}

        if isinstance(value, dict):
            node = dict(
                schema=NODE_SCHEMA,
                kind="object",
                items={k: slot(v) for k, v in value.items()},
            )
        elif isinstance(value, list):
            node = dict(
                schema=NODE_SCHEMA, kind="array", items=[slot(v) for v in value]
            )
        else:
            node = dict(schema=NODE_SCHEMA, kind="value", value=value)
        key = self.put(compact(node), "json")
        self.encoded[signature] = key
        return key

    def decode(self, key):
        if key in self.values:
            return self.values[key]
        if key in self.visiting:
            raise ValueError("cyclic evidence object reference")
        self.visiting.add(key)
        try:
            node = json.loads(self.get(key, "json"))
            if node.get("schema") != NODE_SCHEMA:
                raise ValueError("unknown evidence object schema")

            def unslot(item):
                if not isinstance(item, dict) or len(item) != 1:
                    raise ValueError("invalid evidence value slot")
                if "ref" in item:
                    return self.decode(item["ref"])
                if "value" in item:
                    return item["value"]
                raise ValueError("unknown evidence value slot")

            if (
                node["kind"] == "object"
                and set(node) == {"schema", "kind", "items"}
                and isinstance(node["items"], dict)
            ):
                value = {k: unslot(v) for k, v in node["items"].items()}
            elif (
                node["kind"] == "array"
                and set(node) == {"schema", "kind", "items"}
                and isinstance(node["items"], list)
            ):
                value = [unslot(v) for v in node["items"]]
            elif node["kind"] == "value" and set(node) == {"schema", "kind", "value"}:
                value = node["value"]
            else:
                raise ValueError("invalid evidence object shape")
            self.values[key] = value
            return value
        finally:
            self.visiting.discard(key)

    def archive(self, data, *, json_file):
        descriptor = dict(sha256=digest(data), size=len(data))
        if json_file:
            value = json.loads(data)
            codes = list(ENCODINGS)
            if not data.startswith((b"{\n", b"[\n")):
                codes = codes[2:] + codes[:2]
            for code in codes:
                if serialize(value, code) == data:
                    return dict(
                        descriptor, encoding=code, object_sha256=self.encode(value)
                    )
        return dict(descriptor, encoding="bytes", object_sha256=self.put(data, "blob"))

    def restore(self, descriptor):
        if descriptor.get("encoding") in ENCODINGS:
            data = serialize(
                self.decode(descriptor["object_sha256"]), descriptor["encoding"]
            )
        elif descriptor.get("encoding") == "bytes":
            data = self.get(descriptor["object_sha256"], "blob")
        else:
            raise ValueError("unknown evidence encoding")
        if digest(data) != descriptor["sha256"] or len(data) != descriptor["size"]:
            raise ValueError("reconstructed original evidence bytes differ")
        return data


def _reference(path):
    try:
        value = json.loads(Path(path).read_bytes())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return (
        value
        if isinstance(value, dict) and value.get("schema") == REFERENCE_SCHEMA
        else None
    )


def _store_at(path, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError("relative evidence store path required")
    folder = (Path(path).parent / relative).resolve()
    # All repository projections share this controlled store. Custom temporary
    # stores may be used for tests, but a store cannot be a projection member.
    if folder == Path(path).parent or folder.is_relative_to(Path(path).parent):
        raise ValueError("evidence store cannot live inside a projection")
    if Path(path).resolve().is_relative_to(ROOT) and folder != STORE.resolve():
        raise ValueError("repository evidence must use the controlled shared store")
    return ObjectStore(folder)


def read_bytes(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("symlink evidence member rejected")
    reference = _reference(path) if path.suffix == ".json" else None
    if reference is None:
        return path.read_bytes()
    if set(reference) != {"schema", "store", "original"}:
        raise ValueError("invalid evidence reference")
    return _store_at(path, reference["store"]).restore(reference["original"])


def read_json(path):
    """Read ordinary JSON or validate and resolve a compact evidence reference."""
    return json.loads(read_bytes(path))


def source_closure(path):
    """Bind only the reachable immutable objects, never the growing whole store."""
    path = Path(path).resolve()
    reference = _reference(path) if path.suffix == ".json" else None
    if reference is None:
        return {}
    store = _store_at(path, reference["store"])
    store.restore(reference["original"])
    return {
        store.path(key, kind).relative_to(ROOT).as_posix(): key
        for key, kind in sorted(store.reachable)
    }


def is_projection(folder):
    return (Path(folder) / MANIFEST).is_file()


def _manifest(folder):
    folder = Path(folder).resolve()
    path = folder / MANIFEST
    if path.is_symlink():
        raise ValueError("symlink projection manifest rejected")
    value = json.loads(path.read_bytes())
    _validate_manifest(value)
    return value, _store_at(path, value["store"])


def _validate_manifest(value):
    if (
        value.get("schema") != PROJECTION_SCHEMA
        or value.get("physical_release") is not False
    ):
        raise ValueError("unreleased evidence projection required")
    if value.get("original_seal") not in {"snapshot.json", "receipt.json"}:
        raise ValueError("original evidence seal required")
    if value["original_seal"] not in value["files"]:
        raise ValueError("original seal missing from evidence projection")


def verify_projection(folder):
    """Verify storage, exact original membership and original byte hashes."""
    folder = Path(folder).resolve()
    manifest, store = _manifest(folder)
    if any(p.is_symlink() for p in folder.rglob("*")):
        raise ValueError("symlink evidence member rejected")
    actual = {
        p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()
    }
    return _verify_members(folder, manifest, store, actual, Path.read_bytes)


def _verify_members(folder, manifest, store, actual, read):
    if actual != set(manifest["files"]) | {MANIFEST}:
        raise ValueError("evidence projection member set differs")
    original_size = 0
    for name, descriptor in manifest["files"].items():
        _safe_name(name)
        path = _under(folder / name, folder)
        data = store.restore(descriptor)
        original_size += len(data)
        if path.suffix == ".json":
            try:
                reference = json.loads(read(path))
            except (json.JSONDecodeError, UnicodeDecodeError):
                reference = None
            if (
                not isinstance(reference, dict)
                or set(reference) != {"schema", "store", "original"}
                or reference.get("original") != descriptor
                or _store_at(path, reference["store"]).folder != store.folder
            ):
                raise ValueError("projection reference differs from manifest: " + name)
        elif read(path) != data:
            raise ValueError("local evidence asset differs: " + name)
    if (
        manifest["original_seal_sha256"]
        != manifest["files"][manifest["original_seal"]]["sha256"]
    ):
        raise ValueError("archived original seal hash differs")
    return dict(
        integrity_verified=True,
        original_bytes=original_size,
        original_files=len(manifest["files"]),
        reachable_objects=len(store.reachable),
        physical_release=False,
        numerical_recomputation_performed=False,
    )


class _GitStore(ObjectStore):
    """Read CAS bytes from Git objects, never from the mutable working tree."""

    def __init__(self, folder, read, members):
        super().__init__(folder)
        self.read = read
        self.members = members

    def path(self, key, kind):
        path = super().path(key, kind)
        if kind == "json":
            legacy = path.with_name(key + ".json")
            return legacy if legacy in self.members else legacy.with_suffix(".json.gz")
        return path

    def get(self, key, kind):
        path = self.path(key, kind)
        data = self.read(path)
        if digest(data) != key:
            raise ValueError("evidence object hash differs: " + key)
        self.reachable.add((key, kind))
        if path.suffix == ".gz":
            try:
                return gzip.decompress(data)
            except (OSError, EOFError) as error:
                raise ValueError("invalid compressed evidence object") from error
        return data


def verify_git_projection(folder, *, repository=ROOT, revision=None):
    """Verify a publication using only the Git index or a committed tree.

    Working copies, ignored files and untracked CAS objects cannot satisfy this
    check. Reading Git blobs directly gives clean-checkout semantics without a
    duplicate checkout of the (potentially large) evidence store. With no
    ``revision`` the staged index is checked, allowing this gate before commit.
    """
    repository = Path(repository).resolve()
    folder = Path(folder).absolute()
    relative = folder.relative_to(repository).as_posix()
    _safe_name(relative)
    command = ["git", "-C", str(repository)]
    if revision is None:
        records = subprocess.check_output(
            command + ["ls-files", "--stage", "-z"]
        ).split(b"\0")
    else:
        records = subprocess.check_output(
            command + ["ls-tree", "-r", "-z", revision]
        ).split(b"\0")
    members = {}
    for record in records:
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, middle, final = metadata.decode("ascii").split()
        if revision is None:
            if final != "0":
                raise ValueError("unmerged Git index cannot verify publication")
            object_id = middle
        else:
            if middle != "blob":
                continue
            object_id = final
        members[repository / os.fsdecode(name)] = (mode, object_id)
    with subprocess.Popen(
        command + ["cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ) as process:

        def read(path):
            path = Path(path)
            if path not in members:
                raise ValueError("publication member absent from Git: " + str(path))
            mode, object_id = members[path]
            if mode not in {"100644", "100755"}:
                raise ValueError("non-file Git publication member rejected")
            process.stdin.write((object_id + "\n").encode("ascii"))
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                raise ValueError("invalid Git publication blob")
            data = process.stdout.read(int(header[2]))
            if process.stdout.read(1) != b"\n":
                raise ValueError("truncated Git publication blob")
            return data

        try:
            manifest = json.loads(read(folder / MANIFEST))
            _validate_manifest(manifest)
            actual = {
                path.relative_to(folder).as_posix()
                for path in members
                if path.is_relative_to(folder)
            }
            store_path = _store_at(folder / MANIFEST, manifest["store"]).folder
            store = _GitStore(store_path, read, members)
            result = _verify_members(folder, manifest, store, actual, read)
            return dict(
                result, git_publication_verified=True, git_revision=revision or "index"
            )
        finally:
            process.stdin.close()
            process.wait()


@contextmanager
def materialized(folder):
    """Reconstruct byte-exact originals for the unchanged historical verifier."""
    folder = Path(folder).resolve()
    verify_projection(folder)
    manifest, store = _manifest(folder)
    build = ROOT / "build/evidence-materialized"
    build.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="snapshot-", dir=build) as temporary:
        destination = Path(temporary)
        for name, descriptor in manifest["files"].items():
            target = destination / _safe_name(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(store.restore(descriptor))
        yield destination


def publish_files(files, destination, *, store=STORE, original_seal="snapshot.json"):
    """Archive file bytes once and write a small new review projection directly.

    ``files`` maps original relative paths to bytes or existing source Paths.
    No complete uncompressed copy is written to the publication directory.
    """
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("fresh evidence projection destination required")
    objects = ObjectStore(store)
    descriptors, assets = {}, {}
    for name, source in sorted(files.items()):
        _safe_name(name)
        data = source if isinstance(source, bytes) else Path(source).read_bytes()
        descriptors[name] = objects.archive(
            data, json_file=Path(name).suffix == ".json"
        )
        if Path(name).suffix != ".json":
            assets[name] = data
    if original_seal not in descriptors:
        raise ValueError("projection requires original seal bytes")
    # Prove reconstruction before creating or replacing any published member.
    for name, descriptor in descriptors.items():
        data = (
            files[name]
            if isinstance(files[name], bytes)
            else Path(files[name]).read_bytes()
        )
        if objects.restore(descriptor) != data:
            raise ValueError("archived bytes differ before publication")
    destination.mkdir(parents=True)
    manifest = dict(
        schema=PROJECTION_SCHEMA,
        store=os.path.relpath(objects.folder, destination),
        original_seal=original_seal,
        original_seal_sha256=descriptors[original_seal]["sha256"],
        files=descriptors,
        physical_release=False,
        applicability="Original source seals retained; storage integrity grants no current applicability or engineering release.",
    )
    for name, descriptor in descriptors.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".json":
            target.write_bytes(
                pretty(
                    dict(
                        schema=REFERENCE_SCHEMA,
                        store=os.path.relpath(objects.folder, target.parent),
                        original=descriptor,
                    )
                )
            )
        else:
            target.write_bytes(assets[name])
    (destination / MANIFEST).write_bytes(pretty(manifest))
    return verify_projection(destination)


def migrate(folder, *, store=STORE, reencode=False):
    """Replace legacy JSON copies only after lossless archival has been proved."""
    folder = Path(folder).resolve()
    if is_projection(folder):
        if not reencode:
            return verify_projection(folder)
        verify_projection(folder)
        manifest, original_store = _manifest(folder)
        files = {
            name: original_store.restore(descriptor)
            for name, descriptor in manifest["files"].items()
        }
    else:
        files = {}
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                raise ValueError("symlink legacy evidence rejected")
            if path.is_file():
                files[path.relative_to(folder).as_posix()] = path
    if "snapshot.json" not in files:
        raise ValueError("legacy snapshot seal required")
    # Stage at the same directory depth, so all final relative store paths
    # already resolve correctly. Original files remain intact until archival
    # and replacement verification have both completed.
    staged = Path(tempfile.mkdtemp(prefix=".evidence-stage-", dir=folder.parent))
    staged.rmdir()
    try:
        publish_files(files, staged, store=store)
        build = (
            ROOT / "build/evidence-materialized"
            if folder.is_relative_to(ROOT)
            else folder.parent
        )
        build.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="migration-original-", dir=build
        ) as temporary:
            retained = Path(temporary) / folder.name
            folder.rename(retained)
            try:
                staged.rename(folder)
                verified = verify_projection(folder)
            except BaseException:
                if folder.exists():
                    folder.rename(Path(temporary) / "failed-projection")
                retained.rename(folder)
                raise
        return verified
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def collect_unreferenced(*, delete=False):
    """Audit append-only store reachability; remove only explicitly orphaned bytes.

    Published artifact roots and CAS objects named by retained source-hash maps
    are roots. No object named by any surviving original source seal is removed.
    Migration uses this after replacing an encoding, never during publication.
    """
    store = ObjectStore(STORE)
    projections = []
    source_refs = set()

    def inspect(value):
        if isinstance(value, dict):
            for name, item in value.items():
                if (
                    isinstance(name, str)
                    and name.startswith("docs/design-engine/evidence-store/sha256/")
                    and isinstance(item, str)
                    and HASH.fullmatch(item)
                ):
                    path = _under(ROOT / name, STORE)
                    if path.name not in {
                        item + ".json",
                        item + ".json.gz",
                        item + ".blob",
                    }:
                        raise ValueError("retained evidence source-hash path differs")
                    source_refs.add(
                        (item, "blob" if path.suffix == ".blob" else "json")
                    )
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)

    for manifest_path in sorted((ROOT / "docs/design-engine").rglob(MANIFEST)):
        if manifest_path.is_relative_to(STORE):
            continue
        try:
            record = json.loads(manifest_path.read_bytes())
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict) or record.get("schema") != PROJECTION_SCHEMA:
            continue
        folder = manifest_path.parent
        verify_projection(folder)
        manifest, referenced_store = _manifest(folder)
        if referenced_store.folder != store.folder:
            raise ValueError("unexpected published evidence store")
        projections.append(folder.relative_to(ROOT).as_posix())
        for name, descriptor in manifest["files"].items():
            data = store.restore(descriptor)
            if Path(name).suffix == ".json":
                inspect(json.loads(data))
    # Named source objects may themselves be JSON DAG roots.
    pending = list(source_refs)
    checked = set()
    while pending:
        key, kind = pending.pop()
        if (key, kind) in checked:
            continue
        checked.add((key, kind))
        data = store.get(key, kind)
        if kind == "json":
            store.decode(key)
        else:
            try:
                inspect(json.loads(data))
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        pending.extend(source_refs - checked)
    keep = {store.path(key, kind) for key, kind in store.reachable}
    all_objects = set(store.folder.glob("sha256/*/*"))
    if any(path.is_symlink() or not path.is_file() for path in all_objects):
        raise ValueError("invalid evidence store object member")
    orphaned = sorted(all_objects - keep)
    result = dict(
        schema="osr-evidence-garbage-audit/1",
        projections=projections,
        retained_objects=len(keep),
        unreferenced_objects=len(orphaned),
        unreferenced_bytes=sum(path.stat().st_size for path in orphaned),
        deletion_performed=delete,
        physical_release=False,
    )
    if delete:
        for path in orphaned:
            path.unlink()
    return result
