"""Free-free beam modes and work-conjugate modal attachment operators.

The beam verifies numerical transfer, not local shell/joint resistance. Generated
shells have separate identities and masses; no empty body box becomes material.
"""
from pathlib import Path
import math
import numpy as np
from scipy.linalg import eigh
from engineering.industrialisation.common import finite, fingerprint


def read_native_modes(path):
    active=False;rows=[]
    for line in Path(path).read_text().splitlines():
        if 'E I G E N V A L U E   O U T P U T' in line:active=True;continue
        if active and 'P A R T I C I P A T I O N' in line:break
        f=line.split()
        if active and len(f)==5 and f[0].isdigit():
            values=[float(x) for x in f[1:]]
            if not np.isfinite(values).all() or values[2]<0 or values[3]!=0:raise ValueError('unsupported native modal result')
            rows.append(dict(mode=int(f[0]),eigenvalue=values[0],frequency_hz=values[2]))
    if [r['mode'] for r in rows]!=list(range(1,13)):raise ValueError('complete twelve-mode native shell output required')
    rigid=max(r['frequency_hz'] for r in rows[:6])<.01
    if not rigid or min(r['frequency_hz'] for r in rows[6:])<=.05:raise ValueError('native shell rigid/flexible modal separation failed')
    return dict(modes=rows,near_zero_rigid_modes=6,rigid_verification_threshold_hz=.01,frequency_order_comparison_only=True,
        physical_modal_correlation=False,full_spatial_insertion=False)


def beam_modes(length_m, mass_per_m, ei_nm2, *, elements=24, modes=6):
    L=finite(length_m,'beam length',1e-6);rho=finite(mass_per_m,'line mass',1e-6);EI=finite(ei_nm2,'bending stiffness',1e-6)
    if type(elements) is not int or not 4<=elements<=128 or not 1<=modes<=min(20,2*elements):raise ValueError('modal budget outside bounds')
    h=L/elements;K=np.zeros((2*(elements+1),)*2);M=K.copy()
    ke=EI/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
    me=rho*h/420*np.array([[156,22*h,54,-13*h],[22*h,4*h*h,13*h,-3*h*h],[54,13*h,156,-22*h],[-13*h,-3*h*h,-22*h,4*h*h]])
    for i in range(elements):
        ix=np.arange(2*i,2*i+4);K[np.ix_(ix,ix)]+=ke;M[np.ix_(ix,ix)]+=me
    values,vectors=eigh(K,M);order=np.arange(2,2+modes);lam=values[order];phi=vectors[:,order]
    if np.any(lam<=0):raise ValueError('positive flexible modes required')
    return dict(schema='osr-free-free-beam-modes/1',length_m=L,line_mass_kg_m=rho,ei_nm2=EI,elements=elements,
        nodes_x_m=np.linspace(0,L,elements+1).tolist(),frequencies_hz=(np.sqrt(lam)/(2*math.pi)).tolist(),
        shapes_mass_normalized=phi.tolist(),modal_mass=(phi.T@M@phi).tolist(),modal_stiffness=(phi.T@K@phi).tolist(),
        rigid_mode_count=2,rigid_mode_eigenvalues=values[:2].tolist(),physical_validation=False,
        basis='Euler-Bernoulli vertical bending verification; torsion/shell/openings/equipment distribution not represented')


def attachment_shape(model, station_m):
    x=finite(station_m,'attachment station',0.);L=model['length_m'];n=model['elements']
    if x>L:raise ValueError('attachment outside component')
    h=L/n;i=min(n-1,int(x/h));s=(x-i*h)/h
    N=np.array([1-3*s*s+2*s**3,h*(s-2*s*s+s**3),3*s*s-2*s**3,h*(-s*s+s**3)])
    return N@np.asarray(model['shapes_mass_normalized'])[2*i:2*i+4]


def modal_joint(model,station_m,stiffness_n_m,*,rigid_dofs=2):
    """Couple body heave/pitch plus flexible modes to an external attachment."""
    if rigid_dofs!=2:raise ValueError('heave/pitch operator requires two rigid coordinates')
    k=finite(stiffness_n_m,'attachment stiffness',1e-6)
    B=np.r_[1.,station_m-model['length_m']/2,attachment_shape(model,station_m),-1.]
    return dict(displacement_map=B.tolist(),stiffness_si=(k*np.outer(B,B)).tolist(),mode_model_sha256=fingerprint(model),
        basis='work-conjugate vertical attachment; independent subassembly, full spatial insertion pending')


def carbody_shell(output, *, length=18.5, width=2.65, floor=.8, roof=3.25, door_x=(-4.255,4.255), door_width=1.27, door_top=3.,thickness=.003,youngs_pa=210e9,density=7850.,mesh=.6):
    """Create an original hollow S4 shell with exact door opening boundaries."""
    for v,name in [(length,'length'),(width,'width'),(thickness,'thickness'),(youngs_pa,'modulus'),(density,'density'),(mesh,'mesh')]:finite(v,name,1e-9)
    if not floor<door_top<roof or mesh<.1 or mesh>2:raise ValueError('shell opening/mesh outside domain')
    path=Path(output)
    if path.exists():raise ValueError('retain previous shell evidence')
    path.mkdir(parents=True);xs=sorted(set([round(float(x),10) for x in np.linspace(-length/2,length/2,math.ceil(length/mesh)+1)]+[x+s*door_width/2 for x in door_x for s in (-1,1)]))
    if min(xs)<-length/2 or max(xs)>length/2:raise ValueError('door outside body')
    ys=np.linspace(-width/2,width/2,math.ceil(width/mesh)+1);zs=sorted(set([floor,door_top,roof,*np.linspace(floor,roof,math.ceil((roof-floor)/mesh)+1)]))
    nodes={};elements=[];area=0.
    def node(p):
        key=tuple(round(float(v),9) for v in p)
        return nodes.setdefault(key,len(nodes)+1)
    def quad(p):
        nonlocal area
        elements.append([node(v) for v in p]);area+=float(np.linalg.norm(np.cross(np.array(p[1])-p[0],np.array(p[3])-p[0])))
    for a,b in zip(xs,xs[1:]):
        for y0,y1 in zip(ys,ys[1:]):
            for z in (floor,roof):quad([[a,y0,z],[b,y0,z],[b,y1,z],[a,y1,z]])
        for z0,z1 in zip(zs,zs[1:]):
            if z1<=door_top and any(abs((a+b)/2-x)<door_width/2-1e-9 for x in door_x):continue
            for y in (-width/2,width/2):quad([[a,y,z0],[b,y,z0],[b,y,z1],[a,y,z1]])
    for x in (-length/2,length/2):
        for y0,y1 in zip(ys,ys[1:]):
            for z0,z1 in zip(zs,zs[1:]):quad([[x,y0,z0],[x,y1,z0],[x,y1,z1],[x,y0,z1]])
    lines=['*HEADING','OSR proposed hollow carbody with four door portals; assumed steel; no release','*NODE']
    lines += [str(i)+','+','.join(map(str,p)) for p,i in nodes.items()]
    lines += ['*ELEMENT,TYPE=S4,ELSET=BODY']+[str(i)+','+','.join(map(str,p)) for i,p in enumerate(elements,1)]
    lines += ['*NSET,NSET=ALL,GENERATE',f'1,{len(nodes)},1']
    lines += ['*MATERIAL,NAME=ASSUMED_STEEL','*ELASTIC',f'{youngs_pa},0.3','*DENSITY',str(density),'*SHELL SECTION,ELSET=BODY,MATERIAL=ASSUMED_STEEL',str(thickness),'*STEP','*FREQUENCY','12','*NODE FILE','U','*END STEP']
    (path/'carbody.inp').write_text('\n'.join(lines)+'\n')
    return dict(schema='osr-hollow-carbody-shell/1',node_count=len(nodes),element_count=len(elements),material_area_m2=area,mass_kg=area*thickness*density,
        roof_z_m=roof,portal_count=4,thickness_m=thickness,model_definition_sha256=fingerprint(dict(nodes={str(i):p for p,i in nodes.items()},elements=elements,thickness=thickness,youngs_pa=youngs_pa,density=density)),
        installation_variant='proposed raised-roof structural article; separate from current rigid-body residual allocation',
        open_domains=['frame/roof/underframe load paths','bogie shell and joint details','equipment mounting mass','shell convergence and modal correlation','spatial modal insertion'],physical_validation=False,production_released=False)
