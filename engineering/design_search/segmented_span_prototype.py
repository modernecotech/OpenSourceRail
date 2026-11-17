"""Candidate-bound prototype planning packet for the retained segmented span.

This compiles an existing immutable calculation; it does not solve a joint,
temporary stage, foundation or installed price.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('docs/design-engine/v07-affordable-corridor/evidence/civil-20261117-box20-segmented-001')
OUTPUT = Path('docs/design-engine/v07-segmented-span/plan.json')
COST_OUTPUT = Path('docs/design-engine/v07-segmented-span/cost-handoff.json')
SCHEMA = 'osr-v07-segmented-span-prototype-plan/1'
CANDIDATE = 'abcf7e942fd1337c9872869d684ac9a8055ce94bd3e9c35de0dbcbe07f49ac82'
SOURCE_MANIFEST_SHA256 = '263776c13f7fed60e1b18359eb11ade3cd6f345b6db641439489ca7f21e01470'


def encoded(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def source(root: Path) -> tuple[dict, dict, dict]:
    folder = root / SOURCE
    if digest(folder / 'manifest.json') != SOURCE_MANIFEST_SHA256:
        raise ValueError('Civil source manifest differs from admitted evaluation')
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    for name in ('input.json', 'result.json'):
        if digest(folder / name) != manifest['files_sha256'][name]:
            raise ValueError('Civil source packet changed: ' + name)
    request = json.loads((folder / 'input.json').read_bytes())
    result = json.loads((folder / 'result.json').read_bytes())
    if (result['candidate_id'] != CANDIDATE
            or manifest['physical_candidate_id'] != CANDIDATE
            or result['evaluation_id'] != manifest['evaluation_id']
            or result['input_id'] != request['input_id']
            or request['input_id'] != manifest['input_id']):
        raise ValueError('Civil candidate, evaluation or input identity differs')
    if request['input_id'] != sha256(encoded({k: v for k, v in request.items() if k != 'input_id'})).hexdigest():
        raise ValueError('Civil source input identity differs')
    if result['physical_accepted'] is not False or result['selected_reference_changed'] is not False:
        raise ValueError('Research candidate cannot inherit physical acceptance')
    physical = result['physical_definition']
    if (request['requirements']['span_m'], physical['piece_length_m'],
            physical['pieces_per_span'], physical['beam_family']) != (20, 10, 2, 'box-beam'):
        raise ValueError('Unexpected physical span revision')
    return manifest, request, result


def build(root: Path = ROOT) -> dict:
    root = Path(root)
    manifest, request, result = source(root)
    physical = result['physical_definition']
    counts = {name: result['counts'][name] for name in ('pilot_1p5km', 'demonstrator_2km')}
    each = counts['demonstrator_2km']
    if (each['beam_spans'], each['ten_m_segments'], each['independent_supports'], each['bearings']) != (200, 400, 202, 800):
        raise ValueError('Two-kilometre construction quantity basis differs')
    study = result['beam_whole_span_model']
    joint_stations = [row for row in study['local_envelope'] if row['x_m'] == 10.0]
    if len(joint_stations) != 1 or len(study['local_envelope']) != 41:
        raise ValueError('Whole-beam local moving-load envelope coverage differs')
    peak_station = max(study['local_envelope'], key=lambda row: row['max_live_moment_Nm'])
    lift = result['lifting_transport']
    foundation = result['foundation']
    if any(x is not None for x in (result['cost']['candidate_complete_installed_cost_iqd'],
                                   result['cost']['candidate_complete_installed_cost_usd'],
                                   study['segmented_candidate_structural_pass'])):
        raise ValueError('Unmeasured span acceptance or installed cost cannot be inherited')
    plan = {
        'schema': SCHEMA,
        'purpose': 'prototype-production quotation and controlled test planning',
        'maturity': 'prototype planning; fabrication dimensions and qualification held',
        'physical_candidate_id': CANDIDATE,
        'source_evaluation_id': result['evaluation_id'],
        'source_input_id': request['input_id'],
        'selected_vehicle_candidate_id': request['ancestry']['vehicle_candidate_id'],
        'selected_reference_changed': False,
        'physical_accepted': False,
        'manufacturing_release': False,
        'operating_release': False,
        'source_sha256': {str(SOURCE / name): digest(root / SOURCE / name)
                          for name in ('input.json', 'result.json', 'manifest.json')}
                         | {'engineering/design_search/segmented_span_prototype.py': digest(Path(__file__))},
        'physical_scope': {
            'span_m': 20, 'pieces_per_beam': 2, 'nominal_piece_m': 10,
            'joint_closure_m_hypothesis': 0.002,
            'bearing_units_per_beam': physical['bearing_sets_per_beam'],
            'track_centres_y_m': physical['track_centres_y_m'],
            'footing_m_hypothesis': [physical['footing_length_m'], physical['footing_width_m'], physical['footing_thickness_m']],
            'pier_height_m_hypothesis': physical['pier_height_m'],
            'pier_section_area_m2_hypothesis': physical['pier_area_m2'],
            'joint_and_tendon_structural_design': None,
            'site_foundation_design': None,
        },
        'calculated_screens': {
            'whole_beam_only': {
                'maximum_live_moment_Nm': study['maximum_live_moment_Nm'],
                'maximum_live_moment_section_x_m': peak_station['x_m'],
                'nominal_joint_plane_x_m': 10.0,
                'nominal_joint_plane_local_envelope': joint_stations[0],
                'maximum_service_compression_Pa': study['maximum_service_compression_Pa'],
                'maximum_service_tension_Pa': study['maximum_service_tension_Pa'],
                'maximum_transfer_compression_Pa': study['maximum_transfer_compression_Pa'],
                'maximum_transfer_tension_Pa': study['maximum_transfer_tension_Pa'],
                'deflection_upper_bound_m': study['source_deflection_upper_bound_m'],
                'dynamic_factor_applied_once': study['dynamic_factor_applied_once'],
                'segmented_joint_or_erection_pass': None,
            },
            'handling_hypothesis': {
                'piece_bare_kg': lift['half_segment_bare_kg_hypothesis'],
                'hook_kg_including_rigging_and_contingency': lift['half_required_hook_kg_hypothesis'],
                'crane_chart_kg_at_12m_hypothesis': request['lifting_hypothesis']['chart_capacity_kg_at_radius'],
                'road_payload_kg_hypothesis': request['lifting_hypothesis']['road_payload_kg'],
                'certified_chart_and_transport_permit': None,
            },
            'footing_gravity_only': {
                'pressure_kPa_under_200kPa_soil_hypothesis': foundation['gravity_closed_soil_pressure_kPa_hypothesis'],
                'required_area_m2_at_200kPa_hypothesis': foundation['necessary_minimum_areas_m2_by_soil_kPa']['200.0'],
                'required_area_m2_at_100kPa_hypothesis': foundation['necessary_minimum_areas_m2_by_soil_kPa']['100.0'],
                'settlement_lateral_uplift_seismic_and_tower_pad_checks': None,
            },
        },
        'engineering_checks': {
            'moving_load': {'source': 'whole 20 m continuous box under retained crowd control and +250 kg/car reserve',
                            'whole_beam_envelope_calculated': True, 'segmented_joint_screen': None},
            'torsion': {'status': 'held', 'required_actions': ['unequal track/rail loading', 'walkway eccentricity',
                                                               'braking and lateral actions', 'wind'],
                        'measured_twist_rad': None},
            'prestress_transfer': {'status': 'held for keyed closure and tower-restrained stages',
                                   'joint_tendon_force_N': None, 'anchor_zone_capacity_N': None},
            'handling': {'status': 'necessary mass screen only', 'lifting_attachment_capacity_N': None,
                         'actual_crane_capacity_at_measured_radius_kg': None},
            'temporary_stability': {'status': 'held for stages S1 through S4',
                                    'tower_reaction_N': None, 'tower_pad_pressure_kPa': None},
            'foundation': {'status': 'gravity-only pressure screen at hypothetical soil capacity',
                           'site_allowable_pressure_kPa': None, 'settlement_m': None,
                           'lateral_uplift_seismic_and_scour_screen': None},
            'deformation_feedback': {'selected_running_support': 'passive steel wheels; no selected magnetic support gap',
                                     'whole_beam_deflection_upper_bound_m': study['source_deflection_upper_bound_m'],
                                     'measured_joint_twist_creep_and_settlement_m': None,
                                     'future_LIM_or_magnetic_clearance_input': 'measured deformation required; no unselected gap limit assumed'},
        },
        'straight_span_quantities': counts,
        'interfaces': [
            {'id': 'segment-joint', 'datum': 'x=10 m nominal span midpoint',
             'known': 'two nominal 10 m pieces and 2 mm closure hypothesis',
             'controlled_shop_length_m': None, 'approved_tolerance_m': None,
             'hold': 'Reconcile cut lengths, 2 mm closure and end-bearing datums before mould release; detail keys, shear transfer, ducts, tendon force and anchor zones.'},
            {'id': 'beam-bearing-pier', 'datum': 'four bearing units counted per beam',
             'known': '20 m nominal span; independent support lines at y=-1.6 m and +1.6 m',
             'bearing_seat_xyz_m': None, 'approved_tolerance_m': None,
             'hold': 'Define bearing centres, restraint directions, reactions, rotation, replacement jacks and pier seat reinforcement.'},
            {'id': 'rail-guideway', 'datum': 'rail running surface and beam longitudinal axis',
             'known': '70 direct-fastener sets per 20 m beam in quantity model',
             'rail_and_fastener_xyz_m': None, 'approved_tolerance_m': None,
             'hold': 'Survey rail/beam datums, fastening pitch and installation envelope; check wheel, launch equipment and evacuation clearance.'},
            {'id': 'temporary-tower', 'datum': 'nominal midspan under each active segmented beam',
             'known': 'one temporary tower placement per beam in quantity model',
             'tower_geometry_and_foundation': None, 'approved_tolerance_m': None,
             'hold': 'Design tower foundation, bracing, head restraint, reaction path and monitored release; avoid joint/duct interference.'},
            {'id': 'lifting-and-haul', 'datum': 'one 10 m segment; four-sling concept',
             'known': '29.592 t bare and 34.201 t provisional hook hypotheses',
             'lifting_insert_xyz_m': None, 'approved_tolerance_m': None,
             'hold': 'Design attachments, segment handling stresses, restraints, road axle loads and crane configuration at measured radius.'},
            {'id': 'station-transition', 'datum': 'first nonstandard station/guideway support',
             'known': 'straight-span counts exclude station/crossover structure',
             'station_support_geometry': None, 'approved_tolerance_m': None,
             'hold': 'Separate platform, launch/brake, utilities, evacuation and station support loads from standard span.'},
        ],
        'erection_stages': [
            {'id': 'S0', 'load_path': 'site soil -> approved footing/pier and separate braced tower pad',
             'release_evidence': 'geotechnical profile, footing and tower-pad design, access and crane standing ground'},
            {'id': 'S1', 'load_path': 'first 10 m segment -> end bearing and braced temporary tower',
             'release_evidence': 'lifting insert proof, temporary reaction, lateral/torsional stability and survey'},
            {'id': 'S2', 'load_path': 'both segments -> two end bearings and temporary tower; joint not yet structural',
             'release_evidence': 'joint fit, unbalanced lift/wind case, bearing reactions and tower restraint'},
            {'id': 'S3', 'load_path': 'closed joint and tensioned tendons -> supported segmented beam plus tower',
             'release_evidence': 'cure, tendon force/elongation, anchorage zone and prop-restrained prestress transfer'},
            {'id': 'S4', 'load_path': 'controlled tower unloading -> end bearings, piers and footings',
             'release_evidence': 'measured reactions, camber, crack state, twist and rail datum after release'},
            {'id': 'S5', 'load_path': 'rail, train and access actions -> jointed beam, bearings, supports and soil',
             'release_evidence': 'moving load, torsion, fatigue, braking, wind, settlement and monitored proof test'},
        ],
        'prototype_qa_gates': [
            {'id': 'Q1', 'item': 'match-cast mould, cage and ducts', 'record': 'survey datums, material lots, bar/duct cover and dimensional inspection'},
            {'id': 'Q2', 'item': 'handling and delivery', 'record': 'concrete release strength, insert proof, mass, restraint, road permit and crane chart'},
            {'id': 'Q3', 'item': 'joint and tensioning', 'record': 'face profile, closure, epoxy batch/cure, tendon force/elongation and anchor inspection'},
            {'id': 'Q4', 'item': 'tower release', 'record': 'staged reaction, displacement, camber, twist, cracking and bearing seat survey'},
            {'id': 'Q5', 'item': 'span proof and maintenance baseline', 'record': 'load positions, deformation, strain, rail gauge and repeat survey schedule'},
        ],
        'supplier_quote_schedule_2km': [
            {'item': '10 m precast segment stock and handling inserts; joint assembly excluded', 'quantity': each['ten_m_segments'], 'unit': 'segment', 'unit_quote_iqd': None},
            {'item': 'match-cast structural joint and continuous post-tension package', 'quantity': each['beam_spans'], 'unit': 'jointed beam', 'unit_quote_iqd': None},
            {'item': 'temporary tower installation, monitoring and removal', 'quantity': each['temporary_tower_placements'], 'unit': 'placement', 'unit_quote_iqd': None},
            {'item': 'certified segment lift at measured radius', 'quantity': each['required_piece_lifts'], 'unit': 'lift', 'unit_quote_iqd': None},
            {'item': 'pier, foundation and geotechnical work', 'quantity': each['independent_supports'], 'unit': 'support', 'unit_quote_iqd': None},
            {'item': 'bearing and replaceable restraint assembly', 'quantity': each['bearings'], 'unit': 'unit', 'unit_quote_iqd': None},
            {'item': 'direct rail fastener set', 'quantity': each['direct_fastener_sets'], 'unit': 'set', 'unit_quote_iqd': None},
            {'item': 'rail stock', 'quantity': each['rail_stock_m'], 'unit': 'm', 'unit_quote_iqd': None},
            {'item': 'rail butt weld and inspection', 'quantity': each['field_butt_welds_for_20m_rail_stock_hypothesis'], 'unit': 'weld', 'unit_quote_iqd': None},
            {'item': 'continuous protected access', 'quantity': each['continuous_protected_access_track_m_required'], 'unit': 'track-m', 'unit_quote_iqd': None},
        ],
        'cost_status': {
            'candidate_complete_installed_cost_iqd': None,
            'unsegmented_whole_beam_30km_class_C_proxy_iqd': result['cost']['fresh_unsegmented_line30_civil_class_C_proxy_iqd'],
            'proxy_is_not_this_candidate_price': True,
            'unpriced_scopes': ['joint', 'tower and release', 'extra crane cycles', 'bearings design', 'site ground and access',
                                'station transitions', 'drainage and utilities', 'QA and rework', 'maintenance and replacement'],
        },
        'mandatory_next_tests': result['next_measurements'],
    }
    plan['plan_id'] = sha256(encoded(plan)).hexdigest()
    return plan


def build_cost_handoff(root: Path = ROOT) -> dict:
    """Quote quantities and substitution rules, with no inferred installed total."""
    root = Path(root)
    plan = build(root)
    if (root / OUTPUT).read_bytes() != encoded(plan):
        raise ValueError('Civil prototype plan differs before cost handoff')
    _, _, result = source(root)
    two = result['counts']['demonstrator_2km']
    route = result['counts']['route']
    proxy = result['cost']
    if (two['route_m'], route['route_m']) != (2000, 30000):
        raise ValueError('Civil quote route lengths differ')

    def row(name, key, unit, treatment, overlap, quote):
        return dict(item=name, quantity_2km=two[key], quantity_30km=route[key], unit=unit,
                    cost_treatment=treatment, baseline_overlap=overlap,
                    supplier_input=quote, unit_quote_iqd=None, baseline_credit_iqd=None,
                    delta_iqd=None, supplier=None, local_value_added_fraction=None)

    rows = [
        row('complete segmented beam factory package', 'beam_spans', 'beam', 'replace',
            'whole-beam factory, prestress/anchor and end-joint allowances',
            'Quote two segment stocks, match-cast structural joint, tendons, anchors, inserts, cure, QA and rejection allowance as one beam package.'),
        row('segment stock breakdown only', 'ten_m_segments', 'segment', 'breakdown_only',
            'inside complete segmented beam factory package',
            'Disclose material, cage, form, casting and handling-insert component of the complete beam quote; do not add again.'),
        row('joint and tendon breakdown only', 'beam_spans', 'joint', 'breakdown_only',
            'inside complete segmented beam factory package',
            'Disclose key/epoxy/duct/tendon/anchor, tension and inspection component; do not add again.'),
        row('certified segment crane lift', 'required_piece_lifts', 'lift', 'replace',
            'whole-beam crane erection allowance',
            'Measured radius, hook load, rigging, crane chart, paid hours, mats and standby.'),
        row('temporary tower placement and release', 'temporary_tower_placements', 'placement', 'increment',
            'no qualified tower in whole-beam base',
            'Tower/pad design, installation, bracing, monitoring, release and removal.'),
        row('pier and site foundation', 'independent_supports', 'support', 'replace',
            'gravity-minimum footing/pier proxy',
            'Geotechnical-selected footing/pile, pier, bearing seat, excavation, groundwater and seismic/lateral checks.'),
        row('bearing and restraint unit', 'bearings', 'unit', 'replace',
            'Class C four-pad-per-beam allowance',
            'Supplier bearing, anchor, restraint, QA and replacement-jack interface.'),
        row('rail stock', 'rail_stock_m', 'm', 'replace',
            'whole-beam rail stock allowance', 'Rail section, transport, handling and installed geometry.'),
        row('direct fastener set', 'direct_fastener_sets', 'set', 'replace',
            'whole-beam direct-fastener allowance', 'Fastener, pad, insulation, anchor and installation/inspection.'),
        row('rail butt weld and inspection', 'field_butt_welds_for_20m_rail_stock_hypothesis', 'weld', 'replace',
            '20 m stock-length field-weld allowance', 'Weld procedure, operator, NDT, rework and possessions.'),
        row('continuous protected access', 'continuous_protected_access_track_m_required', 'track-m', 'replace_or_add_after_scope_audit',
            '30 km nonstation walkway proxy; 2 km coverage unconfirmed',
            'Accessible protected route, fixings, drainage, guard and inspection access.'),
    ]
    foot_delta_30 = proxy['selected_3m_footing_additional_concrete_and_rebar_proxy_iqd']
    foot_delta_2 = foot_delta_30 * two['independent_supports'] / route['independent_supports']
    handoff = {
        'schema': 'osr-v07-segmented-span-cost-handoff/1',
        'purpose': 'candidate-specific supplier and site quote input; no installed price inferred',
        'physical_candidate_id': plan['physical_candidate_id'],
        'selected_vehicle_candidate_id': plan['selected_vehicle_candidate_id'],
        'civil_source_evaluation_id': plan['source_evaluation_id'],
        'civil_plan_id': plan['plan_id'],
        'civil_plan_sha256': digest(root / OUTPUT),
        'selected_reference_changed': False,
        'physical_accepted': False,
        'manufacturing_release': False,
        'quote_rows': rows,
        'site_specific_open_rows': [
            {'item': 'geotechnical investigation and ground improvement', 'quantity_2km': None, 'quantity_30km': None,
             'unit_quote_iqd': None, 'reason': 'alignment, boreholes, groundwater and foundation family not surveyed'},
            {'item': 'station, terminal and crossover civil interface', 'quantity_2km': None, 'quantity_30km': None,
             'unit_quote_iqd': None, 'reason': 'straight-span arithmetic excludes nonstandard structures'},
            {'item': 'haul route permits, utilities and traffic management', 'quantity_2km': None, 'quantity_30km': None,
             'unit_quote_iqd': None, 'reason': 'actual road/site access and utility conflicts not surveyed'},
        ],
        'comparison_only': {
            'unsegmented_2km_installed_civil_proxy_iqd': None,
            'unsegmented_30km_class_C_civil_proxy_iqd': proxy['fresh_unsegmented_line30_civil_class_C_proxy_iqd'],
            'unsegmented_30km_class_C_civil_proxy_usd': proxy['fresh_unsegmented_line30_civil_class_C_proxy_usd'],
            'three_m_footing_material_delta_30km_iqd': foot_delta_30,
            'three_m_footing_material_delta_2km_by_support_ratio_iqd': foot_delta_2,
            'footing_delta_is_material_only_and_not_added_when_full_support_quoted': True,
            'proxy_is_not_segmented_candidate_installed_cost': True,
        },
        'reconciliation_rule': 'Each replace row requires a candidate quote and corresponding baseline credit before its delta can be summed. Increment rows enter once. Breakdown-only rows are disclosed inside the complete beam quote and never summed separately. Site-specific rows need survey and quote. The 3 m footing material proxy is a comparator only when a full support quote replaces the baseline support line.',
        'symbolic_cost_formula': {
            '2km': 'unsegmented_2km_scope_matched_baseline + SUM(replacement_quote - matching_baseline_credit) + SUM(increment_quote) + site_specific_quotes',
            '30km': 'unsegmented_30km_class_C_proxy + SUM(replacement_quote - matching_baseline_credit) + SUM(increment_quote) + site_specific_quotes',
            'breakdown_only_rows_in_rollup': False,
            'formula_evaluable_with_current_inputs': False,
        },
        'candidate_installed_civil_cost_2km_iqd': None,
        'candidate_installed_civil_cost_30km_iqd': None,
        'candidate_civil_delta_2km_iqd': None,
        'candidate_civil_delta_30km_iqd': None,
        'unpriced_rows_count': len(rows) + 3,
    }
    handoff['cost_handoff_id'] = sha256(encoded(handoff)).hexdigest()
    return handoff


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('write', 'check', 'write-cost', 'check-cost'))
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    cost = args.action.endswith('-cost')
    target = args.root / (COST_OUTPUT if cost else OUTPUT)
    raw = encoded(build_cost_handoff(args.root) if cost else build(args.root))
    if args.action.startswith('write'):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    elif target.read_bytes() != raw:
        raise ValueError('Segmented-span prototype plan is stale')
    print(json.dumps({'path': str(target), 'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}, sort_keys=True))


if __name__ == '__main__':
    main()
