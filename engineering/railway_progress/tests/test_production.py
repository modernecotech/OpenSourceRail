"""Manufacturing hypotheses retain purchased, tooling and price uncertainty."""
from copy import deepcopy
from math import pi,fsum
import pytest
from engineering.reference_cell import vehicles,bundle
from engineering.railway_progress import alternatives,coordinator,production as p,identity,FLAGS


@pytest.fixture(scope='module')
def inputs():
    v=vehicles.evaluate('V1');base=bundle.materialize(v,2000.)
    a=alternatives.evaluate(v,base);b,c=coordinator.compose(v,2000.,a)
    return v,b,c,a


@pytest.fixture(scope='module')
def result(inputs):
    v,b,c,a=inputs;return p.compile(v,c,a,b['candidate_id'])


@pytest.mark.parametrize('g',[
    dict(kind='box',dimensions_m=[2.,.1,.005],net_volume_m3=.001),
    dict(kind='tube',dimensions_m=dict(length=2.,outer_radius=.2,inner_radius=.18),net_volume_m3=pi*(.2**2-.18**2)*2),
    dict(kind='cylinder',dimensions_m=dict(length=.04,radius=.02),net_volume_m3=pi*.02**2*.04)])
def test_dimensional_blanks_are_at_least_exact_net_geometry(g):
    r=p.blank(g)
    assert r['blank_volume_m3']>=g['net_volume_m3']
    assert r['removed_volume_m3']==pytest.approx(r['blank_volume_m3']-g['net_volume_m3'])
    assert r['yield_fraction']==pytest.approx(g['net_volume_m3']/r['blank_volume_m3'])
    assert 0<r['yield_fraction']<=1
    assert r['approved_work_instruction'] is None


def test_purchased_envelope_never_fills_raw_material_or_zeroes_unknown_cycle(result):
    rows=[x for x in result['routings'] if x['blank']['net_volume_m3'] is None]
    assert rows and result['purchased_occurrences']==sum(x['quantity'] for x in rows)
    for x in rows:
        assert x['blank']['blank_volume_m3'] is None and x['blank']['yield_fraction'] is None
        assert x['labour_h_per_unit'] is None and x['qualified_manufacturing_cycle_h'] is None
        assert x['material_scope_cost_usd'] is None and x['tooling'] is None
    assert result['complete_installed_cost_usd'] is None and result['whole_life_cost_usd'] is None


def test_full_stock_mass_and_c_hypotheses_do_not_become_quoted_cost_or_release(inputs,result):
    v,b,c,a=inputs
    parts={x['physical_definition_id']:x for x in v['registry']['parts']}
    counted=fsum(parts[o['part_definition_id']]['mass']['calculated_kg'] for o in v['registry']['occurrences'] if parts[o['part_definition_id']]['geometry']['kind']!='envelope')
    assert result['net_counted_vehicle_stock_kg']==pytest.approx(counted,abs=1e-6)
    assert result['dimensioned_vehicle_blank_kg']>=result['net_counted_vehicle_stock_kg']>0
    assert result['removed_or_offcut_vehicle_stock_kg']==pytest.approx(result['dimensioned_vehicle_blank_kg']-result['net_counted_vehicle_stock_kg'])
    assert result['process_assumptions']['source_class']=='C'
    assert result['process_assumptions']['source_id']==identity({k:v for k,v in result['process_assumptions'].items() if k!='source_id'})
    assert result['tooling_cost_usd'] is None
    tools=[r['tooling'] for r in result['routings'] if r['tooling']]
    assert tools and all(t['tool_price_usd'] is None and not t['qualified'] for t in tools)
    assert all(r['production_release'] is False for r in result['routings'])
    draft=result['ERPNext_drafts']
    assert draft['submission_allowed'] is False and draft['docstatus']==0
    assert draft['items_disabled'] is True and draft['active_BOMs'] is False
    assert all(result[k] is False for k in FLAGS)
    assert result['evaluation_id']==identity({k:v for k,v in result.items() if k!='evaluation_id'})


def test_assumption_revision_changes_evaluation_without_reinventing_physical_candidate(inputs,result):
    v,b,c,a=inputs;q=p.assumptions();q['material_usd_per_kg']=[3.,40.];q['source_id']=identity({k:v for k,v in q.items() if k!='source_id'})
    r=p.compile(v,c,a,b['candidate_id'],process=q)
    assert r['candidate_id']==result['candidate_id'] and r['evaluation_id']!=result['evaluation_id']
    assert r['known_vehicle_stock_process_cost_usd']!=result['known_vehicle_stock_process_cost_usd']


@pytest.mark.parametrize('field,value',[('source_class','A'),('material_usd_per_kg',[-2.,30.]),('labour_usd_per_h',[40.,8.]),('cutting_m_per_h',[0.,30.]),('shift_hours',0),('workstations',-1),('composite_cure_h',[48.,12.])])
def test_resealed_invalid_rates_cannot_create_fake_evidence_or_negative_cost(inputs,field,value):
    v,b,c,a=inputs;q=p.assumptions();q[field]=value;q['source_id']=identity({k:v for k,v in q.items() if k!='source_id'})
    with pytest.raises(ValueError):p.compile(v,c,a,b['candidate_id'],process=q)


@pytest.mark.parametrize('change',['vehicle','civil','alternative'])
def test_mixed_component_or_cell_identity_is_refused(inputs,change):
    v,b,c,a=deepcopy(inputs)
    if change=='vehicle':v['registry']['occurrences'][0]['part_definition_id']='f'*64
    elif change=='civil':c['candidate_id']='f'*64
    else:a['body_candidate_id']='f'*64;a['evaluation_id']=identity({k:v for k,v in a.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):p.compile(v,c,a,b['candidate_id'])


def test_material_substitution_requires_new_part_and_registry_revisions(inputs):
    v,b,c,a=deepcopy(inputs)
    v['registry']['parts'][0]['material_id']='unqualified-material-substitution'
    v['evaluation_id']=identity({k:v for k,v in v.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):p.compile(v,c,a,b['candidate_id'])
