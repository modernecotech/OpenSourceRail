"""Independent analytical fixtures for the exploration model's limited domain."""
from __future__ import annotations

import math

import numpy as np


def simple_beam(count=16, *, shear=True, springs=None):
    import openseespy.opensees as ops
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    length, E, area, inertia, shear_area, density = 20., 30e9, 1.2, .18, .45, 3000.
    G = E/2.4 if shear else 1e20
    for i in range(count+1):
        ops.node(i+1, length*i/count, 0.)
    if springs is None:
        ops.fix(1, 1, 1, 0); ops.fix(count+1, 0, 1, 0)
    else:
        for tag, node, x in ((count+2, 1, 0.), (count+3, count+1, length)):
            ops.node(tag, x, 0.); ops.fix(tag, 1, 1, 1)
            ops.uniaxialMaterial('Elastic', tag, springs)
            ops.element('zeroLength', tag, tag, node, '-mat', tag, '-dir', 2)
        ops.fix(1, 1, 0, 0)
    ops.geomTransf('Linear', 1)
    for i in range(count):
        ops.element('ElasticTimoshenkoBeam', i+1, i+1, i+2, E, G, area, inertia, shear_area, 1,
                    '-mass', density, '-cMass')
    return ops, dict(length=length, E=E, G=G, area=area, inertia=inertia, shear_area=shear_area, mass_per_m=density)


def static_setup(ops):
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral'); ops.algorithm('Linear')
    ops.integrator('LoadControl', 1.); ops.analysis('Static')
    if ops.analyze(1) != 0:
        raise RuntimeError('native analytical fixture failed')


def moving_point_analytical(t, length, speed, force, EI, mass_per_m, rotary_ratio):
    """Undamped Rayleigh beam modal sum including rotary inertia, 25 modes."""
    exit_time = length/speed
    total = 0.
    for n in range(1, 26):
        inertia_factor = 1+rotary_ratio*(n*math.pi/length)**2
        omega = (n*math.pi/length)**2*math.sqrt(EI/(mass_per_m*inertia_factor))
        excitation = n*math.pi*speed/length
        scale = (2*force/(mass_per_m*length*inertia_factor))/(omega**2-excitation**2)
        def displacement(s):
            return scale*(math.sin(excitation*s)-excitation/omega*math.sin(omega*s))
        if t <= exit_time:
            q = displacement(t)
        else:
            velocity = scale*excitation*(math.cos(excitation*exit_time)-math.cos(omega*exit_time))
            q = displacement(exit_time)*math.cos(omega*(t-exit_time))+velocity/omega*math.sin(omega*(t-exit_time))
        total += q*math.sin(n*math.pi/2)
    return -total


def run():
    from engineering.civil_exploration.model import axle_nodal_loads
    checks = []
    def check(name, actual, expected, tolerance):
        error = abs(actual-expected)/max(abs(expected), 1e-12)
        checks.append(dict(name=name, actual=actual, expected=expected, relative_error=error,
                           relative_tolerance=tolerance, passed=error <= tolerance))
    # Includes native shear deformation, rather than comparing a rectangular
    # surrogate with a Pi section and silently accepting different shear areas.
    for count in (8, 16, 32):
        ops, b = simple_beam(count)
        w = 20000.
        ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1)
        ops.eleLoad('-ele', *range(1, count+1), '-type', '-beamUniform', -w)
        static_setup(ops)
        expected = 5*w*b['length']**4/(384*b['E']*b['inertia'])+w*b['length']**2/(8*b['G']*b['shear_area'])
        check(f'Timoshenko UDL mesh {count}', abs(ops.nodeDisp(count//2+1, 2)), expected, 1e-6)
        ops.reactions()
        check(f'UDL reaction balance {count}', ops.nodeReaction(1, 2)+ops.nodeReaction(count+1, 2), w*b['length'], 1e-8)
    ops, b = simple_beam(16, springs=100e6)
    force = 100000.
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(9, 0., -force, 0.)
    static_setup(ops)
    expected = force*b['length']**3/(48*b['E']*b['inertia'])+force*b['length']/(4*b['G']*b['shear_area'])+force/(2*100e6)
    check('point load plus elastic support settlement', abs(ops.nodeDisp(9, 2)), expected, 1e-6)
    ops, b = simple_beam(32, shear=False)
    frequencies = [math.sqrt(v)/(2*math.pi) for v in ops.eigen('-genBandArpack', 2)]
    for n, frequency in enumerate(frequencies, 1):
        rotary = 1+b['inertia']/b['area']*(n*math.pi/b['length'])**2
        expected = n*n*math.pi/(2*b['length']**2)*math.sqrt(b['E']*b['inertia']/(b['mass_per_m']*rotary))
        check(f'Rayleigh modal frequency {n}', frequency, expected, .002)
    # Independent finite-support cantilever check used for pier/ground coupling.
    import openseespy.opensees as ops
    ops.wipe(); ops.model('basic', '-ndm', 2, '-ndf', 3)
    ops.node(1, 0., 0.); ops.node(2, 0., 0.); ops.node(3, 0., 8.)
    ops.fix(1, 1, 1, 1)
    for i, k in enumerate((10e6, 100e6, 100e6), 1):
        ops.uniaxialMaterial('Elastic', i, k)
    ops.element('zeroLength', 1, 1, 2, '-mat', 1, 2, 3, '-dir', 1, 2, 3)
    ops.geomTransf('Linear', 1)
    ops.element('ElasticTimoshenkoBeam', 2, 2, 3, 30e9, 12.5e9, 3., .5625, 2.5, 1)
    ops.timeSeries('Constant', 1); ops.pattern('Plain', 1, 1); ops.load(3, 100000., 0., 0.)
    static_setup(ops)
    expected = 100000.*(8**3/(3*30e9*.5625)+8/(12.5e9*2.5)+1/10e6+8**2/100e6)
    check('pier bending, shear, foundation translation and rotation', abs(ops.nodeDisp(3, 1)), expected, 1e-6)
    # Moving-force benchmark: separate closed-form modal superposition, not
    # comparison of two runs of the same solver. Refine mesh and time together.
    errors = []
    for count, dt in ((16, .01), (32, .005), (64, .0025)):
        ops, b = simple_beam(count, shear=False)
        length, speed, force = b['length'], 10., 100000.
        times = np.arange(0, length/speed+dt/2, dt)
        matrix = np.asarray([axle_nodal_loads(np.linspace(0, length, count+1), speed*t, [0.], [force]) for t in times])
        for node in range(1, count+2):
            ops.timeSeries('Path', node, '-dt', dt, '-values', *(-matrix[:, node-1]).tolist())
            ops.pattern('Plain', node, node); ops.load(node, 0., 1., 0.)
        ops.constraints('Plain'); ops.numberer('RCM'); ops.system('BandGeneral'); ops.algorithm('Linear')
        ops.integrator('Newmark', .5, .25); ops.analysis('Transient')
        actual, exact = [], []
        for t in times[1:]:
            if ops.analyze(1, dt) != 0:
                raise RuntimeError('moving-force fixture failed')
            actual.append(ops.nodeDisp(count//2+1, 2))
            exact.append(moving_point_analytical(float(t), length, speed, force, b['E']*b['inertia'], b['mass_per_m'], b['inertia']/b['area']))
        error = float(np.max(np.abs(np.asarray(actual)-exact))/max(abs(v) for v in exact))
        errors.append(error)
        checks.append(dict(name=f'moving-force mesh {count} dt {dt}', normalised_history_error=error,
                           relative_tolerance=.06, passed=error < .06))
    checks.append(dict(name='moving-force refinement improves agreement', errors=errors,
                       passed=errors[-1] < errors[0] and errors[-1] < .01))
    ops.wipe()
    return dict(schema='osr-civil-benchmarks/1', passed=all(c['passed'] for c in checks), checks=checks,
                applicability='Linear 2D, elastic Timoshenko sections, linear springs, smooth moving point forces; verification only.',
                physical_validation=False)
