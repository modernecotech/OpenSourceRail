"""Compose one wheel/wayside physical candidate and its honest readiness gates."""
from pathlib import Path
from . import ROOT,FLAGS
from .common import encoded,identity,source_map
from engineering.development_baseline import selection
IDS=('selection_id','candidate_id','body_candidate_id','support_component_id','propulsion_component_id')

def merge(*maps):
    value={}
    for mapping in maps:
        for key,digest in mapping.items():
            if key in value and value[key]!=digest:raise ValueError('mixed source revisions: '+key)
            value[key]=digest
    return dict(sorted(value.items()))

def build(root=ROOT):
    from . import operations,civil
    root=Path(root);baseline=selection.load(root);car=baseline['vehicle']
    ops=operations.evaluate(car,root=root);structures=civil.evaluate(car,root=root)
    for domain in (ops,structures):
        for name in IDS[1:]:
            if domain[name]!=car[name]:raise ValueError('mixed physical '+name)
        if any(domain.get(k) is not v for k,v in FLAGS.items()):raise ValueError('domain cannot grant release')
    gates=[
      ('installed-vehicle','unknown','Locate and weigh all residual stock, joinery, bogie and service assemblies; obtain complete CG and inertia.'),
      ('isolated-underframe-stiffness','fail','The isolated hollow side-sill fixtures exceed the declared deflection limit. Whole-body load sharing through retained longitudinal members, posts and joints must be demonstrated or redesigned.'),
      ('body-and-bogie-structure','unknown','Concentrated bogie support changes the body load path. Local/frame fixtures do not establish joined-body stress, buckling, fatigue, crash, modes or bogie qualification.'),
      ('wheel-rail-dynamics','unknown','Qualify wheel profiles, hunting, curves, suspension, ride, flange forces and derailment containment.'),
      ('station-LIM-force-map','unknown','No accepted thrust/current/frequency/gap/temperature map for the complete station drive and moving secondary; targets are required forces.'),
      ('station-electrical-thermal','unknown','Qualify inverters, section handoff, supply, slip/secondary heat, unwanted normal forces and 120-second repeated duty.'),
      ('independent-braking','unknown','Validate supplier brake/WSP/adhesion/thermal curves, channel failures, parking, receiving-power loss and degraded gradients.'),
      ('hot-weather-services','unknown','HVAC delivered capacity and COP at 50 C, roof long-term structural temperature and actively cooled service pack remain unqualified.'),
      ('coupled-journey','unknown','Reference motion is analytical. Required physical drive/brake maps, wheel dynamics and flexible-body model are not available for a qualified six-car trip.'),
      ('GoA4-protection','unknown','Existing Rust ATP/interlocking and new wheel interface predicates require candidate-correlated braking, sensing, timing, communications and fault evidence.'),
      ('civil-and-site','unknown','Alternative sections are necessary screens. Prestress, fatigue, torsion, lateral/derailment loads, foundations, survey, erection and independent review remain open.'),
      ('rescue-and-evacuation','unknown','Motorless off-zone restart needs a protected rescue/tow system, emergency access and an acceptable high-viaduct evacuation plan.'),
      ('whole-system-economics','unknown','No same-service supplier quotes or complete CAPEX/OPEX/renewal comparison; lower installed cost has not been established.'),
      ('city-regeneration','hold','Preserve 266 geographic inputs. Numerical city publication is held pending reference propulsion, braking, route and economic evidence.'),
    ]
    result=dict(schema='osr-current-development-evaluation/2',version='0.6.0',family='wheel_rail_station_lim',
        **{k:car[k] for k in IDS[1:]},selection_id=baseline['selection_id'],selection=baseline['selection'],
        development_default=True,configuration_adopted_for_development=True,
        selection_purpose='Reference engineering and prototype investigation; no city deployment or economic acceptance',
        selection_rationale='User-selected wheel/rail station-power architecture eliminates suspension electromagnets and continuous magnetic facing steel. The vehicle may be heavier, station LIM remains unqualified and economic superiority is unknown.',
        vehicle=car,service=ops,civil=structures,
        gates=[dict(gate=name,state=state,reason=reason,evidence_maturity='analytical',physical_acceptance=False) for name,state,reason in gates],
        source_sha256=merge(car['source_sha256'],ops['source_sha256'],structures['source_sha256'],baseline['source_sha256'],
            source_map(root,('engineering/station_rail/evaluation.py','engineering/station_rail/families.py','engineering/development_baseline/selection.py'))),**FLAGS)
    result['evaluation_id']=identity(result);return result

def validate(record,root=ROOT):
    if record!=build(root):raise ValueError('evaluation differs from selected definitions')
    return True

def summary(record):
    p=record['service']['selected_scenario']['profile'];z=record['service']['selected_station']
    return dict(schema='osr-current-development-summary/2',version='0.6.0',family=record['family'],
        **{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],development_default=True,
        selection_revision=record['selection']['revision'],selection_purpose=record['selection_purpose'],
        selection_rationale=record['selection_rationale'],mass=record['vehicle']['mass'],
        vehicle=record['selection']['vehicle'],
        service=dict(headway_s=120.,dwell_s=35.,cars=6,passengers_per_car=46,capacity_pphpd=8280.,
            launch_speed_cap_m_s=20.,prototype_station_spacing_m=2000.,prototype_runtime_s=p['runtime_s'],
            shared_winding_m=z['length_m'] if z else None,
            nominal_resource_interval_s=z['nominal_resource_interval_s'] if z else None,
            physical_headway_qualified=False,actual_thrust_map_available=False),
        gates=record['gates'],**FLAGS)
