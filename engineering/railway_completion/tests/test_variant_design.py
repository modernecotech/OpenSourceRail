"""Physical wayside revision must propagate beyond its field experiment."""
from copy import deepcopy
from math import fsum
import gzip
import json
import pytest

from engineering.station_rail.common import identity
from engineering.railway_completion import variant_design as v


@pytest.fixture(scope='module')
def results():
    return {kind:v.evaluate(kind) for kind in v.KINDS}


def test_two_physical_motor_rewrites_have_distinct_candidate_motor_and_brake_ids(results):
    assert len({r['candidate_id'] for r in results.values()})==3
    assert len({r['motor_component_id'] for r in results.values()})==3
    assert len({r['brake_definition_id'] for r in results.values()})==3
    assert len({r['body_candidate_id'] for r in results.values()})==1
    assert len({r['support_component_id'] for r in results.values()})==1
    reference=results['reference']
    assert reference['candidate_id']==reference['parent_reference_bundle_id']
    for kind in ('wide-return','rewound'):
        r=results[kind]
        assert r['bundle']['parent_bundle_id']==reference['candidate_id']
        assert r['bundle']['brake_definition']['propulsion_component_id']==r['motor_component_id']
        assert r['bundle']['brake_definition']['candidate_id']==r['candidate_id']


def test_all_downstream_stages_and_full_federated_bom_use_same_new_candidate(results):
    for r in results.values():
        candidate=r['candidate_id']
        stages=[r[k] for k in ('inventory','ledger','infrastructure','civil','delivery','federated_BOM','electrical_bound','quantities','economics')]
        stages += [r['ledger']['scene']]+[m['result'] for m in r['motion']]
        assert all(stage['candidate_id']==candidate for stage in stages)
        assert set(r['stage_bindings']['stage_candidate_ids'].values())=={candidate}
        for key in ('engineering_BOM','manufacturing_BOM'):
            assert all(row['candidate_id']==candidate for row in r['federated_BOM'][key])
        assert all(row['candidate_id']==candidate and row['disabled']==1 for row in r['federated_BOM']['ERPNext']['items'])
        assert r['delivery']['ERPNext']['posted'] is False and r['delivery']['ERPNext']['ready_for_import'] is False
        assert r['evaluation_id']==identity({k:value for k,value in r.items() if k!='evaluation_id'})


def test_onboard_actual_stock_mass_and_support_remain_identical_while_wayside_mass_changes(results):
    projected=[]
    for r in results.values():
        stock=[row for row in r['ledger']['scene']['occurrences'] if row['system'].startswith('vehicle/')]
        projected.append(identity(stock))
        assert r['quantities']['unchanged_onboard_stock'] is True
        assert abs(r['quantities']['train_account_reconciliation_residual_kg'])<1e-6
        assert r['quantities']['complete_installed_train_mass_kg'] is None
        assert r['bundle']['architecture_case']['physical_definition']['onboard']['driven_axle_count']==0
    assert len(set(projected))==1
    mass=[results[k]['quantities']['bare_primary_mass_kg_all_banks'] for k in v.KINDS]
    assert mass[0]<mass[1]<mass[2]
    assert results['reference']['quantities']['added_bare_primary_mass_kg_all_banks']==0
    # Extra100mm vs25mm backiron: two faces ×75mm ×160mm ×100m ×7850kg/m3.
    assert mass[1]-mass[0]==pytest.approx(2*.075*.16*100*7850)
    assert results['rewound']['quantities']['bare_copper_mass_kg_all_banks']==pytest.approx(
        results['reference']['quantities']['bare_copper_mass_kg_all_banks']*45/25)


def test_primary_stock_geometry_bom_and_infrastructure_weight_reconcile(results):
    for r in results.values():
        q=r['quantities'];scene=r['ledger']['scene']
        wayside=[row for row in scene['occurrences'] if row['system']=='wayside/primary']
        assert q['bank_count']==5 and q['primary_face_count']==10
        assert q['bank_stock_occurrences']==486 and q['total_primary_stock_occurrences']==2430
        assert len(wayside)==2430
        assert fsum(row['mass_kg'] for row in wayside)==pytest.approx(q['bare_primary_mass_kg_all_banks'])
        assert r['infrastructure']['known_wayside_stock_weight_N']==pytest.approx(q['bare_primary_mass_kg_all_banks']*9.80665)
        assert r['infrastructure']['span_count']==106
        assert abs(r['infrastructure']['force_residual_N'])<1e-5
        assert abs(r['infrastructure']['first_moment_residual_Nm'])<1e-2
    base=results['reference']['infrastructure']
    for kind in ('wide-return','rewound'):
        r=results[kind]
        expected=r['quantities']['added_bare_primary_mass_kg_all_banks']*9.80665
        assert r['infrastructure']['known_dead_weight_N']-base['known_dead_weight_N']==pytest.approx(expected)
        difference=fsum(a['known_dead_reaction_N']-b['known_dead_reaction_N'] for a,b in zip(r['infrastructure']['supports'],base['supports']))
        assert difference==pytest.approx(expected)


def test_old_bare_beam_cannot_be_promoted_to_a_wayside_loaded_structural_pass(results):
    for r in results.values():
        c=r['civil']
        assert c['complete_beam_reassessment_includes_wayside_plant'] is False
        assert c['same_candidate_known_deadload_evaluation_id']==r['infrastructure']['evaluation_id']
        assert 'omits the new wayside plant' in c['base_beam_deadload_scope']
        assert c['engineering_accepted'] is False
        assert r['infrastructure']['complete_installed_pier_foundation_loads'] is None


def test_required_motion_does_not_invent_available_force_or_electrical_energy(results):
    for r in results.values():
        assert [m['name'] for m in r['motion']]==['empty','normal','crowd','adverse-normal']
        assert all(m['result']['forward_motion']['admission']['admitted'] is False for m in r['motion'])
        assert all(m['result']['forward_motion']['execution']=='not-run' for m in r['motion'])
        assert all(m['result']['physical_journey_completed'] is False for m in r['motion'])
        assert r['electrical_bound']['phase_voltage_peak_V']==375.
        assert r['operating_map_id'] is None and r['available_propulsion_verified'] is False
        assert all(r[flag] is False for flag in v.FLAGS)


def test_economics_retains_full_unpriced_scope_and_no_winner(results):
    for r in results.values():
        e=r['economics'];bom=r['federated_BOM']
        assert set(e['unpriced_occurrence_ids'])=={row['id'] for row in bom['engineering_BOM']}
        assert e['quoted_occurrences']==0 and e['whole_life_cost_USD'] is None
        assert e['complete_installed_CAPEX_USD'] is None and e['purchased_energy_kWh'] is None
        assert e['economic_winner'] is None and r['integrated_selection'] is None
        assert r['open_tasks']


def test_unknown_variant_is_rejected_before_expensive_generation():
    with pytest.raises(ValueError,match='Explicit'):v.evaluate('untracked-primary')


def test_publication_semantics_reject_forged_mass_after_all_hashes_are_resealed(tmp_path,results,monkeypatch):
    calls=[]
    def generated(kind,root=None):
        calls.append(kind)
        return deepcopy(results[kind])
    monkeypatch.setattr(v,'evaluate',generated)
    manifest=v.publish(tmp_path)
    assert v.verify_publication(tmp_path)['verified']
    assert calls==list(v.KINDS)*2
    path=tmp_path/'wide-return.json.gz'
    forged=json.loads(gzip.decompress(path.read_bytes()))
    forged['quantities']['bare_primary_mass_kg_all_banks']+=1000.
    forged['evaluation_id']=identity({k:value for k,value in forged.items() if k!='evaluation_id'})
    path.write_bytes(gzip.compress(v.encoded(forged),mtime=0))
    manifest['files_sha256'][path.name]=v.digest(path)
    entry=next(r for r in manifest['entries'] if r['kind']=='wide-return')
    entry['quantities']=forged['quantities'];entry['evaluation_id']=forged['evaluation_id']
    manifest['publication_id']=identity({k:value for k,value in manifest.items() if k!='publication_id'})
    (tmp_path/v.MANIFEST).write_bytes(v.encoded(manifest))
    with pytest.raises(ValueError,match='semantic replay'):v.verify_publication(tmp_path)
