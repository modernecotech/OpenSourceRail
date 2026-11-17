import hashlib
import json
import math
import os
from pathlib import Path
import tomllib

from engineering.station_rail import vehicle, braking
from engineering.design_search.architecture_demand import demand, G

ROOT = Path.cwd()
OUT = ROOT / 'build/v07-ethos/station-power-20261117-a'
paths = [
    'AGENTS.md',
    'campaigns/whole-railway-architecture-search.toml',
    'campaigns/line30-affordable-benchmark.toml',
    'docs/design-engine/line30-benchmark/README.md',
    'docs/design-engine/line30-benchmark/result.json',
    'docs/design-engine/line30-benchmark/manifest.json',
    'build/v07-ethos/line30-current-20261117-a/result.json',
    'build/v07-ethos/line30-current-20261117-a/manifest.json',
    'docs/design-engine/v06-architecture/README.md',
    'docs/design-engine/v06-architecture/summary.json',
    'docs/design-engine/architecture-reach-closure/result.json',
    'docs/design-engine/propulsion-layout/README.md',
    'engineering/design_search/architecture_demand.py',
    'engineering/design_search/architecture_reach_closure.py',
    'engineering/design_search/railway_architecture.py',
    'engineering/station_rail/vehicle.py',
    'engineering/station_rail/braking.py',
    'engineering/station_rail/electrical.py',
    'engineering/station_rail/operations.py',
    'engineering/station_rail/common.py',
    'engineering/development-baseline.toml',
]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def save(name, value):
    (OUT / name).write_bytes(canonical(value) + b'\n')

spec = tomllib.loads((ROOT / 'campaigns/whole-railway-architecture-search.toml').read_text())
line = json.loads((ROOT / 'docs/design-engine/line30-benchmark/result.json').read_text())
line_current = json.loads((ROOT / 'build/v07-ethos/line30-current-20261117-a/result.json').read_text())
line_current_manifest = json.loads((ROOT / 'build/v07-ethos/line30-current-20261117-a/manifest.json').read_text())
v = vehicle.build(ROOT)
rot = braking.rotating_stock(v)['equivalent_inertial_mass_kg_per_car']
m = v['mass']['accounted_cap_loaded_kg_per_car']
assert v['candidate_id'] == '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
assert line['requirements_id'] == 'a18e0f20b6ec40e067aff40213b312ae756f7f3389ee5b43059225cf92d05ff4'
assert line_current['requirements_id'] == line['requirements_id']
assert line_current['evaluation_id'] == line_current_manifest['evaluation_id'] == '947dd7cbcac7c260da721150912fba47531c96fd3f7a28365c394249608ee869'
assert line_current_manifest['manifest_id'] == 'b455f1f9cfa98bd41d958c736862e75578c831d287db7b5c95ca48b5a82af2c4'
assert spec['requirements']['capacity_pphpd'] == 8280.0
assert spec['scenario']['adverse_grade_fraction'] == .02
assert spec['scenario']['receiving_command_m'] == 350.0
inputs = dict(
    schema='osr-station-power-equal-service-input/1',
    source_commit=os.popen('git rev-parse HEAD').read().strip(),
    source_sha256={p: sha(ROOT / p) for p in paths},
    physical_reference_candidate_id=v['candidate_id'],
    budget_anchor=dict(historical_source_stale_for_current=True, mechanism=line['baseline_mechanism'], requirements_id=line['requirements_id'],
                       evaluation_id=line['evaluation_id'], baseline_evaluation_id=line['baseline_evaluation_id'],
                       benchmark_definition_id=line['benchmark_definition_id'],
                       benchmark_selection_id=line['benchmark_selection_id']),
    current_line30_packet=dict(result_path='build/v07-ethos/line30-current-20261117-a/result.json',
                               manifest_id=line_current_manifest['manifest_id'],
                               evaluation_id=line_current['evaluation_id'],
                               baseline_evaluation_id=line_current['baseline_evaluation_id'],
                               requirements_id=line_current['requirements_id'],
                               engineering_accepted=False,physical_accepted=False),
    service=dict(route_km=30, stations=12, cars=6, car_length_m=17, normal_places_per_car=46,
                 places_per_train=276, offered_pphpd=8280, headway_s=120,
                 speed_cap_m_s=20, independent_service_deceleration_m_s2=.6,
                 dwell_s=35, crowd_control_per_car=160, accessibility_mandatory=True),
    comparison_mass=dict(accounted_normal_loaded_kg_per_car=m, rotating_equivalent_kg_per_car=rot,
                         complete_installed_kg=None, basis='Selected passive-wheel v0.6 reference; equal-accounted-mass sensitivity only'),
    local_segment_variables=dict(spacing_m=spec['space']['station_spacing_m'], launch_command_m=spec['space']['station_launch_command_m'],
                                 uphill_grade_fraction=[0,.01,.02], receiving_command_m=350,
                                 recovery='external protected tow for station-only; self drive for powered-wheel is unproven'),
    model=dict(acceleration_command_m_s2=.4, rolling_coefficient=.0025,
               constant_resistance_N_per_car=50, aero_coefficient_N_s2_m2=1.8, headwind_m_s=0,
               dt_s=.2, runtime_limit_s=600, maximum_steps=10000,
               assumption='Demand targets only; no available force/current/thermal or brake qualification')
)
inputs['input_id'] = hashlib.sha256(canonical(inputs)).hexdigest()
save('input.json', inputs)
def research_id(architecture, spacing_m, launch_m, driven_axles):
    definition=dict(parent_selected_candidate_id=v['candidate_id'], architecture=architecture,
                    station_spacing_m=spacing_m, launch_command_m=launch_m,
                    driven_axles=driven_axles, receiving_reservation_m=350,
                    installation_complete=False)
    return hashlib.sha256(canonical(definition)).hexdigest()

rows=[]
for S in spec['space']['station_spacing_m']:
    for grade in [0,.01,.02]:
        for L in spec['space']['station_launch_command_m']:
            res=demand(S,m,rot,powered_windows=[[0,L]],cars=6,speed_cap_m_s=20,
                       acceleration_m_s2=.4,deceleration_m_s2=.6,grade=grade,
                       dt=.2,maximum_runtime_s=600,maximum_steps=10000)
            # Resistance floor after launch. Taking speed cap is optimistic for an
            # upper bound, so a shortfall proves failure under this model.
            F_floor=m*G*(.0025+grade)+50
            stop_upper=L+(.5*(m+rot)*20**2/F_floor if F_floor>0 else math.inf)
            row=dict(architecture='station-only-unpowered-wheel',research_configuration_id=research_id('station-only-unpowered-wheel',S,L,0),spacing_m=S,grade_up_fraction=grade,
                     launch_command_m=L,receiving_reserved_m=350,
                     demand_id=res['demand_id'],execution=res['execution'],numerical_validity=res['numerical_validity'],
                     target_reached=res['reachable'],reason=res['reason'],runtime_s=res['runtime_s'],
                     final_position_m=res['final_position_m'],final_speed_m_s=res['final_speed_m_s'],
                     peak_speed_m_s=res['peak_speed_m_s'],peak_required_force_kN_train=res['peak_required_force_N_train']/1000,
                     peak_required_power_MW_train=res['peak_required_power_W_train']/1e6,
                     demanded_mechanical_kWh_train=res['traction_mechanical_energy_J_train']/3.6e6,
                     friction_brake_kWh_train=res['friction_brake_energy_J_train']/3.6e6,
                     relative_energy_residual=res['relative_energy_residual'],
                     optimistic_stop_position_upper_m=stop_upper,
                     necessary_reach_failure=stop_upper<S-1e-6,
                     complete_installed_mass_kg=None, available_force_N=None, actual_thermal_duty=None,
                     physical_journey_completed=False)
            rows.append(row)
        # P6 sustained traction 24 driven axles is one explicit powered-wheel
        # comparison. It is a target demand; onboard equipment remains unweighed.
        res=demand(S,m,rot,powered_windows=[[0,S]],cars=6,speed_cap_m_s=20,
                   acceleration_m_s2=.4,deceleration_m_s2=.6,grade=grade,
                   dt=.2,maximum_runtime_s=600,maximum_steps=10000)
        for driven_axles in [12,24]:
            fraction=driven_axles/24
            mu_optimistic=(.4/G+.0025+grade)/fraction
            rows.append(dict(architecture='powered-wheel-sustained',research_configuration_id=research_id('powered-wheel-sustained',S,S,driven_axles),spacing_m=S,grade_up_fraction=grade,
                             launch_command_m=S,driven_axles=driven_axles,
                             demand_id=res['demand_id'],execution=res['execution'],numerical_validity=res['numerical_validity'],
                             target_reached=res['reachable'],reason=res['reason'],runtime_s=res['runtime_s'],
                             peak_required_force_kN_train=res['peak_required_force_N_train']/1000,
                             peak_required_power_MW_train=res['peak_required_power_W_train']/1e6,
                             demanded_mechanical_kWh_train=res['traction_mechanical_energy_J_train']/3.6e6,
                             friction_brake_kWh_train=res['friction_brake_energy_J_train']/3.6e6,
                             relative_energy_residual=res['relative_energy_residual'],
                             optimistic_uniform_axle_adhesion_mu_floor=mu_optimistic,
                             pass_campaign_mu_0_1_hypothesis=mu_optimistic<=.1,
                             complete_installed_mass_kg=None, available_force_N=None, actual_thermal_duty=None,
                             physical_journey_completed=False))
train_mass=6*m
train_dynamic=6*(m+rot)
brake_mu_floor_level=(train_dynamic*.6-train_mass*G*.0025-6*50)/(train_mass*G)
outputs=dict(schema='osr-station-power-equal-service-screen/1',input_id=inputs['input_id'],
             execution='completed',numerical_validity='conditional-model',engineering_screen='open',
             evidence_maturity='analytical-demand',physical_accepted=False,
             candidate_selection_id=None,selected_reference_changed=False,
             model_coverage=dict(station_propulsion='Demand only; fixed stator groups, phase registration, position-dependent overlap, R/L/flux, converter current/voltage, repeated thermal losses and receiving braking not established',
                                 wheel_propulsion='Demand only; current/torque map, converter, battery/conductor, cooling, protection, axle loads and adhesion not established'),
             rows=rows,
             service_compatibility=dict(identical_30km_12_stations_8280pphpd_maintained_in_input=True,
                                        local_spacing_not_uniform_route=True,
                                        average_interstation_m=30000/11,
                                        actual_30km_timetable_and_fleet_proven=False,
                                        retained_historical_line30_budget_usd_per_route_km=line['baseline_price_per_route_km_usd']['base'],
                                        current_replay_line30_budget_usd_per_route_km=line_current['baseline_price_per_route_km_usd']['base'],
                                        current_replay_evaluation_id=line_current['evaluation_id'],
                                        comparative_installed_cost_USD=None),
             necessary_bounds=dict(grade_energy_kWh_per_100t_per_2km={str(g):100000*G*g*2000/3.6e6 for g in [0,.01,.02]},
                                   reference_train_grade_energy_kWh_per_2km={str(g):train_mass*G*g*2000/3.6e6 for g in [0,.01,.02]},
                                   independent_brake_mu_floor_level=brake_mu_floor_level,
                                   independent_brake_mu_floor_2pct_downhill=brake_mu_floor_level+.02,
                                   campaign_brake_mu_hypothesis=.05,
                                   brake_note='Optimistic uniform axle loading, v≈0 resistance, no extra installed mass; actual brake/adhesion, thermal and fault capability unknown'),
             explicit_holds=['No selected propulsion installation or equal-service installed cost',
                             'Station winding groups/overlap/phase registration and converter R/L/flux/current/voltage not coupled to moving train',
                             'Repeated 120 s launch and receiving brake duty with protection/cooling not measured',
                             'Independent stopping/parking, crowd load, accessibility, rescue and degraded headway unproven',
                             '30 km alignment, 11 segment distribution, turnback and timetable not evaluated',
                             'New motor, converter, feeders, switchgear, cooling, cables, protection, supports and maintenance envelopes unweighed/unpriced',
                             'Powered-wheel motor/gearbox/inverter/store/conductor/charge/protection, bearing and bogie effects unweighed/unpriced'],
             next_physical_test='Instrument one full-scale station launch group and full passive-fin bogie/carriage at representative loaded/crowd ballast: moving entry/centred/exit force with registered phases, measured R/L/flux/current/voltage, 0/1/2% equivalent grade loads, independent receiving stop and parking, lost group and protected tow, repeated 120 s hot-duty thermal equilibrium; independently review raw calibrated measurements before a 1.5–2 km pilot.')
outputs['evaluation_id']=hashlib.sha256(canonical(outputs)).hexdigest()
save('output.json',outputs)
print(json.dumps(dict(input_id=inputs['input_id'],evaluation_id=outputs['evaluation_id'],rows=len(rows),station_reached=sum(r['target_reached'] for r in rows if r['architecture'].startswith('station')),station_total=sum(r['architecture'].startswith('station') for r in rows),station_necessary_failures=sum(r.get('necessary_reach_failure',False) for r in rows)),sort_keys=True))
