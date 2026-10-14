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
    "electrical-balance": "Constant-OCV quadratic current, energy, SOC and zero-cooling heat against an independent closed-form fixture",
    "prestress-reference": "FHWA independently published elastic-shortening example, converted to SI; no project material adoption",
    "vehicle-conservation": "Actual physical mass and gravity reaction balance across separate equipment and mass-normalized research body modes",
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
    elif case == "electrical-balance":
        from .electrical_installation import cooling_loss_duty

        result = cooling_loss_duty(
            dict(
                nominal_voltage_v=100.0,
                resistance_ohm=0.1,
                thermal_capacity_j_k=100.0,
                capacity_ah=100.0,
                soc_min=0.1,
                soc_max=0.9,
                temperature_limit_c=50.0,
                discharge_current_limit_a=50.0,
                charge_current_limit_a=50.0,
            ),
            [dict(duration_s=20.0, terminal_power_w=990.0)],
            initial_soc=0.8,
            initial_temperature_c=20.0,
            ambient_temperature_c=20.0,
        )
        # 100 I - 0.1 I² = 990 selects the low-current root I=10 A.
        expected = dict(soc=0.8 - 10 * 20 / (100 * 3600), temperature_c=22.0)
        result = dict(actual=result, independent_expected=expected)
        passed = all(
            abs(result["actual"]["history"][-1][key] - value) < 1e-10
            for key, value in expected.items()
        )
    elif case == "prestress-reference":
        from .civil_qualification import elastic_shortening, REFERENCES

        inch, ksi = 0.0254, 6894757.293168361
        group = dict(
            metallic_area_m2=44 * 0.153 * inch**2,
            pretransfer_stress_pa=202.5 * ksi,
            steel_modulus_pa=28500 * ksi,
            eccentricity_m=31.38 * inch,
        )
        loss = elastic_shortening(
            [group],
            area_m2=1085 * inch**2,
            inertia_m4=733320 * inch**4,
            concrete_modulus_pa=4200 * ksi,
            self_weight_moment_nm=20142 * 4448.2216152605 * inch,
        )
        result = dict(
            computed_loss_ksi=loss[0] / ksi,
            published_loss_ksi=13.7,
            reference=REFERENCES["elastic_shortening"],
            provisional_absolute_tolerance_ksi=0.05,
        )
        passed = abs(result["computed_loss_ksi"] - 13.7) < 0.05
    elif case == "vehicle-conservation":
        from engineering.civil_exploration.variant_compiler import compile_variant
        from .vehicle_confirmation import assembly_diagnostics

        package = compile_variant()
        result = [assembly_diagnostics(package, mode_count=count) for count in (2, 4)]
        passed = all(
            row["mass_relative_error"] < 1e-12
            and row["reaction_relative_error"] < 1e-12
            and row["minimum_static_contact_n"] > 0
            and row["modal_preload_residual_n"] < 1e-6
            for row in result
        )
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
