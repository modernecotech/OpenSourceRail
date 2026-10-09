"""Native research concrete/steel sections, P-delta piers and nonlinear piles.

These models require supplied properties. Demonstration profiles are synthetic
verification cases, never site-calibrated resistance or approved reinforcement.
"""
from __future__ import annotations
import math
from pathlib import Path
import csv

from osr_mech.civil.exploration import section_properties


def fields(value, required):
    if set(value) != set(required):
        raise ValueError('nonlinear contract fields differ: '+str(set(value)^set(required)))
    for key, v in value.items():
        if key not in ('basis', 'measured') and (type(v) not in (float, int) or not math.isfinite(v)):
            raise ValueError('nonlinear input must be finite: '+key)
    if type(value['basis']) is not str or not value['basis'] or type(value['measured']) is not bool:
        raise ValueError('research profile needs explicit property provenance')


def setup(ops):
    ops.constraints('Plain'); ops.numberer('RCM'); ops.system('UmfPack')
    ops.test('NormUnbalance', 1e-5, 100); ops.algorithm('NewtonLineSearch')


def curve_file(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def fibre_section(ops, regions, material, steel, tag=1):
    fields(material, ('fpc_pa','peak_strain','residual_pa','ultimate_strain','unloading_ratio','tensile_pa','softening_pa','basis','measured'))
    fields(steel, ('yield_pa','modulus_pa','hardening_ratio','reinforcement_ratio','cover_m','basis','measured'))
    if not (material['fpc_pa'] < material['residual_pa'] < 0 and material['ultimate_strain'] < material['peak_strain'] < 0):
        raise ValueError('concrete compression/softening signs or ordering invalid')
    if not 0 < material['unloading_ratio'] < 1 or min(material['tensile_pa'], material['softening_pa']) <= 0:
        raise ValueError('invalid concrete tension/unloading properties')
    if not 0 < steel['reinforcement_ratio'] < .1 or not 0 <= steel['hardening_ratio'] < 1 or min(steel['yield_pa'], steel['modulus_pa'], steel['cover_m']) <= 0:
        raise ValueError('invalid steel reinforcement properties')
    s = section_properties(regions)
    ops.uniaxialMaterial('Concrete02', tag*10, material['fpc_pa'], material['peak_strain'], material['residual_pa'],
                         material['ultimate_strain'], material['unloading_ratio'], material['tensile_pa'], material['softening_pa'])
    ops.uniaxialMaterial('Steel01', tag*10+1, steel['yield_pa'], steel['modulus_pa'], steel['hardening_ratio'])
    ops.section('Fiber', tag)
    ratio = steel['reinforcement_ratio']
    for r in regions:
        # Two-point Gauss integration gives exact initial area/second moment.
        for layer in range(16):
            lo = r['z_m']-r['height_m']/2+layer*r['height_m']/16
            hi = lo+r['height_m']/16
            for sign in (-1., 1.):
                coordinate = (lo+hi)/2+sign*(hi-lo)/(2*math.sqrt(3))
                ops.fiber(coordinate-s['centroid_z_m'], r['y_m'], r['width_m']*(hi-lo)/2*(1-ratio), tag*10)
    bar_locations = [s['bottom_m']+steel['cover_m']-s['centroid_z_m'], s['top_m']-steel['cover_m']-s['centroid_z_m']]
    if min(bar_locations) >= 0 or max(bar_locations) <= 0:
        raise ValueError('reinforcement cover does not fit the section')
    for location in bar_locations:
        ops.fiber(location, 0., s['area_m2']*ratio/2, tag*10+1)
    concrete_E = 2*material['fpc_pa']/material['peak_strain']
    stiffness = concrete_E*s['inertia_y_m4']*(1-ratio)+sum(steel['modulus_pa']*s['area_m2']*ratio/2*y*y for y in bar_locations)
    return dict(section=s, initial_EI_nm2=stiffness, reinforcement_area_m2=s['area_m2']*ratio,
                reinforcement='lumped top/bottom layers; not fabrication detailing')


def moment_curvature(regions, concrete, steel, *, axial_force_n=0., target_curvature=.006, steps=120, output=None):
    import openseespy.opensees as ops
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3)
    ops.node(1,0.,0.); ops.node(2,0.,0.); ops.fix(1,1,1,1); ops.fix(2,0,1,0)
    section = fibre_section(ops, regions, concrete, steel)
    ops.element('zeroLengthSection',1,1,2,1)
    ops.timeSeries('Constant',1); ops.pattern('Plain',1,1); ops.load(2,-axial_force_n,0.,0.)
    setup(ops); ops.integrator('LoadControl',1.); ops.analysis('Static')
    if ops.analyze(1):
        raise RuntimeError('nonlinear section axial load did not converge')
    ops.loadConst('-time',0.)
    ops.timeSeries('Linear',2); ops.pattern('Plain',2,2); ops.load(2,0.,0.,1.)
    rows=[]; status='completed'
    # Register a small first increment for an independent elastic tangent check.
    targets=[1e-7]+[target_curvature*i/steps for i in range(1,steps+1)]
    for target in targets:
        ops.integrator('DisplacementControl',2,3,target-ops.nodeDisp(2,3))
        if ops.analyze(1):
            status='nonconverged'; break
        ops.reactions()
        rows.append(dict(curvature_per_m=ops.nodeDisp(2,3), moment_nm=-ops.nodeReaction(1,3), axial_strain=ops.nodeDisp(2,1)))
    if not rows:
        raise RuntimeError('no nonlinear section results')
    if output: curve_file(output,rows)
    return dict(schema='osr-civil-moment-curvature/1',status=status,initial_EI_nm2=section['initial_EI_nm2'],
                observed_initial_EI_nm2=rows[0]['moment_nm']/rows[0]['curvature_per_m'],
                peak_moment_nm=max(abs(r['moment_nm']) for r in rows),curve=rows,
                axial_force_n=axial_force_n,material_inputs=dict(concrete=concrete,steel=steel),
                physical_validation=False,physical_release=False,
                gaps=['measured stress/strain and confinement','bar/tendon detailing','cyclic degradation and bond','independent physical tests'])


def pile(profile, output=None):
    import openseespy.opensees as ops
    fields(profile, ('length_m','diameter_m','modulus_pa','elements','pult_n_m','y50_m','tult_n_m','z50_m',
                     'tip_ultimate_n','tip_z50_m','group_reduction','axial_force_n','lateral_force_n','steps','basis','measured'))
    positive=[v for k,v in profile.items() if k not in ('basis','measured')]
    if min(positive) <= 0 or not 0 < profile['group_reduction'] <= 1 or type(profile['elements']) is not int or type(profile['steps']) is not int:
        raise ValueError('invalid pile dimensions or spring/load parameters')
    n=profile['elements']; dz=profile['length_m']/n; d=profile['diameter_m']
    ops.wipe(); ops.model('basic','-ndm',2,'-ndf',3); ops.geomTransf('PDelta',1)
    springs=[]
    for i in range(n+1):
        node=i+1; ground=1000+i
        ops.node(node,0.,-i*dz); ops.node(ground,0.,-i*dz); ops.fix(ground,1,1,1)
        tributary=dz/2 if i in (0,n) else dz
        p=profile['pult_n_m']*tributary*profile['group_reduction']
        t=profile['tult_n_m']*tributary
        ops.uniaxialMaterial('PySimple1',2000+i,2,p,profile['y50_m'],0.)
        ops.uniaxialMaterial('TzSimple1',3000+i,2,t,profile['z50_m'])
        ops.element('zeroLength',1000+i,ground,node,'-mat',2000+i,3000+i,'-dir',1,2)
        springs.append(dict(node=node,tributary_m=tributary,pult_n=p,tult_n=t,element_id=1000+i))
    ops.uniaxialMaterial('QzSimple1',4000,2,profile['tip_ultimate_n'],profile['tip_z50_m'],0.,0.)
    ops.element('zeroLength',4000,1000+n,n+1,'-mat',4000,'-dir',2)
    for i in range(n):
        ops.element('elasticBeamColumn',i+1,i+1,i+2,math.pi*d*d/4,profile['modulus_pa'],math.pi*d**4/64,1)
    ops.timeSeries('Linear',1); ops.pattern('Plain',1,1)
    ops.load(1,profile['lateral_force_n'],-profile['axial_force_n'],0.)
    setup(ops); ops.integrator('LoadControl',1/profile['steps']); ops.analysis('Static')
    rows=[]; status='completed'
    for step in range(profile['steps']):
        if ops.analyze(1):status='nonconverged';break
        ops.reactions(); factor=ops.getLoadFactor(1)
        horizontal=sum(ops.nodeReaction(1000+i,1) for i in range(n+1))
        vertical=sum(ops.nodeReaction(1000+i,2) for i in range(n+1))
        if not math.isclose(horizontal,-profile['lateral_force_n']*factor,abs_tol=1.,rel_tol=1e-6) or not math.isclose(vertical,profile['axial_force_n']*factor,abs_tol=1.,rel_tol=1e-6):
            raise ValueError('nonlinear pile reaction balance failed')
        rows.append(dict(load_factor=factor,head_lateral_m=ops.nodeDisp(1,1),head_settlement_m=-ops.nodeDisp(1,2),
                         peak_moment_nm=max(abs(ops.eleForce(i+1)[j]) for i in range(n) for j in (2,5))))
    if not rows:raise RuntimeError('no nonlinear pile results')
    if output:curve_file(output,rows)
    return dict(schema='osr-civil-nonlinear-pile/1',status=status,curve=rows,springs=springs,profile=profile,
                transformations='PDelta',native_materials=['PySimple1','TzSimple1','QzSimple1'],physical_release=False,
                gaps=['site spring calibration','pile group interaction beyond supplied reduction','groundwater/scour/liquefaction','instrumented axial/lateral tests'])


def pier_pdelta(height_m, area_m2, inertia_m4, modulus_pa, axial_n, horizontal_n):
    """Finite-column second-order response, independently checked by a fixture."""
    import openseespy.opensees as ops
    responses={}
    for transform in ('Linear','PDelta'):
        ops.wipe();ops.model('basic','-ndm',2,'-ndf',3);ops.geomTransf(transform,1)
        for i in range(17):ops.node(i+1,0.,height_m*i/16)
        ops.fix(1,1,1,1)
        for i in range(16):ops.element('elasticBeamColumn',i+1,i+1,i+2,area_m2,modulus_pa,inertia_m4,1)
        ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(17,horizontal_n,-axial_n,0.)
        setup(ops);ops.integrator('LoadControl',.05);ops.analysis('Static')
        if ops.analyze(20):raise RuntimeError('P-delta column nonconvergence')
        responses[transform]=ops.nodeDisp(17,1)
    critical=math.pi**2*modulus_pa*inertia_m4/(4*height_m**2)
    k=math.sqrt(axial_n/(modulus_pa*inertia_m4))
    analytical=horizontal_n/axial_n*(math.tan(k*height_m)/k-height_m)
    return dict(linear_drift_m=responses['Linear'],pdelta_drift_m=responses['PDelta'],
                amplification=responses['PDelta']/responses['Linear'],euler_cantilever_load_n=critical,
                axial_fraction_of_euler=axial_n/critical,analytical_drift_m=analytical,
                analytical_relative_error=abs(responses['PDelta']/analytical-1),physical_release=False,
                domain='elastic finite-column second-order verification; no concrete strength acceptance')
