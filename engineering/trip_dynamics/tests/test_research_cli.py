"""Bounded adapter/transport tests; numerical solvers are not run here."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import types

import pytest

from engineering.trip_dynamics import __main__ as cli
from engineering.trip_dynamics import experiments as e


@pytest.fixture
def adapters(monkeypatch):
    candidates=[dict(candidate_id=str(i)*64,name='mock-epm-'+str(i),
        schema='osr-epm-candidate/1',physical_accepted=False)for i in (1,2,3)]
    epm=types.ModuleType('engineering.electropermanent');epm.__path__=[]
    cat=types.ModuleType('engineering.electropermanent.catalogue')
    publication=types.ModuleType('engineering.electropermanent.publication')
    magnetic=types.ModuleType('engineering.magnetic_confirmation')
    cat.candidates=lambda root:deepcopy(candidates)
    for name,module in [('engineering.electropermanent',epm),
        ('engineering.electropermanent.catalogue',cat),
        ('engineering.electropermanent.publication',publication),
        ('engineering.magnetic_confirmation',magnetic)]:monkeypatch.setitem(sys.modules,name,module)
    return dict(catalogue=cat,publication=publication,magnetic=magnetic,candidates=candidates)


@pytest.fixture
def worker(monkeypatch,tmp_path,adapters):
    from engineering.trip_dynamics import magnetic_maps,campaign
    monkeypatch.setattr(e,'_definitions',lambda root:{})
    monkeypatch.setattr(magnetic_maps,'current_magnetic_evidence',lambda root:{})
    monkeypatch.setattr(campaign,'source_snapshot',lambda *args:{'mock-adapter-contract':'a'*64})
    return tmp_path/'repo',adapters


@pytest.mark.parametrize('action',['epm-screen','magnetic-confirmation'])
@pytest.mark.parametrize('parameters',[{'getdp':'/bin/sh'},{'source_root':'/etc'},{'cases':['coarse']},
                                     {'vehicle_id':'a'*64},{'timeout_s':9000}])
def test_research_request_accepts_no_client_controls_or_paths(tmp_path,action,parameters):
    with pytest.raises(ValueError,match='unsupported parameters'):
        e.execute(dict(action=action,parameters=parameters),tmp_path/'unused',tmp_path/'no-repo')
    assert not (tmp_path/'unused').exists()


def test_epm_delegates_to_its_own_publication_without_motion_wrapper(tmp_path,worker):
    root,modules=worker;seen=[]
    raw=dict(schema='osr-electropermanent-publication/1',study_id='e'*64,
             counts={'candidates':3},next_experiment={'physical_accepted':False},physical_accepted=False)
    def run(output,*,root):
        seen.append((output,root));output.mkdir(parents=True)
        e._write(output/'manifest.json',raw)
        return deepcopy(raw)
    modules['publication'].run=run
    answer=e.execute(dict(action='epm-screen',parameters={}),tmp_path/'job',root)
    assert seen==[(tmp_path/'job/electropermanent',root)]
    assert answer['result']==raw and answer['execution_status']=='completed'
    assert answer['vehicle_id'] is None and answer['scenario'] is None
    assert not answer['motion_executed'] and not answer['journey_accepted'] and not answer['physical_accepted']
    assert json.loads((tmp_path/'job/result.json').read_text())==raw
    assert 'electropermanent/manifest.json' in {x['path']for x in answer['outputs']}


@pytest.mark.parametrize('reuse_exists',[False,True])
@pytest.mark.parametrize('case_state,expected',[('completed','completed'),('nonconverged','completed'),
                                              ('failed','failed'),('interrupted','failed'),('unknown','failed')])
def test_confirmation_uses_fixed_tools_three_cases_and_keeps_all_dispositions(tmp_path,worker,reuse_exists,case_state,expected):
    root,modules=worker;seen=[]
    reuse=root/'build/trip-dynamics/finite-coupon3d-v2'
    if reuse_exists:reuse.mkdir(parents=True)
    raw=dict(schema='osr-magnetic-confirmation/1',execution_status='completed',
        rows=[dict(case=name,execution_status=case_state if name=='fine' else 'completed',
                   full_source_converged=case_state=='completed',force_credit=False,
                   demag_proxy_margin_A_per_m=-100.)for name in ('coarse','fine','expanded')],
        comparison={'force_screen':'fail','material_model':'unqualified'},force_map_generated=False,physical_accepted=False)
    def run(output,**kwargs):
        seen.append((output,kwargs));output.mkdir(parents=True)
        e._write(output/'receipt.json',raw)
        return deepcopy(raw)
    modules['magnetic'].run=run
    answer=e.execute(dict(action='magnetic-confirmation',parameters={}),tmp_path/'job',root)
    assert seen==[(tmp_path/'job/magnetic-confirmation',dict(root=root,
        getdp=root/'build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp',
        reuse_mesh_root=reuse if reuse_exists else None,cases=('coarse','fine','expanded')))]
    assert answer['execution_status']==expected and answer['result']==raw
    assert json.loads((tmp_path/'job/result.json').read_text())==raw
    assert not answer['motion_executed'] and not answer['journey_accepted']
    assert 'magnetic-confirmation/receipt.json' in {x['path']for x in answer['outputs']}


@pytest.mark.parametrize('error',[RuntimeError('mock solver runtime failure'),ValueError('mock generated case failed')])
def test_research_runtime_failures_remain_failed_with_prior_artifacts(tmp_path,worker,error):
    root,modules=worker
    def run(output,**kwargs):
        output.mkdir(parents=True);(output/'retained-log.txt').write_text(str(error));raise error
    modules['magnetic'].run=run
    answer=e.execute(dict(action='magnetic-confirmation',parameters={}),tmp_path/'job',root)
    assert answer['execution_status']=='failed' and str(error) in answer['result']['reason']
    assert 'magnetic-confirmation/retained-log.txt' in {x['path']for x in answer['outputs']}


def test_incomplete_case_collection_cannot_claim_completed_confirmation(tmp_path,worker):
    root,modules=worker
    raw=dict(schema='osr-magnetic-confirmation/1',execution_status='completed',
        rows=[dict(case='coarse',execution_status='completed',force_credit=False)],physical_accepted=False)
    modules['magnetic'].run=lambda *args,**kwargs:deepcopy(raw)
    answer=e.execute(dict(action='magnetic-confirmation',parameters={}),tmp_path/'job',root)
    assert answer['execution_status']=='failed' and answer['result']==raw


@pytest.mark.parametrize('command,action',[('epm','epm-screen'),('magnetic-confirmation','magnetic-confirmation')])
def test_research_cli_constructs_only_empty_parameter_action(tmp_path,monkeypatch,capsys,command,action):
    seen=[]
    monkeypatch.setattr(e,'execute',lambda request,output,root:seen.append((request,output,root))or{'ok':True})
    assert cli.main([command,'--output',str(tmp_path/'fresh'),'--source-root',str(tmp_path/'source')])==0
    assert seen==[(dict(action=action,parameters={}),tmp_path/'fresh',tmp_path/'source')]
    assert json.loads(capsys.readouterr().out)=={'ok':True}
    with pytest.raises(SystemExit) as error:cli.main([command,'--output',str(tmp_path/'fresh'),'--getdp','/bin/sh'])
    assert error.value.code==2


def _catalogue_sources(monkeypatch):
    """Five independent existing vehicle choices, separate from EPM bundles."""
    from engineering.trip_dynamics import magnetic_maps,vehicle
    rows=[]
    for i in range(5):
        rows.append(dict(candidate_id=str(i+4)*64,label='existing-'+str(i),body_family='retained',magnetic_family='retained',
            geometry_id='a'*64,material_id='b'*64,comparison_aw3_kg_per_car=30000.,
            comparison_empty_kg_per_car=18000.,payload_aw3_kg_per_car=12000.,modules_per_car=24,
            cars=6,car_length_m=17.,unknown_installed_inventory=['unknown']))
    publication='docs/design-engine/vehicle-optimisation/'
    definitions=dict(canonical=rows[0],alternatives=rows[1:],source_bindings={publication+'manifest.json':'c'*64},
                     requested_gfrp_optimisation={'status':'unknown'})
    monkeypatch.setattr(e,'_definitions',lambda root:deepcopy(definitions))
    monkeypatch.setattr(magnetic_maps,'current_magnetic_evidence',lambda root:dict(records=[],source_sha256={}))
    def checked(root,path,digest):
        if path.endswith('manifest.json'):return json.dumps({'files_sha256':{'equipment.json':'d'*64,'HVAC.json':'e'*64}}).encode()
        return b'{}'
    monkeypatch.setattr(vehicle,'_checked',checked)
    return rows


def test_epm_catalogue_is_raw_three_bundles_with_separate_five_vehicle_choices(tmp_path,monkeypatch,adapters):
    rows=_catalogue_sources(monkeypatch)
    answer=e.catalogue(tmp_path)
    assert [x['vehicle_id']for x in answer['vehicles']]==[x['candidate_id']for x in rows]
    assert answer['electropermanent']==adapters['candidates']
    assert answer['research_publications']=={
        'electropermanent':'/api/trip/publications/electropermanent/README.md',
        'magnetic-confirmation':'/api/trip/publications/magnetic-confirmation/README.md'}


@pytest.mark.parametrize('corruption',['duplicate','missing','accepted'])
def test_malformed_epm_candidate_identity_or_maturity_is_refused(tmp_path,monkeypatch,adapters,corruption):
    _catalogue_sources(monkeypatch);raw=deepcopy(adapters['candidates'])
    if corruption=='duplicate':raw[1]['candidate_id']=raw[0]['candidate_id']
    if corruption=='missing':raw.pop()
    if corruption=='accepted':raw[0]['physical_accepted']=True
    adapters['catalogue'].candidates=lambda root:raw
    with pytest.raises(ValueError,match='candidate|acceptance'):e.catalogue(tmp_path)
