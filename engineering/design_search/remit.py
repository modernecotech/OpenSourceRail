"""Functional transport remit, separate from a selected hardware recipe."""
from copy import deepcopy
from .requirement_policy import catalogue as policy
from engineering.station_rail.common import identity


def default():
    r=dict(schema='osr-functional-railway-remit/1',revision='GENERATIVE-REMIT-1',
        intent='Affordable accessible comfortable urban transport with independent protection, stopping and recovery',
        mandatory={k:deepcopy(v) for k,v in policy()['criteria'].items() if v['category']=='mandatory_obligation'},
        advisory_targets={k:deepcopy(v) for k,v in policy()['criteria'].items() if v['category']=='project_preference'},
        model_domains={k:deepcopy(v) for k,v in policy()['criteria'].items() if v['category']=='numerical_validity_domain'},
        objectives=['whole-life-cost','construction-time','installed-mass','energy-per-offered-service','maintenance-and-repair','import-dependence'],
        preferences=['local-manufacture','simple-repeatable-parts','replaceable-service-modules','comfortable-seated-service'],
        revisable=['car-length-width-formation','material-form-and-manufacturing','structural-and-assembly-topology',
            'running-gear-and-gauge','propulsion-and-energy-distribution','station-speed-spacing-headway','civil-support-and-erection'],
        reference_selector='engineering/development-baseline.toml',reference_is_universal_requirement=False,
        demonstration=dict(length_m=17.,width_m=2.65,floor_z_m=1.,roof_z_m=3.7,
            fixed_seats=44,wheelchair_places=2,normal_people=46,crowd_control_people=160,person_mass_kg=75.,
            bogie_centres_x_m=[-6.4,6.4],passenger_area_changes_allowed=False,
            purpose='Fixed-accommodation structural competition; other lengths/formations create separate contexts'),
        quantitative_functional_limits='Derive from actual function/interfaces and reviewed evidence; no universal L/500 rule',
        scope='A research remit and an example comparison context, not qualification or a city-specific transport specification')
    r['requirement_revision']=identity(r);return r


def context(*,length_m=17.,width_m=2.65,cars=6):
    r=default()
    if not 8<=length_m<=24 or not 2<=width_m<=3.2 or type(cars) is not int or not 1<=cars<=12:raise ValueError('Bounded example geometry context required; extend generator domain explicitly')
    r['demonstration'].update(length_m=length_m,width_m=width_m,cars=cars,bogie_centres_x_m=[-.3764705882352941*length_m,.3764705882352941*length_m])
    r['requirement_revision']=identity({k:v for k,v in r.items() if k!='requirement_revision'});return r
