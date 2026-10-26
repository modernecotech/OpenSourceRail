from copy import deepcopy
import json
import pytest
from engineering.design_search import dfma as d

CID='1'*64


def graph():
    parts=[dict(id='roof-wall-'+str(i),mass_kg=2.,manufacturing_occurrence_id='roof-extrusion',
        functions=['roof_structure','pv_mount','cable_route','drainage','hvac_duct'],load_roles=['primary-structure'],
        process='extrusion',form='aluminium-extrusion') for i in range(4)]
    parts.append(dict(id='duct-module',mass_kg=None,manufacturing_occurrence_id='duct-module',
        functions=['hvac_duct'],load_roles=['service'],removable=True,removal_path=None))
    return dict(candidate_id=CID,parts=parts,joins=[dict(id='duct-flange',part_ids=['roof-wall-0','duct-module'],method='bolted',fastener_count=4)])


def test_actual_solid_rows_group_to_explicit_manufacturing_occurrences():
    r=d.evaluate(graph())
    assert r['geometric_stock_rows']==5 and r['declared_manufacturing_occurrences']==2
    assert r['resolved_manufactured_component_count']==2 and r['complete_vehicle_component_count'] is None
    assert r['labor']['fabrication']['operation_count']==2
    assert r['known_stock_mass_subtotal_kg']==8. and r['unknown_mass_stock_ids']==['duct-module']
    assert r['complete_installed_mass_kg'] is None and r['complete_installed_cost_USD'] is None
    integration=r['function_integration'][0]
    assert integration['roof_service_integration'] and len(integration['functions'])==5
    assert integration['net_cost_delta_USD'] is None and integration['net_installed_mass_delta_kg'] is None
    assert all(o['labor_h'] is None and o['tooling_cost_USD'] is None for o in r['operations'])
    assert r['economic_winner'] is None and not r['physical_accepted']


def test_missing_occurrence_grouping_and_row_mass_do_not_become_extra_components_or_zero():
    g=graph()
    for row in g['parts']:row.pop('manufacturing_occurrence_id')
    g['parts'][0]['quantity']=3
    r=d.evaluate(g)
    assert r['resolved_manufactured_component_count'] is None and len(r['unknown_occurrence_stock_ids'])==5
    assert r['known_stock_mass_subtotal_kg']==8. # mass_kg is already total per row, not multiplied again
    assert r['labor']['assembly']['complete_labor_h'] is None
    assert r['complete_tooling_cost_USD'] is None


def test_only_exact_source_bound_operation_hours_are_accounted(tmp_path):
    g=graph();op='fabricate:roof-extrusion'
    g['operations']=[dict(id=op,labor_h=99.)]
    unproven=d.evaluate(g,root=tmp_path)
    assert next(o for o in unproven['operations'] if o['id']==op)['labor_h'] is None
    record=dict(schema='osr-dfma-operation-evidence/1',candidate_id=CID,operation_id=op,
        part_ids=['roof-wall-'+str(i) for i in range(4)],basis='process-estimate',labor_h=1.25,elapsed_h=2.,tooling_cost_USD=None,
        fixture_scope='Synthetic test of receipt matching; not production evidence')
    p=tmp_path/'hours.json';p.write_text(json.dumps(record));g['operations'][0]['evidence']=dict(path='hours.json',sha256=d.digest(p))
    r=d.evaluate(g,root=tmp_path);out=next(o for o in r['operations'] if o['id']==op)
    assert out['labor_h']==1.25 and out['elapsed_h']==2. and out['tooling_cost_USD'] is None
    assert r['labor']['fabrication']['source_claimed_labor_h_subtotal']==1.25
    assert r['labor']['fabrication']['complete_labor_h'] is None
    record['candidate_id']='2'*64;p.write_text(json.dumps(record));g['operations'][0]['evidence']['sha256']=d.digest(p)
    with pytest.raises(ValueError,match='different candidate'):d.evaluate(g,root=tmp_path)


def test_integration_comparison_preserves_repair_consequences_and_unknown_net_savings():
    a=graph();b=dict(candidate_id='2'*64,parts=[],joins=[])
    for i,f in enumerate(['roof-structure','solar-mount','cable-route','drainage','hvac-duct']):
        b['parts'].append(dict(id='component-'+str(i),mass_kg=3.,manufacturing_occurrence_id='component-'+str(i),functions=[f],removable=i>0))
        if i:b['joins'].append(dict(id='attach-'+str(i),part_ids=['component-0','component-'+str(i)],method='bolted',fastener_count=None))
    r=d.compare(a,b)
    assert r['same_declared_function_tags'] and not r['functional_equivalence_verified']
    assert r['left']['function_integration'] and not r['right']['function_integration']
    assert r['declared_assembly_interface_difference']==3
    assert r['net_installed_mass_delta_kg'] is None and r['net_installed_cost_delta_USD'] is None and r['winner'] is None
    assert 'every listed function' in r['left']['function_integration'][0]['repair_coupling']


def test_duplicate_absent_parts_unmodelled_material_and_structural_clip_require_explicit_work():
    g=graph();g['parts'].append(deepcopy(g['parts'][0]))
    with pytest.raises(ValueError,match='Unique actual stock'):d.evaluate(g)
    g=graph();g['joins'][0]['part_ids'].append('missing-part')
    with pytest.raises(ValueError,match='existing distinct'):d.evaluate(g)
    with pytest.raises(ValueError,match='Registered component'):d.evaluate(graph(),{'roof-wall-0':'invented-material'})
    g=graph();g['joins'][0].update(method='clip-only',load_roles=['primary-structure'])
    r=d.evaluate(g)
    assert len(r['joint_holds'])==1 and not r['engineering_accepted']
    assert r['evaluation_id']==d.identity({n:v for n,v in r.items() if n!='evaluation_id'})
    g=graph();g['operations']=[dict(id='fabricate:roof-extrusion',prerequisites=['inspect:duct-flange'])]
    with pytest.raises(ValueError,match='cycle'):d.evaluate(g)
