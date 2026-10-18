#!/usr/bin/env python3
"""Hourly, read-only engineering snapshots and retained native CAD pictures."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import fcntl
import hashlib
from html import escape
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.continuous_design import research

DEFAULT = Path.home() / ".local/state/opensourcerail/continuous-design"
UNIT = "osr-design-progress"
SCHEMA = "osr-design-progress/1"
SCOPE = ("Provisional research geometry. Native solids, equivalent 1D elastic beams and other explicitly scoped research checks "
         "do not qualify joints, fatigue, soil, dynamics or a complete train. "
         "Manufacturing and physical release remain open.")


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic(path, text):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text)
    temp.replace(path)


def verified(row, workspace, names):
    folder = Path(row["folder"]).resolve()
    if not folder.is_relative_to((workspace / "epochs" / row["baseline"]).resolve()):
        raise ValueError("attempt outside declared epoch")
    if sha(folder / "receipt.json") != row["receipt_sha"]:
        raise ValueError("receipt changed")
    receipt = read(folder / "receipt.json")
    if receipt["key"] != row["key"] or receipt["baseline_sha256"] != row["baseline"]:
        raise ValueError("receipt identity mismatch")
    for name in names:
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or sha(path) != receipt["files_sha256"].get(name):
            raise ValueError("changed presentation input: " + name)
    return folder, receipt


def collect(workspace):
    active = read(workspace / "active.json")
    baseline = active["baseline_sha256"]
    heartbeat = read(workspace / "status.json")
    db = sqlite3.connect((workspace / "queue.sqlite").as_uri() + "?mode=ro", uri=True, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.execute("BEGIN")  # one consistent read snapshot, no writer locks/migrations
        from engineering.continuous_design.service import Store
        from engineering.continuous_design import eligibility
        store=SimpleNamespace(db=db, result=lambda row: Store.result(None,row))
        summary = research.summary(store, baseline)
        resolver=eligibility.Resolver(store,baseline)
        for champion in summary['champions']:
            champion['modeled_mass_kg'] = db.execute('SELECT mass FROM observations WHERE key=?', (champion['key'],)).fetchone()[0]
        lanes = {lane: dict(Counter({r[0]: r[1] for r in db.execute(
            "SELECT status,COUNT(*) FROM jobs WHERE baseline=? AND lane=? GROUP BY status", (baseline, lane))}))
            for lane in ("mechanical", "civil", "software", "integration")}
        provider = dict(db.execute("SELECT status,COUNT(*) FROM provider WHERE baseline=? GROUP BY status", (baseline,)))
        needs = [dict(r) for r in db.execute(
            "SELECT lane,item_id FROM needs WHERE baseline=? AND state='open' ORDER BY lane,item_id LIMIT 12", (baseline,))]
        # Prefer confirmed champions, then the lightest confirmed passing example.
        selected = {}
        for lane in ("mechanical", "civil"):
            rows = db.execute("""SELECT j.*,o.context,o.mass FROM observations o
                JOIN jobs j ON j.key=o.key WHERE o.baseline=? AND o.lane=?
                AND o.study_pass=1 AND o.native_confirmed=1
                ORDER BY (o.key IN (SELECT key FROM champions WHERE id IN
                    (SELECT MAX(id) FROM champions WHERE baseline=? GROUP BY kind,context))) DESC,
                    o.mass,o.key""", (baseline, lane, baseline))
            for row in rows:
                if not resolver.state(row['key'])['eligible']:
                    continue
                confirmation = db.execute("""SELECT j.* FROM promotions p JOIN jobs j ON p.task_key=j.key
                    WHERE p.child=? AND j.baseline=? AND j.status='completed'""", (row["key"], baseline)).fetchone()
                if confirmation:
                    selected[lane] = (dict(row), dict(confirmation))
                    break
        heartbeat_age = max(0, time.time() - heartbeat["heartbeat_unix"])
        state = heartbeat.get("state") if heartbeat.get("baseline_sha256")==baseline else "epoch transition"
        if heartbeat_age > 60:
            state = "stale heartbeat; runner activity unconfirmed"
        return dict(schema=SCHEMA, generated_unix=time.time(), baseline_sha256=baseline,
            heartbeat_age_seconds=heartbeat_age, runner_state=state,
            reporting_source_sha256=sha(__file__),
            renderer_source_sha256=sha(Path(__file__).with_name('design-progress-mesh.py')),
            presentation_tessellation_tolerance_mm=1.0,
            lanes=lanes, research=summary, provider_states=provider, open_needs=needs,
            scope=SCOPE, pictures={}, render_errors={}), selected
    finally:
        db.close()


def render(workspace, child, confirmation, output, lane, baseline):
    child_folder, _ = verified(child, workspace, ("result.json",))
    common='study-confirmation' in json.loads(confirmation['task'])['kind']
    model_name='output/physical-contract.json' if common else 'output/model-definition.json'
    cad_name='output/cad/candidate.FCStd' if common else 'output/cad/model.FCStd'
    folder, receipt = verified(confirmation, workspace, (
        "result.json",model_name,cad_name,"output/cad/native-cad.json"))
    result = read(folder / "result.json")
    if (receipt["task"]["parameters"]["child"] != child["key"] or not result["study_pass"]
        or result["verification"]["levels"]["native_geometry"]["state"] != "passed"):
        raise ValueError("confirmation is not passing native evidence for selected child")
    model = read(folder / model_name)
    native = read(folder / "output/cad/native-cad.json")
    if native["input_sha256"] != sha(folder / model_name):
        raise ValueError("native geometry input mismatch")
    source = folder / cad_name
    with tempfile.TemporaryDirectory(prefix=".cad-", dir=output) as directory:
        temp = Path(directory)
        copied = temp / "model.FCStd"
        shutil.copyfile(source, copied)
        if sha(copied) != receipt["files_sha256"][cad_name]:
            raise ValueError("native copy changed")
        mesh = temp / "mesh.json"
        script = temp / "render.py"
        helper = Path(__file__).with_name("design-progress-mesh.py")
        script.write_text("import runpy\nrunpy.run_path(" + repr(str(helper)) + ")[\"export_mesh\"](" +
                          repr(str(copied)) + "," + repr(str(mesh)) + ")\n")
        binary = shutil.which("FreeCADCmd") or shutil.which("freecadcmd")
        command = [binary] if binary else ["flatpak", "run", "--filesystem=" + str(temp),
            "--filesystem=" + str(helper.parent), "--command=FreeCADCmd", "org.freecad.FreeCAD"]
        with (output / (lane + "-render.log")).open("w") as log:
            subprocess.run([*command, str(script)], stdout=log, stderr=subprocess.STDOUT,
                           timeout=120, check=True)
        data = read(mesh)
    if {p["id"] for p in data["parts"]} != {p["id"] for p in model["parts"]}:
        raise ValueError("rendered part identity mismatch")
    plot(data, output / (lane + ".png"), lane, child, baseline)
    return dict(child_key=child["key"], confirmation_key=confirmation["key"],
        context=child["context"], mass_kg=child["mass"], part_count=len(data["parts"]),
        image=lane + ".png", image_sha256=sha(output / (lane + ".png")),
        source_fcstd=str(source), source_sha256=sha(source),
        receipt_sha256=confirmation["receipt_sha"], model_sha256=sha(folder / model_name),
        numerical_scope=result['verification']['scope'],
        evidence=result["verification"]["evaluated_level"],
        selection="Confirmed passing research example; other contexts may have newer analytical champions",
        analytical_result=str(child_folder / "result.json"), confirmation_result=str(folder / "result.json"))


def rasterize(polygons, depths, colors, width=1600, height=600):
    """Opaque orthographic z-buffer; embedded strands cannot show through concrete."""
    import numpy as np

    polygons=np.asarray(polygons,dtype=float)
    depths=np.asarray(depths,dtype=float)
    low,high=polygons.min(axis=(0,1)),polygons.max(axis=(0,1))
    scale=min((width-1)/max(high[0]-low[0],1e-9),(height-1)/max(high[1]-low[1],1e-9))*.95
    pixels=(polygons-(low+high)/2)*scale
    pixels[:,:,0]+=(width-1)/2
    pixels[:,:,1]=(height-1)/2-pixels[:,:,1]
    image=np.empty((height,width,3));image[:]=[245/255,247/255,250/255]
    buffer=np.full((height,width),-np.inf)
    for triangle,z,color in zip(pixels,depths,colors):
        xmin,ymin=np.maximum(np.floor(triangle.min(axis=0)).astype(int),[0,0])
        xmax,ymax=np.minimum(np.ceil(triangle.max(axis=0)).astype(int),[width-1,height-1])
        if xmin>xmax or ymin>ymax:
            continue
        a,b,c=triangle
        denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator)<1e-10:
            continue
        y,x=np.ogrid[ymin:ymax+1,xmin:xmax+1]
        w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/denominator
        w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/denominator
        w2=1-w0-w1
        depth=w0*z[0]+w1*z[1]+w2*z[2]
        region=buffer[ymin:ymax+1,xmin:xmax+1]
        visible=(w0>=-1e-8)&(w1>=-1e-8)&(w2>=-1e-8)&(depth>region)
        region[visible]=depth[visible]
        image[ymin:ymax+1,xmin:xmax+1][visible]=color
    return image


def plot(mesh, path, lane, child, baseline):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import to_rgb
    import numpy as np

    fig = plt.figure(figsize=(14, 5.5), facecolor="#f5f7fa")
    ax = fig.add_axes([.04, .21, .92, .57])
    ax.set_facecolor("#f5f7fa")
    # Orthographic projection preserves proportions while filling a wide sheet.
    azimuth, elevation = np.deg2rad([24, 32])
    right = np.array([np.cos(azimuth), np.sin(azimuth), 0])
    forward = np.array([-np.sin(azimuth), np.cos(azimuth), 0])
    up = -np.sin(elevation)*forward + np.array([0, 0, np.cos(elevation)])
    camera = np.cos(elevation)*forward + np.array([0, 0, np.sin(elevation)])
    polygons, colors, depths = [], [], []
    for part in mesh["parts"]:
        vertices = np.array(part["vertices"])
        name = part["id"].lower()
        color = "#91a7b7" if lane == "civil" else "#24798c"
        if "strand" in name or "bolt" in name or "pad" in name:
            color = "#dd9740"
        elif "bolster" in name or "footing" in name or "cap" in name:
            color = "#45647b"
        faces = vertices[np.array(part['faces'])]
        normals = np.cross(faces[:,1]-faces[:,0], faces[:,2]-faces[:,0])
        lengths = np.linalg.norm(normals, axis=1)
        normals /= np.maximum(lengths[:,None], 1e-12)
        light = np.array([-.3, -.4, .866])
        shades = .65 + .35 * np.abs(normals @ light)
        polygons.extend(np.stack([faces @ right, faces @ up], axis=2))
        colors.extend(shades[:,None]*np.array(to_rgb(color)))
        depths.extend(faces @ camera)
    ax.imshow(rasterize(polygons,depths,colors), interpolation='lanczos')
    ax.axis('off')
    context=child['context']
    title=('Equipment mounting and duct research assembly' if context.startswith('six-car-equipment') else
        '20m manufactured civil kit'+(' with station package' if context.endswith('-station-package') else '') if context.startswith('kit-20m') else
        'Roof cassette' if context.startswith('roof-cassette') else
        '100m civil reference: five two-track bays' if context.startswith('fixed-100m') else
        "Vehicle underframe" if lane == "mechanical" else "Precast beam and support envelopes")
    fig.suptitle(title + " | retained native CAD", fontsize=18, color="#18384c", y=.94)
    fig.text(.06, .84, child["context"] + f"  |  {len(mesh['parts'])} modeled solids  |  {child['mass']:,.0f} kg modeled mass", fontsize=11)
    fig.text(.06, .12, "Provisional research geometry | joints, full reinforcement and complete systems remain open", fontsize=10)
    fig.text(.06, .07, f"Candidate {child['key'][:16]} | epoch {baseline[:12]} | orthographic, exact proportions | no release credit", fontsize=9)
    fig.savefig(path, dpi=120)
    plt.close(fig)


def html_report(report, base=""):
    h = lambda x: escape(str(x), quote=True)
    counts = report["research"]["counts"]
    stamp = datetime.fromtimestamp(report["generated_unix"], timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>OpenSourceRail progress</title>',
        '<meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="60">',
        ('<base href="'+h(base)+'">') if base else '',
        '<style>body{font:17px system-ui;color:#18384c;background:#f5f7fa;max-width:1100px;margin:2rem auto;padding:1rem}img{width:100%}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:.5rem;border-bottom:1px solid #ccc}code{overflow-wrap:anywhere}article{background:white;padding:1rem;margin:1rem 0}small{color:#45647b}</style>',
        '<h1>OpenSourceRail research progress</h1><p>'+stamp+' | '+h(report['runner_state'])+
        ' | heartbeat age at capture '+str(round(report['heartbeat_age_seconds']))+' seconds</p>',
        '<p>Epoch <code>'+h(report['baseline_sha256'][:16])+'</code>. This document refreshes every minute; new snapshots are generated hourly.</p>',
        '<p>'+h(report['scope'])+'</p>',
        '<p>Evaluated '+str(counts['evaluated'])+'; research rejections '+str(counts['rejected'])+
        '; passing numerical checks '+str(counts['numerically_confirmed'])+
        '; executable checks '+str(counts['executable_verified'])+'. Evidence categories overlap.</p>',
        '<p>'+h(report['delta_description'])+'</p>',
        '<table><tr><th>Lane</th><th>Completed experiments</th><th>Waiting</th><th>Running</th><th>Execution errors</th></tr>']
    for lane, c in report['lanes'].items():
        lines.append('<tr>'+''.join('<td>'+h(v)+'</td>' for v in (lane,c.get('completed',0),
            c.get('queued',0)+c.get('deferred',0),c.get('running',0),c.get('error',0)))+'</tr>')
    lines.extend(['</table><p>AI call states: '+h(report['provider_states'])+'</p>'])
    lines.append('<p>Dependent integration dispositions: '+h(report['research'].get('integration_dispositions',{}))+'</p>')
    latest=report['research']['last_useful_improvement_unix']
    lines.append('<p>Last recorded useful improvement: '+h(datetime.fromtimestamp(latest,timezone.utc).isoformat() if latest else 'none')+'</p>')
    lines.append('<h2>Changes to the research shortlist</h2>')
    for change in report['champion_changes']:
        lines.append('<p>'+h(change['context'])+': '+h(change['description'])+'</p>')
    if not report['champion_changes']:
        lines.append('<p>No shortlist changes since the previous snapshot.</p>')
    for lane, picture in report['pictures'].items():
        lines.extend(['<article><h2>'+h(lane.title())+'</h2><img alt="'+h(lane+' native CAD geometry')+'" src="'+h(picture['image'])+'">',
            '<p>'+h(picture['selection'])+'</p><p>Evidence: '+h(picture['evidence'])+
            '. '+h(picture.get('numerical_scope','Numerical scope is equivalent 1D elastic bending.'))+'</p><p><a href="'+h(Path(picture['source_fcstd']).as_uri())+'">FreeCAD model</a> | <a href="'+
            h(Path(picture['confirmation_result']).as_uri())+'">Confirmation record</a></p></article>'])
    for lane, error in report['render_errors'].items():
        lines.append('<p>Geometry unavailable for '+h(lane)+': '+h(error)+'</p>')
    alternatives=report['research'].get('delivery_shortlist',[])
    if alternatives:
        lines.append('<h2>Alternatives for delivery and manufacture</h2><p>Different objectives retain different candidates. Delivery times and costs depend on declared inputs; acceptance remains open.</p><ul>')
        for candidate in alternatives:
            lines.append('<li>'+h(candidate['context'])+' | '+h(candidate['key'][:12])+' | '+h(', '.join(candidate['roles']))+'</li>')
        lines.append('</ul>')
    lines.append('<h2>Open capability and evidence requests</h2><ul>')
    for need in report['open_needs']:
        lines.append('<li>'+h(need['lane'])+': '+h(need['item_id'])+'</li>')
    lines.append('</ul><small>Reporting reads the queue and retained artifacts; it does not run design experiments or alter acceptance.</small></html>')
    return '\n'.join(lines)


def prune(root, keep=48, maximum_bytes=256*1024*1024):
    # Delete only owned presentation snapshots, never attempts or native evidence.
    owned = []
    for path in (root / "snapshots").iterdir():
        if path.is_symlink() or not path.is_dir() or not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", path.name):
            continue
        marker = path / "snapshot.json"
        if marker.is_file() and read(marker).get("schema") == SCHEMA:
            size = sum(p.stat().st_size for p in path.iterdir() if p.is_file())
            owned.append((path, size))
    owned.sort(key=lambda item: item[0].name)
    total = sum(size for _,size in owned)
    while len(owned)>1 and (len(owned)>keep or total>maximum_bytes):
        path,size=owned.pop(0); shutil.rmtree(path); total-=size


def notify(report, root):
    binary = shutil.which("gdbus")
    if not binary:
        return "unavailable: gdbus is not installed"
    counts = report['research']['counts']
    body = f"{counts['evaluated']} evaluated; {counts['numerically_confirmed']} passing numerical checks.\n"+report['delta_description']
    body += '\n<a href="'+(root/'latest.html').as_uri()+'">Open geometry and progress report</a>'
    picture = next(iter(report['pictures'].values()), None)
    icon = str(root / report['snapshot'] / picture['image']) if picture else "applications-engineering"
    result = subprocess.run([binary,'call','--session','--dest','org.freedesktop.Notifications',
        '--object-path','/org/freedesktop/Notifications','--method','org.freedesktop.Notifications.Notify',
        'OpenSourceRail','0',icon,'OpenSourceRail hourly progress',body,'[]',
        "{'desktop-entry': <'opensourcerail-progress'>}",'15000'],capture_output=True,text=True,timeout=10)
    return 'sent: '+result.stdout.strip() if result.returncode==0 else 'unavailable: '+result.stderr.strip()[:500]


def snapshot(workspace, *, desktop=False):
    workspace = workspace.resolve()
    root = workspace / "progress"
    (root / "snapshots").mkdir(parents=True, exist_ok=True, mode=0o700)
    with (root / ".report.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        report, selected = collect(workspace)
        previous = read(root / "latest.json") if (root / "latest.json").exists() else None
        report['delta_description'] = 'First snapshot for this source epoch; comparison starts here.'
        report['delta'] = None
        report['champion_changes'] = []
        if previous and previous['baseline_sha256']==report['baseline_sha256']:
            delta={k:v-previous['research']['counts'].get(k,0) for k,v in report['research']['counts'].items()}
            report['delta']=delta
            elapsed=round((report['generated_unix']-previous['generated_unix'])/60)
            report['delta_description']=f"Since the previous snapshot ({elapsed} min): {delta['evaluated']:+d} evaluated, {delta['rejected']:+d} research rejections, {delta['numerically_confirmed']:+d} passing numerical checks."
            prior={(c['kind'],c['context']):c for c in previous['research']['champions']}
            for champion in report['research']['champions']:
                old=prior.get((champion['kind'],champion['context']))
                if old is None or old['key']!=champion['key']:
                    mass=champion['modeled_mass_kg']
                    description=f"New research candidate {champion['key'][:12]}, modeled mass {mass:,.1f} kg."
                    if old and old.get('modeled_mass_kg') is not None:
                        description+=f" Previous candidate: {old['modeled_mass_kg']:,.1f} kg in the same context."
                    report['champion_changes'].append(dict(context=champion['context'],description=description))
        name=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+__import__('uuid').uuid4().hex[:8]
        report['snapshot']='snapshots/'+name
        with tempfile.TemporaryDirectory(prefix='.snapshot-',dir=root) as temporary:
            output=Path(temporary)
            for lane in ('mechanical','civil'):
                try:
                    if lane not in selected:
                        raise ValueError('no native-confirmed passing candidate in the active epoch')
                    report['pictures'][lane]=render(workspace,*selected[lane],output,lane,report['baseline_sha256'])
                except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
                    report['render_errors'][lane]=str(exc)[:500]
            (output/'report.html').write_text(html_report(report))
            (output/'snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
            output.rename(root/report['snapshot'])
        atomic(root/'latest.html',html_report(report,report['snapshot']+'/'))
        atomic(root/'latest.json',json.dumps(report,indent=2)+'\n')
        prune(root)
        if desktop:
            try:
                notification=notify(report,root)
            except (OSError,subprocess.SubprocessError) as exc:
                notification='unavailable: '+str(exc)
            atomic(root/'notification.json',json.dumps(dict(at=time.time(),result=notification))+'\n')
        return dict(report=str(root/'latest.html'),snapshot=str(root/report['snapshot']),
                    counts=report['research']['counts'],render_errors=report['render_errors'])


def unit_text(workspace):
    def quote(value):
        return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%')+'"'
    command=' '.join(quote(v) for v in (sys.executable,Path(__file__).resolve(),'snapshot','--workspace',workspace,'--notify'))
    service=('[Unit]\nDescription=OpenSourceRail geometry progress snapshots\n\n[Service]\nType=oneshot\n'
        'ExecStart='+command+'\nNice=15\nCPUQuota=100%\nMemoryMax=1G\nTasksMax=128\n'
        'TimeoutStartSec=5min\nKillMode=control-group\nUMask=0077\n')
    timer=('[Unit]\nDescription=OpenSourceRail hourly geometry progress\n\n[Timer]\n'
        'OnCalendar=hourly\nPersistent=true\nAccuracySec=30s\n\n[Install]\nWantedBy=timers.target\n')
    return {UNIT+'.service':service,UNIT+'.timer':timer}


def install(workspace):
    folder=Path.home()/'.config/systemd/user'
    folder.mkdir(parents=True,exist_ok=True)
    units=unit_text(workspace.resolve())
    for name,content in units.items():
        path=folder/name
        if path.exists() and path.read_text().splitlines()[:2]!=content.splitlines()[:2]:
            raise ValueError('existing unit has another owner: '+str(path))
    for name,content in units.items():
        atomic(folder/name,content)
    subprocess.run(['systemd-analyze','--user','verify',*[str(folder/n) for n in units]],check=True)
    subprocess.run(['systemctl','--user','daemon-reload'],check=True)
    subprocess.run(['systemctl','--user','enable','--now',UNIT+'.timer'],check=True)
    return dict(timer=UNIT+'.timer',cadence='hourly',report=str(workspace.resolve()/'progress/latest.html'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['snapshot','install'])
    parser.add_argument('--workspace',type=Path,default=DEFAULT)
    parser.add_argument('--notify',action='store_true',help='Show a local desktop notification if a session is available')
    args=parser.parse_args()
    print(json.dumps(install(args.workspace) if args.action=='install' else snapshot(args.workspace,desktop=args.notify),indent=2))
