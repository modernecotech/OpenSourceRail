"""Quantities and rates survive aggregation and the native input adapter."""
from copy import deepcopy
import math
import pytest
from engineering.ferrite_maglev import candidate_manufacturing as m
from osr_erpnext.maglev_manufacturing import stock_lines


def test_actual_candidate_module_mass_and_aggregated_valuation():
    candidate=m.magnetics.definition();rows=m.module_materials(candidate);grouped=m.aggregate(rows)
    assert len(grouped)<len(rows)
    assert math.isclose(sum(r['mass_kg'] for r in rows),candidate['module']['mass_kg'])
    assert sum(r['extended_cost_usd'] for r in rows)==pytest.approx(sum(r['extended_cost_usd'] for r in grouped))
    assert set(i for r in rows for i in r['geometry_part_ids'])==set(i for r in grouped for i in r['geometry_part_ids'])


def test_three_candidate_products_have_quantities_units_costs_and_current_identity():
    package=m.lifecycle_package();m.lifecycle.contract.validate_package(package)
    assert package['configuration_sha256']==m.magnetics.definition()['configuration_sha256']
    assert len(package['products'])==3 and not package['manufacturing_release']
    for p in package['products']:
        rows=stock_lines(p)
        actual=sum(r['quantity']*r['rate'] for r in rows)
        assert abs(actual-p['estimated_material_process_cost_usd'])<=sum(.001*r['engineering_unit_rate_usd']+.005*r['quantity'] for r in rows)+1e-7
        assert all(0<=r['native_quantity_increment']<.001 for r in rows)
        assert any(r['quantity']!=1 for r in rows)
        assert all(r['purchase_quantity']==4*r['quantity'] for r in rows)
        assert p['cut_schedule'] and p['complete_product_cost'] is False
    m.lifecycle.planning_bundle(package)


@pytest.mark.parametrize('mutation',['yield','rate','nan','release'])
def test_false_yield_valuation_and_release_refused(mutation):
    row=m.module_materials(m.magnetics.definition())[0];row=deepcopy(row)
    if mutation=='yield':row['purchase_quantity']*=2
    elif mutation=='rate':row['unit_rate_usd']*=2
    elif mutation=='nan':row['purchase_quantity']=float('nan')
    else:row['purchase_release']=True
    with pytest.raises(ValueError):m.validate_line(row)


def test_old_fixture_mode_is_not_relabelled_quantitative():
    p=m.lifecycle.lifecycle_package()['products'][0]
    assert all(r['quantity']==r['rate']==1 for r in stock_lines(p))


def test_explicit_section_span_changes_geometry_quantities_revision_and_lifecycle():
    candidate=m.magnetics.definition()
    reference=m.product_definition(candidate)
    shorter=m.product_definition(candidate,selection=dict(section_id='narrow-deep-reference',span_m=20.))
    wider=m.product_definition(candidate,selection=dict(section_id='wider-intermediate',span_m=25.))
    assert reference['selected_beam']==dict(section_id='narrow-deep-reference',span_m=25.)
    assert shorter['beam']['concrete_volume_m3']<reference['beam']['concrete_volume_m3']
    assert shorter['beam']['reaction_rail_and_attachment_steel_mass_kg']<reference['beam']['reaction_rail_and_attachment_steel_mass_kg']
    assert len({value['products'][1]['geometry_sha256'] for value in (reference,shorter,wider)})==3
    assert len({value['products'][1]['product_revision_sha256'] for value in (reference,shorter,wider)})==3
    package=m.lifecycle_package(candidate,selection=shorter['selected_beam'])
    assert package['configuration_sha256']==candidate['configuration_sha256']
    assert package['products'][1]==shorter['products'][1]
    assert package['positions'][1]['product_id']==shorter['products'][1]['product_id']
    geometry=m.civil_geometry(candidate,selection=shorter['selected_beam'])
    concrete=sum(part['volume_m3'] for part in geometry['parts'] if part['material']=='concrete')
    assert concrete==pytest.approx(shorter['beam']['concrete_volume_m3'])
    row=next(row for row in shorter['products'][1]['cut_schedule'] if row['component_scope']=='precast-concrete')
    assert set(row['geometry_part_ids'])=={'civil/'+part['id'] for part in geometry['parts'] if part['material']=='concrete'}


def test_foreign_beam_and_conflicting_architecture_are_rejected():
    candidate=m.magnetics.definition()
    beam=m.structures.selected_beam(candidate,selection=dict(section_id='narrow-deep-reference',span_m=20.))
    foreign=deepcopy(beam);foreign['configuration_sha256']='f'*64
    with pytest.raises(ValueError,match='configuration'):
        m.product_definition(candidate,beam=foreign)
    with pytest.raises(ValueError,match='differ'):
        m.product_definition(candidate,beam=beam,selection=dict(section_id='narrow-deep-reference',span_m=25.))
    counterfeit=deepcopy(beam);counterfeit['beam']['concrete_volume_m3']*=.5
    with pytest.raises(ValueError,match='quantities'):
        m.product_definition(candidate,beam=counterfeit)
    declared=deepcopy(candidate);declared['architecture']=dict(guidebeam=dict(section_id='wider-intermediate',span_m=25.))
    with pytest.raises(ValueError,match='architecture'):
        m.product_definition(declared,selection=dict(section_id='narrow-deep-reference',span_m=25.))


def test_unchanged_launch_stock_binds_new_candidate_and_refuses_mixed_source():
    candidate=m.magnetics.definition();source=candidate['configuration_sha256']
    revised=deepcopy(candidate);revised['configuration_sha256']='e'*64
    revised['source_candidate_configuration_sha256']=source
    rows,coil=m.launch_materials(revised)
    assert coil['configuration_sha256']==revised['configuration_sha256']
    assert coil['source_configuration_sha256']==source
    assert sum(row['mass_kg'] for row in rows)==pytest.approx(coil['total_mass_kg'])
    revised['propulsion_band']['mass_kg']+=1
    with pytest.raises(ValueError,match='propulsion source'):
        m.launch_materials(revised)
