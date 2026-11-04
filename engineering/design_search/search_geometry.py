"""Candidate-bound native CAD and exact polyhedral stock IFC handoffs.

The package represents one car's nominal cut stock in vehicle coordinates. It
does not invent joint solids, unlocated equipment, installed clearance or a
complete six-car train. CAD generation is explicit and limited to one job.
"""
from __future__ import annotations

from copy import deepcopy
import json
from math import isfinite
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import time

import numpy as np

from engineering.station_rail import ROOT, common
from engineering.station_rail.common import digest, encoded, identity
from . import design_grammar, grammar_geometry, railway_bundle, wheel_twin

PRODUCER="engineering/design_search/search_geometry.py"
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False,installed_mass_complete=False)
MODULES=(design_grammar,grammar_geometry,railway_bundle,wheel_twin)
LOADED={module.PRODUCER:digest(module.__file__) for module in MODULES}
LOADED[PRODUCER]=digest(__file__)
LOADED["engineering/station_rail/common.py"]=digest(common.__file__)
SCOPE="One-car nominal body stock under the canonical six-car railway bundle; joints and unlocated equipment excluded, complete installed geometry unknown"
REPRESENTATION="Exact outward faceted box/four-wall stock surfaces, correlated with native CAD occurrence volumes; complete installed geometry unknown"


def _regular(path):
    if not stat.S_ISREG(Path(path).lstat().st_mode):
        raise ValueError("Ordinary non-symlink geometry file required")
    return Path(path)


def _read(path):
    path=_regular(path)
    with path.open("rb") as source:
        before=os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size>64*1024*1024:raise ValueError("Geometry record exceeds 64 MiB")
        raw=source.read(64*1024*1024+1);after=os.fstat(source.fileno())
    if len(raw)>64*1024*1024 or any(getattr(before,k)!=getattr(after,k) for k in
            ("st_dev","st_ino","st_size","st_mtime_ns","st_ctime_ns")):
        raise ValueError("Geometry record changed while reading")
    def unique(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError("Duplicate geometry record key")
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=unique,
        parse_constant=lambda value:(_ for _ in ()).throw(ValueError("Nonfinite geometry record")))


def _runtime():
    return dict(python_version=sys.version,python_implementation=platform.python_implementation(),
        python_executable_sha256=digest(Path(sys.executable).resolve()),numpy_version=np.__version__,
        threads={key:os.environ.get(key) for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")})


def _sources(body,bundle,root):
    root=Path(root).resolve()
    if root!=ROOT.resolve():raise ValueError("Use the source checkout that imported geometry adapters")
    for module in MODULES:
        if digest(module.__file__)!=LOADED[module.PRODUCER]:raise ValueError("Loaded geometry dependency changed")
    if digest(__file__)!=LOADED[PRODUCER] or digest(common.__file__)!=LOADED["engineering/station_rail/common.py"]:
        raise ValueError("Loaded geometry source changed")
    for name,sha in body["sources"].items():
        if name in bundle["source_sha256"] and bundle["source_sha256"][name]!=sha:
            raise ValueError("Body and railway bundle source epochs differ")
    source={**body["sources"],**bundle["source_sha256"],**LOADED}
    for name,sha in source.items():
        relative=Path(name)
        if relative.is_absolute() or ".." in relative.parts or digest(_regular(root/relative))!=sha:
            raise ValueError("Geometry source epoch differs: "+name)
    return dict(sorted(source.items()))


def _binding(body,bundle):
    design_grammar.validate(body);railway_bundle.validate(bundle)
    if (bundle["body_candidate_id"]!=body["candidate_id"]
            or bundle["body_definition_id"]!=body["definition_id"]):
        raise ValueError("Geometry cannot combine a different body or bundle definition")
    return dict(candidate_id=bundle["candidate_id"],body_candidate_id=body["candidate_id"],
        body_definition_id=body["definition_id"],bundle_definition_id=bundle["definition_id"],
        support_component_id=bundle["support_component_id"],propulsion_component_id=bundle["propulsion_component_id"],
        body_requirement_revision=body["requirement_revision"],requirement_revision=bundle["requirement_revision"])


def mesh(part):
    """Exact outward triangles for a box or a straight four-wall hollow tube."""
    if type(part.get("volume_m3")) not in (int,float) or not isfinite(part["volume_m3"]) or part["volume_m3"]<=0:
        raise ValueError("Explicit finite positive stock volume required")
    if part.get("kind")=="box":
        size=np.asarray(part["size_m"],dtype=float);origin=np.asarray(part["at_m"],dtype=float)
        if size.shape!=(3,) or origin.shape!=(3,) or not np.all(np.isfinite(size)) or not np.all(np.isfinite(origin)) or min(size)<=0:
            raise ValueError("Finite positive box geometry required")
        vertices=np.array([[x,y,z] for z in (0.,size[2]) for x,y in ((0.,0.),(size[0],0.),(size[0],size[1]),(0.,size[1]))])+origin
        quads=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        expected=float(np.prod(size));holes=0
    elif part.get("kind")=="oriented-RHS":
        w,h,t=[part[k] for k in ("width_m","height_m","wall_m")]
        if any(type(v) not in (int,float) or not isfinite(v) or v<=0 for v in (w,h,t)) or 2*t>=min(w,h):
            raise ValueError("Positive hollow four-wall RHS required")
        start=np.asarray(part["start_m"],dtype=float);end=np.asarray(part["end_m"],dtype=float)
        if start.shape!=(3,) or end.shape!=(3,) or not np.all(np.isfinite(start)) or not np.all(np.isfinite(end)):
            raise ValueError("Finite RHS endpoints required")
        length=float(np.linalg.norm(end-start))
        if length<=0:raise ValueError("Distinct RHS endpoints required")
        rotation=grammar_geometry.basis(part)
        corners=lambda b,d:[(-b/2,-d/2),(b/2,-d/2),(b/2,d/2),(-b/2,d/2)]
        outer,inner=corners(w,h),corners(w-2*t,h-2*t)
        local=np.array([[x,y,z] for loop in (outer,inner) for z in (0.,length) for x,y in loop])
        vertices=local@rotation.T+start
        quads=[]
        for i in range(4):
            j=(i+1)%4
            quads.extend(((i,j,j+4,i+4),(8+i,12+i,12+j,8+j),
                          (i,8+i,8+j,j),(4+i,4+j,12+j,12+i)))
        expected=(w*h-(w-2*t)*(h-2*t))*length;holes=1
    else:
        raise ValueError("Unsupported actual stock primitive; no placeholder geometry permitted")
    faces=np.array([tri for a,b,c,d in quads for tri in ((a,b,c),(a,c,d))],dtype=int)
    triangles=vertices[faces]
    volume=float(np.einsum("ij,ij->i",triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()/6)
    edges={}
    for triangle in faces:
        for a,b in zip(triangle,np.roll(triangle,-1)):
            key=tuple(sorted((int(a),int(b))));edges.setdefault(key,[]).append((int(a),int(b)))
    if any(len(rows)!=2 or rows[0]!=rows[1][::-1] for rows in edges.values()):
        raise ValueError("Faceted stock must have consistently oriented closed edges")
    if abs(volume-expected)>max(1e-11,expected*1e-8) or volume<=0:
        raise ValueError("Outward faceted stock volume differs from actual four-wall/box geometry")
    if abs(part["volume_m3"]-expected)>max(1e-11,expected*1e-8):
        raise ValueError("Stock declared volume differs from exact geometry")
    return dict(id=part["id"],vertices_m=vertices.tolist(),triangles=faces.tolist(),native_volume_m3=expected,
        mesh_volume_m3=volume,closed_surface=True,bore_count=holes,
        surface_euler_characteristic=len(vertices)-len(edges)+len(faces))


def prepare(body,bundle,*,root=ROOT):
    binding=_binding(body,bundle);sources=_sources(body,bundle,root)
    meshes=[mesh(part) for part in body["parts"]]
    value=dict(schema="osr-search-geometry-plan/1",**binding,execution="not-requested",source_sha256=sources,
        runtime=_runtime(),
        occurrence_count=len(meshes),geometry_id=identity(body["physical"]["geometry"]),mesh_id=identity(meshes),
        known_gross_stock_volume_m3=sum(row["native_volume_m3"] for row in meshes),
        complete_installed_geometry=False,scope=SCOPE,
        resources=dict(maximum_native_CAD_jobs=1,CAD_subprocess_timeout_s=180,IFC_cooperative_budget_s=60),**FLAGS)
    value["plan_id"]=identity(value)
    return value


def _tool():
    flatpak=shutil.which("flatpak")
    if flatpak is None:raise ValueError("FreeCAD Flatpak launcher unavailable")
    result=subprocess.run([flatpak,"info","--show-commit","org.freecad.FreeCAD"],capture_output=True,timeout=10,check=False)
    if result.returncode:raise ValueError("FreeCAD Flatpak installation unavailable")
    import ifcopenshell
    import ifcopenshell._ifcopenshell_wrapper as compiled
    return dict(flatpak_path=str(Path(flatpak).resolve()),flatpak_sha256=digest(Path(flatpak).resolve()),
        FreeCAD_flatpak_commit=result.stdout.decode().strip(),ifcopenshell_version=ifcopenshell.version,
        ifcopenshell_compiled_sha256=digest(Path(compiled.__file__).resolve()),
        python_version=sys.version,python_implementation=platform.python_implementation(),
        python_executable_sha256=digest(Path(sys.executable).resolve()),numpy_version=np.__version__)


def _native_input(body):
    parts=deepcopy(body["parts"])
    for part in parts:
        if part["kind"]=="oriented-RHS":
            part.update(length_m=float(np.linalg.norm(np.array(part["end_m"])-part["start_m"])),basis=grammar_geometry.basis(part).tolist())
    return dict(candidate_id=body["candidate_id"],parts=parts)


def _inventory(folder):
    values={}
    for path in sorted(Path(folder).rglob("*")):
        if path.is_symlink():raise ValueError("Ordinary geometry package paths required")
        if path.is_dir():continue
        _regular(path)
        if path.relative_to(folder).as_posix()!="manifest.json":values[path.relative_to(folder).as_posix()]=digest(path)
    return values


def _reopen_ifc(path,bundle,meshes):
    import ifcopenshell,ifcopenshell.geom
    from ifcopenshell.util.element import get_pset
    from ifcopenshell.util.shape import get_volume
    start=time.monotonic();document=ifcopenshell.open(str(_regular(path)))
    objects=document.by_type("IfcBuildingElementProxy");expected={r["id"]:r for r in meshes}
    if len(objects)!=len(expected) or {obj.Name for obj in objects}!=set(expected):
        raise ValueError("Reopened IFC occurrence identities differ")
    for obj in objects:
        if time.monotonic()-start>60:raise TimeoutError("IFC reopening cooperative time budget exhausted")
        props=get_pset(obj,"OSR_Research_Identity")
        if (props.get("candidate_id")!=bundle["candidate_id"] or props.get("occurrence_id")!=obj.Name
                or props.get("frame")!="vehicle" or props.get("physical_accepted") is not False
                or props.get("complete_installed_twin") is not False):
            raise ValueError("Reopened IFC canonical bundle, occurrence or scope differs")
        shape=ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(),obj)
        row=expected[obj.Name];volume=abs(get_volume(shape.geometry))
        if abs(volume-row["native_volume_m3"])>max(1e-10,row["native_volume_m3"]*1e-7):
            raise ValueError("Reopened faceted IFC volume differs from exact CAD stock")
        actual=np.asarray(shape.geometry.verts).reshape((-1,3));corners=np.asarray(row["vertices_m"])
        if (np.max(np.min(np.linalg.norm(actual[:,None,:]-corners[None,:,:],axis=2),axis=1))>1e-7
                or np.max(np.min(np.linalg.norm(corners[:,None,:]-actual[None,:,:],axis=2),axis=1))>1e-7):
            raise ValueError("Reopened IFC stock positions/corners differ")
    return dict(part_count=len(objects),identity_and_exact_stock_volume_verified=True)


def build(body,bundle,output,*,root=ROOT,native_cad_jobs=0):
    if type(native_cad_jobs) is not int or native_cad_jobs not in (0,1):raise ValueError("Explicit zero-or-one native CAD job required")
    plan=prepare(body,bundle,root=root);folder=Path(output)
    if folder.exists() or folder.is_symlink():raise ValueError("Fresh geometry handoff directory required")
    folder.mkdir(parents=True)
    meshes=[mesh(part) for part in body["parts"]]
    result=dict(schema="osr-search-geometry-handoff/1",plan=plan,execution="not-requested",native_CAD_jobs=0,
        native_CAD=None,IFC=None,tool=None,scope=SCOPE,complete_installed_geometry=False,**_binding(body,bundle),**FLAGS)
    if native_cad_jobs:
        tool=_tool()
        cad=grammar_geometry.export(body,folder/"CAD")
        if grammar_geometry.read_export(body,folder/"CAD")!=cad or _read(folder/"CAD/input.json")!=_native_input(body):
            raise ValueError("Native CAD input/body/occurrences differ")
        native_volumes={row["id"]:row["volume_m3"] for row in cad["occurrences"]}
        if set(native_volumes)!={row["id"] for row in meshes}:raise ValueError("Native CAD occurrence coverage differs")
        for row in meshes:
            if abs(native_volumes[row["id"]]-row["native_volume_m3"])>max(1e-10,row["native_volume_m3"]*1e-7):
                raise ValueError("Native CAD and exact faceted hollow stock volumes differ")
        ifc=wheel_twin._ifc(folder,bundle,[dict(part,twin_frame="vehicle") for part in body["parts"]],dict(rows=meshes))
        ifc["representation"]=REPRESENTATION
        result.update(execution="completed-known-stock",native_CAD_jobs=1,native_CAD=cad,IFC=ifc,tool=tool)
        if _tool()!=tool:raise ValueError("Geometry tool/runtime changed during export")
    (folder/"result.json").write_bytes(encoded(result))
    (folder/"mesh.json").write_bytes(encoded(dict(rows=meshes)))
    manifest=dict(schema="osr-search-geometry-manifest/1",**_binding(body,bundle),plan_id=plan["plan_id"],
        source_sha256=plan["source_sha256"],files_sha256=_inventory(folder),**FLAGS)
    manifest["manifest_id"]=identity(manifest)
    (folder/"manifest.json").write_bytes(encoded(manifest))
    return verify(body,bundle,folder,root=root)


def verify(body,bundle,output,*,root=ROOT):
    """Replay hashes/inputs and reopen IFC; never export CAD or IFC again."""
    folder=Path(output)
    if folder.is_symlink() or not folder.is_dir():raise ValueError("Ordinary geometry handoff directory required")
    manifest=_read(folder/"manifest.json");result=_read(folder/"result.json");plan=prepare(body,bundle,root=root)
    expected_manifest_keys={"schema","plan_id","source_sha256","files_sha256","manifest_id",*_binding(body,bundle),*FLAGS}
    expected_result_keys={"schema","plan","execution","native_CAD_jobs","native_CAD","IFC","tool","scope","complete_installed_geometry",*_binding(body,bundle),*FLAGS}
    if (manifest.get("schema")!="osr-search-geometry-manifest/1"
            or set(manifest)!=expected_manifest_keys
            or manifest.get("manifest_id")!=identity({k:v for k,v in manifest.items() if k!="manifest_id"})
            or manifest.get("source_sha256")!=plan["source_sha256"] or manifest.get("plan_id")!=plan["plan_id"]
            or manifest.get("files_sha256")!=_inventory(folder)
            or any(manifest.get(k)!=v for k,v in _binding(body,bundle).items())
            or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError("Geometry handoff manifest, sources, payload or candidate binding differs")
    meshes=[mesh(part) for part in body["parts"]]
    if _read(folder/"mesh.json")!=dict(rows=meshes) or result.get("plan")!=plan:
        raise ValueError("Geometry handoff differs from exact current body stock")
    if (set(result)!=expected_result_keys or result.get("schema")!="osr-search-geometry-handoff/1"
            or result.get("scope")!=SCOPE or result.get("complete_installed_geometry") is not False
            or any(result.get(k)!=v for k,v in _binding(body,bundle).items())
            or any(result.get(k) is not False for k in FLAGS)):
        raise ValueError("Geometry result candidate or release flags differ")
    if result.get("execution")=="not-requested":
        if type(result.get("native_CAD_jobs")) is not int or result.get("native_CAD_jobs")!=0 or result.get("native_CAD") is not None or result.get("IFC") is not None or result.get("tool") is not None:
            raise ValueError("Unrequested geometry cannot claim native execution")
        if set(manifest["files_sha256"])!={"result.json","mesh.json"}:raise ValueError("Unrequested geometry has extra native payload")
    elif result.get("execution")=="completed-known-stock":
        if type(result.get("native_CAD_jobs")) is not int or result.get("native_CAD_jobs")!=1 or result.get("tool")!=_tool():raise ValueError("Native geometry tool/runtime differs")
        if grammar_geometry.read_export(body,folder/"CAD")!=result["native_CAD"] or _read(folder/"CAD/input.json")!=_native_input(body):
            raise ValueError("Native CAD candidate, input or correlation differs")
        _reopen_ifc(folder/"wheel-stock.ifc",bundle,meshes)
        if (result["IFC"].get("execution")!="completed" or result["IFC"].get("part_count")!=len(meshes)
                or result["IFC"].get("native_reopened") is not True
                or result["IFC"].get("representation")!=REPRESENTATION
                or any(result["IFC"].get(k) is not False for k in wheel_twin.FLAGS)):
            raise ValueError("Completed IFC result differs")
    else:raise ValueError("Unknown geometry execution disposition")
    _sources(body,bundle,root)
    return dict(verified=True,manifest_id=manifest["manifest_id"],**result)
