"""Compound-safe centroid adapter tests with fake shapes, no native executions."""
import ast
from types import SimpleNamespace

import pytest

from engineering.reference_cell import native_cad as n
from engineering.reference_cell.tests.test_geometry import vehicle
from engineering.station_rail.common import digest,encoded,identity


def details_function():
    tree=ast.parse(n.worker_script())
    node=next(v for v in tree.body if isinstance(v,ast.FunctionDef) and v.name=='details')
    context=dict(App=SimpleNamespace(Vector=lambda x,y,z:SimpleNamespace(x=x,y=y,z=z)))
    exec(compile(ast.Module(body=[node],type_ignores=[]),'compound-centroid-fixture','exec'),context)
    return context['details']


def shape(centroid=(1000.,2000.,3000.),volume=2e9,*,compound=True):
    solid=SimpleNamespace(Volume=volume,CenterOfMass=SimpleNamespace(x=centroid[0],y=centroid[1],z=centroid[2]))
    bounds=SimpleNamespace(XMin=0.,YMin=1000.,ZMin=2000.,XMax=2000.,YMax=3000.,ZMax=4000.)
    result=SimpleNamespace(Volume=volume,Solids=[solid],BoundBox=bounds)
    if not compound:result.CenterOfMass=solid.CenterOfMass
    return result


@pytest.mark.parametrize('compound',[True,False])
def test_actual_primitive_centroid_comes_from_solid_without_needing_compound_property(compound):
    fake=shape(compound=compound)
    if compound:assert not hasattr(fake,'CenterOfMass')
    result=details_function()(fake)
    assert result['centroid_m']==[1.,2.,3.]
    assert result['volume_m3']==2.
    assert result['bounds_min_m']==[0.,1.,2.]
    assert result['bounds_max_m']==[2.,3.,4.]


@pytest.mark.parametrize('count',[0,2])
def test_compound_fallback_does_not_hide_disconnected_or_missing_primitive_solids(count):
    fake=shape();fake.Solids*=count
    with pytest.raises(ValueError,match='exactly one solid'):details_function()(fake)


def test_zero_volume_cannot_be_assigned_a_fabricated_centroid():
    with pytest.raises(ValueError,match='Positive'):details_function()(shape(volume=0.))


def test_worker_is_identical_to_frozen_upstream_outside_the_narrow_centroid_function():
    assert digest(n.upstream.__file__)==n.UPSTREAM_SHA256
    assert n.worker_script().replace(n._NEW,n._OLD,1)==n.upstream._NATIVE_SCRIPT
    assert n.worker_script().count(n._NEW)==1
    assert n._source(dict(source_sha256={}))[n.UPSTREAM]==n.UPSTREAM_SHA256


def test_changed_upstream_identity_requires_a_new_audit(monkeypatch):
    monkeypatch.setattr(n,'UPSTREAM_SHA256','0'*64)
    with pytest.raises(ValueError):n.worker_script()
    with pytest.raises(ValueError):n._source(dict(source_sha256={}))


def test_missing_native_tool_remains_unexecuted_without_fake_files(vehicle,tmp_path,monkeypatch):
    monkeypatch.setattr(n.upstream,'_native_command',lambda script:None)
    result=n.export_native(vehicle,tmp_path/'native')
    assert result['execution']=='not-run' and result['physical_accepted'] is False
    assert not list((tmp_path/'native').iterdir())


@pytest.mark.parametrize('budget',[dict(timeout_s=241),dict(memory_bytes=4*1024**3)])
def test_adapter_cannot_exceed_the_revised_authorized_native_budget(vehicle,tmp_path,budget):
    with pytest.raises(ValueError,match='budget'):n.export_native(vehicle,tmp_path/'native',**budget)


def test_resealed_physical_acceptance_cannot_trigger_native_reopening(vehicle,tmp_path):
    folder=tmp_path/'native';folder.mkdir()
    receipt=dict(schema='osr-reference-cell-compound-safe-native/1',candidate_id=vehicle['candidate_id'],
        registry_id=vehicle['registry']['registry_id'],source_sha256=n._source(vehicle),
        execution='completed',native_reopened=True,complete_installed_geometry=False,
        files_sha256={},**n.FLAGS)
    receipt['physical_accepted']=True;receipt['receipt_id']=identity(receipt)
    (folder/'native-receipt.json').write_bytes(encoded(receipt))
    with pytest.raises(ValueError,match='disposition'):n.verify_native(vehicle,folder)


@pytest.mark.parametrize('executable',['/usr/bin/FreeCADCmd','/usr/bin/freecadcmd','/usr/bin/flatpak'])
def test_bytecode_policy_is_set_before_python_and_forwarded_explicitly_into_flatpak(tmp_path,monkeypatch,executable):
    calls=[]
    def run(command,**kwargs):
        calls.append((command,kwargs));return SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
    monkeypatch.setattr(n.subprocess,'run',run)
    command=[executable,'run','--command=FreeCADCmd','org.freecad.FreeCAD','worker.py'] if executable.endswith('flatpak') else [executable,'worker.py']
    original=list(command)
    n._run_native(command,tmp_path,240,3*1024**3)
    actual,options=calls[0]
    assert command==original
    assert options['env']['PYTHONDONTWRITEBYTECODE']=='1'
    assert options['env']['OMP_NUM_THREADS']=='1' and options['env']['OPENBLAS_NUM_THREADS']=='1'
    assert options['timeout']==240 and callable(options['preexec_fn'])
    if executable.endswith('flatpak'):
        assert actual==[executable,'run','--env=PYTHONDONTWRITEBYTECODE=1',*original[2:]]
    else:
        assert actual==original and all('--env=' not in argument for argument in actual)


def test_unexpected_flatpak_subcommand_is_not_silently_rewritten(tmp_path):
    with pytest.raises(ValueError,match='run command'):
        n._run_native(['/usr/bin/flatpak','info','org.freecad.FreeCAD'],tmp_path,240,3*1024**3)


@pytest.mark.parametrize('flatpak',[False,True])
def test_actual_launch_source_and_bytecode_live_outside_the_issued_inventory(tmp_path,monkeypatch,flatpak):
    issued=tmp_path/'issued';issued.mkdir();calls=[]
    def discover(script):
        if flatpak:
            return ['/usr/bin/flatpak','run','--filesystem='+str(script.parent),'--command=FreeCADCmd','org.freecad.FreeCAD',str(script)]
        return ['/usr/bin/FreeCADCmd',str(script)]
    monkeypatch.setattr(n.upstream,'_native_command',discover)
    def run(command,**options):
        launcher=n.Path(command[-1])
        assert launcher.parent!=issued and launcher.parent.parent==issued.parent
        assert launcher.exists() and (issued/'native-worker.py').exists()
        actual=launcher.read_text();calls.append((list(command),actual))
        # Emulate FreeCAD creating a cache beside the file it actually imports.
        (launcher.parent/'__pycache__').mkdir()
        assert not (issued/'__pycache__').exists()
        return SimpleNamespace(returncode=0,stdout=b'',stderr=b'')
    monkeypatch.setattr(n.subprocess,'run',run)
    script=n.worker_script();data={}
    n._launch_export(issued,script,data,240,3*1024**3)
    assert set(p.name for p in issued.iterdir())=={'native-input.json','native-worker.py'}
    assert (issued/'native-worker.py').read_text()==script
    assert data['launch']['launcher_source']==calls[0][1]
    assert data['launch']['mechanism']=='temporary-sibling-launcher'
    assert n._validate_launch(data,script)==data['launch']
    command=calls[0][0]
    if flatpak:
        grants=[arg for arg in command if arg.startswith('--filesystem=')]
        assert len(grants)==2
        assert '--filesystem='+str(issued.resolve()) in grants
        assert '--filesystem=home' not in grants and '--filesystem=host' not in grants
    else:
        assert not any(arg.startswith('--filesystem=') for arg in command)


def test_launcher_provenance_cannot_change_the_recorded_canonical_script(tmp_path):
    script=n.worker_script();issued=str((tmp_path/'original-issuance').resolve())
    actual='FOLDER='+repr(issued)+'\n'+script
    data=dict(launch=dict(mechanism='temporary-sibling-launcher',issued_directory_at_execution=issued,
        canonical_worker_sha256=n.sha256(script.encode()).hexdigest(),launcher_source=actual,
        launcher_source_sha256=n.sha256(actual.encode()).hexdigest(),
        filesystem_policy='launcher-directory and explicit issued-directory; no added broad home grant'))
    assert n._validate_launch(data,script)
    data['launch']['launcher_source']+='\n# unrecorded program change'
    with pytest.raises(ValueError,match='launcher source'):n._validate_launch(data,script)
