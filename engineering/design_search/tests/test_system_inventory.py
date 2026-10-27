from copy import deepcopy
import json
import pytest
from engineering.design_search import system_inventory as inv,design_grammar as g,grammar_geometry as geometry,dfma


@pytest.fixture(scope='module')
def body():return g.build(g.parameters())


def test_actual_ebom_mbom_and_retained_geometry_coverage_stay_separate(body):
    r=inv.evaluate(body,bundle_id='1'*64)
    assert r['candidate_id']==r['bundle_id']=='1'*64 and r['body_candidate_id']==body['candidate_id']
    assert len(r['engineering_BOM'])==len(body['parts'])+len(body['joins'])+len(body['retained_equipment_accounts'])
    rows={x['id']:x for x in r['engineering_BOM']}
    assert rows[body['parts'][0]['id']]['geometry']['definition']==body['parts'][0]
    account=body['retained_equipment_accounts'][0]
    assert rows[account['id']]['accounted_mass_kg']==account['mass_kg'] and rows[account['id']]['geometry'] is None
    assert rows[body['joins'][0]['id']]['accounted_mass_kg'] is None
    assert r['accounted_empty_mass_kg']==pytest.approx(body['known_structure_stock_kg']+sum(x['mass_kg'] for x in body['retained_equipment_accounts']))
    assert 0<r['geometry_coverage']['located_fraction_of_accounted_mass']<1
    assert r['complete_installed_mass_kg'] is None and r['complete_installed_CG_m'] is None and r['complete_installed_inertia_kg_m2'] is None
    assert len(r['component_tasks'])>=len(body['joins'])+len(body['retained_equipment_accounts'])
    assert all(x['component_occurrence_id'] and x['required_artifacts'] for x in r['component_tasks'])
    rhs=next(cut for row in r['manufacturing_BOM'] for cut in row['nominal_cuts_and_blanks'] if cut['kind']=='hollow-section-cut')
    assert rhs['length_m']>0 and rhs['wall_m']>0 and rhs['end_mitre_or_clevis_geometry'] is None
    assert r['supply_coverage']['complete_installed_CAPEX_USD'] is None and r['economic_winner'] is None


def test_exact_body_projections_are_required_and_input_aliases_do_not_mutate_records(body):
    geo=geometry.mass_properties(body);manufacturing=dfma.evaluate(body)
    r=inv.evaluate(body,bundle_id='2'*64,geometry_record=geo,dfma_record=manufacturing)
    assert r['known_gross_stock_mass_properties']==geo
    bad=deepcopy(geo);bad['known_gross_stock_mass_kg']+=1
    with pytest.raises(ValueError,match='different body geometry'):inv.evaluate(body,bundle_id='2'*64,geometry_record=bad)
    bad=deepcopy(manufacturing);bad['candidate_id']='f'*64
    with pytest.raises(ValueError,match='different body'):inv.evaluate(body,bundle_id='2'*64,dfma_record=bad)
    altered=deepcopy(body);report=inv.evaluate(altered,bundle_id='3'*64);before=report['evaluation_id']
    altered['parts'][0]['functions'].append('after-evaluation-mutation')
    assert report['evaluation_id']==before==inv.identity({k:v for k,v in report.items() if k!='evaluation_id'})


def test_quote_coverage_requires_exact_bundle_component_currency_units_and_quantity(body,tmp_path):
    base=inv.evaluate(body,bundle_id='4'*64);part=base['engineering_BOM'][0]
    row=dict(schema='osr-system-supply-evidence/1',bundle_id='4'*64,component_occurrence_id=part['id'],
        component_definition_id=part['component_definition_id'],evidence_kind='supplier-quote',supplier='Synthetic test supplier',
        source_locator='Synthetic receipt matching test, not a commercial quotation',quantity_unit='kg',quoted_quantity=part['accounted_mass_kg'],
        unit_price_USD=2.,currency='USD',lead_time_days=12.)
    p=tmp_path/'quote.json';p.write_text(json.dumps(row));evidence=dict(path=p.name,sha256=inv.digest(p))
    r=inv.evaluate(body,bundle_id='4'*64,source_root=tmp_path,supply_evidence=[evidence])
    assert r['supply_coverage']['quoted_component_count']==1 and r['supply_coverage']['lead_time_known_count']==1
    assert r['supply_coverage']['known_quoted_stock_cost_subtotal_USD']==pytest.approx(2*part['accounted_mass_kg'])
    assert r['supply_coverage']['complete_installed_CAPEX_USD'] is None
    for field,bad in [('bundle_id','5'*64),('component_definition_id','6'*64),('currency','EUR'),('quoted_quantity',.0000001)]:
        wrong={**row,field:bad};p.write_text(json.dumps(wrong));evidence['sha256']=inv.digest(p)
        with pytest.raises(ValueError):inv.evaluate(body,bundle_id='4'*64,source_root=tmp_path,supply_evidence=[evidence])


def test_comparison_scope_and_material_supply_do_not_invent_properties(body):
    a=inv.evaluate(body,bundle_id='6'*64,comparison_context=dict(route='same-loop',service='same-demand'))
    b=inv.evaluate(body,bundle_id='7'*64,comparison_context=dict(route='different-loop',service='same-demand'))
    assert a['comparison_scope_id']!=b['comparison_scope_id']
    assert all(r['supply_evidence'] is None for r in a['engineering_BOM'])
    source=next(r for r in a['engineering_BOM'] if r.get('material_id')=='gfrp_skin_research')
    assert source['material_supply']['database_record'] is None and source['material_supply']['grade_allowables'] is None
    assert a['quantities']['installed_CAPEX_USD']['value'] is None
    with pytest.raises(ValueError,match='canonical bundle'):inv.evaluate(body,bundle_id='body-is-not-a-bundle')


def test_roof_rewrite_changes_real_inventory_but_preserves_retained_account_basis(body):
    roof=g.rewrite(body,'integrate-roof-functions',reason='Stock and process comparison test')
    a=inv.evaluate(body,bundle_id='8'*64);b=inv.evaluate(roof,bundle_id='9'*64)
    assert a['comparison_scope_id']==b['comparison_scope_id']
    assert a['body_candidate_id']!=b['body_candidate_id'] and a['manufacturing_BOM']!=b['manufacturing_BOM']
    assert a['quantities']['retained_accounted_equipment_kg']==b['quantities']['retained_accounted_equipment_kg']
    assert all(r['repair_removal_path'] is None and r['net_joint_cut_mass_kg'] is None for r in b['manufacturing_BOM'])
