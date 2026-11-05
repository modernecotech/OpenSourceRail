"""The active baseline defines a transport search, not an installed drive."""
from copy import deepcopy
from pathlib import Path
import tomllib

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity

PRODUCER='engineering/development_baseline/propulsion_policy.py'
SELECTOR='engineering/development-baseline.toml'
REQUIRED_OUTPUTS=('candidate-geometry-and-installed-mass','force-speed-position-and-energy',
    'independent-degraded-braking-and-recovery','electrical-thermal-and-clearance',
    'passenger-service-accessibility-and-comfort','production-construction-and-maintenance',
    'installed-and-whole-life-cost')
DEFAULTS=dict(selection_mode='candidate-specific',prescribed_powered_length=False,
    automatic_hardware_adoption=False,reference_controls_are_requirements=False,
    examples_are_exhaustive=False,physical_qualification_required=True,
    architecture_examples=['station-cable-capstan','station-common-drive-rollers','compact-LIM',
        'distributed-wayside','onboard-electric-traction','hybrid','custom-transport-approach'],
    headways_s=[90.,120.,150.,180.,200.,240.,300.],
    accelerations_m_s2=[.6,.8,1.,1.2,1.5],
    service_decelerations_m_s2=[.6,.8,1.],speeds_kmh=[50.,60.,72.],
    required_outputs=list(REQUIRED_OUTPUTS))


def validate(config):
    p=config.get('propulsion_design')
    if not isinstance(p,dict):raise ValueError('Explicit candidate-specific propulsion policy required')
    for key in ('selection_mode','prescribed_powered_length','automatic_hardware_adoption',
                'reference_controls_are_requirements','examples_are_exhaustive','physical_qualification_required'):
        if (p.get(key)!=DEFAULTS[key] or (isinstance(DEFAULTS[key],bool) and type(p.get(key)) is not bool)):raise ValueError('Active propulsion policy differs: '+key)
    if (p.get('required_outputs')!=list(REQUIRED_OUTPUTS)
            or any('powered_length' in k and k!='prescribed_powered_length' for k in p)
            or any(k.startswith('selected_') for k in p)):
        raise ValueError('An installed propulsion layout cannot be prescribed by the baseline')
    from math import isfinite
    for key in ('headways_s','accelerations_m_s2','service_decelerations_m_s2','speeds_kmh'):
        values=p.get(key)
        if (not isinstance(values,list) or not values
                or any(type(x) not in (int,float) or not isfinite(x) or x<=0 for x in values)):
            raise ValueError('Explicit positive search examples required: '+key)
    if not p.get('architecture_examples'):raise ValueError('Open architecture examples required')
    return deepcopy(p)


def load(root=ROOT):
    root=Path(root);config=tomllib.loads((root/SELECTOR).read_text());p=validate(config)
    value=dict(schema='osr-candidate-specific-propulsion-policy/1',policy=p,
        reference_vehicle_candidate_id=config['vehicle_candidate_id'],
        reference_passive_interface_id=config['propulsion_component_id'],
        selected_installed_propulsion_id=None,selected_architecture=None,
        selected_powered_length_m=None,selected_acceleration_m_s2=None,
        selected_braking_m_s2=None,selected_headway_s=None,
        reference_vehicle_is_installed_drive_selection=False,
        kinematic_distance_is_powered_hardware_length=False,
        reference_controls_scope='Explicit reproducibility controls, not active design requirements',
        source_sha256={n:digest(root/n) for n in (PRODUCER,SELECTOR)},
        engineering_accepted=False,physical_accepted=False,manufacturing_release=False,
        operating_release=False,movement_authority=False)
    value['policy_id']=identity(value);return value
