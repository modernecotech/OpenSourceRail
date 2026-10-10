"""Declared elastic torsion and composite slip diagnostics; no capacity claim."""
from __future__ import annotations
import math
import numpy as np


def rectangle_torsion(width,height,terms=100):
    """Saint-Venant rectangle series, not its polar second moment of area."""
    if min(width,height)<=0:raise ValueError('positive torsion dimensions required')
    a,b=max(width,height),min(width,height)
    series=sum(math.tanh(n*math.pi*a/(2*b))/n**5 for n in range(1,2*terms,2))
    return a*b**3*(1/3-64*b/(math.pi**5*a)*series)


def matrix(section,records,closed=False):
    regions=section['regions'];roles=section.get('material_roles',['concrete']*len(regions));rows=[]
    for r,role in zip(regions,roles):
        m=records[role];E=m['youngs_modulus_pa']*m.get('stiffness_factor',1.)
        component='gxz_pa' if r['height_m']>r['width_m'] else 'gxy_pa'
        G=m['orthotropic'][component]*m.get('stiffness_factor',1.) if m.get('orthotropic') else E/(2*(1+m['poisson_ratio']))
        rows.append((r,role,E,G,r['width_m']*r['height_m']))
    EA=sum(E*A for _,_,E,_,A in rows);yc=sum(r['y_m']*E*A for r,_,E,_,A in rows)/EA
    zc=sum(r['z_m']*E*A for r,_,E,_,A in rows)/EA
    EIy=sum(E*A*(r['height_m']**2/12+(r['z_m']-zc)**2) for r,_,E,_,A in rows)
    EIz=sum(E*A*(r['width_m']**2/12+(r['y_m']-yc)**2) for r,_,E,_,A in rows)
    if closed and len(rows)%4==0:
        GJ=0.
        for i in range(0,len(rows),4):
            top,bottom,left,right=rows[i:i+4]
            w=abs(right[0]['y_m']-left[0]['y_m']);h=abs(top[0]['z_m']-bottom[0]['z_m'])
            compliance=(w/(top[3]*top[0]['height_m'])+w/(bottom[3]*bottom[0]['height_m'])+
                        h/(left[3]*left[0]['width_m'])+h/(right[3]*right[0]['width_m']))
            GJ+=4*(w*h)**2/compliance
        torsion_basis='thin-wall closed-cell Bredt model; concentric skins share rotation through assumed perfect bond'
    else:
        GJ=sum(G*rectangle_torsion(r['width_m'],r['height_m']) for r,_,_,G,_ in rows)
        torsion_basis='Saint-Venant rectangular regions; additive open strips, warping/distortion and junction corrections uncovered'
    return dict(EA_n=EA,EIy_nm2=EIy,EIz_nm2=EIz,GJ_nm2=GJ,centroid_y_m=yc,centroid_z_m=zc,
                torsion_basis=torsion_basis,capacity_qualified=False)


def partial_interaction(span,top,bottom,connector_n_m2,load_n_m,elements=24):
    """Two axial layers, shared Euler-Bernoulli bending and distributed slip.

    DOFs per node: upper/lower axial displacement, vertical displacement and
    rotation. Interface energy is integral(k*(u1-u2+d*rotation)^2)/2.
    Measures empty/noncomposite vs perfect-bond limits without inventing bond.
    """
    for layer in (top,bottom):
        if set(layer)!={'E_pa','area_m2','inertia_m4','centroid_z_m'} or any(type(v) not in (int,float) or not math.isfinite(v) for v in layer.values()):
            raise ValueError('composite layer units/coverage invalid')
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (span,connector_n_m2,load_n_m)) or type(elements) is not int:
        raise ValueError('composite input must be finite')
    if min(span,top['E_pa'],bottom['E_pa'],top['area_m2'],bottom['area_m2'],top['inertia_m4'],bottom['inertia_m4'])<=0 or connector_n_m2<0 or load_n_m<0 or not 4<=elements<=200:
        raise ValueError('partial interaction input outside domain')
    n=4*(elements+1);K=np.zeros((n,n));f=np.zeros(n);L=span/elements;d=abs(top['centroid_z_m']-bottom['centroid_z_m'])
    EI=top['E_pa']*top['inertia_m4']+bottom['E_pa']*bottom['inertia_m4']
    kb=EI/L**3*np.asarray([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
    points,weights=np.polynomial.legendre.leggauss(3)
    for i in range(elements):
        local=np.zeros((8,8));indices=list(range(4*i,4*i+8));bending=[2,3,6,7]
        local[np.ix_(bending,bending)]+=kb
        for layer,mat in ((0,top),(1,bottom)):
            ix=[layer,layer+4];local[np.ix_(ix,ix)]+=mat['E_pa']*mat['area_m2']/L*np.asarray([[1.,-1.],[-1.,1.]])
        for point,weight in zip(points,weights):
            x=(point+1)/2
            rotation=np.asarray([(-6*x+6*x*x)/L,1-4*x+3*x*x,(6*x-6*x*x)/L,-2*x+3*x*x])
            slip=np.zeros(8);slip[[0,4]]=[1-x,x];slip[[1,5]]=[x-1,-x];slip[bending]+=d*rotation
            local+=connector_n_m2*np.outer(slip,slip)*weight*L/2
        K[np.ix_(indices,indices)]+=local
        f[[4*i+2,4*i+3,4*i+6,4*i+7]]+=load_n_m*np.asarray([L/2,L*L/12,L/2,-L*L/12])
    fixed={1,2,4*elements+2}
    if connector_n_m2==0:fixed.add(0)
    free=[i for i in range(n) if i not in fixed];u=np.zeros(n);u[free]=np.linalg.solve(K[np.ix_(free,free)],f[free])
    reactions=K@u-f
    if not math.isclose(-sum(reactions[i] for i in fixed if i%4==2),load_n_m*span,rel_tol=1e-7):raise ValueError('partial interaction reaction balance failed')
    coupled_EI=EI+top['E_pa']*top['area_m2']*bottom['E_pa']*bottom['area_m2']/(top['E_pa']*top['area_m2']+bottom['E_pa']*bottom['area_m2'])*d*d
    return dict(peak_deflection_m=float(max(abs(u[2::4]))),maximum_interface_slip_m=float(max(abs(u[0::4]-u[1::4]+d*u[3::4]))),
                noncomposite_limit_m=5*load_n_m*span**4/(384*EI),perfect_bond_limit_m=5*load_n_m*span**4/(384*coupled_EI),
                connector_n_m2=connector_n_m2,elements=elements,physical_validation=False,
                domain='linear two-layer axial/bending/shear-slip coupling; no debonding, local failure or cyclic/fire law')
