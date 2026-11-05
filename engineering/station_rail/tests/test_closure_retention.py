"""An epoch wrapper preserves the original evidence and cannot promote it."""
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import tarfile

import pytest

from engineering.station_rail import closure_artifacts
from engineering.station_rail import closure_retention as retention
from engineering.station_rail.common import digest, encoded, identity


def fixture(root, monkeypatch, *, wrong_raw_reference=False, conflicting_source=False):
    # Exercise the original wrapper branch with an explicitly old-family fixture.
    # Current-policy retention is independently checked against the pinned Git packet.
    from engineering.development_baseline import selection
    monkeypatch.setattr(selection, 'load', lambda _: dict(selection=dict(family='wheel_rail_station_lim')))
    packet = root / retention.PACKET
    packet.mkdir(parents=True)
    original = b"original_numerical_producer = True\n"
    source_name = "engineering/original.py"
    source = root / source_name
    source.parent.mkdir(parents=True)
    source.write_bytes(original)
    producer = root / retention.PRODUCER
    producer.parent.mkdir(parents=True)
    producer.write_bytes(Path(retention.__file__).read_bytes())
    ids = dict(zip(retention.PHYSICAL_IDS, (letter * 64 for letter in "1234")))
    context = dict(reference_ids=deepcopy(ids), selection_id="5" * 64,
        source_sha256={retention.PRODUCER: digest(producer)})
    monkeypatch.setattr(retention, "_context", lambda _: deepcopy(context))
    source_map = {source_name: sha256(original).hexdigest()}
    metadata = {}
    for key, (filename, schema) in retention.ARCHIVES.items():
        raw = root / "raw" / key
        raw.mkdir(parents=True)
        result = dict(schema=schema, source_sha256=deepcopy(source_map), **retention.RAIL_FLAGS)
        if key in ("coarse", "fine", "frame"):
            result.update(ids)
        if key in ("solid", "fit"):
            result["parent_candidate_id"] = ids["candidate_id"]
        if wrong_raw_reference and key == "frame":
            result["candidate_id"] = "9" * 64
        if conflicting_source and key == "fit":
            source.write_bytes(b"another_original_epoch = True\n")
            result["source_sha256"][source_name] = digest(source)
        if key not in ("coarse", "fine"):
            result["evaluation_id"] = identity(result)
        (raw / "result.json").write_bytes(encoded(result))
        manifest = dict(source_sha256=result["source_sha256"],
            files_sha256={"result.json": digest(raw / "result.json")}, **retention.RAIL_FLAGS)
        manifest["manifest_id"] = identity(manifest)
        (raw / "manifest.json").write_bytes(encoded(manifest))
        compact = closure_artifacts.export(raw, packet / filename, root=root, include_all=True)
        metadata[key] = dict(archive_name=filename, archive_sha256=digest(packet / filename),
            compact_manifest_id=compact["compact_manifest_id"], retained_raw_payload_complete=True)
        source.write_bytes(original)
    summary = dict(schema="osr-v06-native-followup/1", **ids,
        parent_evaluation_id="6" * 64, selection_id=context["selection_id"],
        complete_station_to_station_journey=False, **retention.RAIL_FLAGS)
    summary["followup_id"] = identity(summary)
    (packet / "summary.json").write_bytes(encoded(summary))
    (packet / "README.md").write_text("Original immutable follow-up reader.\n")
    manifest = dict(schema="osr-v06-followup-publication/1", archives=metadata,
        followup_id=summary["followup_id"], parent_candidate_id=ids["candidate_id"],
        source_sha256=source_map,
        files_sha256={p.name: digest(p) for p in packet.iterdir()}, **retention.RAIL_FLAGS)
    manifest["manifest_id"] = identity(manifest)
    (packet / "manifest.json").write_bytes(encoded(manifest))
    source.write_text("current_producer = True\n")
    before = {p.name: digest(p) for p in packet.iterdir()}
    return original, context, before


def reseal(path, changes):
    record = json.loads(path.read_bytes())
    record.update(changes)
    record["retention_id"] = identity({key: value for key, value in record.items() if key != "retention_id"})
    path.write_bytes(encoded(record))


def test_retention_keeps_all_seven_original_archives_and_separates_current_context(tmp_path, monkeypatch):
    original, context, before = fixture(tmp_path, monkeypatch)
    result = retention.build(tmp_path, resolver=lambda *_: original)
    assert result["verified"] and result["original_native_archive_count"] == 7
    assert result["original_source_count"] == 1
    assert {p.name: digest(p) for p in (tmp_path / retention.PACKET).iterdir()} == before
    assert all(result[key] is value for key, value in retention.FLAGS.items())
    assert result["numerical_reexecuted"] is result["current_evaluator_admission"] is False
    assert result["physical_comparison_proven"] is False
    assert result["current_context_match"] == "reference-identities-only"
    assert result["nested_attempt_source_epochs_enumerated"] is False
    manifest = json.loads((tmp_path / retention.OUTPUT / "manifest.json").read_bytes())
    assert manifest["current_reference_ids"] == context["reference_ids"]
    assert manifest["current_context_source_sha256"] == context["source_sha256"]
    with tarfile.open(tmp_path / retention.OUTPUT / "producer.tar.gz", "r:gz") as archive:
        assert archive.getnames() == ["engineering/original.py"]
        assert archive.extractfile("engineering/original.py").read() == original
    assert retention.verify(tmp_path)["retention_id"] == result["retention_id"]
    assert retention.build(tmp_path)["retention_id"] == result["retention_id"]


def test_wrong_recovered_source_leaves_no_partial_wrapper(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="Recovered original producer bytes differ"):
        retention.build(tmp_path, resolver=lambda *_: b"wrong")
    assert not (tmp_path / retention.OUTPUT).exists()
    assert not list((tmp_path / retention.OUTPUT).parent.glob(".physical-followup-retention-*"))


def test_current_identity_mismatch_and_conflicting_original_epochs_are_rejected(tmp_path, monkeypatch):
    _, context, _ = fixture(tmp_path, monkeypatch)
    context["reference_ids"]["candidate_id"] = "9" * 64
    with pytest.raises(ValueError, match="current selected candidate"):
        retention.build(tmp_path)
    other = tmp_path / "other"
    fixture(other, monkeypatch, conflicting_source=True)
    with pytest.raises(ValueError, match="Conflicting original producer binding"):
        retention.build(other)


def test_raw_result_reference_is_checked_after_archive_receipts_pass(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch, wrong_raw_reference=True)
    with pytest.raises(ValueError, match="Raw native reference identities differ: frame"):
        retention.build(tmp_path)


def test_publication_tampering_and_resealed_promotion_scope_are_rejected(tmp_path, monkeypatch):
    original, _, _ = fixture(tmp_path, monkeypatch)
    retention.build(tmp_path, resolver=lambda *_: original)
    path = tmp_path / retention.OUTPUT / "manifest.json"
    reseal(path, {"current_evaluator_admission": True})
    with pytest.raises(ValueError, match="context or scope differs"):
        retention.verify(tmp_path)
    reseal(path, {"current_evaluator_admission": False})
    (tmp_path / retention.PACKET / "README.md").write_text("changed original reader")
    with pytest.raises(ValueError, match="publication payload differs"):
        retention.verify(tmp_path)


def test_producer_archive_cannot_escape_even_with_resealed_wrapper_hashes(tmp_path, monkeypatch):
    original, _, _ = fixture(tmp_path, monkeypatch)
    retention.build(tmp_path, resolver=lambda *_: original)
    archive_path = tmp_path / retention.OUTPUT / "producer.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        item = tarfile.TarInfo("../escape")
        item.size = len(original)
        archive.addfile(item, io.BytesIO(original))
    reseal(tmp_path / retention.OUTPUT / "manifest.json",
        {"producer_archive_sha256": digest(archive_path)})
    with pytest.raises(ValueError, match="repository-relative"):
        retention.verify(tmp_path)
    assert not (tmp_path / "escape").exists()


def test_output_cannot_overlap_original_packet_or_follow_symlinks(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch)
    for path in ("../escape", retention.PACKET, retention.PACKET + "/wrapper"):
        with pytest.raises(ValueError):
            retention.build(tmp_path, output=path)
    link = tmp_path / "linked"
    link.symlink_to(tmp_path / retention.PACKET, target_is_directory=True)
    with pytest.raises(ValueError, match="symbolic links"):
        retention.build(tmp_path, output="linked/wrapper")


def test_real_packet_all_seven_compact_indexes_and_original_bindings_verify_read_only():
    manifest, summary, sources, archives = retention._packet(retention.ROOT)
    assert len(archives) == 7 and len(sources) >= 26
    assert manifest["parent_candidate_id"] == summary["candidate_id"]
    assert archives["frame"]["retained_raw_payload_complete"] is False
    assert archives["solid"]["omitted_raw_file_count"] > 0
