"""Native cyclic friction-bearing and finite connection verification fixtures."""
from __future__ import annotations
import math
from .nonlinear import curve_file


def friction_cycle(output=None,normal_force_n=1e6,friction=.3,initial_stiffness_n_m=1e8):
    import openseespy.opensees as ops
    if min(normal_force_n,friction,initial_stiffness_n_m)<=0 or friction>1:
        raise ValueError('invalid contact/friction parameters')
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',3)
    ops.node(1,0.,0.);ops.node(2,0.,0.);ops.fix(1,1,1,1)
    ops.frictionModel('Coulomb',1,friction)
    ops.uniaxialMaterial('Elastic',1,1e9);ops.uniaxialMaterial('Elastic',2,1e8)
    ops.element('flatSliderBearing',1,1,2,1,initial_stiffness_n_m,'-P',1,'-Mz',2,'-orient',0.,1.,0.,-1.,0.,0.)
    ops.timeSeries('Constant',1);ops.pattern('Plain',1,1);ops.load(2,0.,-normal_force_n,0.)
    ops.constraints('Transformation');ops.numberer('RCM');ops.system('UmfPack')
    ops.test('NormUnbalance',1e-5,100);ops.algorithm('NewtonLineSearch');ops.integrator('LoadControl',1.);ops.analysis('Static')
    if ops.analyze(1):raise RuntimeError('bearing normal preload failed')
    ops.loadConst('-time',0.)
    positions=[0.,.001,.002,.004,.006,.01,.006,.002,0.,-.004,-.01,-.004,0.]
    ops.timeSeries('Path',2,'-dt',1.,'-values',*positions);ops.pattern('Plain',2,2);ops.sp(2,1,1.)
    ops.wipeAnalysis();ops.constraints('Transformation');ops.numberer('RCM');ops.system('BandGeneral')
    ops.test('NormUnbalance',1e-5,100);ops.algorithm('NewtonLineSearch');ops.integrator('LoadControl',1.);ops.analysis('Static')
    rows=[]
    for _ in positions[1:]:
        if ops.analyze(1):raise RuntimeError('bearing cyclic imposed displacement failed')
        force=ops.eleForce(1)
        rows.append(dict(slip_m=ops.nodeDisp(2,1),shear_n=force[3],normal_n=-force[4]))
    if output:curve_file(output,rows)
    limit=normal_force_n*friction
    peak=max(abs(r['shear_n']) for r in rows)
    return dict(schema='osr-civil-friction-joint/1',curve=rows,expected_coulomb_limit_n=limit,
                peak_shear_n=peak,benchmark_passed=math.isclose(peak,limit,rel_tol=1e-6),
                physical_release=False,domain='native flat slider, constant compression, ideal Coulomb cyclic slip',
                gaps=['measured friction/rate/temperature','connection anchorage','wear, fatigue and bearing replacement'])
