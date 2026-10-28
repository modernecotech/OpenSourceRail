"""Independent conditional NPV, coverage, commercial and equal-service controls."""
from copy import deepcopy
import pytest
from engineering.reference_cell import economics as e,identity

CANDIDATE='a'*64


def service(calendar=False):
    s=dict(cars=6,car_length_m=17.,normal_places_per_car=46,headway_s=120.,station_spacing_m=2000.,fleet_trainsets=4,
        normal_capacity_pphpd=8280.,estimate_date='2026-10-28',protected_service_qualified=False,
        engineering_evidence_qualified=False,risk_basis='same-unqualified-reference-cell')
    if calendar:s['required_cashflows']=[dict(scope=scope,year=i%3,physical_scope=scope+'/specific-operation') for i,scope in enumerate(e.SCOPES)]
    return s


def record(scope='rolling-stock',candidate=CANDIDATE,s=None,**kw):
    s=s or service();values=dict(candidate_id=candidate,scope=scope,physical_scope=[scope+'/specific-operation'],
        quantity=[2.,2.],unit_cost_usd=[100.,150.],year=0,source_class='C',source_id='b'*64,
        source_date='2026-10-01',location='test-reference-cell',quantity_basis='two-unit-budget',
        service_context_id=e.service_identity(s),method='TEST explicitly bounded engineering estimate, no market assertion')
    values.update(kw);return e.make_record(**values)


def test_missing_cost_never_becomes_whole_life_zero_or_cheapest():
    s=service();r=e.evaluate(CANDIDATE,[],20,.05,s)
    assert r['known_scope_npv_usd']==[0.,0.] and r['conditional_declared_calendar_npv_usd'] is None
    assert r['complete_installed_whole_life_cost_usd'] is None
    assert set(r['missing_whole_life_scopes'])==set(e.SCOPES)
    assert r['actual_quote_coverage'] is None and r['integrated_winner'] is None
    assert not r['bound_ranking_is_value_of_information'] and not r['physical_accepted']


def test_quantity_bounds_year_discount_and_known_annual_subtotals_are_exact():
    s=service();r=e.evaluate(CANDIDATE,[record(s=s,year=2)],5,.1,s)
    assert r['known_scope_npv_usd']==pytest.approx([200/1.1**2,300/1.1**2])
    assert r['annual'][2]['known_scope_usd']==[200.,300.]
    assert r['annual'][0]['known_scope_usd']==[0.,0.]
    assert r['conditional_declared_calendar_npv_usd'] is None
    assert r['estimated_charge_count']==1


def test_complete_declared_calendar_is_conditional_estimate_never_physical_wholelife_winner():
    s=service(True);rows=[record(scope=x['scope'],year=x['year'],s=s) for x in s['required_cashflows']]
    r=e.evaluate(CANDIDATE,rows,10,.05,s)
    expected=[sum((200.,300.)[k]/1.05**x['year'] for x in s['required_cashflows']) for k in (0,1)]
    assert r['conditional_declared_calendar_npv_usd']==pytest.approx(expected)
    assert r['declared_calendar_complete'] and r['conditional_estimate_coverage']==1.
    assert r['actual_quote_coverage']==0 and r['complete_installed_whole_life_cost_usd'] is None
    assert r['open_protection_or_evidence'] and r['integrated_winner'] is None


@pytest.mark.parametrize('rows',[lambda s:[record(s=s),record(s=s)],
 lambda s:[record(s=s,physical_scope=['train/car/processing']),record(s=s,physical_scope=['train/car'])],
 lambda s:[record(s=s),record(scope='maintenance',s=s,physical_scope=['rolling-stock/specific-operation'])]])
def test_duplicate_or_overlapping_physical_costs_across_scopes_are_rejected(rows):
    s=service()
    with pytest.raises(ValueError):e.evaluate(CANDIDATE,rows(s),5,.05,s)


def test_same_component_operation_can_recur_in_explicit_different_years():
    s=service();rows=[record(scope='maintenance',s=s,year=y) for y in (1,2)]
    r=e.evaluate(CANDIDATE,rows,5,0.,s)
    assert r['known_scope_npv_usd']==[400.,600.]


@pytest.mark.parametrize('changes',[
 {'candidate_id':'c'*64},{'service_context_id':'c'*64},{'currency':'EUR'},{'source_id':'not-a-hash'},
 {'source_date':'tomorrow'},{'source_date':'2027-01-01'},{'quantity':[0.,1.]},{'quantity':[3.,2.]},
 {'unit_cost_usd':[float('nan'),1.]},{'source_class':'D'},{'year':30},{'method':''},
])
def test_malformed_or_incomparable_source_and_quantity_inputs_rejected(changes):
    s=service()
    try:r=record(s=s,**changes)
    except (ValueError,TypeError):return
    with pytest.raises(ValueError):e.evaluate(CANDIDATE,[r],20,.05,s)


def test_actual_quote_without_external_authentication_is_held_not_estimated_or_silently_free():
    s=service();q=record(s=s,source_class='A',source_document_sha256='d'*64,supplier='TEST ONLY',valid_until='2027-01-01')
    r=e.evaluate(CANDIDATE,[q],5,.05,s)
    assert r['held_actual_source_record_ids']==[q['record_id']]
    assert r['actual_authenticated_charge_count']==0 and r['known_scope_npv_usd']==[0.,0.]
    assert r['conditional_declared_calendar_npv_usd'] is None


def test_authenticated_actual_source_is_scoped_and_context_identity_required():
    s=service();q=record(s=s,source_class='A',source_document_sha256='d'*64,supplier='TEST ONLY',valid_until='2027-01-01')
    with pytest.raises(ValueError):e.evaluate(CANDIDATE,[q],5,.05,s,authenticator=lambda *a:True)
    r=e.evaluate(CANDIDATE,[q],5,.05,s,authenticator=lambda *a:True,authentication_context_id='e'*64)
    assert r['actual_authenticated_charge_count']==1 and r['known_scope_npv_usd']==[200.,300.]
    assert r['records'][0]['externally_authenticated'] and r['integrated_winner'] is None


def test_quote_expiry_source_document_and_no_self_attestation_bypass():
    s=service()
    for changes in ({'valid_until':'2025-01-01'},{'source_document_sha256':'bad'}):
        q=record(s=s,source_class='A',source_document_sha256='d'*64,supplier='TEST ONLY',valid_until='2027-01-01')
        q.update(changes);q['record_id']=identity({k:v for k,v in q.items() if k!='record_id'})
        with pytest.raises(ValueError):e.evaluate(CANDIDATE,[q],5,.05,s,authenticator=lambda *a:True,authentication_context_id='e'*64)


def test_sensitivity_uses_supported_discounted_bound_width_not_invented_missing_price():
    s=service();narrow=record(s=s,physical_scope=['train/a'],unit_cost_usd=[10.,11.])
    wide=record(s=s,physical_scope=['train/b'],unit_cost_usd=[10.,100.],year=1)
    r=e.evaluate(CANDIDATE,[narrow,wide],5,.1,s)
    rank=r['sensitivity_bound_width_ranking']
    assert rank[0]['record_id']==wide['record_id']
    assert rank[0]['npv_bound_width_usd']==pytest.approx(180/1.1)
    assert r['unbounded_missing_quotes_or_measurements'] and not r['bound_ranking_is_value_of_information']


@pytest.mark.parametrize('key,value',[('fleet_trainsets',5),('headway_s',121.),('cars',5),('station_spacing_m',1500.),('risk_basis','different-risk')])
def test_changed_fleet_headway_capacity_route_or_risk_requires_new_comparison_basis(key,value):
    s=service();other=dict(s);other[key]=value;other.pop('normal_capacity_pphpd')
    a=e.evaluate(CANDIDATE,[],20,.05,s);b=e.evaluate('b'*64,[],20,.05,other)
    with pytest.raises(ValueError,match='Equal'):e.compare([a,b])


def test_unknown_cost_candidate_is_not_ranked_cheapest_and_forged_result_rejected():
    s=service(True);rows=[record(scope=x['scope'],year=x['year'],s=s) for x in s['required_cashflows']]
    a=e.evaluate(CANDIDATE,rows,10,.05,s);unknown=e.evaluate('b'*64,[],10,.05,s)
    c=e.compare([a,unknown]);assert c['unknown_cost_candidates']==['b'*64] and c['integrated_winner'] is None
    a['known_scope_npv_usd']=[0.,0.]
    with pytest.raises(ValueError):e.compare([a,unknown])


def test_required_calendar_rejects_omitted_scopes_duplicates_and_unplanned_charge():
    s=service(True);partial=deepcopy(s);partial['required_cashflows'].pop()
    with pytest.raises(ValueError):e.evaluate(CANDIDATE,[],10,.05,partial)
    duplicate=deepcopy(s);duplicate['required_cashflows'].append(duplicate['required_cashflows'][0])
    with pytest.raises(ValueError):e.evaluate(CANDIDATE,[],10,.05,duplicate)
    with pytest.raises(ValueError):e.evaluate(CANDIDATE,[record(s=s,physical_scope=['unplanned/item'])],10,.05,s)


def test_resealed_cost_record_cannot_grant_hardware_release():
    s=service();r=record(s=s,manufacturing_release=True)
    with pytest.raises(ValueError,match='release'):e.evaluate(CANDIDATE,[r],10,.05,s)


def test_cost_provenance_and_source_epoch_remain_visible_in_result():
    s=service();r=e.evaluate(CANDIDATE,[record(s=s)],10,.05,s)
    row=r['records'][0]
    assert row['location']=='test-reference-cell' and row['source_date']=='2026-10-01' and row['currency']=='USD'
    assert r['source_sha256']==e.sources()
    stale=deepcopy(r);stale['source_sha256'][e.PRODUCER]='f'*64;stale['evaluation_id']=identity({k:v for k,v in stale.items() if k!='evaluation_id'})
    with pytest.raises(ValueError,match='source'):e.compare([stale])
