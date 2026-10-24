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
