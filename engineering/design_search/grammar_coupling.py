"""Propagate same-candidate declared accounts; missing physics stays unknown."""
from copy import deepcopy
from engineering.station_rail import vehicle,braking,civil
from engineering.station_rail.common import identity
from . import architecture_demand,design_grammar


def evaluate(candidate):
    design_grammar.validate(candidate);reference=vehicle.build();v=deepcopy(reference);p=candidate['parameters']
    tare=candidate['known_structure_stock_kg']+sum(r['mass_kg'] for r in candidate['retained_equipment_accounts'])
    v['candidate_id']=candidate['candidate_id'];v['body_candidate_id']=candidate['candidate_id']
    v['mass'].update(accounted_tare_kg_per_car=tare,accounted_cap_loaded_kg_per_car=tare+46*75.,accounted_160_control_kg_per_car=tare+160*75.)
    v['physical_definition']['vehicle'].update(cars=p['cars'],body_length_m=p['length_m'],body_width_m=p['width_m'])
    v['physical_definition']['support']['bogie_centres_x_m']=[-.3764705882352941*p['length_m'],.3764705882352941*p['length_m']]
    rot=braking.rotating_stock(reference)['equivalent_inertial_mass_kg_per_car'];profiles=[]
    for D in (1500.,2000.,3000.):
        r=architecture_demand.demand(D,v['mass']['accounted_cap_loaded_kg_per_car'],rot,cars=p['cars'],powered_windows=[[0.,500.]])
        raw=r.pop('demand_id');trace=r.pop('trace');r.update(raw_demand_id=raw,trace_sha256=identity(trace),schema='osr-grammar-required-motion-index/1');r['demand_id']=identity(r);profiles.append(r)
    result=dict(candidate_id=candidate['candidate_id'],known_body_stock_kg=candidate['known_structure_stock_kg'],accounted_tare_hypothesis_kg_per_car=tare,
        normal_sprung_load_mass_kg=candidate['structure']['load_basis']['sprung_mass_hypothesis_kg'],
        normal_account_hypothesis_kg_per_car=v['mass']['accounted_cap_loaded_kg_per_car'],crowd_account_hypothesis_kg_per_car=v['mass']['accounted_160_control_kg_per_car'],
        rotating_equivalent_kg_per_car=rot,required_motion=profiles,
        civil=[civil.alternative(v,20.,f,'crowd_control') for f in ('box-beam','twin-beam','u-beam')],
        actual_motor_map=None,complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,
        force_motion_thermal_braking_journey_completed=False,whole_life_cost_USD=None,
        coupling_scope='Explicit account propagation, not a converged physical force/heat/deflection system. Bogie stock and service accounts retained; mounts/placement and missing items require new engineering.',
        OpenMDAO_execution='not-run: physical feedback laws unavailable',physical_accepted=False)
    expected=(tare-6730.+46*75.)
    if abs(expected-result['normal_sprung_load_mass_kg'])>1e-6:raise ValueError('Native structure and motion/civil use inconsistent mass accounts')
    result['evaluation_id']=identity(result);return result
