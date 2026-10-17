"""Storage integrity tests: historical bytes, failed cases and bindings survive."""

from copy import deepcopy
import json
from pathlib import Path
import gzip
from unittest.mock import patch
import tempfile
import unittest

from engineering.generative_design import evidence_store as es


class EvidenceStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = self.root / "objects"
        self.folder = self.root / "published"

    def tearDown(self):
        self.tmp.cleanup()

    def files(self):
        # The same failed evidence occurs in multiple reports and twice inside
        # one payload; it must remain visible while its payload is stored once.
        case = dict(
            id="failed-reference",
            values=list(range(1600)),
            checks={"manufacturing": {"status": "failed"}},
            physical_release=False,
        )
        report = dict(
            candidates=[case, deepcopy(case)],
            selected_candidate_ids=[],
            physical_release=False,
        )
        files = {
            "search.json": es.pretty(report),
            "models/search.json": es.pretty(report),
            "native/model.FCStd": b"retained-native-bytes\0",
            "plot.svg": b"<svg/>",
            "unusual.json": b'{"unissued":true,"physical_release":false}',
        }
        files["snapshot.json"] = es.pretty(
            dict(
                schema="historical-seal/1",
                physical_release=False,
                source_sha256={"source.py": "b" * 64},
                files_sha256={name: es.digest(data) for name, data in files.items()},
            )
        )
        return files

    def publish(self, files=None):
        return es.publish_files(files or self.files(), self.folder, store=self.store)

    def test_lossless_original_seal_json_native_and_failed_cases(self):
        files = self.files()
        self.publish(files)
        with es.materialized(self.folder) as restored:
            for name, original in files.items():
                self.assertEqual((restored / name).read_bytes(), original)
        self.assertEqual(
            es.read_json(self.folder / "search.json")["candidates"][0]["checks"][
                "manufacturing"
            ]["status"],
            "failed",
        )
        self.assertFalse(
            es.read_json(self.folder / "snapshot.json")["physical_release"]
        )
        self.assertEqual(
            es.read_bytes(self.folder / "unusual.json"), files["unusual.json"]
        )

    def test_identical_files_and_nested_cases_share_objects(self):
        files = self.files()
        self.publish(files)
        first = json.loads((self.folder / "search.json").read_bytes())
        second = json.loads((self.folder / "models/search.json").read_bytes())
        self.assertEqual(first["original"], second["original"])
        objects = list(self.store.rglob("*.json.gz"))
        stored = sum(p.stat().st_size for p in self.store.rglob("*") if p.is_file())
        self.assertLess(stored, sum(map(len, files.values())) / 2)
        repeated_case_nodes = [
            p for p in objects if b"failed-reference" in gzip.decompress(p.read_bytes())
        ]
        self.assertEqual(len(repeated_case_nodes), 1)
        self.assertLess(
            sum(p.stat().st_size for p in self.folder.rglob("*.json")), 6000
        )

    def test_reference_and_manifest_mismatch_fails(self):
        self.publish()
        path = self.folder / "search.json"
        reference = json.loads(path.read_bytes())
        reference["original"]["size"] += 1
        path.write_bytes(es.pretty(reference))
        with self.assertRaises(ValueError):
            es.verify_projection(self.folder)

    def test_missing_or_corrupt_shared_object_fails(self):
        self.publish()
        path = next(self.store.rglob("*.json.gz"))
        original = path.read_bytes()
        path.write_bytes(original + b" ")
        with self.assertRaisesRegex(ValueError, "object hash differs"):
            es.verify_projection(self.folder)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "missing evidence object"):
            es.verify_projection(self.folder)

    def test_local_native_mutation_and_extra_file_fail(self):
        self.publish()
        path = self.folder / "native/model.FCStd"
        original = path.read_bytes()
        path.write_bytes(original + b"changed")
        with self.assertRaisesRegex(ValueError, "local evidence asset differs"):
            es.verify_projection(self.folder)
        path.write_bytes(original)
        (self.folder / "extra.txt").write_text("unsealed")
        with self.assertRaisesRegex(ValueError, "member set differs"):
            es.verify_projection(self.folder)

    def test_source_closure_does_not_include_unrelated_new_objects(self):
        self.publish()
        with patch.object(es, "ROOT", self.root), patch.object(es, "STORE", self.store):
            before = es.source_closure(self.folder / "search.json")
            es.ObjectStore(self.store).archive(
                es.pretty({"new": list(range(9000))}), json_file=True
            )
            self.assertEqual(before, es.source_closure(self.folder / "search.json"))
            for name, expected in before.items():
                self.assertEqual(es.digest((self.root / name).read_bytes()), expected)

    def test_minified_utf8_is_reconstructed_byte_exactly(self):
        files = self.files()
        original = (
            json.dumps(
                {"text": "manufacturing ≥ required", "failed": list(range(2000))},
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode()
            + b"\n"
        )
        files["minified.json"] = original
        self.publish(files)
        descriptor = json.loads((self.folder / "minified.json").read_bytes())[
            "original"
        ]
        self.assertEqual(descriptor["encoding"], "json-compact-utf8-sorted-newline")
        self.assertEqual(es.read_bytes(self.folder / "minified.json"), original)

    def test_compressed_object_hash_binds_actual_stored_bytes(self):
        self.publish()
        for path in self.store.rglob("*.json.gz"):
            self.assertEqual(path.name.split(".")[0], es.digest(path.read_bytes()))
            self.assertEqual(
                json.loads(gzip.decompress(path.read_bytes()))["schema"], es.NODE_SCHEMA
            )

    def test_manifest_original_seal_hash_must_match(self):
        self.publish()
        path = self.folder / es.MANIFEST
        manifest = json.loads(path.read_bytes())
        manifest["original_seal_sha256"] = "0" * 64
        path.write_bytes(es.pretty(manifest))
        with self.assertRaisesRegex(ValueError, "seal hash differs"):
            es.verify_projection(self.folder)

    def test_symlink_member_and_traversal_are_rejected(self):
        self.publish()
        path = self.folder / "plot.svg"
        path.unlink()
        path.symlink_to(self.root / "external.svg")
        (self.root / "external.svg").write_bytes(b"<svg/>")
        with self.assertRaisesRegex(ValueError, "symlink"):
            es.verify_projection(self.folder)
        with self.assertRaisesRegex(ValueError, "unsafe evidence member"):
            es.publish_files(
                {"../escape.json": b"{}"}, self.root / "bad", store=self.store
            )

    def test_migration_preserves_original_bytes_and_is_idempotent(self):
        files = self.files()
        self.folder.mkdir()
        for name, data in files.items():
            path = self.folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        first = es.migrate(self.folder, store=self.store)
        manifest_bytes = (self.folder / es.MANIFEST).read_bytes()
        second = es.migrate(self.folder, store=self.store)
        self.assertEqual(first, second)
        self.assertEqual(manifest_bytes, (self.folder / es.MANIFEST).read_bytes())
        self.assertEqual(
            {name: es.read_bytes(self.folder / name) for name in files}, files
        )

    def test_prune_retains_artifacts_and_objects_named_by_original_source_map(self):
        docs = self.root / "docs/design-engine"
        docs.mkdir(parents=True)
        store_path = docs / "evidence-store"
        packet = docs / "historical"
        objects = es.ObjectStore(store_path)
        bound = objects.put(b"old source object bytes", "blob")
        orphan = objects.put(b"unpublished temporary bytes", "blob")
        files = self.files()
        seal = json.loads(files["snapshot.json"])
        source_name = objects.path(bound, "blob").relative_to(self.root).as_posix()
        seal["source_sha256"] = {source_name: bound}
        files["snapshot.json"] = es.pretty(seal)
        with patch.object(es, "ROOT", self.root), patch.object(es, "STORE", store_path):
            es.publish_files(files, packet, store=store_path)
            before = es.collect_unreferenced()
            self.assertEqual(before["unreferenced_objects"], 1)
            self.assertTrue(objects.path(orphan, "blob").is_file())
            result = es.collect_unreferenced(delete=True)
            self.assertTrue(result["deletion_performed"])
            self.assertFalse(objects.path(orphan, "blob").exists())
            self.assertTrue(objects.path(bound, "blob").is_file())
            self.assertEqual(
                es.read_bytes(packet / "search.json"), files["search.json"]
            )
            self.assertTrue(es.verify_projection(packet)["integrity_verified"])

    def test_prune_fails_before_deletion_when_retained_source_object_is_missing(self):
        docs = self.root / "docs/design-engine"
        docs.mkdir(parents=True)
        store_path = docs / "evidence-store"
        packet = docs / "historical"
        files = self.files()
        seal = json.loads(files["snapshot.json"])
        seal["source_sha256"] = {
            "docs/design-engine/evidence-store/sha256/00/"
            + "0" * 64
            + ".blob": "0" * 64
        }
        files["snapshot.json"] = es.pretty(seal)
        with patch.object(es, "ROOT", self.root), patch.object(es, "STORE", store_path):
            es.publish_files(files, packet, store=store_path)
            orphan = es.ObjectStore(store_path).put(b"unreferenced", "blob")
            with self.assertRaisesRegex(ValueError, "missing evidence object"):
                es.collect_unreferenced(delete=True)
            self.assertTrue(es.ObjectStore(store_path).path(orphan, "blob").exists())

    def test_nested_literal_ref_keys_are_preserved_as_data(self):
        files = self.files()
        files["literal.json"] = es.pretty(
            {"value": {"ref": "0" * 64}, "ref": {"value": 2}}
        )
        self.publish(files)
        self.assertEqual(
            es.read_bytes(self.folder / "literal.json"), files["literal.json"]
        )

    def test_corrupt_existing_immutable_object_is_never_overwritten(self):
        self.publish()
        path = next(self.store.rglob("*.json.gz"))
        path.write_bytes(b"corruption")
        with self.assertRaisesRegex(ValueError, "immutable evidence object differs"):
            es.publish_files(self.files(), self.root / "another", store=self.store)
        self.assertEqual(path.read_bytes(), b"corruption")


if __name__ == "__main__":
    unittest.main()
