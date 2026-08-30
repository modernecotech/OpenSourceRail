#!/usr/bin/env python3
"""Run small deterministic checks against the installed engineering stack."""

from __future__ import annotations

import json
import math
import os
import shutil
import sys
from importlib.metadata import version
from pathlib import Path


def check_ifc() -> dict[str, object]:
    import ifcopenshell

    model = ifcopenshell.file(schema="IFC4X3")
    project = model.create_entity(
        "IfcProject",
        GlobalId=ifcopenshell.guid.new(),
        Name="OSR toolchain smoke project",
    )
    return {
        "schema": model.schema,
        "project_count": len(model.by_type("IfcProject")),
        "project_name": project.Name,
    }


def check_opensees() -> dict[str, object]:
    import openseespy.opensees as ops

    stiffness = 1000.0
    load = 1.0
    expected = load / stiffness
    ops.wipe()
    ops.model("basic", "-ndm", 1, "-ndf", 1)
    ops.node(1, 0.0)
    ops.node(2, 1.0)
    ops.fix(1, 1)
    ops.uniaxialMaterial("Elastic", 1, stiffness)
    ops.element("truss", 1, 1, 2, 1.0, 1)
    ops.timeSeries("Linear", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(2, load)
    ops.system("BandSPD")
    ops.numberer("Plain")
    ops.constraints("Plain")
    ops.integrator("LoadControl", 1.0)
    ops.algorithm("Linear")
    ops.analysis("Static")
    return_code = ops.analyze(1)
    displacement = float(ops.nodeDisp(2, 1))
    ops.wipe()
    if return_code != 0 or not math.isclose(displacement, expected, rel_tol=1e-9):
        raise RuntimeError(
            f"OpenSees axial-bar mismatch: rc={return_code}, "
            f"actual={displacement}, expected={expected}"
        )
    return {"axial_displacement_m": displacement, "expected_m": expected}


def check_pandapower() -> dict[str, object]:
    import pandapower as pp

    network = pp.create_empty_network(sn_mva=1.0)
    source = pp.create_bus(network, vn_kv=20.0)
    load_bus = pp.create_bus(network, vn_kv=20.0)
    pp.create_ext_grid(network, source, vm_pu=1.0)
    pp.create_line_from_parameters(
        network,
        source,
        load_bus,
        length_km=1.0,
        r_ohm_per_km=0.1,
        x_ohm_per_km=0.1,
        c_nf_per_km=0.0,
        max_i_ka=1.0,
    )
    pp.create_load(network, load_bus, p_mw=0.1, q_mvar=0.02)
    pp.runpp(network)
    voltage = float(network.res_bus.vm_pu.at[load_bus])
    if not network.converged or not 0.95 < voltage <= 1.0:
        raise RuntimeError(f"pandapower check did not converge acceptably: {voltage=}")
    return {"converged": bool(network.converged), "load_bus_voltage_pu": voltage}


def check_pvlib() -> dict[str, object]:
    import pvlib

    irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=20.0,
        surface_azimuth=180.0,
        dni=800.0,
        ghi=900.0,
        dhi=100.0,
        solar_zenith=30.0,
        solar_azimuth=180.0,
    )
    poa_global = float(irradiance["poa_global"])
    if not math.isfinite(poa_global) or poa_global <= 0.0:
        raise RuntimeError(f"pvlib returned invalid plane-of-array irradiance: {poa_global}")
    return {"poa_global_w_m2": poa_global}


def check_pybamm() -> dict[str, object]:
    import pybamm

    model = pybamm.lithium_ion.SPM()
    solution = pybamm.Simulation(model).solve([0.0, 60.0])
    voltage = float(solution["Terminal voltage [V]"].entries[-1])
    if not 2.5 < voltage < 5.0:
        raise RuntimeError(f"PyBaMM returned invalid terminal voltage: {voltage}")
    return {"spm_voltage_at_60_s_v": voltage}


def check_swmm() -> dict[str, object]:
    from pyswmm import Simulation

    fixture_source = Path("engineering/analysis/benchmarks/swmm/simple-runoff.inp")
    fixture = Path("build/engineering/toolchain/swmm/simple-runoff.inp")
    fixture.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fixture_source, fixture)
    with Simulation(str(fixture)) as simulation:
        step_count = sum(1 for _ in simulation)
        runoff_error = float(simulation.runoff_error)
        routing_error = float(simulation.flow_routing_error)
    if step_count <= 0 or abs(runoff_error) > 1.0 or abs(routing_error) > 1.0:
        raise RuntimeError(
            "SWMM benchmark failed: "
            f"{step_count=}, {runoff_error=}, {routing_error=}"
        )
    return {
        "step_count": step_count,
        "runoff_error_percent": runoff_error,
        "routing_error_percent": routing_error,
    }


def main() -> int:
    report = {
        "versions": {
            package: version(package)
            for package in (
                "ifcopenshell",
                "jupedsim",
                "numba",
                "openseespy",
                "pandapower",
                "pvlib",
                "pybamm",
                "pyswmm",
                "swmm-toolkit",
            )
        },
        "checks": {
            "ifc": check_ifc(),
            "opensees": check_opensees(),
            "pandapower": check_pandapower(),
            "pvlib": check_pvlib(),
            "pybamm": check_pybamm(),
            "swmm": check_swmm(),
        },
        "imports": {
            "jupedsim": __import__("jupedsim").__name__,
            "pyswmm": __import__("pyswmm").__name__,
        },
    }
    output = Path("build/engineering/toolchain/smoke-check.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    result = main()
    # OpenSeesPy and JuPedSim both load native runtimes. Bypass late native
    # finalizers after the report is safely written so the calling shell can
    # proceed to the EnergyPlus/FDS checks deterministically.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(result)
