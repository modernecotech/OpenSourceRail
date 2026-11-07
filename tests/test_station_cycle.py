"""Same-candidate cycle contracts and actual source-bound publication integrity."""
from copy import deepcopy
from pathlib import Path
import gzip,json,shutil
import pytest
from engineering.station_cycle import design,coordinator,publication,history
from engineering.station_pair import lifecycle
from engineering.station_rail.common import identity,encoded,digest


@pytest.fixture(scope='module')
def definitions():return coordinator.requests()


def test_physical_candidates_remain_sealed_after_inventory_mutation(definitions):
    brief,bundle,mass,p,meta=definitions
    designs={m['design']['variant']['candidate_id']:m['design'] for m in meta}
    assert len(designs)==10
    for cid,d in designs.items():
        assert cid==identity(d['variant']['physical_definition'])
        assert d['variant']['body_candidate_id']==bundle['candidate_id']
        if d['recovery_hardware']:
            assert d['variant']['parent_candidate_id']!=cid
            assert any(r['id']=='capture-release-interface-reserve' for r in d['variant']['inventory'])


def test_all_architectures_receive_identical_environment_fault_recipes(definitions):
    meta=definitions[-1];sets={}
    special={'nominal','recovery-disabled','refined-dt','capture-failed','release-failed','reset-failed',
        'slow-reset','storage-leakage','low-transfer-power','initially-full','no-authority'}
    for m in meta:
        sets.setdefault(m['design']['variant']['candidate_id'],set()).add(m['experiment'])
    assert len(sets)==10
    assert all(len(names-special)==18 for names in sets.values())
    assert len({frozenset(names-special) for names in sets.values()})==1


def test_cold_start_and_explicit_external_initial_charge_are_distinct(definitions):
    for m in definitions[-1]:
        initial=sum(s['initial_energy_j'] for s in m['request']['stations'])
        assert (initial>0)==(m['experiment']=='initially-full')
        if m['nominal']:assert initial==0


def test_disabled_recovery_is_same_hardware_but_different_evaluation(definitions):
    nominal={m['design']['variant']['candidate_id']:m for m in definitions[-1] if m['experiment']=='nominal'}
    for m in definitions[-1]:
        if m['experiment']!='recovery-disabled':continue
        a=nominal[m['request']['candidate_id']]
        assert a['design']==m['design']
        assert a['request']['id']!=m['request']['id']
        assert all(x['capture_failed'] and x['release_failed'] for x in m['request']['legs'])


def test_reverse_grade_and_tug_gravity_have_physical_direction(definitions):
    m=next(m for m in definitions[-1] if m['experiment']=='up-2pct' and m['design']['variant']['family']=='cable')
    a,b=(l['journey'] for l in m['request']['legs'][:2])
    assert a['grade_fraction']==.02 and b['grade_fraction']==-.02
    assert a['control']['grade_estimate_fraction']==.02
    assert b['control']['grade_estimate_fraction']==-.02
    assert a['drive']['external_resistance_n']-b['drive']['external_resistance_n']==pytest.approx(2*2500*9.80665*.02)
    assert a['control']['policy_id']==b['control']['policy_id']


@pytest.mark.parametrize('technology',['steel','hydraulic'])
def test_storage_quantity_scales_and_is_not_massless(technology):
    p=design.policy();a=design.size_store(technology,4e6,p);b=design.size_store(technology,8e6,p)
    assert b['active_mass_kg']==pytest.approx(2*a['active_mass_kg'])
    assert b['reserve_envelope_m3']==pytest.approx(2*a['reserve_envelope_m3'])
    assert a['active_mass_kg']>1000
    if technology=='steel':assert b['active_mass_kg']==pytest.approx(59455.62130177515)


@pytest.mark.parametrize('capacity',[0.,-1.,float('nan'),float('inf')])
def test_nonphysical_capacity_rejected(capacity):
    with pytest.raises(ValueError):design.size_store('steel',capacity,design.policy())


def test_added_hardware_has_unique_canonical_cost_owners_and_no_duplicate_parent(definitions):
    d=next(m['design'] for m in definitions[-1] if m['design']['recovery_hardware'])
    p=definitions[3];core={'service':{'total_trainsets':4}}
    rows=design.added_accounts(d,core,p)
    assert len({r['owner'] for r in rows})==len(rows)
    assert all(r['scope'] in lifecycle.SCOPES for r in rows)
    assert all(r['candidate_id']==d['variant']['candidate_id'] for r in rows)
    assert all(r['account_id']==identity({k:v for k,v in r.items() if k!='account_id'}) for r in rows)
    assert all(min(r['cost_usd'].values())>0 for r in rows)
    assert not any(r['owner']=='rolling-stock-delivered' for r in rows)
    interface=next(r for r in rows if r['owner']=='regenerative-vehicle-interface')
    assert interface['quantity']==4
    assert interface['cost_usd']['base']==38400.
    assert any('cooling' in r['owner'] for r in rows)


def test_source_bound_history_is_retained():
    result=history.verify()
    assert result['git_source_commit'].startswith('b5212904e3')
    assert result['study_id']=='5914dc6d539a5757ec5c4027a52d8aeda9ef7c05496d0e46b424afe89890d1f7'
    assert result['physical_accepted'] is False


@pytest.fixture(scope='module')
def published():
    result=publication.verify()
    root=Path(__file__).resolve().parents[1]/publication.OUTPUT
    value=json.loads(gzip.decompress((root/'study.json.gz').read_bytes()))
    return result,root,value


def test_actual_cycle_packet_reconstructs_with_no_selection(published):
    result,root,study=published
    assert result['normal_cases']==18 and result['fault_cases']==254
    assert study['financial_evaluations']==10
    assert study['integrated_selection'] is None
    assert not study['concurrent_service_verified']


def test_arrivals_are_separate_from_jerk_and_service_screens(published):
    for r in published[2]['records']:
        row=r['row']
        if row['maximum_moving_jerk_m_s3'] is not None and row['maximum_moving_jerk_m_s3']>.505:
            assert not row['advisory_screen']
        assert row['service']['requested_headway_s']==200
        assert row['service']['modeled_direction_headway_s']==520
        assert row['cost']['whole_life_NPV_usd']['base'] is None
        assert row['cost']['known_lifecycle_NPV_usd']['base']>row['cost']['installed_capital_usd']['base']


def test_tampered_served_summary_is_rejected(published,tmp_path):
    root=published[1];out=tmp_path/'packet';shutil.copytree(root,out)
    s=json.loads((out/'summary.json').read_bytes());s['rows'][0]['physical_accepted']=True
    (out/'summary.json').write_bytes(encoded(s))
    with pytest.raises(ValueError,match='artifact changed'):publication.verify(output=out)


def test_a_resealed_false_release_is_still_rejected(published,tmp_path):
    out=tmp_path/'packet';shutil.copytree(published[1],out)
    p=out/'manifest.json';m=json.loads(p.read_bytes());m['physical_accepted']=True
    m.pop('manifest_id');m['manifest_id']=identity(m);p.write_bytes(encoded(m))
    with pytest.raises(ValueError,match='grant release'):publication.verify(output=out)


def test_auxiliary_energy_uses_cycle_clock_once_without_extra_final_dwell(published):
    study=published[2]
    for record in study['records']:
        row=record['row'];request=record['request'];result=record['result']
        expected_horizon=max(x['end_time_s'] for x in result['legs'])-request['legs'][0]['departure_time_s']
        power=request['legs'][0]['journey']['auxiliary_power_w']
        e=row['energy_reconciliation']
        assert e['auxiliary_observation_horizon_s']==pytest.approx(expected_horizon)
        assert e['auxiliary_and_charge_loss_grid_j']==pytest.approx(power*expected_horizon/study['brief']['hotel_charge_efficiency_hypothesis'])
