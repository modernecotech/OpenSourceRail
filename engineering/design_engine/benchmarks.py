"""Independent benchmark dispatcher with mathematical versus physical scope."""

from __future__ import annotations
import json
import subprocess, sys
from pathlib import Path
from .contracts import canonical

CASES = {
    "plate-native": "Analytical strip, MITC4 element and independent native homogeneous S8R plate",
    "hollow-section": "Actual manufactured BOX volume, native beam/solid and analytical bending",
    "thermal-native": "Independent prescribed-boundary thermal-block temperature/flux",
    "civil-native": "Existing independent shear/support/modal/moving-force equilibrium fixtures",
}


def run(case, output):
    output = Path(output)
    if output.exists():
        raise ValueError("benchmark output must be fresh")
    output.mkdir(parents=True)
    if case == "plate-native":
        from engineering.panel_response.verification import native

        result = native(output / "native")
        passed = result["numerical_screen_passed"]
    elif case == "hollow-section":
        from engineering.design_consistency.solver import section_benchmark

        result = section_benchmark(output / "native", mesh_size=0.06)
        passed = result["agreement_screen_passed"]
    elif case == "thermal-native":
        script = (
            Path(__file__).resolve().parents[1]
            / "analysis/benchmarks/calculix/thermal_block.py"
        )
        with (output / "native.log").open("w") as stream:
            subprocess.run(
                [sys.executable, str(script), "--output-dir", str(output / "native")],
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=180,
                check=True,
            )
        result = json.loads((output / "native/summary.json").read_text())
        passed = result["passed"]
    elif case == "civil-native":
        from engineering.analysis.benchmarks.civil.exploration import run as civil

        result = civil()
        passed = result["passed"]
    else:
        raise ValueError("unknown independent benchmark case")
    report = dict(
        schema="osr-independent-numerical-benchmark/1",
        case=case,
        scope=CASES[case],
        passed=bool(passed),
        result=result,
        verification_class="mathematical/native formulation only",
        physical_correlation=False,
        physical_release=False,
    )
    (output / "benchmark.json").write_bytes(canonical(report) + b"\n")
    return report
