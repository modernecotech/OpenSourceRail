"""Small shared SI definition/identity helpers for the v0.6 physical candidate."""
from hashlib import sha256
from pathlib import Path
import json
import tomllib
from . import ROOT,BRIEF,FLAGS

def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(value):return sha256(encoded(value)).hexdigest()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def brief(root=ROOT):
    value=tomllib.loads((Path(root)/BRIEF).read_text())
    if value['schema']!='osr-station-rail-brief/1' or value['version']!='0.6.0':raise ValueError('Explicit v0.6 brief required')
    if value['vehicle']['cars']!=6 or value['vehicle']['normal_people_per_car']!=46:raise ValueError('Six-car comfort basis required')
    if any(value['acceptance'].get(k) is not v for k,v in FLAGS.items()):raise ValueError('Development brief cannot grant release')
    # The first reference evaluator has a declared domain, not arbitrary TOML
    # parameter coverage. Refuse edits that a domain still hard-codes rather
    # than publish a different-looking brief over unchanged calculations.
    fixed={
      'vehicle':dict(cars=6,body_length_m=17.,coupling_gap_m=.5,body_width_m=2.65,
        fixed_seats_per_car=44,wheelchair_places_per_car=2,normal_people_per_car=46,
        planned_standing_per_car=0,crowd_control_people_per_car=160,passenger_mass_kg=75.,
        passenger_doors_per_car=2,passenger_door_sides=1,floor_top_above_rail_m=1.,
        onboard_traction_motors=0,onboard_traction_battery_kWh=0.,onboard_permanent_magnets=0),
      'support':dict(track_gauge_m=1.435,bogie_centres_x_m=[-6.4,6.4],bogie_wheelbase_m=2.1,
        wheel_new_diameter_m=.760,wheel_worn_diameter_m=.680,reference_bogie_pair_mass_kg=6730.),
      'propulsion':dict(secondary_length_m=9.,secondary_height_m=.16,secondary_thickness_m=.015,
        secondary_bottom_above_rail_m=.020,primary_target_airgap_each_side_m=.015,
        all_powered_traction_equipment_wayside=True),
      'services':dict(gross_battery_kWh_target=82.8,reference_hotel_kW_per_car=35.,adverse_hotel_kW_per_car=50.,
        emergency_endurance_s_target=1800.,charging_power_kW_per_car_target=200.,charging_efficiency_hypothesis=.95,
        battery_end_of_life_fraction=.8,hot_battery_capacity_fraction_hypothesis=.9,minimum_SOC=.2,maximum_SOC=.9),
      'service':dict(headway_s=120.,dwell_s=35.,launch_speed_cap_m_s=20.,acceleration_m_s2=.4,
        service_deceleration_m_s2=.6,rolling_coefficient_hypothesis=.0025,bearing_drag_N_per_car_hypothesis=50.,
        quadratic_drag_N_per_car_per_m_s_squared_hypothesis=1.8,mainline_grade_fraction_hypothesis=0.,
        station_section_length_m=12.5,prototype_distances_m=[1500.,2000.],
        minimum_independent_train_phase_branches_per_direction=2),
    }
    for group,expected in fixed.items():
        for key,wanted in expected.items():
            if value[group].get(key)!=wanted:raise ValueError('Outside current evaluator domain: '+group+'.'+key)
    return value

def source_map(root,names):
    root=Path(root)
    return {name:digest(root/name) for name in sorted(set((BRIEF,'engineering/station_rail/__init__.py','engineering/station_rail/common.py',*names)))}
