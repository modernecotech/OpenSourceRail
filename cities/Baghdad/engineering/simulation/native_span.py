"""One-axle benchmark of the Airport hollow span between bearing lines, N-m-Pa."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from engineering.performance import run_reserved_command
from cities.Baghdad.engineering.simulation.vehicle_civil import CITY, evaluate


def deck(n, span, force):
    last = 2*n+1
    lines = ["*HEADING", "Airport gross box, central static axle", "*NODE"]
    lines += [f"{i+1},{span*i/(2*n):.10f},0,0" for i in range(last)]
    lines += ["*ELEMENT,TYPE=B32R,ELSET=B"]
    lines += [f"{i+1},{2*i+1},{2*i+2},{2*i+3}" for i in range(n)]
    lines += ["*MATERIAL,NAME=C","*ELASTIC","3.0E10,.2",
              "*BEAM SECTION,ELSET=B,MATERIAL=C,SECTION=BOX","2.,1.4,.18,.20,.18,.20","0.,1.,0.",
              "*BOUNDARY","1,1,3","1,4,4",f"{last},2,3","*NSET,NSET=CENTRE",str(n+1),
              "*STEP","*STATIC","*CLOAD",f"{n+1},3,{-force:.9f}","*NODE PRINT,NSET=CENTRE","U","*END STEP",""]
    return "\n".join(lines)


def worker(folder):
    solver = shutil.which("ccx")
    if not solver:
        raise RuntimeError("CalculiX binary unavailable")
    r = evaluate()
    span = r["selected_span"]["span_actions"]["bearing_span_m"]
    force = max(r["selected"]["axle_kg_per_car"])*9.80665
    inertia = r["selected_span"]["span_actions"]["midspan_I_m4"]
    euler = force*span**3/(48*30e9*inertia)
    rows = []
    for n in (8,16,32):
        path = folder / str(n)
        path.mkdir()
        data = deck(n,span,force).encode()
        (path/"beam.inp").write_bytes(data)
        p = subprocess.run([solver,"beam"], cwd=path, timeout=45, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, env={**os.environ,"OMP_NUM_THREADS":"1"})
        (path/"solver.log").write_bytes(p.stdout)
        p.check_returncode()
        result = (path/"beam.dat").read_text()
        line = re.search(rf"^\s*{n+1}\s+(\S+)\s+(\S+)\s+(\S+)\s*$",result,re.M)
        if not line:
            raise ValueError("Missing centre displacement")
        uz = abs(float(line.group(3)))
        rows.append(dict(elements=n,displacement_m=uz,relative_to_euler=uz/euler-1,
                         input_sha256=hashlib.sha256(data).hexdigest(),
                         output_sha256=hashlib.sha256(result.encode()).hexdigest()))
    report = dict(physical_id=r["physical_id"], vehicle_civil_evaluation_id=r["evaluation_id"], source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  solver_sha256=hashlib.sha256(Path(solver).read_bytes()).hexdigest(), load_n=force,
                  euler_m=euler, cases=rows, fine_mesh_relative_change=rows[-1]["displacement_m"]/rows[-2]["displacement_m"]-1,
                  scope="Prismatic middle section between bearing lines under one centred axle; no solid ends, contact or tendons.")
    (folder/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    with ZipFile(folder/"span-benchmark.zip","x") as archive:
        paths = [folder/"report.json"] + [folder/str(n)/name for n in (8,16,32)
                    for name in ("beam.inp","beam.dat","solver.log")]
        for path in paths:
            member = ZipInfo(str(path.relative_to(folder)), (1980,1,1,0,0,0))
            archive.writestr(member,path.read_bytes(),compress_type=ZIP_DEFLATED)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    parser.add_argument("--worker",action="store_true")
    args = parser.parse_args()
    if args.worker:
        worker(args.output)
    else:
        root = CITY.parents[1]
        args.output.mkdir(parents=True,exist_ok=False)
        _, code = run_reserved_command(root,args.output,"Airport span comparison",32*1024**2,
            [sys.executable,"-m","cities.Baghdad.engineering.simulation.native_span",str(args.output),"--worker"],
            monitor_interval_seconds=.2)
        raise SystemExit(code)
