"""Pure synthetic accounting controls; no actual candidate or business execution."""
from copy import deepcopy
import pytest

from engineering.railway_project import part_accounts as a
from engineering.station_rail.common import identity


def cases(value):
    return dict.fromkeys(a.CASES, value)


def seal(value):
    value.pop('evaluation_id', None)
    value['evaluation_id'] = identity(value)
    return value


def body():
    # The actual P1 catalogue also has item and bounded-purchase-or-process;
    # these values are schema controls, not reused vehicle geometry or prices.
    parts = []
    for pid, quantity, rate in [('sheet', 3, 100.), ('motor', 2, 50.)]:
        parts.append(dict(id=pid, quantity_per_train=quantity, unit='item',
            make_buy='bounded-purchase-or-process', component_definition_id=identity(pid), candidate_id=identity(dict(component=pid)),
            direct_cost_each_usd=cases(rate), cost_basis='Synthetic calculated direct part/process only', source_ids=['SYNTHETIC/'+pid]))
    physical = dict(schema='synthetic-accounting-physical/1', test_only=True,
        parts=[dict(id=p['id'],quantity_per_train=p['quantity_per_train']) for p in parts])
    return seal(dict(schema='osr-vehicle-installation/1', physical_definition=physical, candidate_id=identity(physical),
        parent_candidate_id=identity('synthetic-direct-parent'), parts=parts, patterns=[], materials=[], total_occurrences=5,
        direct_parts_process_usd=cases(400.), source_sha256={'SYNTHETIC':identity('fixture')}))


COST = identity('synthetic-source-cost-evaluation')


def contract(b):
    rows = []
    for p in b['parts']:
        rows.append(dict(part_id=p['id'],source_part_sha256=identity(p),component_definition_id=p['component_definition_id'],
            component_candidate_id=p['candidate_id'],source_cost_id=a.source_cost_identity(b,p,COST),
            account_owner='body/'+p['id'],valuation_basis='existing-direct-parts-process-only',
            make_buy=dict(planning_route='local-fabricate' if p['id']=='sheet' else 'buy-qualified',basis='Synthetic choice',source_reference='SYNTHETIC/decision'),
            conversion=dict(source_unit='item',target_unit='Nos',target_per_source=cases(1.),measurement_basis='count',basis='One discrete source item',source_reference='SYNTHETIC/units'),
            cost_coverage=dict(included=['material','processing'],excluded=['final assembly','freight'],unknown=[]),
            stock=dict(quantity_basis='gross-purchase',gross_each_kg=cases(2.),net_each_kg=cases(1.6),scrap_each_kg=cases(.4),basis='Synthetic gross/net specification',source_reference='SYNTHETIC/stock')))
    return dict(schema='osr-part-account-contract/1',body_candidate_id=b['candidate_id'],body_evaluation_id=b['evaluation_id'],
        cost_evaluation_id=COST,fleet=4,rows=rows)


def compiled(b=None, c=None):
    b = body() if b is None else b
    return a.compile_accounts(b, contract(b) if c is None else c, 4, cost_evaluation_id=COST)


def legacy(result, *, parent=False):
    return seal(dict(schema='osr-legacy-part-accounts/1',candidate_id=result['parent_candidate_id'] if parent else result['body_candidate_id'],
        currency='USD',quantity_basis='project',fleet=4,accounts=[dict(account_id='old-body',coverage_owner_ids=['body/sheet','unresolved/retained'],
            cost_usd=cases(3000.),basis='Synthetic existing residual account, not a new material subtotal')]))


def credit(result, old):
    return dict(legacy_account_id='old-body',legacy_account_sha256=identity(old['accounts'][0]),legacy_evaluation_id=old['evaluation_id'],
        body_candidate_id=result['body_candidate_id'],body_evaluation_id=result['body_evaluation_id'],cost_evaluation_id=COST,part_accounts_evaluation_id=result['evaluation_id'],
        ancestry='same-candidate' if old['candidate_id']==result['body_candidate_id'] else 'direct-parent-revision',
        part_ids=['sheet'],replaced_owner_ids=['body/sheet'],retained_owner_ids=['unresolved/retained'],
        replacement_credit_usd=cases(1000.),basis='Explicit synthetic component replacement credit',source_reference='SYNTHETIC/ownership')


def addition(result, old):
    return dict(legacy_evaluation_id=old['evaluation_id'],body_candidate_id=result['body_candidate_id'],body_evaluation_id=result['body_evaluation_id'],cost_evaluation_id=COST,part_accounts_evaluation_id=result['evaluation_id'],
        legacy_accounts_sha256={r['account_id']:identity(r) for r in old['accounts']},part_ids=['motor'],
        basis='Synthetic motor is explicitly outside all listed legacy account coverage',source_reference='SYNTHETIC/disjoint-ownership')


def test_full_mapping_conserves_count_times_rate_without_mutating_source():
    b=body();before=deepcopy(b);r=compiled(b)
    assert b==before and r['all_source_parts_mapped']
    assert r['evaluation_id']==identity({k:v for k,v in r.items()if k!='evaluation_id'})
    sheet,motor=r['rows']
    assert sheet['target_quantity_project']==cases(12) and sheet['project_direct_cost_usd']==cases(1200.)
    assert motor['target_quantity_project']==cases(8) and motor['project_direct_cost_usd']==cases(400.)
    assert all(not x['procurement_release'] and not x['additive_to_existing_cost_ledger'] for x in r['rows'])
    projected=a.planning_body(b,r)
    assert projected['evaluation_id']==b['evaluation_id'] and 'physical_definition' not in projected
    assert projected['schema']=='osr-unsealed-part-planning-projection/1' and 'candidate_id' not in projected
    assert projected['parts'][0]['unit']=='item' and projected['parts'][0]['make_buy']=='local-fabricate'
    assert b['parts'][0]['make_buy']=='bounded-purchase-or-process'


def test_gross_kg_conversion_changes_quantity_and_rate_once():
    b=body();c=contract(b);x=c['rows'][0]['conversion']
    x.update(target_unit='kg',target_per_source=cases(2.),measurement_basis='gross-purchase-mass')
    r=compiled(b,c)['rows'][0]
    assert r['target_quantity_project']==cases(24.)
    assert r['target_unit_rate_usd']==cases(50.) and r['project_direct_cost_usd']==cases(1200.)
    assert r['stock']['net_each_kg']==cases(1.6) and r['stock']['scrap_each_kg']==cases(.4)


@pytest.mark.parametrize('field', ['conversion','make_buy','cost_coverage','stock'])
def test_missing_decisions_are_holds_not_defaults(field):
    b=body();c=contract(b);c['rows'][0][field]=None;r=compiled(b,c)
    assert not r['all_source_parts_mapped'] and r['held_part_ids']==['sheet']
    if field=='conversion':assert r['rows'][0]['target_unit'] is None
    if field=='make_buy':assert r['rows'][0]['planning_route'] is None


def test_missing_part_mapping_retains_explicit_unknown_row():
    b=body();c=contract(b);c['rows'].pop();r=compiled(b,c)
    assert r['held_part_ids']==['motor'] and r['rows'][1]['project_direct_cost_usd'] is None


def test_fractional_packs_are_held_without_rounding_quantity_or_cost():
    b=body();c=contract(b);c['rows'][0]['conversion'].update(target_unit='Set',measurement_basis='pack-count',target_per_source=cases(.1))
    r=compiled(b,c)['rows'][0]
    assert r['status']=='held' and r['target_quantity_project']['base']==pytest.approx(1.2)
    assert r['project_direct_cost_usd']==cases(1200.)


def test_source_price_basis_and_evidence_cannot_be_implicit():
    b=body();b['parts'][0]['cost_basis']=None;seal(b)
    assert 'sheet' in compiled(b)['held_part_ids']


def test_partial_stock_case_bounds_remain_unknown_not_zero_or_finished_mass():
    b=body();c=contract(b);c['rows'][0]['stock']['gross_each_kg']['high']=None
    r=compiled(b,c)['rows'][0]
    assert r['status']=='held' and r['stock']['gross_each_kg']['high'] is None


def test_varying_occurrence_cost_cannot_silently_use_nominal_each_price():
    b=body();b['patterns']=[dict(id='pattern/'+p['id'],part_id=p['id'],count=p['quantity_per_train'],
        direct_cost_usd=cases(270. if p['id']=='sheet' else 100.)) for p in b['parts']];seal(b)
    r=compiled(b)
    assert r['held_part_ids']==['sheet'] and r['rows'][0]['project_direct_cost_usd'] is None
    assert r['rows'][0]['source_pattern_cost_per_train_usd']==cases(270.)
    assert r['rows'][1]['project_direct_cost_usd']==cases(400.)


def test_matching_occurrence_cost_is_preserved_and_count_mismatch_rejected():
    b=body();b['patterns']=[dict(id='pattern/'+p['id'],part_id=p['id'],count=p['quantity_per_train'],
        direct_cost_usd={c:p['quantity_per_train']*p['direct_cost_each_usd'][c] for c in a.CASES})for p in b['parts']];seal(b)
    assert compiled(b)['all_source_parts_mapped']
    b['patterns'][0]['count']=2;seal(b)
    with pytest.raises(ValueError,match='pattern quantity'):compiled(b)


@pytest.mark.parametrize('price',[None,cases(None),cases(0.)])
def test_unknown_or_zero_price_never_becomes_zero_value(price):
    b=body();b['parts'][0]['direct_cost_each_usd']=price;seal(b);r=compiled(b)
    assert r['held_part_ids']==['sheet'] and r['rows'][0]['project_direct_cost_usd'] is None


@pytest.mark.parametrize('field',['source_part_sha256','component_definition_id','component_candidate_id','source_cost_id'])
def test_wrong_part_revision_or_cost_identity_rejected(field):
    b=body();c=contract(b);c['rows'][0][field]=identity('different')
    with pytest.raises(ValueError,match='identity'):compiled(b,c)


@pytest.mark.parametrize('field',['body_candidate_id','body_evaluation_id','cost_evaluation_id','fleet'])
def test_wrong_candidate_evaluation_or_project_quantity_rejected(field):
    b=body();c=contract(b);c[field]=5 if field=='fleet' else identity('different')
    with pytest.raises(ValueError,match='Mixed'):compiled(b,c)


def test_duplicate_and_orphan_part_mapping_rejected():
    b=body();c=contract(b);c['rows'].append(deepcopy(c['rows'][0]))
    with pytest.raises(ValueError,match='Duplicate'):compiled(b,c)
    c=contract(b);c['rows'][0]['part_id']='unrelated'
    with pytest.raises(ValueError,match='Orphan'):compiled(b,c)


@pytest.mark.parametrize('fault',['source-unit','net-as-gross','scrap','NaN','coverage','route'])
def test_ambiguous_conversion_coverage_and_invalid_numbers_rejected(fault):
    b=body();c=contract(b);r=c['rows'][0]
    if fault=='source-unit':r['conversion']['source_unit']='kg'
    if fault=='net-as-gross':r['conversion'].update(target_unit='kg',measurement_basis='gross-purchase-mass',target_per_source=cases(1.6))
    if fault=='scrap':r['stock']['scrap_each_kg']=cases(0.)
    if fault=='NaN':r['conversion']['target_per_source']=cases(float('nan'))
    if fault=='coverage':r['cost_coverage']['unknown']=['material']
    if fault=='route':r['make_buy']['planning_route']='make'
    with pytest.raises(ValueError):compiled(b,c)


def test_disjoint_bridge_keeps_explicit_reserve_and_conserves_price():
    r=compiled();old=legacy(r);v=a.bridge_accounts(r,old,[credit(r,old)],additions=[addition(r,old)])
    assert v['project_direct_cost_usd']==cases(3600.)
    assert v['known_named_cost_subtotal_usd']==cases(1600.)
    assert v['credits'][0]['retained_cost_usd']==cases(2000.)
    assert not v['additive_to_existing_cost_ledger'] and not v['manufacturing_release']


def test_direct_parent_revision_requires_explicit_ancestry_and_credit():
    r=compiled();old=legacy(r,parent=True)
    assert a.bridge_accounts(r,old,[credit(r,old)],additions=[addition(r,old)])['project_direct_cost_usd']==cases(3600.)
    bad=credit(r,old);bad['ancestry']='same-candidate'
    with pytest.raises(ValueError,match='ancestry'):a.bridge_accounts(r,old,[bad])


def test_named_parts_cannot_be_added_on_top_of_legacy_residual():
    r=compiled()
    with pytest.raises(ValueError,match='uncredited legacy residual'):a.bridge_accounts(r,legacy(r),[])


@pytest.mark.parametrize('fault',['unrelated','legacy-source','source-evaluation','part','duplicate-part','ownership','reserve','credit-too-large','credit-erases-reserve','wrong-fleet'])
def test_mixed_or_duplicate_replacement_cannot_create_a_discount(fault):
    r=compiled();old=legacy(r);x=credit(r,old)
    if fault=='unrelated':old['candidate_id']=identity('unrelated');seal(old);x=credit(r,old)
    if fault=='legacy-source':x['legacy_account_sha256']=identity('other')
    if fault=='source-evaluation':x['cost_evaluation_id']=identity('other')
    if fault=='part':x['part_ids']=['motor']
    if fault=='duplicate-part':x['part_ids']=['sheet','sheet']
    if fault=='ownership':x['replaced_owner_ids']=['unrelated']
    if fault=='reserve':x['retained_owner_ids']=[]
    if fault=='credit-too-large':x['replacement_credit_usd']=cases(4000.)
    if fault=='credit-erases-reserve':x['replacement_credit_usd']=cases(3000.)
    if fault=='wrong-fleet':old['fleet']=8;seal(old);x=credit(r,old)
    with pytest.raises(ValueError):a.bridge_accounts(r,old,[x])


def test_unknown_legacy_rate_retains_hold_not_fake_complete_total():
    r=compiled();old=legacy(r);old['accounts'][0]['cost_usd']=cases(None);seal(old)
    v=a.bridge_accounts(r,old,[credit(r,old)])
    assert v['project_direct_cost_usd']==cases(None) and v['holds']
    assert v['known_named_cost_subtotal_usd']==cases(1600.)


def test_different_owner_name_alone_does_not_authorize_adding_new_bom_to_residual():
    r=compiled();old=legacy(r)
    v=a.bridge_accounts(r,old,[credit(r,old)])
    assert v['project_direct_cost_usd']==cases(None)
    assert any('explicit disjoint addition' in h for h in v['holds'])


@pytest.mark.parametrize('fault',['scope','overlap','repeat','revision'])
def test_addition_requires_whole_legacy_scope_and_unique_disjoint_parts(fault):
    r=compiled();old=legacy(r);x=addition(r,old)
    if fault=='scope':x['legacy_accounts_sha256']={}
    if fault=='overlap':x['part_ids']=['sheet']
    if fault=='repeat':x['part_ids']=['motor','motor']
    if fault=='revision':x['body_evaluation_id']=identity('different')
    with pytest.raises(ValueError):a.bridge_accounts(r,old,[credit(r,old)],additions=[x])


def test_overlapping_legacy_owners_and_duplicate_credits_rejected():
    r=compiled();old=legacy(r);old['accounts'].append({**deepcopy(old['accounts'][0]),'account_id':'duplicate-owner'});seal(old)
    with pytest.raises(ValueError,match='Overlapping'):a.bridge_accounts(r,old,[])
    old=legacy(r);x=credit(r,old)
    with pytest.raises(ValueError,match='Duplicate'):a.bridge_accounts(r,old,[x,x])
