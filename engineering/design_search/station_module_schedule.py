"""One station/booster module quote request from the held demonstrator demand."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from engineering.design_search import station_demonstrator
from engineering.station_rail import vehicle
from engineering.design_search.demonstrator_propulsion import SELECTED, encoded, evaluate, identity

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    'engineering/design_search/station_module_schedule.py',
    'engineering/design_search/station_demonstrator.py',
    'engineering/station_rail/vehicle.py',
    'engineering/development-baseline.toml',
    'docs/design-engine/v07-demonstrator-propulsion/comparison.json',
    'docs/design-engine/v07-demonstrator-propulsion/input.json',
)


def schedule(root=ROOT):
    root=Path(root)
    base=root/'docs/design-engine/v07-demonstrator-propulsion'
    comparison=json.loads((base/'comparison.json').read_bytes())
    inputs=json.loads((base/'input.json').read_bytes())
    if encoded(evaluate(inputs,root))!=(base/'comparison.json').read_bytes():
        raise ValueError('Demonstrator comparison differs from current source and input')
    if (comparison['parent_selected_vehicle_candidate_id'] != SELECTED
            or inputs['parent_selected_vehicle_candidate_id'] != SELECTED
            or comparison['selected_reference_changed'] is not False
            or comparison['physical_accepted'] is not False):
        raise ValueError('Mixed or promoted reference candidate')
    v=vehicle.build(root)
    if v['candidate_id'] != SELECTED or v['physical_accepted'] is not False:
        raise ValueError('Selected vehicle source differs')
    rows=[r for r in comparison['rows'] if r['architecture']=='station-plus-midroute-booster'
          and r['spacing_m']==2000]
    if len(rows)!=3 or {r['grade_up_fraction'] for r in rows}!={0,.01,.02}:
        raise ValueError('Complete booster grade demand required')
    if len({r['railway_research_configuration_id'] for r in rows})!=1:
        raise ValueError('Booster physical configuration differs across evaluations')
    adverse=next(r for r in rows if r['grade_up_fraction']==.02)
    if adverse['powered_windows_m'] != [[0,500],[1000,1250]] or not adverse['analytical_target_reached']:
        raise ValueError('Declared booster demand differs')
    physical=v['physical_definition']
    stock=physical['vehicle'];fin=physical['propulsion'];clearance=v['clearance']
    train_length=stock['cars']*stock['body_length_m']+(stock['cars']-1)*stock['coupling_gap_m']
    if stock['passenger_door_sides']!=1 or stock['onboard_traction_motors']!=0:
        raise ValueError('Passive one-sided vehicle reference required')
    source_sha={p:sha256((root/p).read_bytes()).hexdigest() for p in SOURCES}
    no_reaction=inputs['model']['speed_cap_m_s']**2/(2*inputs['model']['independent_stop_target_m_s2'])
    reaction_s=1.0 # explicit quotation sensitivity, not an approved reaction time
    with_reaction=no_reaction+inputs['model']['speed_cap_m_s']*reaction_s
    receiving_reservation_m=350
    full_train_engagement_minimum=with_reaction+train_length
    receiving_alternatives=[]
    for length in (350,400,450,550):
        definition=dict(parent_booster_railway_research_configuration_id=adverse['railway_research_configuration_id'],
                        receiving_reserved_length_m=length,
                        full_train_engagement_before_brake_hypothesis=True)
        receiving_alternatives.append(dict(
            receiving_research_configuration_id=identity(definition),
            reserved_length_m=length,selected=False,installed_brake_length_m=None,
            nose_stop_margin_with_illustrative_reaction_m=length-with_reaction,
            full_train_engagement_margin_m=length-full_train_engagement_minimum,
            grade_and_adhesion_screen='held: 2% downgrade needs more than inherited mu=0.05',
            full_load_hot_fault_stop_verified=False,
            civil_station_quantity_and_price_effect=None))
    def item(name, demand_basis, *, unit='assembly', installed_quantity=None, rating=None):
        return dict(id=name, demand_basis=demand_basis, quote_unit=unit,
                    installed_quantity=installed_quantity, supplier_rating=rating,
                    installed_mass_kg=None, installed_price_usd=None,
                    source_origin=None, local_make_buy=None,
                    maintenance_clearance_m=None, replacement_time_h=None)
    items=[
        item('station-launch-primary', '500 m full-engagement leading-nose command window; physical stator extent and group overlap unresolved',unit='m of installed primary'),
        item('midroute-booster-primary', '250 m full-engagement leading-nose command window at chainage 1000–1250 m; physical stator extent unresolved',unit='m of installed primary'),
        item('receiving-independent-brake-and-parking',
             f'350/400/450/550 m research reservations; at least {full_train_engagement_minimum:.1f} m before uncertainty if full train engagement precedes braking'),
        item('phase-group-converters-and-dc-link', 'Separate commanded launch/booster windows; group count, simultaneous trains and phase branches to be designed'),
        item('feeder-return-isolation-grounding', 'Station and midroute groups, protected return and safe isolation; route and cable lengths to be surveyed'),
        item('sensors-position-and-protection', 'Registered phase position, train detection, berth, tail clearance, interlocking and fault monitoring'),
        item('cooling-fire-and-enclosure', 'Repeated 120 s launch/receiving duty to hot equilibrium; heat and enclosure environment unknown'),
        item('protected-tow-and-access', 'Independent stalled-train recovery and removal paths; force and access envelope unknown'),
    ]
    value=dict(
        schema='osr-v07-station-module-quote-input/1',
        comparison_evaluation_id=comparison['evaluation_id'],
        parent_selected_vehicle_candidate_id=SELECTED,
        booster_railway_research_configuration_id=adverse['railway_research_configuration_id'],
        selected_reference_changed=False,installed_drive_selected=False,
        module_scope=dict(directional_station_berths=1,midroute_booster_extensions=1,
                          complete_line_module_count=None,station_spacing_m=2000,
                          launch_command_window_m=[0,500],booster_command_window_m=[1000,1250],
                          receiving_reservation_m=receiving_reservation_m,
                          actual_installed_primary_m=None,actual_receiving_brake_m=None,
                          receiving_revision_candidates=receiving_alternatives,
                          full_train_length_m=train_length,train_cars=stock['cars'],
                          one_sided_passenger_doors_per_train=stock['cars']*stock['passenger_doors_per_car'],
                          platform_side_and_door_datum=None),
        mechanical_interfaces=dict(
            coordinate_system='rail running surface z=0; route chainage x at departing train leading nose',
            passive_fin_per_car_m=dict(length=fin['secondary_length_m'],height=fin['secondary_height_m'],
                                       thickness=fin['secondary_thickness_m'],bottom_above_rail=fin['secondary_bottom_above_rail_m']),
            nominal_primary_top_above_rail_m=clearance['station_primary_top_above_rail_m'],
            nominal_airgap_each_side_m=fin['primary_target_airgap_each_side_m'],
            primary_mounting_datum_and_tolerance=None,bearing_rail_and_civil_load_datum=None,
            curves_suspension_wear_turnouts_and_sweep_qualified=False,
            passenger_platform_accessibility_and_evacuation_interface='Required; platform side, level boarding and clearance to one-sided doors unresolved'),
        demand_for_supplier=dict(grade_up_fraction=.02,
                                 peak_required_mechanical_force_kN_train=adverse['peak_required_force_kN_train'],
                                 peak_required_mechanical_power_MW_train=adverse['peak_required_mechanical_power_MW_train'],
                                 required_electrical_power_MW=None,
                                 winding_R_L_flux_current_voltage_vs_position_speed_temperature=None,
                                 converter_continuous_and_peak_rating=None,
                                 measured_repeated_120s_hot_duty=False),
        independent_stop=dict(speed_cap_m_s=inputs['model']['speed_cap_m_s'],
                              target_net_deceleration_m_s2=inputs['model']['independent_stop_target_m_s2'],
                              full_speed_stop_no_reaction_m=no_reaction,
                              illustrative_reaction_s=reaction_s,
                              full_speed_stop_with_illustrative_reaction_m=with_reaction,
                              receiving_reservation_m=receiving_reservation_m,
                              illustrative_margin_m=receiving_reservation_m-with_reaction,
                              full_train_engagement_before_brake_minimum_m=full_train_engagement_minimum,
                              full_train_engagement_before_brake_hypothesis=True,
                              speed_cap_maintained_during_unbraked_runin_hypothesis=True,
                              extra_berth_tail_position_and_uncertainty_clearance_m=None,
                              quoted_receiving_length_m=None,
                              optimistic_mu_floor_2pct_downhill=comparison['independent_brake']['optimistic_mu_floor_2pct_downhill'],
                              brake_type_and_count=None,adhesion_WSP_fade_and_heat_rating=None,
                              independent_power_loss_stop_and_parking_verified=False,
                              limitation='Lengths assume the target net deceleration is already available; mu=0.05 fails the necessary force bound. Full-train run-in is a conservative station-mounted receiving-force hypothesis, not an approved brake geometry.'),
        quote_items=items,
        assembly_qa_sequence=[
            'Survey rail, berth, door/platform, station/civil and booster datums; approve dimensional interface control before equipment manufacture',
            'Supplier submit stator group layout, overlap/phase and fin-clearance drawings, load paths, mounts and removable module envelopes',
            'Fabricate one identified group and representative passive-fin carriage; inspect dimensions, insulation, bonds, polarity and traceable materials',
            'Bench record winding R/L/flux, current/voltage and converter limits; calibrate force and temperature instruments',
            'Install launch, booster and receiving modules with surveyed rail datums, grounding/isolation, protection and maintenance access',
            'Measure moving entry/centre/exit thrust, phase handoff, force ripple and actual current under representative loaded ballast',
            'Test independent full-speed stop, parking, energy sink, loss of power/group/cooling and protected tow before route operation',
            'Repeat 120 s duty to thermal equilibrium; review calibrated raw data and as-built configuration independently',
        ],
        quote_request=dict(single_installed_budgetary_price_usd=None,
                           supplier_to_submit='One scoped installed price with material, local manufacture hours, tooling, civil interfaces, installation, QA, spares, renewals and exclusions identified',
                           requested_characteristics=['group and installed path lengths','force versus x/v/i/T','R/L/flux and converter limits','continuous and peak duty','brake force/fade/WSP','mass and lifting points','maintainable removal envelope','origin and local fabrication hours','single installed price and renewals']),
        protocols={key:station_demonstrator.NEXT[key] for key in ('T05','T07','T08')},
        source_sha256=source_sha,
        engineering_screen='quotation-input-incomplete',
        physical_accepted=False,engineering_accepted=False,
        manufacturing_release=False,operating_release=False,
    )
    value['module_evaluation_id']=identity(value)
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    raw=encoded(schedule())
    if args.check:
        if args.output.read_bytes()!=raw:raise SystemExit('Station module schedule differs from current sources')
    else:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(raw)
    print(json.dumps(dict(module_evaluation_id=json.loads(raw)['module_evaluation_id'],physical_accepted=False),sort_keys=True))


if __name__=='__main__':main()
