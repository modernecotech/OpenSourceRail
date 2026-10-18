"""Exact detailed-child native CAD and independent gross-beam FEM promotion."""
from pathlib import Path
import shutil
import subprocess
import sys

from engineering.twin_workflow import core
from . import beam_confirmation, evidence, tasks, native_properties


class NativeFailure(ValueError):
    """A deterministic violation of a declared native geometry check."""


def native(model_path, output):
    output.mkdir(parents=True)
    script=output/"generate.py"
    violations=('native primitive correspondence:', 'fixture solid interference:', 'native reopen identity mismatch',
        'native reopen state or shape changed', 'STEP occupied volume round-trip mismatch')
    outcome=output/'native-outcome.json'
    script.write_text("import sys,json\nsys.path[:0]="+repr([str(core.ROOT),str(core.ROOT/"design/component-catalogue/src")])+"\n"
        "from engineering.factory_examples.native import export_native\ntry:\n    export_native("+repr(str(model_path.resolve()))+","+repr(str(output.resolve()))+")\n"
        'except Exception as error:\n    state="failed" if isinstance(error,ValueError) and str(error).startswith('+repr(violations)+') else "hold"\n'
        '    with open('+repr(str(outcome.resolve()))+',"w") as stream:json.dump(dict(state=state,error=str(error)),stream)\n    raise\n')
    binary=shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
    command=[binary] if binary else ["flatpak","run","--filesystem="+str(output.parent.resolve()),
        "--filesystem="+str(core.ROOT),"--command=FreeCADCmd","org.freecad.FreeCAD"]
    with (output/"freecad.log").open("w") as log:
        completed=subprocess.run([*command,str(script.resolve())],cwd=core.ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    if outcome.is_file():
        checked=core.read(outcome)
        if checked['state']=='failed':raise NativeFailure(checked['error'])
        raise RuntimeError('Native tool held: '+checked['error'])
    if completed.returncode:
        raise RuntimeError('Native tool execution failed; inspect retained FreeCAD log')
    proof=core.read(output/"native-cad.json",maximum=10_000_000)
    if proof["input_sha256"]!=core.sha(model_path) or not proof["fcstd_reopened"] or not proof["step_reopened"]:
        raise NativeFailure("native child correspondence failed")
    return proof


def properties(kind,assessment,model,output):
    spec=native_properties.specification(kind,assessment,model)
    path=output/'native-properties-input.json';core.write(path,spec,exclusive=True)
    script=output/'measure-native.py'
    script.write_text('import sys\nsys.path[:0]='+repr([str(core.ROOT),str(core.ROOT/'design/component-catalogue/src')])+'\n'
        'from engineering.continuous_design.native_properties import measure\nmeasure('+repr(str((output/'cad/model.FCStd').resolve()))+','+
        repr(str(path.resolve()))+','+repr(str((output/'native-properties.json').resolve()))+')\n')
    binary=shutil.which('FreeCADCmd') or shutil.which('freecadcmd')
    command=[binary] if binary else ['flatpak','run','--filesystem='+str(output.resolve()),'--filesystem='+str(core.ROOT),'--command=FreeCADCmd','org.freecad.FreeCAD']
    with (output/'native-properties.log').open('w') as log:
        subprocess.run([*command,str(script.resolve())],stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True)
    result=native_properties.compare(core.read(output/'native-properties.json',maximum=10_000_000),spec)
    core.write(output/'native-properties-comparison.json',result,exclusive=True)
    return result


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
    errors=[];checks={};proof=None;geometry_properties=None
    try:
        proof=native(path,output/"cad")
        checks["native_exact_child_geometry"]=True
        levels["native_geometry"]=dict(state="passed",checks=["native_exact_child_geometry"],
            part_count=proof["part_count"],interference_checked_ids=proof["interference_checked_ids"],
            scope="Exact simplified child solids, identity, occupied volume, bounds and FCStd/STEP reopen; civil intentional material overlays retained")
        geometry_properties=properties(kind,assessment,model,output)
        checks.update(geometry_properties['checks'])
        if not all(geometry_properties['checks'].values()):
            levels['native_geometry']['state']='failed'
        levels['native_geometry']['checks'].extend(geometry_properties['checks'])
    except NativeFailure as error:
        errors.append(str(error));checks["native_exact_child_geometry"]=False
        levels["native_geometry"]=dict(state="failed",checks=["native_exact_child_geometry"],error=str(error))
    except (subprocess.SubprocessError,ValueError,OSError,RuntimeError) as error:
        errors.append(str(error));checks['native_available']=None
        levels['native_geometry']=dict(state='hold',checks=['native_available'],error=str(error),reason='Tool unavailable, interrupted, or measurement incomplete; no design failure inferred')
    numerical=beam_confirmation.confirm(kind,assessment,output,native_ei=geometry_properties['native_ei_nm2'] if geometry_properties else None)
    checks.update(numerical["checks"])
    numerical_pass=all(numerical["checks"].values())
    for level in ("numerical_confirmation","numerical_robustness"):
        levels[level]=dict(state="passed" if numerical_pass else "failed",checks=list(numerical["checks"]),scope=numerical["scope"])
    return dict(study_pass=all(v is True for v in checks.values()),checks=checks,failed_checks=[k for k,v in checks.items() if v is False],
        held_checks=[k for k,v in checks.items() if v is None],
        verification=dict(evaluated_level="numerical_robustness",levels=levels,independent_physics_rerun=True,
            scope="Candidate-specific equivalent 1D elastic bending plus exact simplified native geometry; physical connections, shell/solid stress and complete system qualification remain open"),
        children=[dict(key=child["key"],kind=kind,study_pass=child["result"]["study_pass"])],
        metrics=dict(native_part_count=proof["part_count"] if proof else None,numerical_cases=len(numerical["cases"])),
        errors=errors,scope="Higher-fidelity research checks of declared simplified child models",**core.FLAGS)
