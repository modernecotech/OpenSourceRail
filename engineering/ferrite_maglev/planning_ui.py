"""Executed browser evidence for the separate owner/builder planning workspace."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import tempfile
from . import model,platform_publication as planning,delivery_platform as platform
ROOT=model.ROOT
OUTPUT=ROOT/'docs/design-engine/ferrite-maglev/planning-ui'
FILES={'checks.json','planning-desktop.png','planning-mobile.png','browser.txt','README.md'}
SCHEMA='osr-planning-browser-evidence/1'


def source_paths():return sorted({Path(__file__),*planning.source_paths(),planning.OUTPUT/'manifest.json',ROOT/'docs/workbench/maglev/app.css',ROOT/'tools/automation/maglev-workbench.py'})
def sources():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in source_paths()}


def publish(output=OUTPUT):
    planning.verify(recompute=False);before=sources();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        command=['node','tools/automation/tests/verify-planning-workspace.mjs',temp];r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240)
        if r.returncode:raise RuntimeError('Actual planning browser failed: '+r.stderr[-2000:])
        files={n:(Path(temp)/n).read_bytes() for n in ('checks.json','planning-desktop.png','planning-mobile.png')};files['browser.txt']=(r.stdout+r.stderr).encode()
    files['README.md']=b'# Planning workspace browser evidence\n\nExecuted actual local browser:266cities,16GISlayers, stop/service edit/export/import, stale proposal refusal, tampered payload hold, responsive mobile layout, private-path refusal and zero outside requests. Screenshots are actual UI observations; no engineered route or physical acceptance.\n\n[Desktop](planning-desktop.png) / [Mobile](planning-mobile.png) / [Executed checks](checks.json)\n'
    if before!=sources():raise ValueError('planning inputs changed during actual browser execution')
    for n,b in files.items():(output/n).write_bytes(b)
    m=dict(schema=SCHEMA,source_sha256=before,files_sha256={n:sha256(b).hexdigest() for n,b in files.items()},command=['node','tools/automation/tests/verify-planning-workspace.mjs','$TEMP'],exit_code=0,**platform.FLAGS);(output/'manifest.json').write_bytes(platform.encoded(m));return verify(output)


def verify(output=OUTPUT):
    from PIL import Image
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    if m['schema']!=SCHEMA or m['source_sha256']!=sources() or m['exit_code']!=0 or set(m['files_sha256'])!=FILES or set(p.name for p in output.iterdir())!=FILES|{'manifest.json'}:raise ValueError('planning browser inputs/inventory differ')
    if any(m.get(k) is not False for k in platform.FLAGS):raise ValueError('planning browser cannot release physical systems')
    for n,h in m['files_sha256'].items():
        if (output/n).is_symlink() or sha256((output/n).read_bytes()).hexdigest()!=h:raise ValueError('browser evidence bytes changed')
    value=json.loads((output/'checks.json').read_bytes());required={'passed','proposal_export_import','stale_import_refused','headway_hold_visible','payload_tamper_held','mobile','private_paths_rejected'}
    if any(value.get(k) is not True for k in required) or value['cities']!=266 or value['layers']!=16 or value['errors'] or value['external'] or value['physical_release'] is not False:raise ValueError('browser result incomplete')
    renderer=value.get('browser_environment',{})
    if renderer.get('mode') not in {'device-isolated-software','software-requested'} or renderer.get('hardware_graphics_devices_hidden') is not (renderer['mode']=='device-isolated-software') or not all(isinstance(renderer.get(k),str) and 1<=len(renderer[k])<=100 for k in ('browser_version','node_version')):raise ValueError('actual browser rendering context missing')
    for n,size in [('planning-desktop.png',(1400,1000)),('planning-mobile.png',(390,844))]:
        with Image.open(output/n) as im:
            im.load()
            if im.format!='PNG' or im.size!=size:raise ValueError('actual planning screenshot dimensions differ')
    return dict(verified=True,passed=True,cities=266,layers=16,**platform.FLAGS)
