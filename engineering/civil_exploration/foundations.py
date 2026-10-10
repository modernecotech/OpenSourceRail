"""Native elastic pile groups condensed to a coupled cap stiffness.

Soil laws are declared research scenarios, not Baghdad resistance or calibrated
p-y curves. Installation methods receive no automatic geotechnical benefit.
"""
from __future__ import annotations
import math

import numpy as np
from osr_mech.civil.exploration import foundation_geometry


def pile_section(parameters):
    d=parameters['pile_diameter_m'];inner=parameters.get('pile_inner_diameter_m',0.)
    if parameters.get('pile_shape','round')=='square':
        return dict(area_m2=d*d,inertia_m4=d**4/12,perimeter_m=4*d,toe_area_m2=d*d)
    return dict(area_m2=math.pi*(d*d-inner*inner)/4,inertia_m4=math.pi*(d**4-inner**4)/64,
                perimeter_m=math.pi*d,toe_area_m2=math.pi*(d*d-inner*inner)/4)


def validate_soil(soil):
    required={'id','basis','calibrated','lateral_n_m2','shaft_n_m2','toe_n_m3','spread_vertical_n_m3',
              'spread_horizontal_n_m3','skin_resistance_pa','toe_resistance_pa','spread_bearing_pa',
              'group_efficiency','planning_resistance_factor'}
    if set(soil)!=required or not soil['basis'] or not soil['id'] or type(soil['calibrated']) is not bool:
        raise ValueError('soil scenario coverage incomplete')
    # Measured/calibrated records need the existing source-bound study workflow.
    if soil['calibrated']:raise ValueError('system research soil cannot self-declare site calibration')
    for key in required-{'id','basis','calibrated'}:
        v=soil[key]
        if type(v) not in (int,float) or not math.isfinite(v) or v<=0:
            raise ValueError('soil scenario needs positive finite inputs: '+key)
    if soil['group_efficiency']>1 or soil['planning_resistance_factor']>1:
        raise ValueError('soil efficiency/resistance factors exceed unity')


def stiffness(parameters,material,soil,elements=8,*,axis='longitudinal'):
    """Three independent unit loads identify the full planar cap compliance."""
    validate_soil(soil);geo=foundation_geometry(parameters)
    if axis not in ('longitudinal','transverse'):raise ValueError('unknown foundation axis')
    if type(elements) is not int or not 2<=elements<=64:raise ValueError('pile discretisation outside bounds')
    if not geo['piles']:
        L,W,_=geo['cap_dimensions_m'];area=L*W
        if axis=='transverse':L,W=W,L
        K=np.diag([soil['spread_horizontal_n_m3']*area,soil['spread_vertical_n_m3']*area,
                   soil['spread_vertical_n_m3']*W*L**3/12])
        nominal=soil['spread_bearing_pa']*area
    else:
        import openseespy.opensees as ops
        ops.wipe();ops.model('basic','-ndm',2,'-ndf',3);ops.geomTransf('Linear',1)
        ops.node(1,0.,0.);node=1;element=0;mat=0
        E=material['youngs_modulus_pa']*material['stiffness_factor'];G=E/(2*(1+material['poisson_ratio']))
        p=pile_section(parameters);eff=soil['group_efficiency'];length=parameters['pile_length_m']
        def spring(first,second,ks):
            nonlocal element,mat
            tags=[]
            for k in ks:
                mat+=1;ops.uniaxialMaterial('Elastic',mat,k);tags.append(mat)
            element+=1;ops.element('zeroLength',element,first,second,'-mat',*tags,'-dir',1,2)
        for pile in geo['piles']:
            x=pile['centre_xy_m'][0 if axis=='longitudinal' else 1];head_y=-parameters['cap_depth_m']
            node+=1;head=node;ops.node(head,x,head_y);ops.rigidLink('beam',1,head)
            previous=head;step=length/elements
            for i in range(elements+1):
                if i:
                    node+=1;current=node;ops.node(current,x,head_y-i*step)
                    element+=1;ops.element('ElasticTimoshenkoBeam',element,previous,current,E,G,p['area_m2'],p['inertia_m4'],5*p['area_m2']/6,1)
                    previous=current
                current=previous
                node+=1;anchor=node;ops.node(anchor,x,head_y-i*step);ops.fix(anchor,1,1,1)
                tributary=step/2 if i in (0,elements) else step
                axial=soil['shaft_n_m2']*tributary*eff
                if i==elements:axial+=soil['toe_n_m3']*p['toe_area_m2']*eff
                spring(anchor,current,[soil['lateral_n_m2']*tributary*eff,axial])
        F=[]
        for axis in range(3):
            tag=100+axis;ops.timeSeries('Constant',tag);ops.pattern('Plain',tag,tag)
            load=[0.,0.,0.];load[axis]=1.;ops.load(1,*load)
            ops.wipeAnalysis();ops.constraints('Transformation');ops.numberer('RCM');ops.system('BandGeneral')
            ops.algorithm('Linear');ops.integrator('LoadControl',1.);ops.analysis('Static')
            if ops.analyze(1):raise RuntimeError('pile-group unit load failed')
            F.append(ops.nodeDisp(1));ops.remove('loadPattern',tag);ops.remove('timeSeries',tag)
        compliance=np.asarray(F).T
        if not np.allclose(compliance,compliance.T,rtol=1e-7,atol=1e-13):
            raise ValueError('pile-group compliance violates reciprocity')
        K=np.linalg.inv(compliance)
        K=(K+K.T)/2  # Reciprocity was checked before removing roundoff.
        nominal=parameters['pile_count']*eff*(soil['skin_resistance_pa']*p['perimeter_m']*length+soil['toe_resistance_pa']*p['toe_area_m2'])
    if min(np.linalg.eigvalsh(K))<=0:raise ValueError('foundation stiffness lacks positive energy')
    # Symmetric pile grids decouple vertical action from the other two axes.
    if max(abs(K[0,1]),abs(K[1,2]))>1e-7*max(np.diag(K)):
        raise ValueError('asymmetric foundation needs a full three-way coupling adapter')
    K[0,1]=K[1,0]=K[1,2]=K[2,1]=0.
    return dict(name=soil['id'],basis=soil['basis'],calibrated=False,
                lateral_stiffness_n_m=float(K[0,0]),axial_stiffness_n_m=float(K[1,1]),
                rotational_stiffness_nm_rad=float(K[2,2]),horizontal_rotation_coupling_n=float(K[0,2]),
                stiffness_matrix=K.tolist(),elements_per_pile=elements,axis=axis,
                planning_axial_resistance_n=nominal*soil['planning_resistance_factor'],
                planning_resistance_basis='synthetic linear soil and nominal strength; not a code resistance or site design',
                limitations=['soil layering/nonlinearity','group shadowing calibration','uplift/cyclic/seismic/liquefaction','scour/groundwater/chemistry','cap structural design'],
                physical_release=False)


def refinement(parameters,material,soil,*,axis='longitudinal'):
    rows=[];error=math.inf
    for n in (4,8,16,32,64):
        rows.append(stiffness(parameters,material,soil,n,axis=axis))
        if len(rows)<3:continue
        fine=np.asarray(rows[-1]['stiffness_matrix']);medium=np.asarray(rows[-2]['stiffness_matrix'])
        error=float(np.linalg.norm(fine-medium)/np.linalg.norm(fine))
        if error<=.05:break
    return dict(levels=rows,relative_stiffness_change=error,relative_limit=.05,passed=error<=.05,
                selected=rows[-1],maximum_elements_per_pile=64,physical_release=False)
