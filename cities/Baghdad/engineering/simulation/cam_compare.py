"""Headless CamCraft MCP coupon replay. Requires the upstream portable Linux CLI."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import time

HERE=Path(__file__).resolve().parent
PRACTICE=HERE.parent/"prototype/cam/training/practice.nc"
TAG="v0.25.0"
COMMIT="7e2a8119c8aec2140135cadbc6afc7922aee955a"


def hashfile(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(path,lo,hi):
    a,b,c=lo
    x,y,z=hi
    verts=((a,b,c),(x,b,c),(x,y,c),(a,y,c),(a,b,z),(x,b,z),(x,y,z),(a,y,z))
    faces=((4,3,2,1),(5,6,7,8),(1,2,6,5),(2,3,7,6),(3,4,8,7),(4,1,5,8))
    path.write_text("".join("v %g %g %g\n"%p for p in verts)+"".join(
        "f %d %d %d\nf %d %d %d\n"%(u,v,w,u,w,t) for u,v,w,t in faces))


def dxf(path,end):
    pairs=[(0,"SECTION"),(2,"ENTITIES")]
    for x1,y1,x2,y2 in ((15,12,43,12),(43,12,43,end)):
        pairs.extend([(0,"LINE"),(8,"CENTRE"),(10,x1),(20,y1),(30,0),(11,x2),(21,y2),(31,0)])
    pairs.extend([(0,"ENDSEC"),(0,"EOF")])
    path.write_text("".join(f"{k}\n{v}\n" for k,v in pairs))


class Server:
    def __init__(self,cli,folder):
        self.cli=Path(cli).resolve()
        self.log=[]
        self.folder=folder
        self.err=(folder/"stderr.log").open("w")
        self.process=subprocess.Popen([str(self.cli),"mcp"],cwd=self.cli.parent,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True,bufsize=1)
        self.i=0

    def rpc(self,method,params):
        self.i+=1
        self.process.stdin.write(json.dumps(dict(jsonrpc="2.0",id=self.i,method=method,params=params))+"\n")
        self.process.stdin.flush()
        line=self.process.stdout.readline()
        if not line:
            raise RuntimeError((self.folder/"stderr.log").read_text())
        reply=json.loads(line)
        if "error" in reply:
            raise ValueError(reply["error"])
        return reply["result"]

    def tool(self,tool_name,**args):
        start=time.monotonic()
        reply=self.rpc("tools/call",dict(name=tool_name,arguments=args))
        payload=[]
        for block in reply.get("content",[]):
            if block["type"]=="image":
                from base64 import b64decode
                raw=b64decode(block["data"])
                payload.append({"png_bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
                (self.folder/f"render-{self.i}.png").write_bytes(raw)
            else:
                try:
                    payload.append(json.loads(block["text"]))
                except (ValueError,KeyError):
                    payload.append(block.get("text",""))
        value=payload[0] if len(payload)==1 else payload
        self.log.append(dict(name=tool_name,args=args,error=reply.get("isError",False),
                             seconds=round(time.monotonic()-start,5),result=value))
        return value

    def close(self):
        self.process.stdin.close()
        self.process.wait(timeout=10)
        self.err.close()
        (self.folder/"transcript.json").write_text(json.dumps(self.log,indent=2)+"\n")


def inspect_nc(path,end):
    """Read posted metric absolute feed endpoints for the two contiguous legs."""
    positions=[]
    pos=dict(X=0.,Y=0.,Z=0.)
    mode=None
    for line in path.read_text().splitlines():
        text=re.sub(r"\([^)]*\)|;.*","",line.upper())
        words=[(k,float(v)) for k,v in re.findall(r"([A-Z])\s*(-?\d*\.?\d+)",text)]
        for k,v in words:
            if k=="G" and v in (0,1,2,3):mode=v
        coords={k:v for k,v in words if k in pos}
        if coords:
            pos.update(coords)
            if mode==1:
                positions.append([pos["X"],pos["Y"],pos["Z"]])
    expected=[[x,y,z] for z in (-.5,-1.) for x,y in ((15,12),(43,12),(43,end))]
    return dict(expected_feed_endpoints=expected,received_feed_endpoints=positions,
                contains_each_expected_endpoint=all(point in positions for point in expected),
                bytes=path.stat().st_size,sha256=hashfile(path))


def evidence(result,server,references):
    cases={}
    for name in ("baseline","target_only","edited","wrong_depth","restored","fault"):
        trial=result[name]
        mesh=trial["render"][0]
        nc=trial["nc_check"]
        cases[name]=dict(verification_ok=trial["verified"]["ok"],post_wrote_file=trial["nc_written"],
                         gate_problems=trial["verified"]["gate"]["problems"],cell_mm=mesh["cell"],
                         judged_cells=mesh["judged_cells"],gouge_mm3=mesh["gouge"]["volume"],
                         max_gouge_mm=mesh["gouge"]["max"],remaining_mm3=mesh["rest"]["volume"],
                         expected_feed_endpoints_present=nc["contains_each_expected_endpoint"] if nc else None,
                         preview_sha256=nc["sha256"] if nc else None)
    if not (all(cases[k]["expected_feed_endpoints_present"] for k in ("baseline","edited","restored"))
            and cases["restored"]["preview_sha256"]==cases["edited"]["preview_sha256"]
            and cases["target_only"]["post_wrote_file"] and 5.5<cases["target_only"]["remaining_mm3"]<6.5
            and not cases["wrong_depth"]["post_wrote_file"] and cases["wrong_depth"]["max_gouge_mm"]>.49
            and not cases["fault"]["post_wrote_file"] and len(result["fixture_findings"]["findings"])==2):
        raise ValueError("Coupon verification outcomes changed; inspect raw transcript")
    return dict(backend="CamCraft",release=TAG,source_commit=COMMIT,license="Apache-2.0",
                binary_sha256=result["cli_sha256"],published_archive_sha256="4dc0269e27a39525346a219db42e6f3a0e213ce3af5b9f15d2736c23ddd14cdf",
                script_sha256=hashfile(Path(__file__)),source_coupon_nc_sha256=result["released_nc_sha256"],
                freecad_design_generator_sha256=hashfile(HERE/"freecad_interactive.py"),
                comparison_step_inputs_sha256={p.name:hashfile(p) for p in sorted(references.glob("wax-coupon-*.step"))},
                protocol=result["server"]["protocolVersion"],server_version=result["server"]["serverInfo"]["version"],
                listed_tools=result["listed_tools"],post="Grbl 1.1",cases=cases,
                direct_open_dxf_trace_generation=result["direct_profile"]["generated"],
                direct_open_dxf_trace_post=result["direct_profile"]["posted"],
                fixture_findings=result["fixture_findings"]["findings"],
                tool_call_count=len(server.log),elapsed_seconds=result["elapsed_seconds"])


def run(cli,folder,references):
    folder=folder.resolve()
    folder.mkdir(parents=True,exist_ok=False)
    server=Server(cli,folder)
    def checked(command,**kwargs):
        result=server.tool(command,**kwargs)
        if server.log[-1]["error"]:
            raise RuntimeError(str(result))
        return result
    def fixture(name,lo,hi):
        path=folder/(name+".obj")
        box(path,lo,hi)
        checked("import_model",name=name,path=str(path))
        checked("add_fixture",model=name)
    def cycle(label):
        generated=server.tool("generate")
        verify=server.tool("verify")
        render=server.tool("render_stock",width=240,height=180,view="top")
        posted=server.tool("post",post="Grbl 1.1",output=str(folder/(label+".nc")))
        return dict(generated=generated,verified=verify,render=render,posted=posted,
                    nc_written=(folder/(label+".nc")).exists(),
                    nc_check=inspect_nc(folder/(label+".nc"),28 if label=="baseline" else 30)
                    if (folder/(label+".nc")).exists() else None)
    started=time.monotonic()
    try:
        implementation=server.rpc("initialize",dict(protocolVersion="2024-11-05",capabilities={},
            clientInfo={"name":"OpenSourceRail coupon study","version":"1"}))
        available=server.rpc("tools/list",{})["tools"]
        checked("add_setup",name="Wax")
        checked("load_machine",builtin="Grbl 3-axis")
        checked("set_setup_post",setup="Wax",post="Grbl 1.1")
        server.tool("get_post_options",setup="Wax")
        blank=folder/"blank.obj"
        box(blank,(0,0,-8),(60,40,0))
        checked("import_model",path=str(blank),name="Blank")
        checked("set_stock",from_model="Blank")
        checked("set_raw_stock_only",on=True)
        checked("import_model",path=str(references/"wax-coupon-baseline.step"),name="Design")
        fixture("South",(0,-6,-8),(60,0,-2))
        fixture("North",(0,40,-8),(60,46,-2))
        checked("add_tool",name="EM3",definition=dict(kind="end_mill",diameter=3.,flute_len=8.,shank_d=3.,
            corner_r=0.,tip_angle=0.,pitch=0.,nose_radius=0.,width=0.,material_group="unknown",shank_len=4.,holder_d=20.,holder_len=30.,rpm=6000.,feed=180.,flutes=2))
        for label,end in (("L28",28),("L30",30)):
            file=folder/(label+".dxf")
            dxf(file,end)
            checked("import_dxf",path=str(file),name=label,units="mm")
        params=dict(clearance_z=5.,top_z=0.,bottom_z=-1.,stepdown=.5,feed=180.,plunge_feed=60.)
        checked("add_operation",kind="Trace",name="WaxSlot",tool="EM3",source="L28",params=params)
        direct_profile=cycle("direct-profile")
        checked("delete_operation",name="WaxSlot")
        for name,a,b in (("LongLeg",[15,12],[43,12]),("ReturnLeg",[43,12],[43,28])):
            checked("add_operation",kind="Slot",name=name,tool="EM3",source="Design",
                    params=dict(**params,a=a,b=b,width=3.,stepover=1.5))
            checked("set_operation_coolant",name=name,coolant="off")
        baseline=cycle("baseline")
        checked("import_model",path=str(references/"wax-coupon-y30.step"),name="Design")
        unedited_target=cycle("target-extension-only")
        checked("edit_operation",name="ReturnLeg",params={"b":[43,30]})
        edited=cycle("edited")
        checked("edit_operation",name="ReturnLeg",params={"bottom_z":-1.5})
        depth=cycle("wrong-depth")
        checked("edit_operation",name="ReturnLeg",params={"bottom_z":-1.0})
        restored=cycle("restored")
        fixture("Obstruction",(35,10,-2),(40,14,3))
        fault=cycle("fault")
        findings=server.tool("get_fixture_findings")
        checked("save_project",path=str(folder/"coupon.camproj"))
        result=dict(tag=TAG,commit=COMMIT,server=implementation,listed_tools=len(available),
                    cli_sha256=hashfile(server.cli),released_nc_sha256=hashfile(PRACTICE),
                    direct_profile=direct_profile,baseline=baseline,target_only=unedited_target,edited=edited,wrong_depth=depth,restored=restored,fault=fault,fixture_findings=findings,
                    elapsed_seconds=round(time.monotonic()-started,4))
        compact=evidence(result,server,references)
        (folder/"evidence.json").write_text(json.dumps(compact,indent=2)+"\n")
        (folder/"result.json").write_text(json.dumps(result,indent=2)+"\n")
    finally:
        server.close()


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cli",type=Path)
    parser.add_argument("folder",type=Path)
    parser.add_argument("references",type=Path)
    a=parser.parse_args()
    run(a.cli,a.folder,a.references.resolve())
