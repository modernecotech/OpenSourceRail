"""One frozen civil FieldCraft replay and honest full-field gallery rendering.

This visual request does not alter a candidate, remesh, or confer engineering
acceptance. A saved result is essential: one probe cannot define a displacement
field. All native work uses the existing bubblewrap/POSIX-budget adapter.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile


SCHEMA = "osr-civil-gallery-replay/1"
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
EXPECTED = dict(
    report_id="ec17e7e1b932293e6cb8c1795746f9de76f8edc7cb23f1157738eac26cfb7309",
    candidate_id="5bab407d93e079c02eaf8a0399cb1707d421fa8976c631524df534ad74d0bb97",
    civil_evaluation_id="79ced43bd512115a7e21a4361f55e39404f64412e64b45866250e0b81db30361",
    cells=22680, nodes=43340,
    probe_xyz_m=[10., 0., 0.],
    probe_U_m=[0.0018766706894536177, 1.1841890292159726e-05, -0.013947614842694347],
)
LIMITATIONS = [
    "One normal-base load pose; gross bonded homogeneous elastic concrete.",
    "Rotation-free ideal bearing lines; no finite contact/compliance model.",
    "No cracking, prestress, segment-joint, fatigue or physical qualification.",
    "Nodal-smoothed FieldCraft stress is not an integration-point peak.",
]


def encoded(v):
    return (json.dumps(v, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def identity(v):
    return hashlib.sha256(encoded(v)).hexdigest()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sealed(v):
    return dict(v, evaluation_id=identity(v))


def check_seal(v):
    if v.get("evaluation_id") != identity({k: x for k, x in v.items() if k != "evaluation_id"}):
        raise ValueError("Evidence seal changed")


def write(path, v):
    Path(path).write_bytes(encoded(v))


def original_tail(path):
    commands = []
    for line in Path(path).read_text().splitlines():
        message = json.loads(line)
        if message.get("method") == "tools/call":
            commands.extend(message["params"]["arguments"].get("commands", []))
    index = max(i for i, c in enumerate(commands) if c["command"] == "file.open")
    tail = commands[index:]
    if [c["command"] for c in tail] != ["file.open", "model.load.create", "model.step.create",
            "model.check", "solve.static", "solve.probe", "results.reactions", "model.info"]:
        raise ValueError("Different checkpoint/tail contract")
    if tail[4]["params"] != {"step": "Research"}:
        raise ValueError("Different solve request")
    return tail


def prepare(source, output, *, root=None):
    """Freeze exact archived inputs before the separately authorized one solve."""
    from engineering.design_search.craft_backends import native
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output or source in output.parents:
        raise ValueError("New visual request must not write inside historical evidence")
    manifest = json.loads((source / "manifest.json").read_bytes()); check_seal(manifest)
    report = json.loads((source / "report.json").read_bytes()); check_seal(report)
    if (report["evaluation_id"] != EXPECTED["report_id"] or
            report["civil_candidate_id"] != EXPECTED["candidate_id"] or
            report["civil_evaluation_id"] != EXPECTED["civil_evaluation_id"]):
        raise ValueError("Different civil candidate/evaluation")
    names = ["report.json", "native-input.json", "case-3/result.json", "case-3/mesh.json",
             "case-3/fieldcraft/stdin.jsonl", "case-3/fieldcraft/rolling-4.fieldcraft"]
    inputs = {}
    for name in names:
        record = manifest["files"][name]; p = source / name
        if p.stat().st_size != record["bytes"] or digest(p) != record["sha256"]:
            raise ValueError("Archived evidence bytes changed: " + name)
        inputs[str(p)] = record["sha256"]
    mesh = json.loads((source / "case-3/mesh.json").read_bytes())
    if len(mesh["elements"]) != EXPECTED["cells"] or len(mesh["nodes"]) != EXPECTED["nodes"]:
        raise ValueError("Different fine mesh")
    tail = original_tail(source / "case-3/fieldcraft/stdin.jsonl")
    output.mkdir(parents=True, exist_ok=False)
    frozen = output / "inputs"; frozen.mkdir()
    checkpoint = frozen / "rolling-4.fieldcraft"
    shutil.copyfile(source / "case-3/fieldcraft/rolling-4.fieldcraft", checkpoint)
    shutil.copyfile(source / "case-3/mesh.json", frozen / "mesh.json")
    write(frozen / "original-tail.json", tail)
    commands = deepcopy(tail)
    commands[0]["params"]["path"] = str(checkpoint)
    execution = output / "execution"
    commands.extend([
        dict(command="results.export.vtu", params=dict(step="Research", path=str(execution / "field.vtu"), encoding="ascii", frames="last")),
        dict(command="file.save", params=dict(path=str(execution / "solved.fieldcraft"), results=True, geometry="embed")),
    ])
    write(output / "commands.json", {"commands": commands})
    root = Path(root or Path(__file__).resolve().parents[2])
    request = sealed(dict(schema=SCHEMA, purpose="README actual FEM result visual, not a new physics trial",
        source=str(source), source_inputs_sha256=inputs, expected=EXPECTED,
        checkpoint_sha256=digest(checkpoint), mesh_sha256=digest(frozen / "mesh.json"),
        original_tail_sha256=digest(frozen / "original-tail.json"), commands_sha256=digest(output / "commands.json"),
        source_sha256={str(Path(__file__).resolve()): digest(__file__),
                       str(root / "engineering/design_search/craft_backends/native.py"): digest(root / "engineering/design_search/craft_backends/native.py"),
                       str(root / "engineering/design_search/craft_backends/tools.json"): digest(root / "engineering/design_search/craft_backends/tools.json")},
        tool_pin=native.pin("fieldcraft"), read_root=str(output), write_root=str(execution),
        resources=dict(solves=1, max_cells=22680, memory_mib_each_process=3072,
                       cpu_s_soft=74, cpu_s_hard=75, wall_s=73, file_limit_bytes=64 * 1024**2),
        limitations=LIMITATIONS, **FLAGS))
    write(output / "request.json", request)
    return request


def read_vtu(path):
    """Read an ASCII native export; retain explicit result-validity flags."""
    import numpy as np
    tree = ET.parse(path); piece = tree.find(".//Piece")
    if piece is None:
        raise ValueError("VTU Piece missing")
    def array(tag, name=None):
        parent = piece.find(tag)
        if parent is None:
            raise ValueError("Missing VTU section " + tag)
        values = parent.findall("DataArray")
        e = next((e for e in values if name is None or e.get("Name") == name), None)
        if e is None or e.get("format", "ascii").lower() != "ascii":
            raise ValueError("Required ASCII VTU array missing: " + str(name))
        n = int(e.get("NumberOfComponents", "1"))
        dtype = int if e.get("type", "").startswith(("Int", "UInt")) else float
        a = np.fromstring(e.text or "", sep=" ", dtype=dtype)
        return a.reshape((-1, n)) if n > 1 else a
    return dict(points=array("Points"), node_label=array("PointData", "node_label"),
        element_label=array("CellData", "element_label"),
        displacement=array("PointData", "displacement"), has_result=array("PointData", "has_result"),
        von_mises=array("PointData", "von_mises"),
        connectivity=array("Cells", "connectivity"), offsets=array("Cells", "offsets"), types=array("Cells", "types"))


def validate_field(field, mesh, *, expected_probe=None):
    """Require the full same-node/same-cell finite field, never fill unknowns."""
    import numpy as np
    nodes, elements = mesh["nodes"], mesh["elements"]
    labels = [int(v) for v in field["node_label"]]
    if len(labels) != len(nodes) or len(set(labels)) != len(labels) or set(labels) != {int(n) for n in nodes}:
        raise ValueError("Full exact node labels required")
    if field["points"].shape != (len(nodes), 3) or field["displacement"].shape != (len(nodes), 3):
        raise ValueError("Full XYZ and U vector required")
    if len(field["has_result"]) != len(nodes) or not np.all(field["has_result"] == 1):
        raise ValueError("Missing native nodal results cannot be plotted as zero")
    if field["von_mises"].shape != (len(nodes),):
        raise ValueError("Full native nodal stress scalar required")
    for name in ("points", "displacement", "von_mises"):
        if not np.isfinite(field[name]).all():
            raise ValueError("Non-finite native field: " + name)
    # FieldCraft's ASCII Points writer rounds to ten decimal places in metres.
    # This is an exchange-format precision check, not a physical tolerance.
    original_xyz = np.asarray([nodes[str(n)] for n in labels])
    coordinate_residual = float(np.abs(field["points"] - original_xyz).max())
    if coordinate_residual > 5.1e-11:
        raise ValueError("Native mesh coordinates changed")
    cell_labels = [int(v) for v in field["element_label"]]
    if len(cell_labels) != len(elements) or set(cell_labels) != {int(n) for n in elements}:
        raise ValueError("Full exact element labels required")
    if len(field["offsets"]) != len(elements) or len(field["types"]) != len(elements):
        raise ValueError("Full exact cell metadata required")
    previous = 0
    for i, (label, end) in enumerate(zip(cell_labels, field["offsets"])):
        end = int(end)
        ids = [labels[int(j)] for j in field["connectivity"][previous:end]]
        if int(field["types"][i]) != 24 or ids != elements[str(label)]:
            raise ValueError("Exact tetra10 connectivity changed")
        previous = end
    if previous != len(field["connectivity"]):
        raise ValueError("Unused VTU connectivity")
    if expected_probe is not None:
        xyz, expected = expected_probe
        indices = np.flatnonzero(np.all(field["points"] == xyz, axis=1))
        if len(indices) != 1 or not np.allclose(field["displacement"][indices[0]], expected, rtol=1e-9, atol=1e-12):
            raise ValueError("Fresh full-field probe differs from retained result")
    return dict(nodes=len(nodes), cells=len(elements), all_nodes_have_result=True,
                max_displacement_m=float(np.linalg.norm(field["displacement"], axis=1).max()),
                max_nodal_von_mises_Pa=float(field["von_mises"].max()),
                ascii_coordinate_max_residual_m=coordinate_residual,
                ascii_coordinate_rounding_bound_m=5.1e-11)


def run(output):
    """Consume a frozen request once; preserve failures and prohibit reruns."""
    from engineering.design_search.craft_backends import native
    from engineering.design_search.craft_backends.fieldcraft import batch_results
    output = Path(output).resolve()
    request = json.loads((output / "request.json").read_bytes()); check_seal(request)
    if (output / "attempt.json").exists() or (output / "execution").exists():
        raise ValueError("Exactly one native solve attempt permitted; retain previous failure")
    for name, want in {**request["source_inputs_sha256"], **request["source_sha256"]}.items():
        if digest(name) != want:
            raise ValueError("Frozen source/input changed: " + name)
    for name, key in [("inputs/rolling-4.fieldcraft", "checkpoint_sha256"), ("inputs/mesh.json", "mesh_sha256"),
                      ("inputs/original-tail.json", "original_tail_sha256"), ("commands.json", "commands_sha256")]:
        if digest(output / name) != request[key]:
            raise ValueError("Frozen replay changed: " + name)
    if native.pin("fieldcraft") != request["tool_pin"]:
        raise ValueError("Pinned FieldCraft changed")
    commands = json.loads((output / "commands.json").read_bytes())["commands"]
    if sum(c["command"] in ("solve.static", "solve.run") for c in commands) != 1:
        raise ValueError("One solve required")
    write(output / "attempt.json", sealed(dict(request_id=request["evaluation_id"], **FLAGS)))
    execution, replies = native.mcp("fieldcraft", [("batch", dict(commands=commands))], output / "execution",
        timeout_s=73, memory_mb=3072, read_root=output)
    result = dict(schema=SCHEMA, request_id=request["evaluation_id"], execution=execution, **FLAGS)
    write(output / "result.json", sealed(result))
    if execution["execution"] != "executed":
        raise ValueError("Native replay failed; failure retained")
    for reply in replies:
        if "error" in reply:
            raise ValueError("Native replay returned JSON-RPC error")
        if reply.get("id") == 2:
            payload = native.payload(reply)
            write(output / "native-payload.json", payload)
            batch_results(payload, len(commands))
    return finalize(output)


def finalize(output):
    """Validate already exported results without issuing any native solve."""
    output = Path(output).resolve()
    request = json.loads((output / "request.json").read_bytes()); check_seal(request)
    result = json.loads((output / "result.json").read_bytes()); check_seal(result)
    result.pop("evaluation_id")
    if result["execution"]["execution"] != "executed":
        raise ValueError("A completed native execution is required")
    # The binary saved mesh is a stronger exact-geometry check than the
    # deliberately rounded ASCII coordinate export.
    with zipfile.ZipFile(output / "inputs/rolling-4.fieldcraft") as before, zipfile.ZipFile(output / "execution/solved.fieldcraft") as after:
        original = before.read("mesh.bin"); fresh = after.read("mesh.bin")
        if original != fresh:
            raise ValueError("Saved native mesh bytes changed")
        if "results.bin" not in after.namelist():
            raise ValueError("Full native solved results were not saved")
        meta = json.loads(after.read("fieldcraft.json"))
        for name, record in meta["parts"].items():
            value = after.read(name)
            if len(value) != record["bytes"] or hashlib.sha256(value).hexdigest() != record["sha256"]:
                raise ValueError("Native saved-project part integrity failed")
        result["native_mesh_bin_sha256"] = hashlib.sha256(fresh).hexdigest()
        result["native_mesh_byte_identical"] = True
    field = read_vtu(output / "execution/field.vtu")
    mesh = json.loads((output / "inputs/mesh.json").read_bytes())
    validation = validate_field(field, mesh, expected_probe=(EXPECTED["probe_xyz_m"], EXPECTED["probe_U_m"]))
    unchanged = all(digest(p) == want for p, want in request["source_inputs_sha256"].items())
    if not unchanged:
        raise ValueError("Archived inputs changed during replay")
    result.update(validation=validation, source_unchanged=True,
        full_field_sha256=digest(output / "execution/field.vtu"),
        saved_results_sha256=digest(output / "execution/solved.fieldcraft"),
        probe_U_m=EXPECTED["probe_U_m"], limitations=LIMITATIONS,
        postprocessor_sha256=digest(__file__))
    write(output / "result.json", sealed(result))
    return result


def exterior_triangles(mesh):
    """Expose quadratic faces and subdivide with their actual midside nodes."""
    faces = {}; edges = ((0,1),(1,2),(2,0),(0,3),(1,3),(2,3))
    for element in mesh["elements"].values():
        mids = {tuple(sorted((element[a], element[b]))): element[4+i] for i, (a,b) in enumerate(edges)}
        for a,b,c in ((0,2,1),(0,1,3),(1,2,3),(0,3,2)):
            a,b,c = element[a],element[b],element[c]; key=tuple(sorted((a,b,c)))
            if key in faces:
                faces[key]=None
            else:
                faces[key]=(a,b,c,mids[tuple(sorted((a,b)))],mids[tuple(sorted((b,c)))],mids[tuple(sorted((c,a)))])
    triangles=[]
    for face in faces.values():
        if face is None: continue
        a,b,c,ab,bc,ca=face
        triangles.extend(((a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)))
    return triangles


def plot(output, path):
    """Scientific plate from native full U, with explicit 100x deformation."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    output, path = Path(output), Path(path)
    result=json.loads((output / "result.json").read_bytes()); check_seal(result)
    if not result.get("validation", {}).get("all_nodes_have_result"):
        raise ValueError("Validated full native field required before rendering")
    if digest(output / "execution/field.vtu") != result["full_field_sha256"]:
        raise ValueError("Solved field changed")
    field=read_vtu(output / "execution/field.vtu")
    mesh=json.loads((output / "inputs/mesh.json").read_bytes())
    validate_field(field, mesh, expected_probe=(EXPECTED["probe_xyz_m"], EXPECTED["probe_U_m"]))
    labels={int(n):i for i,n in enumerate(field["node_label"])}
    tri=np.array([[labels[n] for n in row] for row in exterior_triangles(mesh)])
    xyz=field["points"]; u=field["displacement"]; magnitude=np.linalg.norm(u,axis=1)*1000
    deformed=xyz+100*u
    plt.rcParams.update({"font.family":"DejaVu Sans","text.color":"#14344d","axes.labelcolor":"#14344d"})
    fig=plt.figure(figsize=(15,9.5),dpi=200,facecolor="#f7f9fb")
    fig.text(.055,.94,"20 m viaduct · structural response",size=27,weight="bold")
    fig.text(.055,.901,"FieldCraft 0.7.5  /  actual full-field export  /  same-candidate normal-base load",size=12,color="#426079")
    fig.text(.055,.845,"13.9476 mm",size=26,weight="bold",color="#007f89")
    fig.text(.055,.815,"midspan vertical displacement",size=10,color="#426079")
    fig.text(.40,.845,f"{magnitude.max():.4f} mm",size=26,weight="bold",color="#007f89")
    fig.text(.40,.815,"maximum displacement magnitude",size=10,color="#426079")
    fig.text(.755,.845,"22,680",size=26,weight="bold",color="#007f89")
    fig.text(.755,.815,"quadratic tetrahedra · 43,340 nodes",size=10,color="#426079")
    ax=fig.add_axes([.015,.25,.88,.56],projection="3d",computed_zorder=False)
    cmap=plt.get_cmap("viridis"); norm=Normalize(0,magnitude.max())
    coll=Poly3DCollection(deformed[tri],facecolors=cmap(norm(magnitude[tri].mean(axis=1))),
                          edgecolors="none",antialiased=False,zsort="average")
    ax.add_collection3d(coll)
    ax.set(xlim=(-.5,20.5),ylim=(-1.2,1.2),zlim=(deformed[:,2].min()-.2,xyz[:,2].max()+.5))
    ax.set_box_aspect((20,2.4,3.1));ax.view_init(elev=18,azim=-63);ax.set_proj_type("ortho")
    ax.set_axis_off();ax.set_facecolor("#f7f9fb")
    for x in (.35,19.65):
        z=float(xyz[:,2].min())
        ax.plot([x,x],[-.7,.7],[z,z],color="#183a53",linewidth=4,zorder=100)
    cbax=fig.add_axes([.90,.38,.015,.29])
    cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cbax)
    cb.set_label("Displacement magnitude |U| (mm)",size=11,labelpad=10)
    cb.ax.tick_params(labelsize=9);cb.outline.set_visible(False)
    fig.text(.055,.30,"DEFORMED SHAPE 100×",size=12,weight="bold")
    fig.text(.055,.274,"Coordinates and displacements in metres; color legend converted to millimetres.",size=10,color="#426079")
    line=fig.add_axes([.07,.12,.84,.115],facecolor="#fff")
    mask=(np.abs(xyz[:,1])<1e-10)&(np.abs(xyz[:,2])<1e-10)
    ordered=np.argsort(xyz[mask,0]); xx=xyz[mask,0][ordered];zz=u[mask,2][ordered]*1000
    line.plot(xx,zz,color="#007f89",linewidth=2.2,marker=".",markersize=3)
    line.axhline(0,color="#bccbd5",linewidth=.8)
    line.set(xlim=(0,20),xlabel="Position along span (m)",ylabel="Deck Uᶻ (mm)")
    line.spines[["top","right"]].set_visible(False);line.tick_params(labelsize=9)
    line.grid(axis="y",color="#e1e8ee",linewidth=.6)
    fig.text(.055,.035,"RESEARCH MODEL · gross elastic concrete, ideal bearing lines; cracking, joints, prestress and fatigue unresolved.",size=9,color="#536b7e")
    fig.text(.055,.016,"Numerical result only · no physical or engineering acceptance · civil 5bab407d / evaluation 79ced43b",size=8,color="#637a8c")
    fig.savefig(path,dpi=200,facecolor=fig.get_facecolor());plt.close(fig)
    record=sealed(dict(schema="osr-civil-gallery-figure/1",request_id=result["request_id"],
        field_sha256=result["full_field_sha256"],figure_sha256=digest(path),dimensions_px=[3000,1900],
        deformation_scale=100,field="FieldCraft nodal displacement magnitude",field_units="m",legend_units="mm",
        surface_scalar_method="Arithmetic mean of actual native nodal magnitudes on each rendered triangle",
        deck_profile="Actual top-centerline nodes; line segments join samples, no invented displacement field",
        limitations=LIMITATIONS,**FLAGS))
    write(path.with_suffix(".json"),record)
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest="action",required=True)
    a=sub.add_parser("prepare");a.add_argument("source");a.add_argument("output")
    a=sub.add_parser("run");a.add_argument("output")
    a=sub.add_parser("finalize");a.add_argument("output")
    a=sub.add_parser("plot");a.add_argument("output");a.add_argument("path")
    a=p.parse_args()
    value=prepare(a.source,a.output) if a.action=="prepare" else run(a.output) if a.action=="run" else finalize(a.output) if a.action=="finalize" else plot(a.output,a.path)
    print(json.dumps(value,sort_keys=True))


if __name__=="__main__":main()
