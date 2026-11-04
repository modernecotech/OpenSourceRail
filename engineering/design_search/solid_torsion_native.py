"""Actual-wall C3D20R torsion controls, independent of beam BOX kinematics.

The base restrains warping. A balanced, explicitly lumped end-face force couple
introduces end effects; J is inferred from central section-rotation gradients.
No arbitrary solid-node rotational DOFs or fitted torsion constants are used.
"""
from collections import defaultdict
from math import atan2, fsum, isfinite
from pathlib import Path
import json
import os
import resource
import stat
import subprocess
import time

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, encoded, identity
from . import frame_native

PRODUCER = "engineering/design_search/solid_torsion_native.py"
LOADED = digest(__file__)
MANUAL = "https://www.dhondt.de/ccx_2.23.pdf"
FLAGS = dict(physical_accepted=False, engineering_accepted=False, manufacturing_release=False,
    operating_release=False, configuration_adopted=False, selected_reference_changed=False)
SCHEMA = "osr-solid-rhs-torsion-model/1"
OFFSETS = ((0,0,0),(2,0,0),(2,2,0),(0,2,0),(0,0,2),(2,0,2),(2,2,2),(0,2,2),
    (1,0,0),(2,1,0),(1,2,0),(0,1,0),(1,0,2),(2,1,2),(1,2,2),(0,1,2),
    (0,0,1),(2,0,1),(2,2,1),(0,2,1))
FACE = ((0,0),(2,0),(2,2),(0,2),(1,0),(2,1),(1,2),(0,1))
LIMITATIONS = ["Clamped base restrains warping; finite length and load-introduction effects remain",
    "Positive face-area lumping is a declared discrete torque load, not an exact Saint-Venant end traction",
    "Central rotation-gradient and mesh/length changes must be checked; global end work alone is insufficient",
    "Quadratic solid mesh, integration/locking, stress and material uncertainty remain research questions",
    "No real material, joint, vehicle or physical qualification is established"]


def model(*, width_m=.08, height_m=.16, wall_m=.004, length_m=1.5, E_Pa=70e9, nu=.33, torque_Nm=1., loading_hypothesis="polar-area-lumped-end-traction"):
    return dict(schema=SCHEMA, width_m=width_m, height_m=height_m, wall_m=wall_m,
        length_m=length_m, E_Pa=E_Pa, nu=nu, torque_Nm=torque_Nm,
        material_law="isotropic-linear-elastic-research", source_basis="Declared unqualified aluminium control",
        boundary="base-all-solid-translations-fixed; positive-area-lumped-tangential-end-forces",
        loading_hypothesis=loading_hypothesis)


def _validate(value):
    if value.get("schema") != SCHEMA or value.get("material_law") != "isotropic-linear-elastic-research" or not value.get("source_basis"):
        raise ValueError("Explicit isotropic solid torsion control model required")
    if value.get("boundary") != model()["boundary"]:
        raise ValueError("Declared restrained-base and discrete end-couple control required")
    if value.get("loading_hypothesis","polar-area-lumped-end-traction") not in (
            "polar-area-lumped-end-traction","geometry-normalised-closed-wall-shear-flow"):
        raise ValueError("Explicit supported end-loading hypothesis required")
    for key in ("width_m", "height_m", "wall_m", "length_m", "E_Pa"):
        if type(value.get(key)) not in (int,float) or not isfinite(value[key]) or value[key] <= 0:
            raise ValueError("Positive finite solid geometry and modulus required")
    if 2*value["wall_m"] >= min(value["width_m"],value["height_m"]):
        raise ValueError("Actual positive open RHS hole required")
    if type(value.get("nu")) not in (int,float) or not 0 <= value["nu"] < .49 or type(value.get("torque_Nm")) not in (int,float) or not isfinite(value["torque_Nm"]) or value["torque_Nm"] == 0:
        raise ValueError("Bounded isotropic Poisson ratio and nonzero finite torque required")


def _axis(outer, wall, interior, through):
    a,b = -outer/2,outer/2
    return [a+wall*i/through for i in range(through)] + [a+wall+(outer-2*wall)*i/interior for i in range(interior)] + [b-wall+wall*i/through for i in range(through+1)]


def mesh(value, *, axial_elements=8, width_divisions=2, height_divisions=4, through_wall=1, element_kind="C3D20R"):
    _validate(value)
    if element_kind not in ("C3D20R", "C3D20"):
        raise ValueError("Explicit C3D20R or C3D20 integration method required")
    for number, maximum in ((axial_elements,64),(width_divisions,16),(height_divisions,32),(through_wall,4)):
        if type(number) is not int or not 1 <= number <= maximum:
            raise ValueError("Bounded explicit solid mesh counts required")
    if axial_elements < 8:
        raise ValueError("At least eight axial elements required for central-gradient sampling")
    axes = [[value["length_m"]*i/axial_elements for i in range(axial_elements+1)],
        _axis(value["width_m"],value["wall_m"],width_divisions,through_wall),
        _axis(value["height_m"],value["wall_m"],height_divisions,through_wall)]
    ny,nz = len(axes[1])-1,len(axes[2])-1
    cells = [(j,k) for j in range(ny) for k in range(nz)
             if j < through_wall or j >= ny-through_wall or k < through_wall or k >= nz-through_wall]
    if len(cells)*axial_elements > 2304:
        raise ValueError("Solid element budget exceeded")
    keys, raw_elements = set(), []
    for i in range(axial_elements):
        for j,k in cells:
            element = [(2*i+a,2*j+b,2*k+c) for a,b,c in OFFSETS]
            keys.update(element); raw_elements.append(element)
    if len(keys) > 30_000: raise ValueError("Solid node budget exceeded")
    numbers = {key:i+1 for i,key in enumerate(sorted(keys))}
    def coordinate(axis, index):
        return axes[axis][index//2] if index % 2 == 0 else (axes[axis][index//2]+axes[axis][index//2+1])/2
    nodes = [dict(id=numbers[key], grid_key=list(key), at_m=[coordinate(a,k) for a,k in enumerate(key)]) for key in sorted(keys)]
    weights = defaultdict(float);wall_forces=defaultdict(lambda:[0.,0.]);owners=defaultdict(int)
    area = 0.
    for j,k in cells:
        cell_area = (axes[1][j+1]-axes[1][j])*(axes[2][k+1]-axes[2][k]); area += cell_area
        # Horizontal walls own corner cells; vertical walls own only their
        # intervening height. Shared face nodes receive both owners' forces.
        owner="bottom" if k<through_wall else "top" if k>=nz-through_wall else "left" if j<through_wall else "right"
        direction={"bottom":(1.,0.),"top":(-1.,0.),"left":(0.,-1.),"right":(0.,1.)}[owner];owners[owner]+=1
        for a,b in FACE:
            key=2*j+a,2*k+b;weights[key]+=cell_area/8
            for d in range(2):wall_forces[key][d]+=direction[d]*cell_area/8
    section = [dict(grid_key=list(key), at_yz_m=[coordinate(1,key[0]),coordinate(2,key[1])],weight_m2=weight) for key,weight in sorted(weights.items())]
    denominator = fsum(row["weight_m2"]*fsum(v*v for v in row["at_yz_m"]) for row in section)
    flow=value.get("loading_hypothesis","polar-area-lumped-end-traction")=="geometry-normalised-closed-wall-shear-flow"
    raw_torque=fsum(row["at_yz_m"][0]*wall_forces[tuple(row["grid_key"])][1]-row["at_yz_m"][1]*wall_forces[tuple(row["grid_key"])][0] for row in section)
    loads=[]
    for row in section:
        if flow:
            fy,fz=[v*value["torque_Nm"]/raw_torque for v in wall_forces[tuple(row["grid_key"])]]
        else:
            fy=-value["torque_Nm"]*row["weight_m2"]*row["at_yz_m"][1]/denominator
            fz=value["torque_Nm"]*row["weight_m2"]*row["at_yz_m"][0]/denominator
        loads.append(dict(node_id=numbers[2*axial_elements,*row["grid_key"]],force_N=[0.,fy,fz]))
    result = dict(schema="osr-solid-rhs-torsion-mesh/1",model_id=identity(value),
        settings=dict(axial_elements=axial_elements,width_divisions=width_divisions,height_divisions=height_divisions,through_wall=through_wall,element_kind=element_kind),
        nodes=nodes,elements=[[numbers[key] for key in row] for row in raw_elements],section_points=section,loads=loads,
        base_node_ids=[row["id"] for row in nodes if row["grid_key"][0] == 0],
        area_m2=area,stock_volume_m3=area*value["length_m"],wall_face_owner_counts=dict(sorted(owners.items())),
        corner_ownership="Horizontal top/bottom walls own corner cells; shared nodes accumulate owner contributions",
        applied_force_N=[fsum(row["force_N"][d] for row in loads) for d in range(3)],
        applied_torque_Nm=fsum(s["at_yz_m"][0]*l["force_N"][2]-s["at_yz_m"][1]*l["force_N"][1] for s,l in zip(section,loads)))
    expected = value["width_m"]*value["height_m"]-(value["width_m"]-2*value["wall_m"])*(value["height_m"]-2*value["wall_m"])
    if abs(area-expected) > expected*1e-12 or abs(result["applied_torque_Nm"]-value["torque_Nm"]) > abs(value["torque_Nm"])*1e-12 or max(map(abs,result["applied_force_N"])) > abs(value["torque_Nm"])*1e-10:
        raise ValueError("Actual-wall area or applied end couple does not reconcile")
    result["mesh_id"] = identity(result)
    return result


def deck(value, discretization):
    if discretization != mesh(value,**discretization["settings"]): raise ValueError("Solid mesh differs from model")
    lines = ["*HEADING","Actual hollow RHS solid torsion control; SI N-m-Pa","*NODE,NSET=ALLNODES"]
    lines += [str(n["id"])+","+",".join(f"{v:.16g}" for v in n["at_m"]) for n in discretization["nodes"]]
    lines += ["*ELEMENT,TYPE="+discretization["settings"]["element_kind"]+",ELSET=SOLID"]
    for i,row in enumerate(discretization["elements"],1):
        lines += [str(i)+","+",".join(map(str,row[:15]))+",", ",".join(map(str,row[15:]))]
    lines += ["*MATERIAL,NAME=CONTROL","*ELASTIC",f"{value['E_Pa']:.16g},{value['nu']:.16g}",
        "*SOLID SECTION,ELSET=SOLID,MATERIAL=CONTROL","*NSET,NSET=BASE"]
    base = discretization["base_node_ids"]
    lines += [",".join(map(str,base[i:i+12])) for i in range(0,len(base),12)]
    lines += ["*BOUNDARY","BASE,1,3","*STEP","*STATIC","*CLOAD"]
    lines += [f"{row['node_id']},{d+1},{v:.16g}" for row in discretization["loads"] for d,v in enumerate(row["force_N"]) if v]
    lines += ["*NODE PRINT,NSET=ALLNODES","U","*NODE PRINT,NSET=BASE","RF",
        "*EL PRINT,ELSET=SOLID,TOTALS=ONLY","ELSE","*END STEP",""]
    return "\n".join(lines)


def analyse(value, discretization, dat_path):
    u,reactions,energy = frame_native.parse_dat(dat_path)
    numbers = {tuple(row["grid_key"]):row["id"] for row in discretization["nodes"]}
    coordinates = {row["id"]:row["at_m"] for row in discretization["nodes"]}
    if set(u) != set(coordinates) or not set(discretization["base_node_ids"]) <= set(reactions):
        raise ValueError("Complete solid displacement and base reaction records required")
    nx = discretization["settings"]["axial_elements"]; length = value["length_m"]
    def rotations(indices,points):
        planes=[]
        for i in indices:
            sine,cosine=[],[]
            for row in points:
                y,z=row["at_yz_m"];_,uy,uz=u[numbers[i,*row["grid_key"]]];w=row["weight_m2"]
                sine.append(w*(y*uz-z*uy));cosine.append(w*(y*(y+uy)+z*(z+uz)))
            planes.append(dict(x_m=length*i/(2*nx),angle_rad=atan2(fsum(sine),fsum(cosine))))
        return planes
    def gradient(planes):
        central=[row for row in planes if .25*length-1e-12 <= row["x_m"] <= .75*length+1e-12]
        mx=fsum(row["x_m"] for row in central)/len(central);ma=fsum(row["angle_rad"] for row in central)/len(central)
        slope=fsum((r["x_m"]-mx)*(r["angle_rad"]-ma) for r in central)/fsum((r["x_m"]-mx)**2 for r in central)
        if not isfinite(slope) or slope == 0:raise ValueError("Nonzero finite interior twist gradient required")
        local=[(b["angle_rad"]-a["angle_rad"])/(b["x_m"]-a["x_m"]) for a,b in zip(central,central[1:])]
        return slope,max(abs(v-slope) for v in local)/abs(slope)
    planes=rotations(range(0,2*nx+1,2),discretization["section_points"])
    corners=[row for row in discretization["section_points"] if all(i%2 == 0 for i in row["grid_key"])]
    corner_vertex=rotations(range(0,2*nx+1,2),corners)
    corner_mid=rotations(range(1,2*nx,2),corners)
    slope,spread=gradient(planes);corner_vertex_slope,corner_vertex_spread=gradient(corner_vertex);corner_mid_slope,corner_mid_spread=gradient(corner_mid)
    shear = value["E_Pa"]/(2*(1+value["nu"])); j = value["torque_Nm"]/(shear*slope)
    if not isfinite(j) or j <= 0: raise ValueError("Positive finite interior torsion response required")
    external_work = .5*fsum(fsum(a*b for a,b in zip(row["force_N"],u[row["node_id"]])) for row in discretization["loads"])
    base_torque = fsum(coordinates[n][1]*reactions[n][2]-coordinates[n][2]*reactions[n][1] for n in discretization["base_node_ids"])
    return dict(J_interior_gradient_m4=j,twist_gradient_rad_m=slope,section_rotations=planes,
        central_gradient_relative_spread=spread,
        corner_only_vertex_rotations=corner_vertex,corner_only_midplane_rotations=corner_mid,
        J_vertex_corner_gradient_m4=value["torque_Nm"]/(shear*corner_vertex_slope),
        J_midplane_corner_gradient_m4=value["torque_Nm"]/(shear*corner_mid_slope),
        vertex_corner_gradient_relative_spread=corner_vertex_spread,midplane_corner_gradient_relative_spread=corner_mid_spread,
        calibration_admission=False,inference_state="unverified-interior-gradient-end-boundary-and-mesh-model",
        native_strain_energy_J=energy,external_work_J=external_work,
        energy_work_relative_residual=abs(energy-external_work)/max(abs(energy),1e-30),
        base_reaction_torque_Nm=base_torque,torque_relative_residual=abs(base_torque+value["torque_Nm"])/abs(value["torque_Nm"]),
        force_equilibrium_residual_N=[fsum(reactions[n][d] for n in discretization["base_node_ids"])+discretization["applied_force_N"][d] for d in range(3)],
        J_global_energy_assuming_uniform_twist_m4=2*energy/(shear*slope*slope*length),
        global_energy_is_end_effect_diagnostic_only=True)


def _sources(root):
    if digest(__file__) != LOADED: raise ValueError("Solid torsion source changed after import")
    return frame_native._sources(root,{PRODUCER:LOADED})


def _resources():
    result = dict(frame_native._resources(),maximum_seconds=45)
    limits = [v for v in resource.getrlimit(resource.RLIMIT_CPU) if v != resource.RLIM_INFINITY]
    result["effective_cpu_seconds"] = min([45]+limits)
    return result


def run(value, output, *, execute=False, root=ROOT, **settings):
    if type(execute) is not bool: raise ValueError("Explicit Boolean execution required")
    out=Path(output);out.mkdir(parents=True,exist_ok=False);sources=_sources(root)
    discretization=mesh(value,**settings);text=deck(value,discretization)
    tool=frame_native._tool();resources=_resources()
    request=dict(schema="osr-solid-torsion-native-request/1",model_id=identity(value),mesh_id=discretization["mesh_id"],settings=discretization["settings"],
        execute=execute,tool=tool,resources=resources,runtime=frame_native._runtime(),source_sha256=sources,manual=MANUAL,limitations=LIMITATIONS)
    request["request_id"]=identity(request)
    for name,item in (("model.json",value),("mesh.json",discretization),("input.json",request)):(out/name).write_bytes(encoded(item))
    (out/"solid.inp").write_text(text);(out/"solver.log").write_text("")
    result=dict(schema="osr-solid-torsion-native-result/1",model_id=identity(value),mesh_id=discretization["mesh_id"],request_id=request["request_id"],
        execution="not-run",native_jobs_used=0,elapsed_s=0.,analysis=None,**FLAGS)
    if execute:
        if tool is None:result.update(execution="held",hold_reason="native-tool-unavailable")
        else:
            result["native_jobs_used"]=1;start=time.monotonic()
            try:
                environment=dict(os.environ,OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",CCX_NPROC_RESULTS="1",CCX_NPROC_EQUATION_SOLVER="1",NUMBER_OF_CPUS="1")
                with (out/"solver.log").open("wb") as log:
                    process=subprocess.run([tool["path"],"-i","solid"],cwd=out,env=environment,stdout=log,stderr=subprocess.STDOUT,
                        timeout=45,preexec_fn=lambda:frame_native._limits(resources),check=False)
                result["returncode"]=process.returncode
                if process.returncode:raise ValueError("Native solid solver failed")
                result.update(execution="completed",analysis=analyse(value,discretization,out/"solid.dat"))
            except (ValueError,OSError,subprocess.SubprocessError) as exc:result.update(execution="failed",failure=str(exc))
            result["elapsed_s"]=time.monotonic()-start
    _sources(root);result["evaluation_id"]=identity(result);(out/"result.json").write_bytes(encoded(result))
    manifest=dict(schema="osr-solid-torsion-native-package/1",evaluation_id=result["evaluation_id"],request_id=request["request_id"],source_sha256=sources,
        files_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},**FLAGS)
    manifest["manifest_id"]=identity(manifest);(out/"manifest.json").write_bytes(encoded(manifest))
    return verify(out,root=root)


def verify(output, *, root=ROOT):
    out=Path(output)
    if out.is_symlink() or not out.is_dir() or any(not stat.S_ISREG(p.lstat().st_mode) for p in out.iterdir()):raise ValueError("Regular solid package files required")
    records={name:json.loads((out/name).read_bytes()) for name in ("manifest.json","input.json","model.json","mesh.json","result.json")}
    manifest,request,value,discretization,result=[records[name] for name in ("manifest.json","input.json","model.json","mesh.json","result.json")]
    for record,key in ((manifest,"manifest_id"),(request,"request_id"),(result,"evaluation_id")):
        if record[key]!=identity({k:v for k,v in record.items() if k!=key}):raise ValueError("Solid package identity differs")
    if manifest["schema"]!="osr-solid-torsion-native-package/1" or request["schema"]!="osr-solid-torsion-native-request/1" or result["schema"]!="osr-solid-torsion-native-result/1":raise ValueError("Solid schema differs")
    if manifest["files_sha256"]!={p.name:digest(p) for p in out.iterdir() if p.name!="manifest.json"}:raise ValueError("Solid payload differs")
    if not {"model.json","mesh.json","input.json","solid.inp","solver.log","result.json"} <=set(manifest["files_sha256"]):raise ValueError("Required solid payload missing")
    if request["source_sha256"]!=_sources(root) or manifest["source_sha256"]!=request["source_sha256"]:raise ValueError("Solid source context differs")
    if request["resources"]!=_resources() or request["runtime"]!=frame_native._runtime() or request["tool"]!=frame_native._tool() or type(request["execute"]) is not bool:raise ValueError("Solid tool, runtime or resources differ")
    if discretization!=mesh(value,**request["settings"]) or (out/"solid.inp").read_text()!=deck(value,discretization):raise ValueError("Solid model/mesh/deck differs")
    if any(r["model_id"]!=identity(value) or r["mesh_id"]!=discretization["mesh_id"] for r in (request,result)):raise ValueError("Mixed solid model or mesh identity")
    expected_jobs=1 if request["execute"] and request["tool"] is not None else 0
    if type(result["native_jobs_used"]) is not int or result["native_jobs_used"]!=expected_jobs:raise ValueError("Solid job count differs")
    if not request["execute"]:state="not-run"
    elif request["tool"] is None:state="held"
    elif result["execution"]=="completed":
        state="completed"
        if result.get("returncode")!=0 or result["analysis"]!=analyse(value,discretization,out/"solid.dat"):raise ValueError("Solid native result differs")
    else:
        state="failed"
        if not result.get("failure"):raise ValueError("Native failure reason missing")
    if result["execution"]!=state or (state!="completed" and result["analysis"] is not None) or (expected_jobs==0 and result["elapsed_s"]!=0):raise ValueError("Solid execution state differs")
    if result["request_id"]!=request["request_id"] or manifest["request_id"]!=request["request_id"] or manifest["evaluation_id"]!=result["evaluation_id"] or any(record.get(k) is not False for record in (manifest,result) for k in FLAGS):raise ValueError("Solid context or qualification differs")
    _sources(root)
    return dict(verified=True,manifest_id=manifest["manifest_id"],**result)
