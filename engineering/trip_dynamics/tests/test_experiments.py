from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from engineering.trip_dynamics import experiments as e


@pytest.fixture(scope='module')
def retained_root():
    root=Path(os.environ.get('OSR_SOURCE_ROOT',e.ROOT))
    if not (root/'docs/design-engine/vehicle-optimisation/summary.json').is_file():
        pytest.skip('set OSR_SOURCE_ROOT for sparse checkout retained inputs')
    return root


@pytest.fixture(scope='module')
def catalogue(retained_root):
    return e.catalogue(retained_root)


@pytest.mark.parametrize('job_request',[
    {}, {'action':'experiment','parameters':{},'output':'/tmp/escape'},
    {'action':'shell','parameters':{}}, {'action':[],'parameters':{}},
    {'action':'experiment','parameters':{'max_speed_m_s':100}},
    {'action':'experiment','parameters':{'mode':'exploration'}},
    {'action':'experiment','parameters':{'distance_m':0}},
    {'action':'experiment','parameters':{'temperature_C':40}},
    {'action':'experiment','parameters':{'mechanical_step_s':.01}},
    {'action':'experiment','parameters':{'load_case':'asymmetric'}},
    {'action':'experiment','parameters':{'distance_m':True}},
    {'action':'fixture','parameters':{'fixture':'Code_Aster'}},
    {'action':'verify','parameters':{'path':'/etc/passwd'}},
    {'action':'validate-modal','parameters':{'model_file':'/etc/passwd'}},
    {'action':'validate-map','parameters':{'model_data':{},'vehicle_id':None}},
])
def test_untrusted_parameters_reject_before_output_creation(tmp_path,job_request):
    with pytest.raises((ValueError,TypeError)):
        e.execute(job_request,tmp_path/'never',tmp_path/'not-a-source-repo')
    assert not (tmp_path/'never').exists()


def test_catalogue_preserves_selected_mass_scope_and_material_options(catalogue):
    assert len(catalogue['vehicles'])==5
    rows=catalogue['vehicles']
    assert rows[0]['comparison_aw3_kg_per_car']==pytest.approx(37618.5915003343)
    assert {x['body_family']for x in rows[1:]}=={'retained-frame','6061-T6-envelope',
        '6082-T6-deep-stringers','6005A-T5-wide-stringers'}
    assert catalogue['requested_gfrp_optimisation']['status']=='unknown'
    assert catalogue['fixed_targets']['target_is_candidate_performance'] is False
    for row in rows:
        if row['comparison_aw3_mass_band_kg']:
            assert row['comparison_aw3_kg_per_car']==max(row['comparison_aw3_mass_band_kg'])
        assert row['installed_empty_kg_per_car'] is None
        assert row['cg_m'] is None and row['inertia_kg_m2'] is None
        assert row['physical_accepted'] is False


def test_actual_evidence_selected_variant_uses_own_upper_band_and_no_fallback(tmp_path,retained_root,catalogue,monkeypatch):
    chosen=catalogue['vehicles'][1]
    def no_native(*a,**kw):raise AssertionError('evidence must never run ideal Chrono')
    monkeypatch.setattr(e,'_benchmark',no_native)
    result=e.execute({'action':'experiment','parameters':dict(mode='evidence',vehicle_id=chosen['vehicle_id'],
        distance_m=1500,load_case='empty',temperature_C=50,mechanical_step_s=.0005)},tmp_path/'job',retained_root)
    assert result['execution_status']=='refused'
    assert result['vehicle_id']==chosen['vehicle_id']==result['scenario']['candidate_id']
    assert result['scenario_id']!=result['vehicle_id']
    assert result['comparison_mass_context']['AW3_kg_per_car']==pytest.approx(28066.715270147215)
    assert result['result']['kinematic_target']['total_comparison_mass_kg']==pytest.approx(6*(28066.715270147215-12000))
    assert result['result']['dynamic_execution']=='not-run'
    assert result['result']['distance_travelled_m']==0
    assert all(v['status']=='unevaluated' and v['value'] is None for v in result['result']['requested_outputs'].values())
    assert not (tmp_path/'job/trace.png').exists()
    for item in result['outputs']:
        assert sha256((tmp_path/'job'/item['path']).read_bytes()).hexdigest()==item['sha256']


@pytest.mark.parametrize('identifier',['unknown','', 'f'*64])
def test_unknown_vehicle_does_not_fall_back_to_canonical(tmp_path,retained_root,identifier):
    with pytest.raises(ValueError,match='catalogue'):
        e.execute({'action':'experiment','parameters':{'vehicle_id':identifier}},tmp_path/'job',retained_root)
    assert not (tmp_path/'job').exists()


def test_modal_upload_reports_missing_equipped_properties_without_following_sources(tmp_path,retained_root,catalogue):
    secret=tmp_path/'unread-source';secret.write_text('not part of uploaded model')
    data={'source_sha256':{str(secret):'0'*64}}
    result=e.execute({'action':'validate-modal','parameters':{
        'vehicle_id':catalogue['canonical_vehicle_id'],'model_data':data}},tmp_path/'job',retained_root)
    assert result['execution_status']=='refused'
    assert 'equipped load-case mass/CG/inertia is unknown' in result['result']['reason']
    assert not result['result']['accepted_for_dynamics']
    assert not (tmp_path/'job/unread-source').exists()


def test_synthetic_and_foreign_maps_never_get_candidate_credit(tmp_path,retained_root,catalogue):
    from engineering.trip_dynamics.tests.test_magnetic_maps import fixture,reseal
    value=fixture()
    request={'action':'validate-map','parameters':{'vehicle_id':catalogue['canonical_vehicle_id'],'model_data':value}}
    result=e.execute(request,tmp_path/'foreign',retained_root)
    assert result['execution_status']=='refused' and 'identity mismatch' in result['result']['reason']
    value['identity']['candidate_id']=catalogue['canonical_vehicle_id']
    for row in value['rows']:row['identity']=deepcopy(value['identity'])
    request['parameters']['model_data']=reseal(value)
    result=e.execute(request,tmp_path/'synthetic',retained_root)
    assert result['execution_status']=='refused' and 'synthetic/manufactured' in result['result']['reason']
    assert not result['result']['accepted_for_dynamics']


def test_unavailable_native_benchmark_fails_without_substitute(tmp_path,retained_root,monkeypatch):
    monkeypatch.setattr(e,'_probe_chrono',lambda root:dict(available=False,reason='test missing native environment',fallback=False))
    result=e.execute({'action':'experiment','parameters':{'mode':'benchmark'}},tmp_path/'job',retained_root)
    assert result['execution_status']=='failed'
    assert 'missing native' in result['result']['reason']
    assert not result['physical_accepted'] and not (tmp_path/'job/trace.png').exists()


def test_laminate_fixture_executes_analytical_not_code_aster(tmp_path,retained_root):
    result=e.execute({'action':'fixture','parameters':{'fixture':'laminate'}},tmp_path/'job',retained_root)
    assert result['execution_status']=='completed'
    assert result['result']['executed'] and not result['result']['code_aster_executed']
    assert not result['result']['engineering_accepted']


def test_existing_job_and_symlink_output_refused(tmp_path,retained_root):
    (tmp_path/'used').mkdir();(tmp_path/'used/kept').write_text('retained')
    (tmp_path/'alias').symlink_to(tmp_path/'used',target_is_directory=True)
    for path in [tmp_path/'used',tmp_path/'alias']:
        with pytest.raises(ValueError,match='fresh|ordinary'):
            e.execute({'action':'probe','parameters':{}},path,retained_root)
    assert (tmp_path/'used/kept').read_text()=='retained'


def test_setup_scope_keeps_installer_under_job_and_reports_existing_chrono(tmp_path,retained_root,monkeypatch):
    from engineering.trip_dynamics import setup_tools
    destinations=[]
    def install(path):
        destinations.append(path)
        return dict(global_environment_modified=False)
    monkeypatch.setattr(setup_tools,'install',install)
    monkeypatch.setattr(e,'_probe_chrono',lambda root:dict(available=True,fallback=False,solver_id='a'*64))
    result=e.execute({'action':'setup-tools','parameters':{}},tmp_path/'job',retained_root)
    assert destinations==[tmp_path/'job/tools']
    assert result['result']['global_environment_modified'] is False
    assert result['result']['chrono_environment_installed'] is False
    assert result['result']['existing_private_chrono']['available'] is True
