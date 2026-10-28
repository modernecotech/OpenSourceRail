"""Narrow compound-safe native adapter over the frozen geometry implementation.

The previous failed CAD execution and all five IFC receipts remain unchanged.
Only FreeCAD's primitive centroid access is adapted; quantity, placement,
revision, resource and complete STEP multiset checks remain mandatory.
"""
from pathlib import Path
import json
import os
import resource
import subprocess
import tempfile
from hashlib import sha256

from engineering.station_rail import ROOT
from engineering.station_rail.common import identity,digest,encoded
from . import geometry as upstream
from .vehicles import FLAGS

PRODUCER='engineering/reference_cell/native_cad.py'
UPSTREAM='engineering/reference_cell/geometry.py'
UPSTREAM_SHA256='134bf2846ca8cd6bf8dd6207f0f49c8c5dd02b8524467247d3e91c55068f0d48'
FILES={'native-input.json','native-worker.py','stdout.log','stderr.log','native-result.json','vehicle.FCStd','vehicle.step'}
_OLD="""def details(shape):
    b=shape.BoundBox;c=shape.CenterOfMass
"""
_NEW="""def details(shape):
    # Every current canonical box/cylinder/tube/envelope is one solid. An OCC
    # wrapper may be a Compound, which need not expose CenterOfMass itself.
    # Never average disconnected primitive output or hide an extra solid.
    solids=list(shape.Solids)
    if len(solids)!=1:raise ValueError('A canonical primitive must contain exactly one solid')
    volume=sum(s.Volume for s in solids)
    if volume<=0:raise ValueError('Positive primitive volume required')
    centres=[s.CenterOfMass for s in solids]
    c=App.Vector(*[sum(s.Volume*getattr(p,axis) for s,p in zip(solids,centres))/volume for axis in ('x','y','z')])
    b=shape.BoundBox
"""


def _source(vehicle,root=ROOT):
    if digest(Path(root)/UPSTREAM)!=UPSTREAM_SHA256 or digest(upstream.__file__)!=UPSTREAM_SHA256:
        raise ValueError('Frozen upstream geometry differs; re-audit the native adapter')
    if digest(Path(root)/PRODUCER)!=digest(__file__):raise ValueError('Executing native adapter source differs')
    return {**upstream._source(vehicle),PRODUCER:digest(__file__)}


def worker_script():
    if digest(upstream.__file__)!=UPSTREAM_SHA256 or upstream._NATIVE_SCRIPT.count(_OLD)!=1:
        raise ValueError('Exact frozen primitive-centroid operation required')
    return upstream._NATIVE_SCRIPT.replace(_OLD,_NEW,1)


def _run_native(command,folder,timeout_s,memory_bytes):
    """Set the bytecode policy before either direct or sandboxed Python starts."""
    command=list(command)
    if command and Path(command[0]).name=='flatpak':
        if len(command)<2 or command[1]!='run':raise ValueError('Explicit Flatpak run command required')
        command.insert(2,'--env=PYTHONDONTWRITEBYTECODE=1')
    def limit():resource.setrlimit(resource.RLIMIT_AS,(memory_bytes,memory_bytes))
    return subprocess.run(command,cwd=folder,capture_output=True,timeout=timeout_s,preexec_fn=limit,
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1',
             'OPENBLAS_NUM_THREADS':'1','QT_QPA_PLATFORM':'offscreen'})


def _command(script,issued_folder):
    command=upstream._native_command(script)
    if command is not None and Path(command[0]).name=='flatpak':
        command=list(command)
        if len(command)<2 or command[1]!='run':raise ValueError('Explicit Flatpak run command required')
        # Discovery already grants the launcher directory. Grant only the
        # particular issued directory additionally, never broad home access.
        command.insert(2,'--filesystem='+str(Path(issued_folder).resolve()))
    return command


def _launch_export(folder,script,data,timeout_s,memory_bytes):
    # FreeCAD can compile/reimport its launch file despite the Python bytecode
    # environment policy. Keep the actual launcher and its cache outside the
    # issued inventory; its complete source is retained as execution input.
    with tempfile.TemporaryDirectory(prefix='osr-native-launch-',dir=folder.parent) as temporary:
        launcher=Path(temporary)/'native-launch.py';command=_command(launcher,folder)
        if command is None:return None
        prefix='FOLDER='+repr(str(folder.resolve()))+'\n'
        actual=prefix+script
        data['launch']=dict(mechanism='temporary-sibling-launcher',
            issued_directory_at_execution=str(folder.resolve()),
            canonical_worker_sha256=sha256(script.encode()).hexdigest(),
            launcher_source=actual,launcher_source_sha256=sha256(actual.encode()).hexdigest(),
            filesystem_policy='launcher-directory and explicit issued-directory; no added broad home grant')
        (folder/'native-input.json').write_bytes(encoded(data))
        (folder/'native-worker.py').write_text(script)
        launcher.write_text(actual)
        return _run_native(command,folder,timeout_s,memory_bytes)


def _validate_launch(data,script):
    launch=data.get('launch',{})
    issued=launch.get('issued_directory_at_execution')
    if not isinstance(issued,str) or not Path(issued).is_absolute():raise ValueError('Recorded launcher directory provenance required')
    # The historical path is execution provenance only. It is NEVER used to
    # locate files when the retained package is reopened elsewhere.
    actual='FOLDER='+repr(issued)+'\n'+script
    expected=dict(mechanism='temporary-sibling-launcher',issued_directory_at_execution=issued,
        canonical_worker_sha256=sha256(script.encode()).hexdigest(),launcher_source=actual,
        launcher_source_sha256=sha256(actual.encode()).hexdigest(),
        filesystem_policy='launcher-directory and explicit issued-directory; no added broad home grant')
    if launch!=expected:raise ValueError('Recorded actual launcher source/policy differs')
    return launch


def export_native(vehicle,output,*,cars=(1,),timeout_s=240,memory_bytes=3*1024**3,root=ROOT):
    items=upstream._native_items(vehicle,cars);source=_source(vehicle,root);script=worker_script()
    if type(timeout_s) is not int or not 1<=timeout_s<=240 or type(memory_bytes) is not int or not 1024**3<=memory_bytes<=3*1024**3:
        raise ValueError('Native adapter budget is one to240 seconds and one to3GiB')
    folder=Path(output);upstream._ordinary(folder)
    if folder.exists() and any(folder.iterdir()):raise ValueError('Fresh immutable native adapter directory required')
    folder.mkdir(parents=True,exist_ok=True)
    data=dict(candidate_id=vehicle['candidate_id'],registry_id=vehicle['registry']['registry_id'],
        cars=list(cars),items=items,timeout_s=timeout_s,memory_bytes=memory_bytes,source_sha256=source)
    try:
        proc=_launch_export(folder,script,data,timeout_s,memory_bytes)
        if proc is None:return dict(execution='not-run',candidate_id=vehicle['candidate_id'],cars=list(cars),
            reason='No actual headless FreeCAD tool',complete_installed_geometry=False,**FLAGS)
        (folder/'stdout.log').write_bytes(proc.stdout);(folder/'stderr.log').write_bytes(proc.stderr)
    except subprocess.TimeoutExpired as error:
        (folder/'stdout.log').write_bytes(error.stdout or b'');(folder/'stderr.log').write_bytes(error.stderr or b'')
        raise RuntimeError('Native adapter deadline exceeded; exact failure retained') from error
    if proc.returncode or not (folder/'native-result.json').is_file():raise RuntimeError('Native adapter failed; inputs/logs retained')
    result=json.loads((folder/'native-result.json').read_bytes())
    upstream._check_native(items,result,vehicle['candidate_id'],cars,memory_bytes)
    if {p.name for p in folder.iterdir()}!=FILES or any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):
        raise ValueError('Native adapter exact ordinary export inventory differs')
    if _source(vehicle,root)!=source:raise ValueError('Native adapter source changed during execution')
    receipt=dict(schema='osr-reference-cell-compound-safe-native/1',execution='completed',
        candidate_id=vehicle['candidate_id'],registry_id=vehicle['registry']['registry_id'],cars=list(cars),
        source_sha256=source,input_id=identity(data),FreeCAD_version=result['FreeCAD_version'],
        launch_mechanism=data['launch']['mechanism'],launcher_source_sha256=data['launch']['launcher_source_sha256'],
        files_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()},native_reopened=True,
        complete_installed_geometry=False,**FLAGS)
    receipt['receipt_id']=identity(receipt);(folder/'native-receipt.json').write_bytes(encoded(receipt));return receipt


def verify_native(vehicle,output,receipt=None,*,root=ROOT):
    upstream._validate(vehicle);source=_source(vehicle,root);folder=Path(output);upstream._ordinary(folder)
    if any(not p.is_file() or p.is_symlink() for p in folder.iterdir()):raise ValueError('Ordinary native adapter payload required')
    receipt=receipt or json.loads((folder/'native-receipt.json').read_bytes())
    if (receipt.get('schema')!='osr-reference-cell-compound-safe-native/1'
        or receipt.get('receipt_id')!=identity({k:v for k,v in receipt.items() if k!='receipt_id'})
        or receipt.get('candidate_id')!=vehicle['candidate_id'] or receipt.get('registry_id')!=vehicle['registry']['registry_id']
        or receipt.get('source_sha256')!=source or receipt.get('execution')!='completed'
        or receipt.get('native_reopened') is not True or receipt.get('complete_installed_geometry') is not False
        or any(receipt.get(k) is not False for k in FLAGS)
        or receipt.get('files_sha256')!={p.name:digest(p) for p in folder.iterdir() if p.name!='native-receipt.json'}):
        raise ValueError('Native adapter source/payload/identity/disposition differs')
    if {p.name for p in folder.iterdir()}!=FILES|{'native-receipt.json'}:raise ValueError('Native adapter exact ordinary inventory differs')
    data=json.loads((folder/'native-input.json').read_bytes());items=upstream._native_items(vehicle,receipt['cars'])
    if (data['items']!=items or data['source_sha256']!=source or identity(data)!=receipt['input_id']
        or (folder/'native-worker.py').read_text()!=worker_script()):raise ValueError('Native adapter exact input/worker differs')
    launch=_validate_launch(data,worker_script())
    if receipt.get('launch_mechanism')!=launch['mechanism'] or receipt.get('launcher_source_sha256')!=launch['launcher_source_sha256']:
        raise ValueError('Native receipt launcher provenance differs')
    if type(data['timeout_s']) is not int or not 1<=data['timeout_s']<=240 or not 1024**3<=data['memory_bytes']<=3*1024**3:
        raise ValueError('Reopening resource request exceeds the adapter budget')
    with tempfile.TemporaryDirectory(prefix='osr-compound-safe-reopen-',dir=folder.parent) as temporary:
        temporary=Path(temporary);target=temporary/'reopened.json';script=temporary/'reopen.py'
        script.write_text('FOLDER='+repr(str(folder.resolve()))+'\nVERIFY_ONLY=True\nOUTPUT='+repr(str(target))+'\n'+worker_script())
        command=_command(script,folder)
        if command is None:raise ValueError('Actual FreeCAD tool required to reopen native files')
        proc=_run_native(command,temporary,data['timeout_s'],data['memory_bytes'])
        if proc.returncode or not target.is_file():raise ValueError('Independent native adapter reopening failed')
        actual=json.loads(target.read_bytes());upstream._check_native(items,actual,vehicle['candidate_id'],receipt['cars'],data['memory_bytes'])
    if _source(vehicle,root)!=source:raise ValueError('Native adapter source changed during reopening')
    return dict(verified=True,actual_reopened=True,candidate_id=vehicle['candidate_id'],cars=receipt['cars'],
        occurrences=len(items),recorded_FreeCAD_version=receipt['FreeCAD_version'],
        current_verifier_FreeCAD_version=actual['FreeCAD_version'],native_reuse_eligible=False,
        complete_installed_geometry=False,**FLAGS)
