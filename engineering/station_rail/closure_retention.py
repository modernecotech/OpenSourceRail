"""Retain the exact physical-follow-up source epoch without native admission.

The seven original compact archives, receipts and reader remain unchanged.
This wrapper checks their retained bytes and top-level producer bindings against
archived producer bytes, then compares reference identities with today's selector.
It does not rerun a solver or establish physical equivalence from equal IDs.
"""
import argparse
import gzip
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile

from . import ROOT, FLAGS as RAIL_FLAGS
from .common import digest, encoded, identity
from . import closure_artifacts

PRODUCER = "engineering/station_rail/closure_retention.py"
PACKET = "docs/design-engine/v06-physical-closure"
OUTPUT = "docs/design-engine/retained-physical-followup-source-epoch"
ARCHIVES = {
    "short": ("motor-short.tar.gz", "osr-native-current-excited-LIM/1"),
    "full": ("motor-full.tar.gz", "osr-native-full-station-LIM-2D/1"),
    "coarse": ("brakes-10ms.tar.gz", "osr-native-wheel-braking/1"),
    "fine": ("brakes-5ms.tar.gz", "osr-native-wheel-braking/1"),
    "frame": ("frame-invalid.tar.gz", "osr-v06-native-body-frame/1"),
    "solid": ("frame-solid.tar.gz", "osr-v06-native-solid-frame/1"),
    "fit": ("floor-fit.tar.gz", "osr-v06-native-floor-fit/1"),
}
PHYSICAL_IDS = ("candidate_id", "body_candidate_id", "support_component_id", "propulsion_component_id")
FLAGS = dict(RAIL_FLAGS, configuration_adopted=False, selected_reference_changed=False)
SCOPE = dict(numerical_reexecuted=False, current_evaluator_admission=False,
    omitted_native_fields_restored=False, physical_comparison_proven=False,
    current_context_match="reference-identities-only",
    top_level_source_coverage_complete=True,
    nested_attempt_source_epochs_enumerated=False)
MAX_SOURCES = 256
MAX_SOURCE_BYTES = 64 * 1024**2
MAX_ARCHIVE_BYTES = 256 * 1024**2


def _relative(name):
    if not isinstance(name, str):
        raise ValueError("Ordinary repository-relative path required")
    p = PurePosixPath(name)
    if not name or p.is_absolute() or ".." in p.parts or str(p) != name or "\\" in name:
        raise ValueError("Ordinary repository-relative path required: " + name)
    return Path(name)


def _path(root, name, *, required=True):
    relative = _relative(name)
    path = root / relative
    for current in (path, *path.parents):
        if current == root:
            break
        if current.is_symlink():
            raise ValueError("Retained evidence cannot use symbolic links")
    if required and not path.is_file():
        raise ValueError("Retained evidence file missing: " + name)
    return path


def _hashes(value):
    if not isinstance(value, dict) or not value or len(value) > MAX_SOURCES:
        raise ValueError("Bounded explicit producer bindings required")
    for name, wanted in value.items():
        _relative(name)
        if (not isinstance(wanted, str) or len(wanted) != 64
                or any(ch not in "0123456789abcdef" for ch in wanted)):
            raise ValueError("Exact SHA-256 producer bindings required")
    return dict(value)


def _merge(sources, additional):
    for name, wanted in _hashes(additional).items():
        if name in sources and sources[name] != wanted:
            raise ValueError("Conflicting original producer binding: " + name)
        sources[name] = wanted
    if len(sources) > MAX_SOURCES:
        raise ValueError("Original producer count exceeds the bound")


def _identity(record, key, label):
    if record.get(key) != identity({name: value for name, value in record.items() if name != key}):
        raise ValueError(label + " identity differs")


def _held(record, label):
    if any(record.get(key) is not value for key, value in RAIL_FLAGS.items()):
        raise ValueError(label + " cannot grant physical acceptance or release")


def _context(root):
    from engineering.development_baseline import selection
    selected = selection.load(root)
    vehicle = selected["vehicle"]
    sources = {**vehicle["source_sha256"], **selected["source_sha256"]}
    for name in (PRODUCER, closure_artifacts.__name__.replace(".", "/") + ".py",
            "engineering/station_rail/common.py", "engineering/development_baseline/selection.py"):
        sources[name] = digest(_path(root, name))
    return dict(reference_ids={key: vehicle[key] for key in PHYSICAL_IDS},
        selection_id=selected["selection_id"], source_sha256=sources)


def _packet(root):
    folder = _path(root, PACKET + "/manifest.json").parent
    manifest = json.loads((folder / "manifest.json").read_bytes())
    if manifest.get("schema") != "osr-v06-followup-publication/1":
        raise ValueError("Expected the physical-follow-up publication")
    _identity(manifest, "manifest_id", "Original follow-up manifest")
    _held(manifest, "Original follow-up manifest")
    actual = {}
    for path in folder.rglob("*"):
        if path.is_symlink() or path.is_dir():
            raise ValueError("Only ordinary top-level follow-up files are supported")
        if path.name != "manifest.json":
            actual[path.name] = digest(_path(root, PACKET + "/" + path.name))
    if actual != manifest.get("files_sha256"):
        raise ValueError("Original follow-up publication payload differs")
    summary = json.loads(_path(root, PACKET + "/summary.json").read_bytes())
    if summary.get("schema") != "osr-v06-native-followup/1":
        raise ValueError("Original follow-up summary schema differs")
    _identity(summary, "followup_id", "Original follow-up summary")
    _held(summary, "Original follow-up summary")
    if (manifest.get("followup_id") != summary["followup_id"]
            or manifest.get("parent_candidate_id") != summary.get("candidate_id")
            or summary.get("complete_station_to_station_journey") is not False):
        raise ValueError("Original follow-up reference or disposition differs")
    if set(manifest.get("archives", {})) != set(ARCHIVES):
        raise ValueError("All seven original follow-up archives are required")
    sources = _hashes(manifest.get("source_sha256"))
    archives = {}
    total = 0
    for key, (filename, schema) in sorted(ARCHIVES.items()):
        metadata = manifest["archives"][key]
        path = _path(root, PACKET + "/" + filename)
        if (metadata.get("archive_name") != filename or digest(path) != metadata.get("archive_sha256")
                or path.stat().st_size > MAX_ARCHIVE_BYTES):
            raise ValueError("Original archive binding differs: " + key)
        checked = closure_artifacts.verify(path, root=None)
        if any(metadata.get(name) != checked[name] for name in
                ("compact_manifest_id", "retained_raw_payload_complete")):
            raise ValueError("Original compact archive index differs: " + key)
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getmembers()
            total += sum(member.size for member in members)
            if total > MAX_ARCHIVE_BYTES:
                raise ValueError("Combined retained archive budget exceeded")
            original = json.load(archive.extractfile("raw/manifest.json"))
            result = json.load(archive.extractfile("raw/result.json"))
        _identity(original, "manifest_id", "Raw " + key + " manifest")
        _held(original, "Raw " + key + " manifest")
        _held(result, "Raw " + key + " result")
        if result.get("schema") != schema:
            raise ValueError("Original native result schema differs: " + key)
        if "evaluation_id" in result:
            _identity(result, "evaluation_id", "Raw " + key + " result")
        if original.get("source_sha256") != result.get("source_sha256"):
            raise ValueError("Raw manifest/result producer bindings differ: " + key)
        _merge(sources, original["source_sha256"])
        if key in ("coarse", "fine", "frame") and any(
                result.get(name) != summary.get(name) for name in PHYSICAL_IDS):
            raise ValueError("Raw native reference identities differ: " + key)
        if key in ("solid", "fit") and result.get("parent_candidate_id") != summary["candidate_id"]:
            raise ValueError("Raw native parent identity differs: " + key)
        archives[key] = dict(filename=filename, archive_sha256=digest(path),
            compact_manifest_id=checked["compact_manifest_id"],
            raw_manifest_id=original["manifest_id"],
            raw_result_sha256=original["files_sha256"]["result.json"],
            raw_result_evaluation_id=result.get("evaluation_id"),
            original_source_sha256=original["source_sha256"],
            retained_raw_payload_complete=checked["retained_raw_payload_complete"],
            omitted_raw_file_count=checked["omitted_raw_file_count"])
    return manifest, summary, sources, archives


def _source_bytes(root, name, wanted):
    path = _path(root, name, required=False)
    if path.is_file() and digest(path) == wanted:
        return path.read_bytes()
    commits = subprocess.check_output(["git", "log", "--all", "--format=%H", "--", name],
        cwd=root, text=True).splitlines()
    for commit in commits:
        result = subprocess.run(["git", "show", commit + ":" + name], cwd=root, capture_output=True)
        if result.returncode == 0 and sha256(result.stdout).hexdigest() == wanted:
            return result.stdout
    raise ValueError("Original producer bytes unavailable: " + name + " " + wanted)


def _output(root, output):
    out = _path(root, str(output), required=False)
    packet = root / PACKET
    if out == packet or out in packet.parents or packet in out.parents:
        raise ValueError("Retained wrapper must be separate from the original packet")
    return out


def _expected(root):
    manifest, summary, sources, archives = _packet(root)
    context = _context(root)
    if (any(summary.get(key) != context["reference_ids"][key] for key in PHYSICAL_IDS)
            or summary.get("selection_id") != context["selection_id"]):
        raise ValueError("Retained reference identities differ from the current selected candidate")
    current_sources = _hashes(context["source_sha256"])
    if any(digest(_path(root, name)) != wanted for name, wanted in current_sources.items()):
        raise ValueError("Current reference-context sources changed during verification")
    return dict(schema="osr-retained-physical-followup-source-epoch/1", packet=PACKET,
        original_manifest_id=manifest["manifest_id"],
        original_manifest_sha256=digest(root / PACKET / "manifest.json"),
        original_followup_id=summary["followup_id"],
        original_payload_sha256=manifest["files_sha256"],
        original_source_sha256=sources, original_archive_bindings=archives,
        current_reference_ids=context["reference_ids"], current_selection_id=context["selection_id"],
        current_context_source_sha256=current_sources,
        scope="Original packet, all seven compact archive retained/omitted indexes, and their top-level raw manifest/result producer bindings. Current reference identity equality is not physical equivalence or evaluator admission; nested attempt producer epochs and omitted fields are not reconstructed.",
        **SCOPE, **FLAGS)


def build(root=ROOT, *, output=OUTPUT, resolver=None):
    root = Path(root).resolve()
    out = _output(root, output)
    expected = _expected(root)
    if out.exists():
        return verify(root, output=output)
    provider = _source_bytes if resolver is None else resolver
    stream = io.BytesIO()
    total = 0
    with gzip.GzipFile(fileobj=stream, mode="wb", filename="", compresslevel=9, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name, wanted in sorted(expected["original_source_sha256"].items()):
                raw = provider(root, name, wanted)
                total += len(raw)
                if sha256(raw).hexdigest() != wanted:
                    raise ValueError("Recovered original producer bytes differ: " + name)
                if total > MAX_SOURCE_BYTES:
                    raise ValueError("Retained producer archive exceeds its resource bound")
                info = tarfile.TarInfo(name)
                info.size = len(raw)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(raw))
    compressed = stream.getvalue()
    if len(compressed) > MAX_SOURCE_BYTES:
        raise ValueError("Retained producer archive exceeds its compressed bound")
    expected["producer_archive_sha256"] = sha256(compressed).hexdigest()
    expected["retention_id"] = identity(expected)
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".physical-followup-retention-", dir=out.parent))
    try:
        (stage / "producer.tar.gz").write_bytes(compressed)
        (stage / "manifest.json").write_bytes(encoded(expected))
        verify(root, output=stage.relative_to(root).as_posix())
        # Re-read the current context and original packet before publication.
        if _expected(root) != {key: value for key, value in expected.items()
                if key not in ("producer_archive_sha256", "retention_id")}:
            raise ValueError("Sources or original packet changed during retention")
        if out.exists():
            raise ValueError("Retained wrapper appeared during publication")
        stage.rename(out)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return verify(root, output=output)


def verify(root=ROOT, *, output=OUTPUT):
    from engineering.development_baseline import selection
    if selection.load(root)['selection']['family']=='wheel_rail_vehicle_reference':
        return verify_retired_comparison(root,output=output)
    root = Path(root).resolve()
    out = _output(root, output)
    receipt_path = _path(root, out.relative_to(root).as_posix() + "/manifest.json")
    receipt = json.loads(receipt_path.read_bytes())
    _identity(receipt, "retention_id", "Retained follow-up receipt")
    if {p.name for p in out.iterdir()} != {"manifest.json", "producer.tar.gz"}:
        raise ValueError("Retained wrapper file inventory differs")
    expected = _expected(root)
    if expected != {key: value for key, value in receipt.items()
            if key not in ("producer_archive_sha256", "retention_id")}:
        raise ValueError("Retained follow-up source epoch, context or scope differs")
    producer = _path(root, out.relative_to(root).as_posix() + "/producer.tar.gz")
    if producer.stat().st_size > MAX_SOURCE_BYTES or digest(producer) != receipt.get("producer_archive_sha256"):
        raise ValueError("Retained producer archive bytes differ")
    actual = {}
    total = 0
    with tarfile.open(producer, "r:gz") as archive:
        for member in archive:
            _relative(member.name)
            if not member.isfile() or member.name in actual:
                raise ValueError("Only unique ordinary producer archive members are supported")
            total += member.size
            if len(actual) >= MAX_SOURCES or total > MAX_SOURCE_BYTES:
                raise ValueError("Retained producer archive exceeds its resource bound")
            actual[member.name] = sha256(archive.extractfile(member).read()).hexdigest()
    if actual != receipt["original_source_sha256"]:
        raise ValueError("Original producer coverage or bytes differ")
    dependencies = {PACKET + "/" + name: wanted
        for name, wanted in receipt["original_payload_sha256"].items()}
    dependencies.update({PACKET + "/manifest.json": receipt["original_manifest_sha256"],
        out.relative_to(root).as_posix() + "/manifest.json": digest(receipt_path),
        out.relative_to(root).as_posix() + "/producer.tar.gz": digest(producer),
        **receipt["current_context_source_sha256"]})
    return dict(verified=True, retention_id=receipt["retention_id"],
        original_manifest_id=receipt["original_manifest_id"],
        original_source_count=len(actual), original_native_archive_count=len(ARCHIVES),
        dependency_sha256=dependencies, **SCOPE, **FLAGS)




def verify_retired_comparison(root=ROOT, *, output=OUTPUT):
    """Authenticate the old article under its pinned epoch, never current admission."""
    from . import retired_station_reference
    root=Path(root).resolve();proof=retired_station_reference.verify(root)
    context=_context(root)
    if context['reference_ids']!=proof['reference_candidate_ids']:
        raise ValueError('Retired physical article differs from the reference vehicle interfaces')
    dependencies=dict(proof['dependency_sha256'])
    for path in sorted((root/output).rglob('*')):
        if path.is_file():
            relative=path.relative_to(root).as_posix()
            raw,_=retired_station_reference.reference_bytes(relative,root)
            if path.read_bytes()!=raw:raise ValueError('Retired physical-source archive differs')
            dependencies[relative]=digest(path)
    manifest,summary,_,_=_packet(root)
    raw,_=retired_station_reference.reference_bytes(PACKET+'/manifest.json',root)
    if (root/PACKET/'manifest.json').read_bytes()!=raw:
        raise ValueError('Original physical follow-up manifest differs from the retired epoch')
    for path in (root/PACKET).iterdir():
        if path.is_file():dependencies[path.relative_to(root).as_posix()]=digest(path)
    return dict(verified=True,scope='retired-comparison-packet-and-original-producer-integrity-only',
        original_followup_id=summary['followup_id'],original_manifest_id=manifest['manifest_id'],
        original_selection_id=summary['selection_id'],current_policy_selection_id=context['selection_id'],
        reference_ids=context['reference_ids'],reference_selection_is_physical_equivalence=False,
        dependency_sha256={**dependencies,PRODUCER:digest(root/PRODUCER),**context['source_sha256']},
        current_evaluator_admission=False,numerical_reexecuted=False,**FLAGS)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "verify"))
    action = parser.parse_args().action
    value = (build if action == "build" else verify)()
    print(json.dumps({key: item for key, item in value.items() if key != "dependency_sha256"}, indent=2))
