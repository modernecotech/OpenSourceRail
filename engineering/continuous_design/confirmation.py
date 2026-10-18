"""Exact detailed-child native CAD and independent gross-beam FEM promotion."""
from pathlib import Path
import shutil
import subprocess
import sys

from engineering.twin_workflow import core
from . import beam_confirmation, evidence, tasks


def native(model_path, output):
    output.mkdir(parents=True)
    script=output/"generate.py"
    script.write_text("import sys\nsys.path[:0]="+repr([str(core.ROOT),str(core.ROOT/"design/component-catalogue/src")])+"\n"
        "from engineering.factory_examples.native import export_native\nexport_native("+repr(str(model_path.resolve()))+","+repr(str(output.resolve()))+")\n")
    binary=shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    command=[binary] if binary else ["flatpak","run","--filesystem="+str(output.parent.resolve()),
        "--filesystem="+str(core.ROOT),"--command=FreeCADCmd","org.freecad.FreeCAD"]
    with (output/"freecad.log").open("w") as log:
        subprocess.run([*command,str(script.resolve())],cwd=core.ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600,check=True)
    proof=core.read(output/"native-cad.json",maximum=10_000_000)
    if proof["input_sha256"]!=core.sha(model_path) or not proof["fcstd_reopened"] or not proof["step_reopened"]:
        raise ValueError("native child correspondence failed")
    return proof


def evaluate(envelope, output, children):
    if len(children)!=1:
        raise ValueError("one receipt-bound detailed child required")
    child=children[0];kind=child["task"]["kind"]
    if kind not in {"mechanical-detail","civil-detail"}:
        raise ValueError("confirmation child must be a detailed design")
    module,_=tasks.contexts(kind)
    assessment=child["result"]["assessment"]
    model=module.model_definition(assessment)
    if kind=="mechanical-detail":
        model["interference_roles"]=list({p["role"] for p in model["parts"]})
    path=output/"model-definition.json";core.write(path,model,exclusive=True)
    levels={name:dict(state="not_run",checks=[]) for name in evidence.LEVELS}
    levels["analytical_screening"]=dict(state="passed" if child["result"]["study_pass"] else "failed",
        checks=list(child["result"]["checks"]),child=child["key"])
    errors=[];checks={};proof=None
    try:
        proof=native(path,output/"cad")
        checks["native_exact_child_geometry"]=True
        levels["native_geometry"]=dict(state="passed",checks=["native_exact_child_geometry"],
            part_count=proof["part_count"],interference_checked_ids=proof["interference_checked_ids"],
            scope="Exact simplified child solids, identity, occupied volume, bounds and FCStd/STEP reopen; civil intentional material overlays retained")
    except (subprocess.SubprocessError,ValueError,OSError) as error:
        errors.append(str(error));checks["native_exact_child_geometry"]=False
        levels["native_geometry"]=dict(state="failed",checks=["native_exact_child_geometry"],error=str(error))
    numerical=beam_confirmation.confirm(kind,assessment,output)
    checks.update(numerical["checks"])
    numerical_pass=all(numerical["checks"].values())
    for level in ("numerical_confirmation","numerical_robustness"):
        levels[level]=dict(state="passed" if numerical_pass else "failed",checks=list(numerical["checks"]),scope=numerical["scope"])
    return dict(study_pass=all(checks.values()),checks=checks,failed_checks=[k for k,v in checks.items() if not v],
        verification=dict(evaluated_level="numerical_robustness",levels=levels,independent_physics_rerun=True,
            scope="Candidate-specific equivalent 1D elastic bending plus exact simplified native geometry; physical connections, shell/solid stress and complete system qualification remain open"),
        children=[dict(key=child["key"],kind=kind,study_pass=child["result"]["study_pass"])],
        metrics=dict(native_part_count=proof["part_count"] if proof else None,numerical_cases=len(numerical["cases"])),
        errors=errors,scope="Higher-fidelity research checks of declared simplified child models",**core.FLAGS)
