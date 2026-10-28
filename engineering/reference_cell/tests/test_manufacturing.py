"""Independent no-transaction, uncertainty, quote and occurrence-cost checks."""
from copy import deepcopy
import pytest
from engineering.component_registry import make_part,make_registry,make_occurrence
from engineering.component_registry.materials import lookup
from engineering.reference_cell import manufacturing as m,identity


def fixture():
    mat=lookup('AL-6082-T651-SHEET')
    p=make_part('TEST-PLATE','A',['primary-body'],{'kind':'box','dimensions_m':[1.,1.,.01]},mat['material_id'],
       {'calculated_kg':27.,'lower_bound_kg':26.8,'upper_bound_kg':27.2,'evidence_state':'calculated'},
       {'method':'cut-and-drill','gross_to_net_yield_hypothesis':.8})
    r=make_registry('test',[p],[make_occurrence('plate/1',p),make_occurrence('plate/2',p)],['primary-body'])
    v=dict(candidate_id=r['candidate_id'],registry=r)
    civil=dict(candidate_id=r['candidate_id'],known_material_mass_kg=1000.,construction_sequence=[{'asset':'span/0'}])
    return v,civil


def quote(v,**changes):
    q=dict(candidate_id=v['candidate_id'],part_definition_id=v['registry']['parts'][0]['physical_definition_id'],source_class='A',
       supplier='TEST DISPOSABLE ONLY',source_date='2026-10-01',valid_until='2027-01-01',currency='USD',location='test-cell',
       quantity_basis='one-part',quote_scope='finished-part',source_document_sha256='a'*64,unit_usd=[100.,110.])
    q.update(changes);q['quote_id']=identity(q);return q


def test_each_physical_occurrence_enters_cost_and_bom_once_with_unknown_scope_still_open():
    v,c=fixture();r=m.compile(v,c)
    assert r['EBOM'][0]['quantity']==2
    lo,hi=r['part_costs'][0]['known_scope_subtotal_usd']
    assert r['known_vehicle_scope_conditional_usd']==pytest.approx([2*lo,2*hi])
    assert r['whole_life_cost_usd'] is None and r['complete_CAPEX_usd'] is None
    assert set(r['missing_whole_life_scopes'])==set(m.SCOPES)
    assert r['actual_quote_occurrence_coverage']==0 and r['economic_winner'] is None
    assert not r['ERPNext']['external_transactions_performed'] and not r['ERPNext']['production_orders']
    assert all(i['disabled']==1 for i in r['ERPNext']['items'])
    assert all(q['docstatus']==0 and not q['transaction_submission_allowed'] for q in r['ERPNext']['rfq_drafts'])
    assert r['MBOM'][0]['gross_mass_interval_kg']==pytest.approx([26.8/.8,27.2/.8])


def test_candidate_mismatch_and_untrusted_class_A_quotes_cannot_be_submitted():
    v,c=fixture();other=dict(c,candidate_id='f'*64)
    with pytest.raises(ValueError):m.compile(v,other)
    with pytest.raises(ValueError):m.compile(v,c,quotes=[quote(v)])
    with pytest.raises(ValueError):m.compile(v,c,quotes=[quote(v,candidate_id='f'*64)],authenticator=lambda *x:True)


def test_unit_supplier_price_does_not_erase_installation_inspection_and_logistics():
    v,c=fixture();r=m.compile(v,c,quotes=[quote(v)],authenticator=lambda *x:True)
    cost=r['part_costs'][0]
    assert cost['cost_source_class']!='A'
    assert cost['components_usd']['processing'] is None
    assert cost['known_scope_subtotal_usd'][0]>100. and cost['known_scope_subtotal_usd'][1]>110.
    assert r['complete_installed_vehicle_cost_usd'] is None and not r['physical_accepted']


@pytest.mark.parametrize('change',[
 {'valid_until':'2025-01-01'}, {'source_date':'tomorrow'}, {'source_document_sha256':'not-a-content-hash'},
 {'currency':'EUR'}, {'quantity_basis':'one-car'}, {'quote_scope':'ambiguous'}, {'unit_usd':[110.,100.]},
])
def test_bad_or_incomparable_commercial_record_is_rejected(change):
    v,c=fixture()
    with pytest.raises(ValueError):m.compile(v,c,quotes=[quote(v,**change)],authenticator=lambda *x:True)


def test_duplicate_actual_quotes_need_explicit_selection_and_no_mixed_quote_units():
    v,c=fixture();q=quote(v)
    with pytest.raises(ValueError):m.compile(v,c,quotes=[q,q],authenticator=lambda *x:True)


@pytest.mark.parametrize('yield_value',[0.,-1.,1.1,float('nan')])
def test_invalid_physical_yield_refused_before_negative_or_infinite_gross_mass(yield_value):
    v,c=fixture();p=v['registry']['parts'][0];p['manufacturing']['gross_to_net_yield_hypothesis']=yield_value
    # Use public constructors, so assertions cannot depend on a stale registry hash.
    try:
        p=make_part(p['part_id'],p['revision'],p['functions'],p['geometry'],p['material_id'],p['mass'],p['manufacturing'])
        r=make_registry('test',[p],[make_occurrence('one',p)],['primary-body']);v=dict(candidate_id=r['candidate_id'],registry=r);c=dict(c,candidate_id=r['candidate_id'])
        with pytest.raises(ValueError):m.compile(v,c)
    except ValueError:
        pass


def test_changed_cost_scenario_source_cannot_be_reused_after_unsealed_edit():
    v,c=fixture();s=m.scenario();s['stock_usd_per_kg']=[.01,.02]
    with pytest.raises(ValueError,match='identity'):m.compile(v,c,estimate=s)


def test_raw_blank_quote_keeps_local_processing_while_finished_part_does_not_double_charge():
    v,c=fixture()
    raw=m.compile(v,c,quotes=[quote(v,quote_scope='material-blank')],authenticator=lambda *x:True)
    finished=m.compile(v,c,quotes=[quote(v,quote_scope='finished-part')],authenticator=lambda *x:True)
    assert raw['part_costs'][0]['components_usd']['processing'] is not None
    assert finished['part_costs'][0]['components_usd']['processing'] is None
    assert raw['known_vehicle_scope_conditional_usd'][0]>finished['known_vehicle_scope_conditional_usd'][0]
