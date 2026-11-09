"""Stdlib subprocess controls for the source-only bootstrap prototype."""
import hashlib
import importlib.util
import json
import marshal
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
ENTRY = ROOT / "tools/automation/source-only-entry.py"
LOADER = ROOT / "engineering/rustgis/source_only_import.py"
NS = "osr_entry_fixture"


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class SourceOnlyEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="osr-source-only-entry-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        self.sources = {}
        self.count = 0
        self.write(NS + "/support.py", b"VALUE = 42\n")
        self.write(NS + "/worker.py", b"import sys\nfrom .support import VALUE\n"
            b"def main(argv):\n"
            b"    return dict(argv=argv, value=VALUE, cached=__cached__,\n"
            b"        disabled=sys.dont_write_bytecode, flag=sys.flags.dont_write_bytecode,\n"
            b"        finder_active=any(type(f).__name__ == 'SourceOnlyImporter' for f in sys.meta_path))\n")
        self.manifest = dict(schema="osr-source-only-entry-manifest/1", repo_root=str(self.repo),
            namespaces=[NS], source_sha256=self.sources,
            entrypoints=[dict(module=NS + ".worker", function="main")],
            loader=dict(path=str(LOADER), sha256=sha(LOADER.read_bytes())),
            max_source_bytes=1024 * 1024)

    def write(self, relative, raw):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        self.sources[relative] = sha(raw)
        return path

    def invoke(self, *, argv=None, module=None, function="main", loader_hash=None, loader_path=LOADER,
               manifest_extra=b"", flags=("-I", "-B"), raw_manifest=None, result=None):
        self.count += 1
        manifest_path = self.base / ("manifest-" + str(self.count) + ".json")
        raw = encoded(self.manifest) if raw_manifest is None else raw_manifest
        manifest_path.write_bytes(raw + manifest_extra)
        output = result or self.base / ("result-" + str(self.count) + ".json")
        command = [sys.executable, *flags, str(ENTRY),
            "--loader", str(loader_path), "--loader-sha256", loader_hash or sha(loader_path.read_bytes()),
            "--manifest", str(manifest_path), "--manifest-sha256", sha(raw),
            "--module", module or NS + ".worker", "--function", function,
            "--argv-json", json.dumps(["first", "two words"] if argv is None else argv),
            "--result", str(output)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        run = subprocess.run(command, cwd="/", env=env, text=True,
                             capture_output=True, timeout=10, check=False)
        self.assertTrue(run.stdout, run.stderr)
        report = json.loads(run.stdout)
        self.assertEqual(report["evaluation_id"],
                         sha(encoded({k: v for k, v in report.items() if k != "evaluation_id"})))
        if result is None:
            self.assertEqual(output.read_bytes(), encoded(report))
        return run, report

    def expected_imports(self, worker_status="completed"):
        return [dict(module=NS, path=NS, sha256=None, bytes=None,
                     kind="closed-namespace", execution="completed"),
            *[dict(module=NS + "." + name, path=NS + "/" + name + ".py",
                sha256=self.sources[NS + "/" + name + ".py"],
                bytes=(self.repo / NS / (name + ".py")).stat().st_size,
                kind="source", execution=worker_status if name == "worker" else "completed")
              for name in ("worker", "support")]]

    def test_verified_source_and_exact_records_with_policy_still_active(self):
        run, report = self.invoke()
        self.assertEqual(run.returncode, 0, report)
        self.assertEqual(report["return_value"], dict(argv=["first", "two words"], value=42,
            cached=None, disabled=True, flag=1, finder_active=True))
        self.assertEqual(report["imports"], self.expected_imports())
        self.assertEqual(report["bindings"]["loader"]["sha256"], sha(LOADER.read_bytes()))
        self.assertEqual(report["interpreter"]["isolated"], 1)
        self.assertFalse(list(self.repo.rglob("__pycache__")))

    def test_existing_conflicting_pyc_is_ignored_and_preserved(self):
        src = self.repo / NS / "worker.py"
        cached = Path(importlib.util.cache_from_source(str(src)))
        cached.parent.mkdir()
        raw = (importlib.util.MAGIC_NUMBER +
            struct.pack("<III", 0, int(src.stat().st_mtime), src.stat().st_size) +
            marshal.dumps(compile("raise AssertionError('conflicting pyc executed')", str(src), "exec")))
        cached.write_bytes(raw)
        legacy = src.with_suffix(".pyc")
        legacy.write_bytes(raw)
        run, report = self.invoke()
        self.assertEqual(run.returncode, 0, report)
        self.assertEqual(report["imports"], self.expected_imports())
        self.assertEqual(cached.read_bytes(), raw)
        self.assertEqual(legacy.read_bytes(), raw)
        self.assertEqual(sorted(str(p.relative_to(self.repo)) for p in self.repo.rglob("*.pyc")),
                         sorted(str(p.relative_to(self.repo)) for p in (cached, legacy)))

    def test_stale_loader_digest_prevents_any_project_import(self):
        run, report = self.invoke(loader_hash="0" * 64)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(report["error"]["message"], "SHA256 differs: loader")
        self.assertEqual(report["imports"], [])

    def test_loader_bytes_are_compiled_without_using_conflicting_loader_pyc(self):
        copied = self.base / "pinned-loader.py"
        copied.write_bytes(LOADER.read_bytes())
        self.manifest["loader"] = dict(path=str(copied), sha256=sha(copied.read_bytes()))
        cached = Path(importlib.util.cache_from_source(str(copied)))
        cached.parent.mkdir()
        raw = (importlib.util.MAGIC_NUMBER +
            struct.pack("<III", 0, int(copied.stat().st_mtime), copied.stat().st_size) +
            marshal.dumps(compile("raise AssertionError('conflicting loader pyc executed')", str(copied), "exec")))
        cached.write_bytes(raw)
        run, report = self.invoke(loader_path=copied)
        self.assertEqual(run.returncode, 0, report)
        self.assertEqual(report["bindings"]["loader"]["sha256"], sha(copied.read_bytes()))
        self.assertEqual(report["imports"], self.expected_imports())
        self.assertEqual(cached.read_bytes(), raw)

    def test_stale_source_digest_preserves_prior_namespace_record(self):
        self.sources[NS + "/worker.py"] = "0" * 64
        run, report = self.invoke()
        self.assertEqual(run.returncode, 2)
        self.assertIn("Source SHA256 differs", report["error"]["message"])
        self.assertEqual(report["imports"], self.expected_imports()[:1])

    def test_stale_manifest_digest_is_refused(self):
        run, report = self.invoke(manifest_extra=b" ")
        self.assertEqual(run.returncode, 2)
        self.assertEqual(report["error"]["message"], "SHA256 differs: source_manifest")
        self.assertEqual(report["imports"], [])

    def test_missing_source_module_is_refused_without_fallback(self):
        (self.repo / NS / "worker.py").unlink()
        run, report = self.invoke()
        self.assertEqual(run.returncode, 2)
        self.assertIn("Missing, symlinked or inaccessible source", report["error"]["message"])
        self.assertEqual(len(report["imports"]), 1)

    def test_unlisted_module_or_function_is_not_invoked(self):
        path = self.repo / NS / "omitted.py"
        path.write_bytes(b"raise AssertionError('unlisted module executed')\n")
        for change in (dict(module=NS + ".omitted"), dict(function="other")):
            with self.subTest(change=change):
                run, report = self.invoke(**change)
                self.assertEqual(run.returncode, 2)
                self.assertIn("not allowlisted", report["error"]["message"])
                self.assertEqual(report["imports"], [])

    def test_entrypoint_without_source_allowlist_cannot_be_admitted(self):
        self.manifest["entrypoints"] = [dict(module=NS + ".omitted", function="main")]
        run, report = self.invoke(module=NS + ".omitted")
        self.assertEqual(run.returncode, 2)
        self.assertIn("absent from the source allowlist", report["error"]["message"])

    def test_function_failure_preserves_all_completed_import_records(self):
        self.write(NS + "/worker.py", b"from .support import VALUE\n"
            b"def main(argv):\n    raise RuntimeError('bounded function failure')\n")
        run, report = self.invoke()
        self.assertEqual(run.returncode, 2)
        self.assertEqual(report["imports"], self.expected_imports())
        self.assertEqual(report["error"], dict(type="RuntimeError", message="bounded function failure"))

    def test_import_failure_retains_failed_source_execution(self):
        self.write(NS + "/worker.py", b"from .support import VALUE\n"
            b"raise RuntimeError('bounded import failure')\n")
        run, report = self.invoke()
        self.assertEqual(run.returncode, 2)
        self.assertEqual(report["imports"], self.expected_imports(worker_status="failed"))

    def test_json_argv_is_bounded_and_typed(self):
        for argv in (dict(wrong="shape"), [123], ["x" * 4097]):
            with self.subTest(argv_type=type(argv).__name__):
                run, report = self.invoke(argv=argv)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(report["imports"], [])

    def test_isolation_flag_is_required_with_bytecode_still_disabled(self):
        run, report = self.invoke(flags=("-B",))
        self.assertEqual(run.returncode, 2)
        self.assertEqual(report["interpreter"]["dont_write_bytecode_flag"], 1)
        self.assertIn("python -I -B", report["error"]["message"])
        self.assertEqual(report["imports"], [])

    def test_external_manifest_size_is_bounded(self):
        run, report = self.invoke(raw_manifest=b" " * (4 * 1024 * 1024 + 1))
        self.assertEqual(run.returncode, 2)
        self.assertIn("Ordinary bounded file required: source_manifest", report["error"]["message"])

    def test_existing_result_is_preserved_and_function_is_not_invoked(self):
        result = self.base / "preserved.json"
        result.write_bytes(b"original evidence\n")
        run, report = self.invoke(result=result)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(report["imports"], [])
        self.assertEqual(result.read_bytes(), b"original evidence\n")


if __name__ == "__main__":
    unittest.main()
