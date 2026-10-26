from copy import deepcopy
import gzip,json
from pathlib import Path
import pytest
from engineering.design_search import railway_architecture as a
from engineering.station_rail import vehicle


@pytest.fixture(scope='module')
def inputs():
    spec=a.load_spec();reference=vehicle.build();return spec,reference,a.generate(spec,reference)


def test_broad_cases_keep_physical_and_requirement_identities_separate(inputs):
    spec,ref,cases=inputs
    assert len(cases)==486 and {c['family_id'] for c in cases}==set(spec['families'])
    assert len({c['candidate_id'] for c in cases})<len(cases)
    controls=[c for c in cases if c['family_id'] in ('P1','P2') and c['physical_definition']['formation']['cars']==6 and c['physical_definition']['route']['station_spacing_m']==2000 and c['knobs']['launch_m']==500]
    assert len({c['candidate_id'] for c in controls})==1
    assert len({c['requirement_revision'] for c in controls})==3
    assert all(c['complete_mass_kg'] is None and not c['configuration_adopted'] for c in cases)
    assert ref['physical_definition']['vehicle']['cars']==6


def test_powered_track_counts_train_length_and_periodic_overlap():
    rows=a.periodic_installed_windows([[0.,500.],[1650.,2000.]],2000.,104.5,9.)
    assert sum(b-c for c,b in rows)==pytest.approx(946.5)
    shorter=a.periodic_installed_windows([[0.,500.],[1650.,2000.]],2000.,69.5,9.)
    assert sum(b-c for c,b in shorter)==pytest.approx(911.5)
    assert a.union([[0.,10.],[5.,15.],[20.,21.]])==[[0.,15.],[20.,21.]]


def test_recovery_includes_rotation_and_never_claims_external_rescue(inputs):
    spec,ref,cases=inputs;c=next(c for c in cases if c['family_id']=='P4');m=ref['mass']['accounted_cap_loaded_kg_per_car']
    plain=a.recovery(c,m,spec);rot=a.recovery(c,m,spec,1000.)
    assert rot['required_force_N_at_comparison_mass']-plain['required_force_N_at_comparison_mass']==pytest.approx(c['physical_definition']['formation']['cars']*50.)
    p=a.recovery(cases[0],m,spec)
    assert p['self_recovery_necessary_screen']=='external-recovery-required'
    assert p['external_recovery']['dispatch_time_s'] is None and not p['actual_recovery_demonstrated']


def test_interrupted_demand_creates_model_task_not_design_failure(inputs,monkeypatch):
    from engineering.design_search import architecture_demand
    spec,ref,cases=inputs;original=architecture_demand.demand
    def interrupted(*args,**kwargs):
        r=original(*args,**kwargs);r.update(execution='interrupted',reachable=False);return r
    monkeypatch.setattr(architecture_demand,'demand',interrupted)
    r=a.screen(cases[0],ref['mass']['accounted_cap_loaded_kg_per_car'],1770.,spec)
    assert r['screens']['analytical_reach']=='unknown' and 'analytical_reach' not in r['design_failure_reasons']
    assert a.next_tasks(cases[0],r)[0]['failure_class']=='numerical-resource-or-model'


def test_restart_reuses_exact_requests_and_rejects_changed_cache(inputs,tmp_path,monkeypatch):
    spec,ref,cases=inputs;small=cases[:2]
    monkeypatch.setattr(a,'generate',lambda *args:deepcopy(small))
    first=a.evaluate_campaign(max_new_cases=1,state=tmp_path)
    assert first['state']=='interrupted' and first['new_cases']==1
    completed=a.evaluate_campaign(state=tmp_path)
    journal=json.loads((tmp_path/'journal.json').read_bytes())
    assert len(completed['results'])==2 and journal['cache_hits']==1 and journal['new_cases']==1
    path=tmp_path/(small[0]['case_id']+'.json.gz');raw=json.loads(gzip.decompress(path.read_bytes()))
    raw['request']['comparison_mass_kg_per_car']+=1;path.write_bytes(gzip.compress(a.encoded(raw),mtime=0))
    with pytest.raises(ValueError,match='cache identity'):a.evaluate_campaign(state=tmp_path)
