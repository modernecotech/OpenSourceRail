from copy import deepcopy
from decimal import Decimal as D
import json

import pytest

from engineering.sourcing.manufacturing import laminate_requirements, throughput_upper_bound, crane_screen, compare_raw_material_costs, example_buildups
from engineering.sourcing.model import identity, validate_record

C='a'*64;I='b'*64;S='c'*64;F='d'*64


def laminate(**changes):
    args=dict(candidate_id=C,input_id=I,area_m2='10',plies=[dict(areal_weight_g_m2='600',count=2,fabric_width_m='1.27',material_key='glass')],fibre_mass_fraction='0.5',scrap_fraction='0.1',resin_includes_hardener=True,functional_basis_id=F,source_ids=[S])
    args.update(changes);return laminate_requirements(**args)


def test_mass_fraction_and_gross_yield_are_not_volume_or_markup():
    p=laminate();rows={r['material_key']:r for r in p['material_rows']}
    assert p['dry_glass_net_kg']=='12' and p['mixed_matrix_net_kg']=='12'
    assert D(rows['glass']['gross_mass_kg'])==D('12')/D('.9')
    assert D(rows['glass']['gross_mass_kg'])!=D('12')*D('1.1')
    assert D(rows['glass']['net_length_m'])==D('20')/D('1.27')
    assert rows['mixed-resin-kit']['scope']=='resin-and-included-hardener'
    assert all(r['procurement_scope']=='raw-material' for r in p['material_rows'])
    assert p['candidate_id']==C and p['input_id']==I and p['complete_installed_mass_kg'] is None


def test_unknown_material_process_and_mass_quantities_are_not_zero():
    p=laminate(resin_includes_hardener=False)
    rows={r['material_key']:r for r in p['material_rows']}
    assert rows['base-resin']['net_mass_kg'] is None and rows['catalyst']['net_mass_kg'] is None
    assert rows['core']['gross_mass_kg'] is None and rows['adhesive']['gross_mass_kg'] is None
    assert p['labour_hours'] is None and p['mould_cycle_hours'] is None
    assert p['conditional_material_mass_bounds_kg']['upper'] is None
    assert 'matrix:base-resin-and-catalyst-purchase-split' in p['unknown_additional_quantities']


def test_catalyst_split_preserves_declared_total_mixed_matrix():
    p=laminate(resin_includes_hardener=False,catalyst_ratio='.02')
    rows={r['material_key']:r for r in p['material_rows']}
    assert D(rows['base-resin']['net_mass_kg'])+D(rows['catalyst']['net_mass_kg'])==D(p['mixed_matrix_net_kg'])
    assert p['conditional_known_net_material_kg']=='24'
    with pytest.raises(ValueError,match='Included hardener'):laminate(catalyst_ratio='.02')


def test_core_bondlines_and_removed_consumables_have_distinct_scopes():
    p=laminate(core=dict(thickness_m='.02',density_kg_m3='80'),adhesive=dict(mass_per_area_kg_m2='.1',coverage_count=2),consumables=[dict(material_key='bagging-film',quantity='20',quantity_unit='m2')],labour_hours='4',mould_cycle_hours='24')
    assert p['conditional_known_net_material_kg']=='42'
    film=p['material_rows'][-1];assert film['retained_in_part'] is False and film['installed_mass_kg']=='0'
    assert p['complete_installed_mass_kg'] is None and p['mechanical_compliance'] is None


def test_published_core_density_range_propagates_without_overstating_complete_mass():
    p=laminate(core=dict(thickness_m='.02',density_kg_m3='85',density_range_kg_m3=['81','89']))
    assert p['conditional_known_net_material_kg']=='41'
    assert p['conditional_known_net_material_bounds_kg']['lower']=='40.2'
    assert p['conditional_known_net_material_bounds_kg']['nominal']=='41'
    assert p['conditional_known_net_material_bounds_kg']['upper']=='41.8'
    assert p['conditional_material_mass_bounds_kg']['lower']=='40.2'
    assert p['conditional_material_mass_bounds_kg']['upper'] is None
    with pytest.raises(ValueError,match='within its published range'):
        laminate(core=dict(thickness_m='.02',density_kg_m3='80',density_range_kg_m3=['81','89']))


def test_partially_defined_material_geometry_is_preserved_with_unknown_mass():
    p=laminate(core=dict(thickness_m='.02',density_kg_m3=None),adhesive=dict(product_key='unquoted-bond'))
    rows={r['material_key']:r for r in p['material_rows']}
    assert rows['core']['gross_mass_kg'] is None and rows['core']['declared_material_input']['thickness_m']=='.02'
    assert rows['adhesive']['net_mass_kg'] is None
    assert p['conditional_known_net_material_kg']=='24'


@pytest.mark.parametrize('changes',[
    dict(area_m2=0),dict(fibre_mass_fraction=0),dict(fibre_mass_fraction=1),dict(scrap_fraction=1),dict(scrap_fraction=-.1),
    dict(plies=[dict(areal_weight_g_m2='600',count='1.5')]),dict(candidate_id='wrong'),dict(source_ids=[S,S]),
    dict(core=dict(not_required=True)),dict(resin_includes_hardener=None,catalyst_ratio='.02'),dict(fibre_mass_fraction=float('nan')),
])
def test_invalid_or_unbound_inputs_rejected(changes):
    with pytest.raises(ValueError):laminate(**changes)


def test_declared_parameters_bind_the_record_and_decimal_inputs_serialize():
    original=[dict(areal_weight_g_m2=D('600'),count=2,orientation_deg=[D('-45'),D('45')])];saved=deepcopy(original)
    a=laminate(plies=original,area_m2=D('10'));b=laminate(plies=original,area_m2=D('11'))
    assert original==saved and a['record_id']!=b['record_id'];json.dumps(a);validate_record(a,'process')


def test_casting_rate_is_only_a_ceiling_and_product_transfer_remains_unverified():
    a=throughput_upper_bound(C,I,'2.7','20','8',machine_application='hollow-core-slab',product_application='railway-girder')
    assert a['casting_only_upper_bound_length_m']=='1296' and a['casting_only_upper_bound_units']==64
    assert a['complete_output_units'] is None and a['conditional_steady_state_units_per_shift_upper_bound'] is None
    assert a['application_compatibility']=='unverified-product-process-transfer'
    b=throughput_upper_bound(C,I,'2.7','20','8',machine_application='hollow-core-slab',product_application='hollow-core-slab',cure_hours='24',bed_length_m='120',mould_count=6,crew_count=2,labour_hours_per_unit=1,turnaround_hours=2)
    assert D(b['conditional_steady_state_units_per_shift_upper_bound'])<64 and b['complete_output_units'] is None


def config():
    return dict(crane_model='test-fixture',boom_length_m='30',counterweight_kg='22500',outrigger_setup='full-test',slew_sector='test-sector',reeving_parts=4,chart_revision='fixture-not-physical-evidence')


def test_crane_headline_maximum_cannot_be_used_at_another_radius():
    a=crane_screen(C,I,'40000',radius_m='20')
    assert a['chart_capacity_screen'] is None and a['lift_approved'] is False
    with pytest.raises(ValueError,match='Complete load-chart'):crane_screen(C,I,'40000',radius_m=20,configuration={'crane_model':'100t headline'})
    point=dict(radius_m='10',capacity_kg='100000',configuration=config(),source_id=S)
    with pytest.raises(ValueError,match='Exact operating-radius'):crane_screen(C,I,'40000',radius_m=20,configuration=config(),chart_point=point,source_ids=[S])


def test_exact_chart_point_can_screen_capacity_but_never_approve_lift():
    point=dict(radius_m=D('10'),capacity_kg='50000',configuration=config(),source_id=S)
    a=crane_screen(C,I,'40000',radius_m='10',configuration=config(),chart_point=point,source_ids=[S],rigging_mass_kg='2000',dynamic_factor='1.1',hook_height_m=D('15'))
    assert a['factored_hook_demand_kg']=='46200' and a['chart_capacity_screen'] is True and a['lift_approved'] is False
    assert a['ground_assessment_id'] is None;json.dumps(a)
    over=crane_screen(C,I,'60000',radius_m='10',configuration=config(),chart_point=point,source_ids=[S])
    assert over['chart_capacity_screen'] is False and over['factored_hook_demand_kg'] is None


def test_material_comparison_holds_unknown_prices_and_requires_same_service_basis():
    a=laminate();b=laminate(candidate_id='e'*64,fibre_mass_fraction='.6')
    none=compare_raw_material_costs([a,b],{})
    assert all(r['known_material_subtotal'] is None and r['declared_material_total'] is None for r in none['results'])
    priced=compare_raw_material_costs([a,b],{'glass':dict(unit='m',unit_price='3.13',currency='GBP',source_id=S)})
    assert all(r['known_material_subtotal'] is not None and r['declared_material_total'] is None for r in priced['results'])
    assert priced['qualified_selection'] is None and priced['procurement_winner'] is None
    with pytest.raises(ValueError,match='Same explicit functional'):compare_raw_material_costs([a,laminate(area_m2=11)],{})
    with pytest.raises(ValueError,match='Same currency'):compare_raw_material_costs([a,b],{'glass':dict(unit='m',unit_price='1',currency='USD',source_id=S)})


def test_three_demo_builds_are_explicit_hypotheses_with_new_ids():
    cases=example_buildups();assert len(cases)==3 and len({c['candidate_id'] for c in cases})==3
    assert len({c['functional_basis_id'] for c in cases})==1
    assert all(c['physical_accepted'] is False and c['complete_installed_cost'] is None for c in cases)
