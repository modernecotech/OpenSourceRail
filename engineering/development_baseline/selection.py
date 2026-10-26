"""Resolve the explicit v0.6 wheel/wayside selection; refuse silent fallback."""
from pathlib import Path
import tomllib
from engineering.station_rail.common import encoded,identity,digest
from . import ROOT,INPUT,FLAGS
IDS=('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')

def load(root=ROOT):
    from engineering.station_rail import vehicle
    root=Path(root).resolve();raw=(root/INPUT).read_bytes();config=tomllib.loads(raw.decode())
    if config.get('schema')!='osr-development-baseline-selection/2' or config.get('selected_for_development') is not True:
        raise ValueError('Explicit v0.6 development selection required')
    if config.get('family')!='wheel_rail_station_lim':raise ValueError('Unsupported selected physical family; historical work requires its pinned checkout')
    if any(config['acceptance'].get(k) is not v for k,v in FLAGS.items()):raise ValueError('Selection cannot grant qualification')
    if config['source_brief']!='engineering/station_rail/brief.toml' or digest(root/config['source_brief'])!=config['source_brief_sha256']:
        raise ValueError('Selected physical brief changed; explicitly regenerate the selection')
    from engineering.station_rail.common import brief
    b=brief(root);v=b['vehicle'];s=b['service']
    vehicle_expected=dict(cars=v['cars'],body_length_m=v['body_length_m'],normal_passengers_per_car=v['normal_people_per_car'],
        fixed_seats_per_car=v['fixed_seats_per_car'],wheelchair_places_per_car=v['wheelchair_places_per_car'],
        standing_passengers_per_car=v['planned_standing_per_car'],passenger_doors_total_per_car=v['passenger_doors_per_car'],
        passenger_door_sides=v['passenger_door_sides'],floor_top_above_rail_m=v['floor_top_above_rail_m'],
        onboard_traction_motors=0,onboard_traction_battery_kWh=0.,onboard_permanent_magnets=0)
    service_expected={key:s[key] for key in ('headway_s','dwell_s','launch_speed_cap_m_s','acceleration_m_s2',
        'service_deceleration_m_s2','station_section_length_m','station_winding_library_m')}
    service_expected.update(normal_capacity_pphpd_arithmetic=8280.,prototype_station_spacing_m=2000.)
    if config['vehicle']!=vehicle_expected or config['service']!=service_expected:raise ValueError('Selected requirement mirrors differ from physical brief')
    car=vehicle.build(root=root)
    if config['network_proposal_id']!=identity(dict(candidate_id=car['candidate_id'],service=s,services=b['services'])):
        raise ValueError('Selected service policy identity differs')
    for key in IDS:
        expected=config['vehicle_candidate_id'] if key=='candidate_id' else config[key]
        if car[key]!=expected:raise ValueError('Selected physical '+key+' differs; explicitly regenerate selection')
    if (config['vehicle']['cars'],config['vehicle']['normal_passengers_per_car'],config['service']['headway_s'])!=(6,46,120.):raise ValueError('Comfort formation/service contract differs')
    if config['service']['normal_capacity_pphpd_arithmetic']!=8280.:raise ValueError('Capacity arithmetic differs')
    return dict(schema='osr-development-baseline/2',selection_id=identity(config),selection=config,vehicle=car,
        network_proposal=dict(proposal_id=config['network_proposal_id'],physical_qualified=False),
        development_default=True,source_sha256={INPUT:digest(root/INPUT),config['source_brief']:digest(root/config['source_brief'])},**FLAGS)

def write_selector(root=ROOT):
    """Deliberate coordinator promotion after regenerating physical definitions."""
    from engineering.station_rail import vehicle
    from engineering.station_rail.common import brief
    root=Path(root);b=brief(root);car=vehicle.build(root=root);s=b['service'];v=b['vehicle']
    proposal=identity(dict(candidate_id=car['candidate_id'],service=s,services=b['services']))
    lines=['schema = "osr-development-baseline-selection/2"','revision = "WHEEL-STATION-COMFORT-1"','version = "0.6.0"',
        'family = "wheel_rail_station_lim"','selected_for_development = true','source_brief = "engineering/station_rail/brief.toml"',
        'source_brief_sha256 = "'+digest(root/'engineering/station_rail/brief.toml')+'"',
        'vehicle_candidate_id = "'+car['candidate_id']+'"']
    lines += [key+' = "'+car[key]+'"' for key in IDS[1:]]
    lines += ['network_proposal_id = "'+proposal+'"','[vehicle]',f'cars = {v["cars"]}',
        f'body_length_m = {v["body_length_m"]}',f'normal_passengers_per_car = {v["normal_people_per_car"]}',
        f'fixed_seats_per_car = {v["fixed_seats_per_car"]}',f'wheelchair_places_per_car = {v["wheelchair_places_per_car"]}',
        'standing_passengers_per_car = 0','passenger_doors_total_per_car = 2','passenger_door_sides = 1',
        f'floor_top_above_rail_m = {v["floor_top_above_rail_m"]}','onboard_traction_motors = 0','onboard_traction_battery_kWh = 0.0',
        'onboard_permanent_magnets = 0','[service]']
    for name in ('headway_s','dwell_s','launch_speed_cap_m_s','acceleration_m_s2','service_deceleration_m_s2','station_section_length_m'):
        lines.append(name+' = '+str(s[name]))
    lines += ['normal_capacity_pphpd_arithmetic = 8280.0','prototype_station_spacing_m = 2000.0',
        'station_winding_library_m = '+str(s['station_winding_library_m']),'[acceptance]']
    lines += [k+' = false' for k in FLAGS]
    (root/INPUT).write_text('\n'.join(lines)+'\n');return load(root)
