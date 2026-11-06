"""Delivery bindings and accounting controls; no native solvers or ERP writes."""
from copy import deepcopy
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from time import perf_counter
from types import ModuleType
import json
import os
import shutil
import sys

import pytest


HERE = Path(__file__).resolve().parents[1]
REFERENCE = Path(os.environ.get('OSR_CRAFT_REFERENCE_ROOT',HERE))
package = ModuleType('osr_craft_handoff_tests')
package.__path__ = [str(HERE/'engineering/design_search/craft_backends')]
sys.modules[package.__name__] = package
h = import_module(package.__name__+'.handoff')
c = import_module(package.__name__+'.cases')


@pytest.fixture(scope='module')
def records():
    return {v['case_id']:v for v in c.cases(REFERENCE)}


@pytest.fixture(scope='module')
def outputs(records):
    return {key:h.build(value,REFERENCE) for key,value in records.items()}


def test_complete_sidecars_for_four_cases_are_source_bound_and_unreleased(records,outputs):
    assert sum(len(v['occurrences']) for v in outputs.values()) == 25
    for key,value in outputs.items():
        case = records[key]
        for field in ('candidate_id','component_geometry_id','case_definition_id',
                      'source_candidate_id','source_evaluation_id','source_selection_id','source_study_id'):
            assert value[field] == case[field]
        assert value['handoff_id'] == c.identity({k:v for k,v in value.items() if k!='handoff_id'})
        assert all(value[k] is False for k in c.FLAGS)
        assert value['native_tools_executed'] is False
        assert value['erp_records_written'] is False
        assert value['quantities']['occurrence_count'] == case['expected']['part_count']
        for part in value['occurrences']:
            assert part['candidate_id'] == case['candidate_id']
            assert part['component_geometry_id'] == case['component_geometry_id']
            assert part['volume_m3'] == case['expected']['part_measures'][part['occurrence_id']]['volume_m3']
            assert part['material_mass_kg'] == case['expected']['part_material_masses_kg'][part['occurrence_id']]


def test_same_selected_packet_linked_by_hash_not_repriced(outputs):
    beam = outputs['selected-beam20m']; sill = outputs['selected-side-sill']
    assert beam['candidate_id'] == sill['candidate_id']
    assert beam['selected_delivery']['manifest_id'] == sill['selected_delivery']['manifest_id']
    roles = {link['role'] for link in beam['selected_delivery']['links']}
    assert {'engineering-bom','manufacturing','procurement','vehicle-cost','system-cost',
            'existing-interface-ifc','bim-scope'} <= roles
    for value in (beam,sill):
        accounting = value['cost_accounting']
        assert accounting['mode'] == 'reference-existing-only'
        assert accounting['additive_cost'] is False
        assert accounting['incremental_cost'] is None
        assert accounting['allocated_component_cost'] is None
        assert accounting['totals_recalculated'] is False
        assert all(p['allocated_component_cost'] is None for p in value['occurrences'])
        for link in value['selected_delivery']['links']:
            assert link['sha256'] == sha256((REFERENCE/link['path']).read_bytes()).hexdigest()
        assert value['selected_packet_scope']['complete_installed_BOM'] is False
        assert value['selected_packet_scope']['procurement_price_USD'] is None
        assert value['selected_packet_scope']['procurement_prices_current'] is False
        assert value['selected_packet_scope']['component_cost_allocation_complete'] is False
        assert value['selected_packet_scope']['production_shift_basis']['shifts'] == 2


def test_existing_cost_evaluation_and_line_ids_are_not_relabelled(outputs):
    value = outputs['selected-side-sill']
    assert value['selected_packet_scope']['system_evaluation_candidate_id'] != value['candidate_id']
    for part in value['occurrences']:
        links = part['existing_cost_line_links']
        assert len(links) == 2
        assert {link['role'] for link in links} == {'vehicle-cost','system-cost'}
        assert all(link['source_occurrence_id'] == part['occurrence_id'].removeprefix('source/') for link in links)
        system = next(link for link in links if link['role']=='system-cost')
        assert system['evaluation_candidate_id'] == value['selected_packet_scope']['system_evaluation_candidate_id']
    concrete = outputs['selected-beam20m']['occurrences']
    assert len({p['existing_cost_line_links'][0]['line_id'] for p in concrete}) == 1
    assert all('whole-route' in p['existing_cost_line_links'][0]['coverage'] for p in concrete)


def test_source_ifc_scope_is_not_a_new_complete_vehicle_export(outputs):
    value = outputs['selected-side-sill']
    link = next(l for l in value['selected_delivery']['links'] if l['role']=='existing-interface-ifc')
    assert link['complete_vehicle_IFC'] is False and link['complete_civil_IFC'] is False
    assert 'vehicle not modelled' in link['scope']
    assert 'no new case geometry' in link['relationship']


def test_material_regions_do_not_multiply_extrusions_or_monolithic_beams(outputs):
    beam = outputs['selected-beam20m']; sill = outputs['selected-side-sill']
    assert beam['quantities']['total_material_mass_kg'] == pytest.approx(55704.)
    assert sill['quantities']['total_material_mass_kg'] == pytest.approx(378.87968)
    for value in (beam,sill):
        routes = [p['stock_and_process_hypothesis'] for p in value['occurrences']]
        assert len({r['group_id'] for r in routes}) == 1
        assert all(r['purchase_stock_quantity'] is None for r in routes)
        assert all(r['labour_hours'] is None and r['machine_hours'] is None for r in routes)
        assert all(r['qualified_process'] is False for r in routes)


def test_shuttle_keeps_unknowns_and_does_not_inherit_selected_cost_or_ifc(outputs):
    value = outputs['research-launch-shuttle']
    assert value['selected_delivery'] is None
    assert 'selected_packet_scope' not in value
    assert value['source_selection_id'] is None
    assert value['candidate_id'] != outputs['selected-beam20m']['candidate_id']
    assert value['quantities']['total_material_mass_kg'] is None
    assert len(value['quantities']['unknown_material_mass_occurrences']) == 2
    assert value['quantities']['known_material_mass_subtotal_kg'] > 0
    assert value['cost_accounting']['selected_costs_inherited'] is False
    assert not any(name.startswith(h.EXPORTS+'/') for name in value['source_sha256'])
    assert all(p['existing_cost_line_links'] == [] for p in value['occurrences'])
    assert all(p['allocated_component_cost'] is None for p in value['occurrences'])
    missing = '\n'.join(value['missing_engineering_and_cost_scope'])
    assert 'independent braking' in missing and '30-year' in missing
    assert any('160000kg point mass' in a for a in value['assumptions'])


def test_installed_coordinates_not_exploded_render_offsets(outputs,records):
    case = records['selected-side-sill']; value = outputs['selected-side-sill']
    for part,source in zip(value['occurrences'],case['entities']):
        assert part['installed_geometry']['at_m'] == source['source_entity']['source_at_m']
        assert part['render_offset_applied'] is False
        assert part['installed_geometry'] == source['geometry']


def test_china_bulk_and_make_buy_policy_are_retained_without_extra_discount(outputs):
    for value in outputs.values():
        policy = value['supply_policy']
        assert policy['policy']['default_scenario'] == 'project-make-buy'
        assert 'no additional blanket discount' in policy['policy']['bulk_policy']
        assert 'once per production campaign' in policy['policy']['factory_policy']
        assert policy['additional_blanket_discount'] is None
        assert policy['factory_capital_allocation'] is None
        assert policy['cost_recalculated'] is False
        assert policy['comparison_evaluation_id']
        for name in (policy['policy_path'],policy['observations_path'],
                     policy['comparison_manifest_path'],policy['comparison_summary_path']):
            assert value['source_sha256'][name] == sha256((REFERENCE/name).read_bytes()).hexdigest()
        assert value['cost_accounting']['supply_comparison_is_selected_cost_replacement'] is False


@pytest.mark.parametrize('attack',['candidate','selection','component','exploded','physical','unknown-mass'])
def test_resealed_cross_binding_or_changed_geometry_cannot_enter_delivery(records,attack):
    value = deepcopy(records['research-launch-shuttle' if attack=='unknown-mass' else 'selected-side-sill'])
    if attack=='candidate':value['candidate_id']='a'*64
    elif attack=='selection':value['source_selection_id']='b'*64
    elif attack=='component':value['component_geometry_id']='c'*64
    elif attack=='exploded':value['entities'][0]['presentation_offset_applied']=True
    elif attack=='physical':value['physical_accepted']=True
    elif attack=='unknown-mass':value['expected']['total_material_mass_kg']=0
    value['case_definition_id']=c.identity({k:v for k,v in value.items() if k!='case_definition_id'})
    with pytest.raises(ValueError):h.build(value,REFERENCE)


def test_even_rehashed_delivery_packet_cannot_mix_candidates(records,outputs,tmp_path):
    value = records['selected-side-sill']
    refs = outputs['selected-side-sill']['source_sha256']
    for name in refs:
        source = HERE/name if (HERE/name).is_file() else REFERENCE/name
        target = tmp_path/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    name = h.EXPORTS+'/manufacturing.json'
    target = tmp_path/name
    record = json.loads(target.read_bytes()); record['candidate_id']='d'*64
    target.write_text(json.dumps(record))
    manifest_path = tmp_path/(h.EXPORTS+'/manifest.json')
    manifest = json.loads(manifest_path.read_bytes())
    manifest['files_sha256']['manufacturing.json']=sha256(target.read_bytes()).hexdigest()
    manifest['manifest_id']=c.identity({k:v for k,v in manifest.items() if k!='manifest_id'})
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='Mixed manufacturing candidate_id'):
        h.build(value,tmp_path)


def test_fresh_four_case_delivery_build_is_bounded_and_repeatable(records,outputs):
    start = perf_counter()
    fresh = {key:h.build(value,REFERENCE) for key,value in records.items()}
    assert fresh == outputs
    assert perf_counter()-start < 5.


def test_shared_source_catalogue_does_not_bind_research_to_selected_exports():
    refs = h.sources(REFERENCE)
    assert h.PRODUCER in refs and h.POLICY in refs
    assert not any(name.startswith(h.EXPORTS+'/') for name in refs)
