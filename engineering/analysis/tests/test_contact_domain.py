"""Finite-profile coverage, committed-state guards and immutable history replay."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.civil_exploration.wheel_contact import profile_footprint,TangentialContact,ProfilePair
from engineering.civil_exploration.spatial_vehicle import run_spatial,SpatialDomainError
from engineering.civil_exploration.shared_demo import demonstration
from engineering.civil_exploration.spatial_demo import configuration
from engineering.analysis.contact_domain import audit_history


def test_contact_centre_inside_table_does_not_make_the_whole_ellipse_supported():
    location=dict(contact_y_m=.01,wheel_y_m=.055)
    f=profile_footprint(location,dict(semi_axis_y_m=.006),(-.06,.06),(-.06,.06))
    assert f['wheel_margin_m']==pytest.approx(.005) and f['minimum_clearance_m']==pytest.approx(-.001)
    assert not f['inside_supplied_profiles']
    assert profile_footprint(location,dict(semi_axis_y_m=.004),(-.06,.06),(-.06,.06))['inside_supplied_profiles']
    json.dumps(profile_footprint(location,dict(semi_axis_y_m=.004),(np.float64(-.06),np.float64(.06)),(-.06,.06)))


@pytest.mark.parametrize('value',[True,'0.02',float('nan'),float('inf')])
def test_nonphysical_footprint_values_are_rejected(value):
    with pytest.raises(ValueError):profile_footprint(dict(contact_y_m=value,wheel_y_m=0.),dict(semi_axis_y_m=.002),(-.06,.06),(-.06,.06))


def test_outside_domain_is_rejected_before_committing_contact_state_or_history(monkeypatch):
    model=demonstration();cfg=configuration(model);y=np.linspace(-.002,.002,9)
    cfg['contact']['wheel_profiles']={str(side):[[float(x),float(x*x/4)] for x in y] for side in (-1,1)}
    cfg['contact']['rail_profile']=[[float(x),float(-x*x/.6)] for x in y]
    commits=[];samples=[];original=TangentialContact.commit
    def observer(self,result):commits.append(result);return original(self,result)
    monkeypatch.setattr(TangentialContact,'commit',observer)
    with pytest.raises(SpatialDomainError) as caught:
        run_spatial(model,cfg,dt=.002,duration_s=.004,deck_mesh=2,rail_step=2.,sample_callback=samples.append)
    error=caught.value
    assert error.time_s==pytest.approx(.002) and any(v.startswith('contact-footprint:') for v in error.violations)
    assert error.details and all(d['minimum_clearance_m']<0 for d in error.details if d['kind']=='contact-footprint')
    assert not commits and not samples
    json.dumps(error.details)


def test_reference_tangent_fallback_cannot_become_a_committed_contact(monkeypatch):
    model=demonstration();cfg=configuration(model);original=ProfilePair.locate;calls=[];commits=[];samples=[]
    def unsupported(self,shift,roll=0.):
        calls.append((shift,roll))
        if len(calls)>2:raise ValueError('flange contact outside supplied adapter')
        return original(self,shift,roll)
    monkeypatch.setattr(ProfilePair,'locate',unsupported)
    monkeypatch.setattr(TangentialContact,'commit',lambda *a:commits.append(a))
    with pytest.raises(SpatialDomainError) as caught:
        run_spatial(model,cfg,dt=.002,duration_s=.004,deck_mesh=2,rail_step=2.,sample_callback=samples.append)
    assert any(d['kind']=='contact-location' for d in caught.value.details)
    assert any('flange' in v for v in caught.value.violations) and not commits and not samples


def synthetic_history(model,cfg,path):
    rows=[]
    axles={(r['bogie'],r['axle']) for r in model['instances'] if r['axle'] is not None}
    for t in (.002,.004):
        contacts=[dict(train='train-A',wheelset=f'{b}/axle-{a}',side=s,normal_n=40000.,contact_y_m=0.,wheel_y_m=0.,
                       patch=dict(semi_axis_y_m=.004)) for b,a in sorted(axles) for s in (-1,1)]
        if t==.004:contacts[0]['wheel_y_m']=.059
        rows.append(dict(time_s=t,contacts=contacts))
    with gzip.open(path,'wt') as f:
        for row in rows:f.write(json.dumps(row)+'\n')
    return rows


def test_replay_reports_first_footprint_failure_and_never_claims_complete_passage(tmp_path):
    model=demonstration();cfg=configuration(model);path=tmp_path/'history.gz';synthetic_history(model,cfg,path)
    report=audit_history(model,cfg,path)
    assert report['footprint_exceedance_count']==1 and report['first_footprint_exceedance']['time_s']==.004
    assert not report['all_retained_footprints_inside_supplied_profiles'] and not report['complete_passage_verified']
    assert not report['physical_validation'];json.dumps(report)


@pytest.mark.parametrize('invalid',['missing','duplicate','unknown','time','nonfinite'])
def test_replay_rejects_incomplete_or_corrupted_contact_history(tmp_path,invalid):
    model=demonstration();cfg=configuration(model);path=tmp_path/'history.gz';rows=synthetic_history(model,cfg,path)
    if invalid=='missing':rows[0]['contacts'].pop()
    elif invalid=='duplicate':rows[0]['contacts'].append(deepcopy(rows[0]['contacts'][0]))
    elif invalid=='unknown':rows[0]['contacts'][0]['wheelset']='unknown'
    elif invalid=='time':rows[1]['time_s']=rows[0]['time_s']
    else:rows[0]['contacts'][0]['normal_n']=float('nan')
    with gzip.open(path,'wt') as f:
        for row in rows:f.write(json.dumps(row)+'\n')
    with pytest.raises(ValueError):audit_history(model,cfg,path)


def test_service_runner_records_domain_failure_without_promoting_it_to_passage(tmp_path,monkeypatch):
    api=runpy.run_path(str(ROOT/'tools/automation/shared-service-envelope.py'));fn=api['main'];g=fn.__globals__
    common={'common_api':lambda:{'solver_environment':lambda:{'fixture':True}}}
    monkeypatch.setitem(g,'runpy',SimpleNamespace(run_path=lambda _:common))
    monkeypatch.setitem(g,'source_hashes',lambda _:{'fixture':'unchanged'})
    monkeypatch.setitem(g,'case_matrix',lambda *a:dict(cases=[dict(id='empty-15mps',kind='normal-service',configuration={},passage_plan=dict(duration_s=.004))]))
    def outside(*a,**k):raise SpatialDomainError(.002,['contact-footprint:fixture'],[dict(kind='contact-footprint',minimum_clearance_m=-.001)])
    monkeypatch.setitem(g,'run_spatial',outside)
    folder=tmp_path/'campaign';monkeypatch.setattr(sys,'argv',['service','run','--output',str(folder)])
    assert fn()==2
    row=json.loads((folder/'empty-15mps/failure.json').read_text())
    assert row['status']=='outside-model-domain' and row['time_s']==.002 and not row['complete_passage']
    assert row['domain_details'][0]['minimum_clearance_m']<0
    assert (folder/'receipt.json').is_file()
    with gzip.open(folder/'empty-15mps/history.jsonl.gz','rt') as f:assert f.read()==''


def test_original_parts_review_retains_its_producing_commit_and_cannot_qualify_new_solver():
    api=runpy.run_path(str(ROOT/'tools/automation/verify-shared-review-history.py'))
    result=api['verify'](ROOT/'engineering/civil_exploration/examples/automated-parts-review.json','349cf69d3cc0607924ac6671a59b7f851eff9395')
    assert result['published_sources_verified'] and not result['current_implementation_matches']
    assert not result['current_solver_qualified'] and not result['bulk_campaign_outputs_verified']


def test_published_comparison_binds_inputs_and_rejects_before_the_unsupported_sample():
    comparison=json.loads((ROOT/'engineering/civil_exploration/examples/fulltrain-contact-domain-comparison.json').read_text())
    for relative,digest in comparison['input_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
    assert comparison['probe_time_steps_s']==dict(coarse=.005,time_refined=.0025,guarded=.005)
    assert comparison['guarded_case_status']=='outside-model-domain'
    assert comparison['guarded_stop_time_s']==comparison['last_committed_supported_time_s']+.005
    assert comparison['supported_contact_check_count']==48*comparison['supported_sample_count']
    assert comparison['unsupported_contact_states_committed']==0 and comparison['completed_full_family_passages']==0
    c=comparison['archived_probe_first_exceedances']['coarse'];f=comparison['archived_probe_first_exceedances']['time_refined']
    assert c['wheel_margin_m']-c['lateral_semi_axis_m']<0 and f['wheel_margin_m']-f['lateral_semi_axis_m']<0
    assert c['time_s']==f['time_s']==comparison['guarded_stop_time_s']
    assert not comparison['numerical_time_and_mesh_confirmation_performed'] and not comparison['physical_validation']
