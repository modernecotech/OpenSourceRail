#!/usr/bin/env python3
"""Reproduce elastic beam sanity checks and civil drainage sensitivities.

This is a software/calculation demonstration, never a railway design release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from osr_mech.civil.decked_pi import section_area_m2, approx_mass_kg

ROOT = Path(__file__).resolve().parents[3]


def dependencies():
    paths = ("design/component-catalogue/src/osr_mech/civil/decked_pi.py", "engineering/analysis/drainage_ground_design.py")
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}


def section_inertia() -> tuple[float, float]:
    # Two stems and flange, in metres; horizontal centroidal bending axis.
    parts = [(2.9, .220, .935 + .110), (.600, .935, .4675)]
    centroid = sum(b*h*y for b,h,y in parts) / section_area_m2()
    inertia = sum(b*h**3/12 + b*h*(y-centroid)**2 for b,h,y in parts)
    return centroid, inertia


def run_beams(output: Path) -> dict:
    import openseespy.opensees as ops
    output.mkdir(parents=True, exist_ok=True)
    area = section_area_m2(); centroid, inertia = section_inertia()
    modulus = 30e9; poisson = .2; count = 40
    height = math.sqrt(12*inertia/area); width = area/height
    results = []
    for span in (20., 25.):
        for stage, additional in (("construction", 0.), ("service", 20_000.)):
            w = approx_mass_kg(span)*9.81/span + additional
            analytical = 5*w*span**4/(384*modulus*inertia)
            ops.wipe(); ops.model("basic", "-ndm", 2, "-ndf", 3)
            for i in range(count+1): ops.node(i+1, span*i/count, 0.)
            ops.fix(1, 1, 1, 0); ops.fix(count+1, 0, 1, 0)
            ops.geomTransf("Linear", 1)
            for i in range(count): ops.element("elasticBeamColumn", i+1, i+1, i+2, area, modulus, inertia, 1)
            ops.timeSeries("Linear", 1); ops.pattern("Plain", 1, 1)
            ops.eleLoad("-ele", *range(1,count+1), "-type", "-beamUniform", -w)
            ops.constraints("Plain"); ops.numberer("RCM"); ops.system("BandGeneral"); ops.test("NormDispIncr", 1e-12, 10)
            ops.algorithm("Linear"); ops.integrator("LoadControl", 1.); ops.analysis("Static")
            if ops.analyze(1) != 0: raise RuntimeError("OpenSees elastic solve failed")
            displacement = abs(ops.nodeDisp(count//2+1, 2))
            native = output / f"pi{span:g}-{stage}-opensees.csv"
            native.write_text("node,x_m,uy_m\n" + "".join(f"{i+1},{span*i/count:.12g},{ops.nodeDisp(i+1,2):.12g}\n" for i in range(count+1)))
            job = f"pi{span:g}-{stage}"
            deck = ["*HEADING", "OSR elastic equivalent rectangular beam sanity check; SI units", "*NODE"]
            deck += [f"{i+1},{span*i/count:.12g},0,0" for i in range(count+1)]
            deck += ["*ELEMENT,TYPE=B31,ELSET=BEAM"] + [f"{i+1},{i+1},{i+2}" for i in range(count)]
            deck += ["*NSET,NSET=MID", str(count//2+1), "*MATERIAL,NAME=ELASTIC", "*ELASTIC", f"{modulus},{poisson}",
                     "*BEAM SECTION,ELSET=BEAM,MATERIAL=ELASTIC,SECTION=RECT", f"{width:.12g},{height:.12g}", "0,0,1",
                     "*BOUNDARY", "1,1,3", f"{count+1},2,3", "*STEP", "*STATIC", "*CLOAD"]
            deck += [f"{i+1},2,{-w*span/count*(.5 if i in (0,count) else 1):.12g}" for i in range(count+1)]
            deck += ["*NODE PRINT,NSET=MID", "U", "*END STEP", ""]
            model = output / f"{job}.inp"; model.write_text("\n".join(deck))
            with tempfile.TemporaryDirectory(prefix="osr-civil-ccx-") as temporary:
                shutil.copy2(model, Path(temporary)/model.name)
                execution = subprocess.run(["ccx", job], cwd=temporary, capture_output=True, text=True, timeout=60)
                if execution.returncode: raise RuntimeError(execution.stdout + execution.stderr)
                dat = (Path(temporary)/f"{job}.dat").read_text()
                (output/f"{job}.dat").write_text(dat)
            pattern = rf"^\s*{count//2+1}\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s+([-+0-9.Ee]+)\s*$"
            matches = re.findall(pattern, dat, re.M)
            if len(matches) != 1: raise ValueError("expected one CalculiX midpoint displacement")
            ccx = abs(float(matches[0][1]))
            error = abs(ccx/analytical - 1)
            results.append({"span_m": span, "stage": stage, "line_load_N_m": w, "analytical_deflection_m": analytical,
                "opensees_deflection_m": displacement, "calculix_deflection_m": ccx, "calculix_relative_error": error,
                "opensees_relative_error": abs(displacement/analytical - 1)})
    ops.wipe()
    report = {"scope": "elastic-software-sanity-only", "project_design_accepted": False,
              "opensees_version": ops.version(), "calculix_version": re.search(r"Version\s+([\d.]+)", execution.stdout).group(1), "modulus_Pa": modulus,
              "poisson_ratio": poisson, "area_m2": area, "centroid_m": centroid, "inertia_m4": inertia,
              "calculix_section": "equal area and bending inertia rectangular surrogate; shear response differs",
              "load_basis": "bulk envelope self-weight; illustrative service additional load 20 kN/m; endpoint supports",
              "formula": "5 w L^4 / (384 E I)", "discretisation_elements": count, "results": results,
              "sanity_passed": all(r["opensees_relative_error"] < 1e-6 and r["calculix_relative_error"] < .05 for r in results)}
    report["generator_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["dependency_hashes"] = dependencies()
    report["output_hashes"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.suffix in {".csv", ".inp", ".dat"}}
    (output/"beam-sanity.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    if not report["sanity_passed"]: raise ValueError("elastic solver comparison failed")
    return report


def run_drainage(output: Path) -> dict:
    from engineering.analysis.drainage_ground_design import replay_swmm, inspect_hydraulic_performance
    source = ROOT/"engineering/assurance/civil-reference/drainage"
    results = {}
    # Deliberately strict demonstration limits expose inadequate cases; no site
    # rainfall, levels or authority approval is implied by this exercise.
    limits = {"flow_units": "LPS", "system_units": "SI",
              "nodes": {"J1": {"peak_head": 1., "flooding_volume": 0., "surcharge_duration": 0.},
                        "O1": {"peak_head": 1., "flooding_volume": 0., "surcharge_duration": 0., "outfall_peak_flow": 100.}},
              "links": {"C1": {"peak_depth": .5, "surcharge_duration": 0.}}}
    for name in ("normal", "blocked-drain", "backwater"):
        model = source/f"{name}.inp"
        replay = replay_swmm(model)
        results[name] = {"input_sha256": hashlib.sha256(model.read_bytes()).hexdigest(), "replay": replay,
                         "illustrative_limit_findings": inspect_hydraulic_performance(replay, limits)}
    report = {"scope": "synthetic-drainage-sensitivity-only", "project_design_accepted": False,
              "illustrative_limits": limits, "scenarios": results,
              "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "dependency_hashes": dependencies()}
    output.mkdir(parents=True, exist_ok=True)
    (output/"drainage-sanity.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"build/engineering/civil-reference")
    args = parser.parse_args()
    run_beams(args.output_dir); run_drainage(args.output_dir)
    print("Civil solver and drainage demonstrations reproduced; project release remains pending.")


if __name__ == "__main__": main()
