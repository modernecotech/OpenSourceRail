"""Coordinator integrity and coupling; synthetic fixtures are not solver evidence."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from engineering.station_rail import vehicle
from engineering.station_rail.common import encoded,identity,digest
from engineering.design_search import adaptive_campaign as a


def test_native_cache_requires_exact_request_payload_and_physical_identity(tmp_path):
    request=dict(candidate_id='a'*64,definition_id='b'*64,case='normal',mesh_m=.3,memory_mb=5120,ccx_sha256='c'*64,source_sha256={'fixture.py':'d'*64})
    result=dict(candidate_id='a'*64,definition_id='b'*64,cases=[dict(case='normal',mesh={'mesh_target_dx_m':.3})],tool=dict(requested_memory_mb=5120,ccx_sha256='c'*64),source_sha256=request['source_sha256'],execution='synthetic-test-fixture',**a.FLAGS);result['evaluation_id']=identity(result)
    (tmp_path/'result.json').write_bytes(encoded(result));(tmp_path/'input.inp').write_text('Synthetic integrity fixture\n')
    m=dict(files_sha256={p.name:digest(p) for p in tmp_path.iterdir()},source_sha256=request['source_sha256'],**a.FLAGS);m['manifest_id']=identity(m)
    (tmp_path/'manifest.json').write_bytes(encoded(m));(tmp_path/'request.json').write_bytes(encoded(request))
    assert a._native_record(tmp_path,request)==result
    with pytest.raises(ValueError,match='request'):a._native_record(tmp_path,{**request,'mesh_m':.2})
    forged={**request,'case':'crowd'};(tmp_path/'request.json').write_bytes(encoded(forged))
    with pytest.raises(ValueError,match='case/mesh'):a._native_record(tmp_path,forged)
    (tmp_path/'request.json').write_bytes(encoded(request))
    (tmp_path/'input.inp').write_text('Modified fixture\n')
    with pytest.raises(ValueError,match='payload'):a._native_record(tmp_path,request)


def test_actual_mass_change_propagates_to_demand_and_civil_reactions():
    car=vehicle.build();changed=deepcopy(car)
    for key in ('accounted_tare_kg_per_car','accounted_cap_loaded_kg_per_car','accounted_160_control_kg_per_car'):changed['mass'][key]-=100.
    x=a.coupled_requirements(car,a.specification());y=a.coupled_requirements(changed,a.specification())
    assert y['rotating_equivalent_kg_per_car']==x['rotating_equivalent_kg_per_car']
    for before,after in zip(x['required_profiles'],y['required_profiles']):
        b,c=before['demand'],after['demand']
        assert c['peak_required_force_N_per_car']<b['peak_required_force_N_per_car']
        assert c['demand_id']==identity({k:v for k,v in c.items() if k!='demand_id'})
        assert c['available_force'] is None and not c['physical_journey_completed']
    assert y['civil_comparisons'][0]['maximum_live_moment_Nm']<x['civil_comparisons'][0]['maximum_live_moment_Nm']
    invalid=a.specification();invalid['comparison']['cars']=4
    with pytest.raises(ValueError,match='formation/layout'):a.coupled_requirements(car,invalid)


def test_mesh_trend_cannot_override_energy_invalidity_or_create_acceptance(monkeypatch):
    # Explicit synthetic values exercise classification only; no native record
    # or publication is fabricated from this test.
    car=dict(candidate_id='a'*64,body_candidate_id='b'*64,mass={'accounted_tare_kg_per_car':20000.})
    definition={'definition_id':'c'*64};spec={};cases=[]
    for label in ('normal','normal-fine','crowd'):
        cases.append(dict(case=label,execution='completed',maximum_vertical_displacement_m=.028,
            maximum_longitudinal_displacement_m=.001,maximum_lateral_displacement_m=.002,
            force_balance_relative_error=0.,force_balance_relative_error_all_axes=0.,moment_balance_relative_error_all_axes=0.,energy_relative_residual=0.))
    records=[dict(candidate_id=car['candidate_id'],body_candidate_id=car['body_candidate_id'],definition_id=definition['definition_id'],cases=[c]) for c in cases]
    for r in records:r['evaluation_id']=identity(r)
    monkeypatch.setattr(a,'coupled_requirements',lambda *args:{'fixture':'no physical evidence'})
    r=a.aggregate(car,definition,records,spec)
    assert r['numerical_validity']=='mesh-trend-confirmed'
    assert r['policy_assessment']['declared_hard_screen']=='unknown' and r['integrated_suitability']=='unknown'
    target=next(f for f in r['policy_assessment']['findings'] if f['criterion_id']=='target.global_deflection')
    assert target['status']=='target_exceeded' and not target['hard_screen_failed']
    records[0]['cases'][0]['energy_relative_residual']=.1
    records[0]['evaluation_id']=identity({k:v for k,v in records[0].items() if k!='evaluation_id'})
    invalid=a.aggregate(car,definition,records,spec)
    assert invalid['normal_vertical_displacement_m'] is None and invalid['numerical_validity']=='unconfirmed'
    records[1]['candidate_id']='e'*64
    with pytest.raises(ValueError,match='mixed physical'):a.aggregate(car,definition,records,spec)


def test_next_invocation_resumes_then_advances_instead_of_repeating_first_two():
    definitions=[dict(definition_id=str(i)) for i in range(5)]
    one_partial={'0':{'normal'}}
    assert [d['definition_id'] for d in a._select_definitions(definitions,one_partial,2,True)]==['0','1']
    finished={'0':{'normal','normal-fine','crowd'},'1':{'normal','normal-fine','crowd'}}
    assert [d['definition_id'] for d in a._select_definitions(definitions,finished,2,True)]==['0','1','2','3']
    assert [d['definition_id'] for d in a._select_definitions(definitions,finished,2,False)]==['0','1']
