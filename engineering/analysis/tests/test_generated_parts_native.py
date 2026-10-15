"""Opt-in installed-kernel tests; raw executions are retained under ignored build."""

import json
import os
from pathlib import Path
import sys
import subprocess
import time
import unittest

from engineering.design_engine.generated_parts import compile_definition
from engineering.design_engine.generated_parts_native import (
    NativeFailure,
    _Time,
    _run,
    native_screen,
    toolchain,
)

ROOT = Path(__file__).resolve().parents[3]


@unittest.skipUnless(
    os.environ.get("OSR_RUN_NATIVE_PARTS") == "1",
    "explicit installed native part integration",
)
class NativeGeneratedPartsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = (
            ROOT / "build/generated-parts" / ("native-tests-" + str(time.time_ns()))
        )
        cls.output.mkdir(parents=True)
        if not toolchain()["available"]:
            raise unittest.SkipTest("native CAD/mesh/solver prerequisites unavailable")

    def test_actual_boolean_cad_two_meshes_and_independent_cantilever(self):
        charges = []
        model = compile_definition("mechanical-cleat")
        report = native_screen(
            model,
            self.output / "cleat",
            ROOT,
            remaining_seconds=180,
            charge=lambda n, p: charges.append((n, p)),
        )
        self.assertNotIn("failure", report)
        self.assertEqual(sum(n for n, _ in charges), 3)
        for check in (
            "geometry",
            "mass_inertia",
            "load_equilibrium",
            "mesh_refinement",
            "independent_benchmark",
        ):
            self.assertEqual(
                report["checks"][check]["state"],
                "passed",
                json.dumps(report["checks"][check]),
            )
        self.assertFalse(report["physical_release"])
        for row in report["meshes"]:
            self.assertEqual(row["stress_integration_points"], 4 * row["elements"])
        self.assertIn("cad/part.step", report["artifacts_sha256"])
        self.assertIn("cad/inspection.svg", report["artifacts_sha256"])

    def test_actual_gmsh_rejects_invalid_brep_without_fallback(self):
        folder = self.output / "bad-mesh"
        folder.mkdir()
        bad = folder / "bad.brep"
        bad.write_text("not a CAD BRep\n")
        with self.assertRaises(NativeFailure):
            _run(
                [
                    sys.executable,
                    "-m",
                    "engineering.design_engine.generated_parts_native",
                    "mesh",
                    str(bad),
                    str(folder),
                    ".01",
                    ".2",
                ],
                ROOT,
                folder / "gmsh.log",
                _Time(30),
            )
        self.assertFalse((folder / "mesh.json").exists())

    def test_actual_civil_rhs_uses_same_solid_and_fixed_service_screen(self):
        report = native_screen(
            compile_definition("civil-steel-beam"),
            self.output / "civil",
            ROOT,
            remaining_seconds=180,
        )
        self.assertNotIn("failure", report)
        for check in (
            "geometry",
            "mass_inertia",
            "load_equilibrium",
            "mesh_refinement",
            "independent_benchmark",
            "linear_service",
        ):
            self.assertEqual(report["checks"][check]["state"], "passed")
        self.assertEqual(report["checks"]["linear_service"]["limit_m"], 0.008)
        self.assertEqual(report["checks"]["physical_correlation"]["state"], "unknown")

    @unittest.skipUnless(
        hasattr(os, "pidfd_open"), "Linux owned-descendant PIDfd cleanup"
    )
    def test_timeout_inherits_worker_group_and_kills_only_owned_descendants(self):
        folder = self.output / "owned-timeout"
        folder.mkdir()
        sibling = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"]
        )
        script = (
            "import os,sys,time,subprocess,json,signal; from pathlib import Path; "
            "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
            "signal.signal(signal.SIGTERM,lambda *a:(child.wait(timeout=2),sys.exit(0))); "
            "Path('owned.json').write_text(json.dumps({'group':os.getpgrp(),'child':child.pid})); "
            "time.sleep(60)"
        )
        try:
            with self.assertRaises(TimeoutError):
                _run(
                    [sys.executable, "-c", script],
                    folder,
                    folder / "timeout.log",
                    _Time(1),
                )
            record = json.loads((folder / "owned.json").read_text())
            self.assertEqual(record["group"], os.getpgrp())
            self.assertIsNone(sibling.poll())
            child = Path("/proc") / str(record["child"]) / "stat"
            if child.exists():
                text = child.read_text()
                self.assertEqual(text[text.rfind(")") + 2 :].split()[0], "Z")
        finally:
            sibling.terminate()
            sibling.wait(timeout=3)

    def test_actual_calculix_rejects_invalid_deck_without_fallback(self):
        folder = self.output / "bad-solver"
        folder.mkdir()
        (folder / "broken.inp").write_text(
            "*HEADING\nInvalid retained failure test\n*ELEMENT,TYPE=NOT_AN_ELEMENT\n1,1,2\n*STEP\n*STATIC\n*END STEP\n"
        )
        with self.assertRaises(NativeFailure):
            _run(
                [toolchain()["calculix"]["path"], "-i", "broken"],
                folder,
                folder / "calculix.log",
                _Time(30),
            )
        self.assertIn("*ERROR", (folder / "calculix.log").read_text().upper())

    def test_exhausted_budget_never_launches_native_subprocess(self):
        folder = self.output / "no-budget"
        folder.mkdir()
        with self.assertRaises(TimeoutError):
            _run(
                [sys.executable, "-c", "raise RuntimeError('must not execute')"],
                ROOT,
                folder / "never.log",
                _Time(0),
            )
        self.assertFalse((folder / "never.log").exists())


if __name__ == "__main__":
    unittest.main()
