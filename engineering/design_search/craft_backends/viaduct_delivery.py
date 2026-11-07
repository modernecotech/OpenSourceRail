"""Same-candidate nominal stock and declared civil cost accounts.

This adapter preserves the existing dated competition estimate. It does not
turn its primitive solids into fabricated pieces or add its allowances to a
second corridor budget. Native CAD/FEA changes evaluation evidence, not prices.
"""
from copy import deepcopy
import json
from math import fsum, isclose
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.design_search import civil_shape_geometry as geometry
from engineering.design_search import civil_shape_portfolio as portfolio

PRODUCER = 'engineering/design_search/craft_backends/viaduct_delivery.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, selected_reference_changed=False,
    manufacturing_release=False, operating_release=False,
    procurement_approved=False, movement_authority=False)
CASES = ('low', 'base', 'high')
HOLDS = {
    'reference_box': ['Removable inner core, tendon/anchorage access and casting/inspection access'],
    'ribbed_u': ['Bay mould removal, transverse-rib reinforcement and stripping sequence'],
    'variable_depth_box': ['Stepped transition reinforcement, core release and mould changeovers'],
    'folded_plate': ['Fold-corner reinforcement, cover, placement and temporary stability'],
    'load_following_ribs': ['Stepped rib transfer, reinforcement continuity and mould release'],
    'hybrid_steel_concrete': ['Shear connectors, weld details, deck erection and corrosion interfaces'],
}


def prepare(root=ROOT):
    root = Path(root)
    portfolio.verify(root=root)
    folder = root / portfolio.OUTPUT
    value = json.loads((folder / 'result.json').read_bytes())
    rows = {r['candidate_id']: r for r in value['evaluations']}
    if len(rows) != len(value['evaluations']):
        raise ValueError('Unique source civil candidates required')
    sources = {**value['source_sha256'], PRODUCER: digest(root / PRODUCER),
        portfolio.OUTPUT + '/result.json': digest(folder / 'result.json'),
        portfolio.OUTPUT + '/manifest.json': digest(folder / 'manifest.json')}
    result = dict(portfolio_id=value['portfolio_id'], rows=rows,
        source_sha256=sources, specification=value['specification'])
    result['context_id'] = identity(result)
    return result


def _owner(key):
    if key == 'rails_and_fastenings': return 'rail-and-fastener-interface'
    if key == 'supports_foundations_and_bearings_reserve': return 'shared-support-foundation-bearing-reserve'
    if key == 'site_services_reserve': return 'site-services-reserve'
    if key in ('transport', 'erection', 'site_labour'): return 'delivery-and-site-work'
    return 'structural-factory'


def build(definition, context=None, *, root=ROOT):
    geometry.validate(definition)
    context = prepare(root) if context is None else context
    if context.get('context_id') != identity({k:v for k,v in context.items() if k != 'context_id'}):
        raise ValueError('Civil delivery source context differs')
    q = geometry.quantities(definition)
    row = context['rows'].get(definition['candidate_id'])
    if row is None or row['quantities'] != q:
        raise ValueError('Civil delivery candidate or exact nominal quantities differ')
    if row.get('evaluation_id')!=identity({k:v for k,v in row.items() if k!='evaluation_id'}):
        raise ValueError('Retained civil cost-row evaluation identity differs')
    source_name=portfolio.OUTPUT+'/result.json';source_path=Path(root)/source_name
    if digest(source_path)!=context['source_sha256'].get(source_name):
        raise ValueError('Retained civil pricing source differs')
    canonical=json.loads(source_path.read_bytes())
    expected=next((r for r in canonical['evaluations'] if r['candidate_id']==definition['candidate_id']),None)
    if (canonical['portfolio_id']!=context['portfolio_id'] or row!=expected
            or context['specification']!=canonical['specification']):
        raise ValueError('Civil cost row is not the retained source evaluation')
    estimate = row['cost_estimate']
    if estimate['candidate_id'] != definition['candidate_id']:
        raise ValueError('Mixed civil cost candidate')
    stock = [dict(material_id=m, volume_m3=r['volume_m3'], nominal_stock_mass_kg=r['mass_kg'],
        density_kg_m3=definition['materials'][m]['density_kg_m3'], centroid_m=r['centroid_m'],
        quantity_scope='Nominal material account; not a fabricated component count')
        for m,r in q['by_material'].items()]
    rail_mass = 2 * 60.21 * definition['span_m']
    fasteners, fastening_mass = 70, 70 * 8.
    accounts, cost_cases = [], {}
    for cost in estimate['cases']:
        case = cost['case']
        declared = q['total_nominal_stock_mass_kg'] + cost['preliminary_reinforcement_kg'] + cost['unsized_prestress_reserve_kg'] + rail_mass + fastening_mass
        if not isclose(declared, cost['accounted_delivery_mass_kg'], rel_tol=1e-12, abs_tol=1e-7):
            raise ValueError('Civil mass/reserve accounts do not reconcile')
        accounts.append(dict(case=case, nominal_stock_kg=q['total_nominal_stock_mass_kg'],
            unlocated_reinforcement_allowance_kg=cost['preliminary_reinforcement_kg'],
            unlocated_prestress_allowance_kg=cost['unsized_prestress_reserve_kg'],
            rail_interface_kg=rail_mass, fastening_interface_kg=fastening_mass,
            accounted_delivery_mass_kg=declared, complete_installed_mass_kg=None,
            bearing_and_other_unlocated_hardware_mass_kg=None,
            basis='Existing preliminary quantities; unknown other hardware is not zero'))
        owned = {name: fsum(r[case] for k,r in estimate['line_items_iqd'].items() if _owner(k) == name)
            for name in ('structural-factory', 'rail-and-fastener-interface', 'delivery-and-site-work',
                         'shared-support-foundation-bearing-reserve', 'site-services-reserve')}
        residual = fsum(owned.values()) - cost['scoped_installed_iqd']
        if abs(residual) > 1.:
            raise ValueError('Owned civil cost accounts do not reconcile')
        cost_cases[case] = dict(**cost, owned_accounts_iqd=owned,
            rounding_residual_iqd=residual)
    groups = ([dict(id='concrete-deck', proposed_count=1), dict(id='steel-girders', proposed_count=2)]
        if definition['family'] == 'hybrid_steel_concrete'
        else [dict(id='integrated-precast-span', proposed_count=1)])
    process = [dict(sequence=i+1, operation=operation, status='provisional-method; not released')
        for i,operation in enumerate(estimate['process_route'])]
    value = dict(schema='osr-viaduct-candidate-delivery/1', candidate_id=definition['candidate_id'],
        canonical_quantity_evaluation_id=q['evaluation_id'], source_cost_evaluation_id=row['evaluation_id'],
        source_portfolio_id=context['portfolio_id'], source_context_id=context['context_id'],
        source_sha256=context['source_sha256'], nominal_stock=stock, mass_accounts=accounts,
        proposed_manufactured_groups=groups,
        component_count_basis='Proposed casting/girder groups; section cells and CAD regions are not separate manufactured parts',
        source_prism_count=sum(len(c['sections']) for c in definition['cells']),
        rail_interface=dict(profile='60.21 kg/m planning rail', rails=2, length_m_each=20.,
            fastener_sets=fasteners, assumed_kg_per_complete_set=8., interface_design_verified=False),
        process_route=process, formwork=dict(surface_proxy_m2=q['concrete_contact_surface_m2'],
            developed_mould_area_m2=None, release_and_curing_verified=False,
            reuse_hypothesis=context['specification']['rates']['form_reuses'],
            committed_identical_batch_count=None, production_capacity_verified=False),
        cost=dict(currency='IQD', estimate_class='C', cases=cost_cases,
            assumption_id=estimate['assumption_id'], competition_assumption_id=estimate['competition_assumption_id'],
            basis='Retained dated Iraqi benchmark and Class C process/interface proxies; not the newer China-origin city procurement scenario',
            scope=estimate['scope'], quotes_verified=False, reprice_performed=False,
            additive_to_city_or_corridor_budget=False,
            replacement_rule='Replace matching budget owners; never append this span total to corridor rail/support/erection accounts'),
        manufacturing_holds=HOLDS[definition['family']] + deepcopy(estimate['unresolved']) + [
            'Actual lifting radius, lifting points, rigging and temporary stability',
            'Shared support and span-end ownership before corridor aggregation'],
        business_draft=dict(doctype='BOM', item='OSR-RESEARCH-SPAN-'+definition['candidate_id'][:16],
            candidate_id=definition['candidate_id'], is_active=0, disabled=1, docstatus=0,
            transactions_performed=False, executable_work_order=False,
            material_budget_items=deepcopy(stock), unlocated_reserves_are_purchase_orders=False),
        outline_scope_complete=True, complete_installed_mass_kg=None,
        complete_installed_cost_iqd=None, **FLAGS)
    value['delivery_evaluation_id'] = identity(value)
    return value
