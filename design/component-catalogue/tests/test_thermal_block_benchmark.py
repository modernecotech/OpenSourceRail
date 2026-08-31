from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "engineering/analysis/benchmarks/calculix/thermal_block.py"
SPEC = importlib.util.spec_from_file_location("thermal_block", MODULE_PATH)
assert SPEC and SPEC.loader
thermal_block = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(thermal_block)


def test_calculix_thermal_block_parser_and_acceptance() -> None:
    temperatures = "\n".join(
        f"{node} {20.0 if node <= 4 else 40.0 if node <= 8 else 60.0:.1f}" for node in range(1, 13)
    )
    fluxes = "\n".join(f"{element} {point} -80.0 0.0 0.0" for element in (1, 2) for point in range(1, 9))
    dat_text = f"""
 temperatures for set NALL and time 1.0
{temperatures}

 heat flux (elem, integ.pnt.,qx,qy,qz) for set EALL and time 1.0
{fluxes}
"""

    report = thermal_block.evaluate(dat_text, "CalculiX Version 2.23", "fixture-sha256")

    assert report["passed"] is True
    assert report["tool"] == {"name": "CalculiX", "version": "2.23"}
    assert report["results"]["middle_temperature_error_max_c"] == 0.0
    assert report["results"]["longitudinal_flux_error_max_w_m2"] == 0.0
