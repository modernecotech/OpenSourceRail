from copy import deepcopy
import hashlib
import sys
from pathlib import Path
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.integration_programme import joints,flexible,battery,stations,lifecycle,condition


def test_six_resultants_recover_and_virtual_work_matches():
    group=joints.bolt_group([[-.4,-.2,0],[-.4,.2,0],[.4,-.2,0],[.4,.2,0]],.012,.03,210e9)
    load=np.array([500.,-200.,1000.,30.,70.,60.]);result=joints.assess(group,load)
    K=np.array(group['stiffness_si']);u=np.array(result['relative_pose_si'])
    assert result['resultant_relative_error']<1e-12
    energy=sum(float((np.array(B)@u)@np.array(group['local_stiffness_n_m'])@(np.array(B)@u)) for B in group['maps'])
    assert energy==pytest.approx(float(u@load))
    assert not result['capacity_qualified'] and result['within_declared_strength'] is None
    assert np.linalg.eigvalsh(K).min()>0
    with pytest.raises(ValueError):joints.bolt_group([[0,0,0]]*3,.012,.03,210e9)


def test_free_free_modes_match_independent_analytical_root_and_transfer_work():
    coarse=flexible.beam_modes(18.5,400.,3e8,elements=8);fine=flexible.beam_modes(18.5,400.,3e8,elements=32)
    expected=4.730040744862704**2/(2*np.pi*18.5**2)*np.sqrt(3e8/400.)
    assert abs(fine['frequencies_hz'][0]-expected)<abs(coarse['frequencies_hz'][0]-expected)
    assert fine['frequencies_hz'][0]==pytest.approx(expected,rel=2e-5)
    assert np.array(fine['modal_mass'])==pytest.approx(np.eye(6),abs=1e-9)
    joint=flexible.modal_joint(fine,4.,2e6);B=np.array(joint['displacement_map']);q=np.arange(len(B))*.001;force=123.
    assert float(q@(B*force))==pytest.approx(float(B@q)*force)
    assert np.linalg.eigvalsh(joint['stiffness_si']).min()>-1e-8
    with pytest.raises(ValueError):flexible.attachment_shape(fine,20.)


def test_shell_has_actual_material_area_portals_and_thickness_mass(tmp_path):
    r=flexible.carbody_shell(tmp_path/'shell')
    L=18.5;W=2.65;H=3.25-.8
    area=2*L*W+2*L*H+2*W*H-4*1.27*(3.-.8)
    assert r['material_area_m2']==pytest.approx(area,rel=1e-8)
    assert r['mass_kg']==pytest.approx(area*.003*7850.)
    assert r['portal_count']==4 and not r['production_released']


def pack():
    return dict(soc_min=.1,soc_max=.9,capacity_ah=100.,discharge_current_limit_a=300.,charge_current_limit_a=200.,thermal_capacity_j_k=20000.,cooling_conductance_w_k=10.)
def maps():
    return dict(soc=[.1,.5,.9],temperature_c=[-10.,25.,60.],ocv_v=[[95,100,105],[100,105,110],[102,107,112]],resistance_ohm=[[.2]*3,[.1]*3,[.08]*3],basis='synthetic',capacity_reference_soh=1.)


def test_battery_charge_discharge_energy_and_temperature_maps():
    p=battery.Battery(pack(),maps());start=p.soc
    discharge=p.step(5000,10);assert discharge['current_a']>0 and p.soc<start
    assert abs(discharge['electrical_residual_j'])<1e-6 and abs(discharge['thermal_residual_j'])<1e-8
    charge=p.step(-3000,10);assert charge['current_a']<0 and charge['chemical_energy_j']<0
    assert abs(charge['electrical_residual_j'])<1e-6
    old=p.soc
    with pytest.raises(ValueError):p.step(1e7,10)
    assert p.soc==old
    assert not charge['physical_validation'] and not charge['calibrated']
    with pytest.raises(ValueError):battery.Battery(pack(),maps(),temperature_c=90)


def test_aged_capacity_is_not_applied_twice_and_duplicate_power_rejected():
    p=pack();p['capacity_ah']=90.;m=maps();m['capacity_reference_soh']=.9
    b=battery.Battery(p,m,soh=.9);r=b.step(1000,1)
    assert .8-b.soc==pytest.approx(r['current_a']/(3600*90.))
    assert battery.power_ledger([dict(id='motor',power_w=100),dict(id='hvac',power_w=20)])['total_terminal_power_w']==120
    with pytest.raises(ValueError):battery.power_ledger([dict(id='hvac',power_w=20)]*2)


def station():
    nodes=[dict(id='platform'),dict(id='concourse'),dict(id='safe',exit=True)]
    edges=[dict(id='stairs',**{'from':'platform','to':'concourse'},mobility=['walking'],capacity_people_s=2.,travel_s=2.),dict(id='lift',**{'from':'platform','to':'concourse'},mobility=['walking','wheelchair'],capacity_people_s=.5,travel_s=4.),dict(id='exit',**{'from':'concourse','to':'safe'},mobility=['walking','wheelchair'],capacity_people_s=3.,travel_s=2.)]
    cohorts=[dict(id='walking',node='platform',people=20.,mobility='walking'),dict(id='wheelchair',node='platform',people=2.,mobility='wheelchair')]
    return nodes,edges,cohorts


def test_interacting_station_conserves_people_and_reports_inaccessible_power_failure():
    n,e,c=station();healthy=stations.simulate(n,e,c,duration_s=60)
    outage=stations.simulate(n,e,c,duration_s=60,outages=[dict(edge='lift',start_s=0,end_s=100)])
    assert healthy['numerical_clearance_completed'] and sum(healthy['completed_by_cohort'].values())==pytest.approx(22)
    assert all(abs(r['conservation_residual_people'])<1e-9 for r in healthy['history'])
    assert not outage['numerical_clearance_completed'] and outage['max_unroutable_people']==2
    assert outage['within_declared_clearance_limit'] is None and not outage['fire_tenability_accepted']


def test_installed_lifetime_missing_categories_cannot_rank_and_discount_is_independent():
    entries=[dict(id=c,category=c,quantity=2.,unit_price_usd=100.,year=10.,quote_sha256=None) for c in lifecycle.REQUIRED]
    r=lifecycle.installed_cost(entries,years=30,discount_rate=.05)
    assert r['complete_installed_lifecycle_present_usd']==pytest.approx(len(entries)*200/1.05**10)
    assert r['eligible_for_cost_ranking'] and not r['supplier_quotes_complete']
    entries[0]['unit_price_usd']=None;r=lifecycle.installed_cost(entries,years=30,discount_rate=.05)
    assert not r['eligible_for_cost_ranking'] and r['complete_installed_lifecycle_present_usd'] is None
    with pytest.raises(ValueError):lifecycle.installed_cost(entries+entries,years=30,discount_rate=.05)


def test_condition_measurement_identity_calibration_and_independent_revision(tmp_path):
    def evidence(name,kind):
        p=tmp_path/name;p.write_text('Test-only retained record; not a physical measurement')
        return dict(path=name,kind=kind,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),revision='test-fixture',approved_by='test-fixture')
    installed=dict(serial='S1',manufactured_revision='R1',configuration_sha256='a'*64)
    obs=dict(serial='S1',manufactured_revision='R1',configuration_sha256='a'*64,quantity='wheel-radius',unit='m',value=.37,uncertainty=.001,instrument_serial='T1',measured_at='2026-10-11T12:00:00Z',evidence=evidence('measurement','measurement'))
    cal=dict(instrument_serial='T1',quantity='wheel-radius',unit='m',uncertainty=.0005,minimum=.1,maximum=.5,valid_from='2026-01-01T00:00:00Z',valid_until='2026-12-31T00:00:00Z',evidence=evidence('calibration','calibration'))
    out=condition.bind(installed,obs,cal,root=tmp_path)
    assert installed==dict(serial='S1',manufactured_revision='R1',configuration_sha256='a'*64)
    assert out['manufactured_revision']=='R1' and out['condition_revision_sha256'] and out['analysis_reexecution_required']
    wrong=deepcopy(obs);wrong['serial']='S2'
    with pytest.raises(ValueError):condition.bind(installed,wrong,cal,root=tmp_path)
    wrong=deepcopy(cal);wrong['valid_until']='2026-10-01T00:00:00Z'
    with pytest.raises(ValueError):condition.bind(installed,obs,wrong,root=tmp_path)


def test_flexible_attachment_stiffness_mass_and_static_reactions_reach_spatial_vehicle():
    from engineering.integration_programme.flexible_vehicle import FlexibleVehicle
    from engineering.civil_exploration.shared_demo import demonstration
    from engineering.civil_exploration.spatial_demo import configuration
    from engineering.civil_exploration.spatial_structure import Route
    from engineering.civil_exploration.spatial_vehicle import SpatialVehicle
    m=demonstration();cfg=configuration(m);rigid=SpatialVehicle(m,cfg['joint_laws']);flex=FlexibleVehicle(m,cfg['joint_laws'])
    route=Route(cfg['route']);K,C,M,(_,plans)=flex.matrices(route,0.,0.)
    assert flex.total_mass==pytest.approx(rigid.total_mass)
    assert sum(c['static_n'] for c in flex.contacts)==pytest.approx(flex.total_mass*9.81,rel=1e-12)
    assert all(c['static_n']>0 for c in flex.contacts)
    assert np.min(np.linalg.eigvalsh(M))>0 and K==pytest.approx(K.T,rel=1e-12,abs=1e-10)
    assert any(np.any(p['J'][:,flex.rigid_size:]) for p in plans)
    q=flex.static_coordinates;assert np.linalg.norm(q[flex.rigid_size:])>0
    # Work of every joint remains conjugate after adding modal coordinates.
    rng=np.random.default_rng(10);dq=rng.normal(size=flex.size)*1e-5
    for p in plans:
        F=p['joint']['K']@(p['J']@dq)
        assert float(dq@(p['J'].T@F))==pytest.approx(float((p['J']@dq)@F))
    assert flex.modal_observation('car-1',3.,q,q*0,q*0)['flexible_displacement_m']!=0


def test_osrd_example_units_effort_domains_and_tail_release_are_explicit():
    from engineering.integration_programme.osrd_examples import retained_example,resistance,effort,tail_speed_limit,acceleration_experiment
    stock,meta=retained_example();assert meta['data_license']=='LGPL-3.0-only' and not meta['physical_validation']
    assert resistance(stock,15.)==pytest.approx(390000*(.0077+.0003312*15+2.2032e-5*15**2))
    assert effort(stock,25.,mode='1500V',comfort='STANDARD')==140000
    with pytest.raises(ValueError):effort(stock,40.)
    with pytest.raises(ValueError):effort(stock,15.,mode='unsupported')
    with pytest.raises(ValueError):effort(stock,15.,electrical_profile='unreviewed')
    sections=[dict(begin_m=0.,end_m=100.,speed_m_s=10.)]
    assert tail_speed_limit(209.9,110.,sections,rolling_stock_limit_m_s=30.)==10.
    assert tail_speed_limit(210.,110.,sections,rolling_stock_limit_m_s=30.)==30.
    a=acceleration_experiment(stock,duration_s=5.,dt_s=.1);b=acceleration_experiment(stock,duration_s=5.,dt_s=.05)
    assert a['history'][-1]['position_m']==pytest.approx(b['history'][-1]['position_m'],rel=1e-5)
    assert a['history'][-1]['speed_m_s']<stock['max_speed'] and not a['full_spatial_force_feedback']


def test_civil_correspondence_identifies_unrepresented_load_path_and_rejects_unknown_roles():
    from types import SimpleNamespace
    from engineering.integration_programme.correspondence import audit
    structure=SimpleNamespace(elements=[dict(kind='pier',nodes=[0,1],station_start=None,station_end=None,track=None,length=5.,properties={'mass_kg_m':100.})],
        coordinates=[np.array([0.,0.,0.]),np.array([0.,0.,5.])],springs=[dict(kind='foundation')],length=24.,tracks=[-2.,2.],gauge=1.435)
    item=dict(id='infra/deck',part_id='deck',role='support-deck-envelope',geometry={'visual':'rectangular reservation'},transform={'translation_m':[0.,0.,0.]},properties={'mass_kg':1000.})
    infra=dict(items=[item],gauge_m=1.435,support_study={'series_stiffness_n_m':1e6})
    r=audit({'configuration':'example'},infra,structure,{'route':'example'})
    assert r['analysis_domains_without_displayed_equivalent']==['foundation','pier']
    assert r['analysis_elements'][0]['mass_kg']==500.
    assert not r['complete_cad_analysis_equivalence'] and not r['rows'][0]['mass_equivalent']
    infra['items']=[dict(item,role='unregistered')]
    with pytest.raises(ValueError,match='unregistered'):audit({},infra,structure,{})
