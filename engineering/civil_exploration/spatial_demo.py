"""Explicit research inputs for the spatial adapter; no supplier defaults."""
from copy import deepcopy
import numpy as np


def configuration(model):
    laws = {}
    for joint in model['joints']:
        if joint['connection'] == 'fixed':
            continue
        k = joint['properties']['design']['stiffness_n_m']
        c = joint['properties']['design']['damping_ns_m']
        if joint['connection'] == 'primary':
            stiffness = [5e6, 5e6, k, 5e5, 0., 5e5]
            damping = [2e4, 2e4, c, 3e3, 0., 3e3]
        elif joint['connection'] == 'secondary':
            stiffness = [2e6, 2e6, k, 3e5, 3e5, 3e5]
            damping = [2e4, 2e4, c, 3e3, 3e3, 3e3]
        else:
            stiffness = [1e7, 1e7, k, 1e6, 1e6, 1e4]
            damping = [2e4, 2e4, c, 3e3, 3e3, 1e3]
        bounds = [[-.5, .5]] * 3 + [[-.2, .2]] * 3
        if joint['connection'] == 'primary':
            bounds[4] = [-1000., 1000.]
        laws[joint['id']] = dict(stiffness_si=np.diag(stiffness).tolist(),
            damping_si=np.diag(damping).tolist(), motion_bounds_si=bounds,
            basis='synthetic six-direction equivalent joint; primary spin is free')
    # Smooth, nonconformal verification profiles, deliberately not a standard tread.
    y = np.linspace(-.06, .06, 13)
    profiles = {str(side): [[float(x), float(side*.01*x+x*x/4)] for x in y]
                for side in (-1, 1)}
    load = dict(id='empty', passenger_mass_kg=75., longitudinal_offset_m=1.,
        lateral_offset_m=.3, passenger_cg_height_m=1., mass_uncertainty_fraction=.1)
    return dict(schema='osr-spatial-analysis-input/1',
        basis='synthetic numerical verification, not project acceptance',
        route=dict(radius_m=0., cant_rad=0., cant_start_m=0., cant_end_m=25.,
                   grade_rad=0., basis='synthetic alignment'),
        joint_laws=laws,
        traffic=[dict(id='train-A', track=0, initial_advance_m=45., arrival_time_s=0.,
                      speed_m_s=15., acceleration_m_s2=0., load_case=load)],
        contact=dict(effective_modulus_pa=115e9, rolling_radius_m=.38,
            wheel_profiles=profiles, rail_profile=[[float(x), float(-x*x/.6)] for x in y],
            tangential_stiffness_n_m=1e7, friction_coefficient=.3,
            basis='synthetic profile and Hertz/bristle parameters'),
        irregularity=dict(amplitude_m=0., wavelength_m=10.), wheel_defect=dict(depth_m=0.),
        bridge_damping_ratio=.02, newton_force_tolerance_n=.1)


def scenarios(model):
    base = configuration(model)
    result = {'straight-empty': base}
    curve = deepcopy(base)
    curve['route'].update(radius_m=800., cant_rad=.04)
    curve['traffic'][0]['load_case']['id'] = 'uneven'
    curve['traffic'][0]['acceleration_m_s2'] = -.5
    result['curve-cant-braking-uneven'] = curve
    dual = deepcopy(base)
    dual['traffic'][0]['load_case']['id'] = 'crush'
    other = deepcopy(dual['traffic'][0])
    other.update(id='train-B', track=1, initial_advance_m=50., speed_m_s=12.)
    dual['traffic'].append(other)
    dual['irregularity']['amplitude_m'] = .0005
    dual['wheel_defect']['depth_m'] = .0001
    result['two-track-crush-defect'] = dual
    degraded = deepcopy(base)
    for law in degraded['joint_laws'].values():
        law['stiffness_si'] = (np.asarray(law['stiffness_si'])*.8).tolist()
    degraded['contact']['friction_coefficient'] = .1
    result['degraded-joints-adhesion'] = degraded
    return result
