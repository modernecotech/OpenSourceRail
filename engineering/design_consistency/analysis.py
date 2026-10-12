"""Bounded research responses; unknown resistance/calibration never becomes a pass."""
from __future__ import annotations
import math
import numpy as np
from osr_mech.engineering_definition import fingerprint
from .contracts import summary


def mandatory_status(checks):
    if any(v not in ('passed','failed','unknown')for v in checks.values()):raise ValueError('three-valued mandatory evidence required')
    return 'blocked' if 'failed' in checks.values() else 'unknown' if 'unknown' in checks.values() else 'passed'


def bolt_screen(joint, *, separating_force_n=20000,shear_force_n=12000,friction=.15,prying_factor=1.5):
    """Elastic bolt/member springs and conservative separated contact/slip checks.

    Compression area is an explicit annulus seed, not a validated pressure cone.
    Force is per four-bolt mount; empirical prying must be replaced by local FE/test.
    """
    if any(not math.isfinite(v) or v<0 for v in (separating_force_n,shear_force_n,friction)) or prying_factor<1:raise ValueError('invalid joint load/friction/prying')
    grip=sum(joint['grip_stack_m']);area=joint['bolt_tensile_area_m2'];young=210e9;n=len(joint['hole_pattern_m'])
    kb=young*area/(grip+.012)
    am=math.pi*(.024**2-.007**2);km=young*am/grip
    fraction=kb/(kb+km);preload=joint['preload_range_n'][0]
    applied=prying_factor*separating_force_n/n
    residual=preload-(1-fraction)*applied;bolt_force=joint['preload_range_n'][1]+fraction*applied
    slip=friction*n*max(0,residual)
    checks={'contact_compression':'passed'if residual>0 else'failed','friction_slip':'passed'if slip>=shear_force_n else'failed',
        'bolt_strength':'unknown','fatigue':'unknown','prying_calibration':'unknown','preload_and_surface_evidence':'unknown','weld_resistance':'unknown'}
    return dict(bolt_stiffness_n_m=kb,member_stiffness_n_m=km,load_fraction=fraction,
        minimum_residual_clamp_n_each=residual,maximum_bolt_stress_pa=bolt_force/area,
        slip_resistance_n=slip,separating_force_n=separating_force_n,shear_force_n=shear_force_n,
        prying_factor=prying_factor,checks=checks,status=mandatory_status(checks),
        fatigue_stress_range_pa=fraction*applied/area,fatigue_cycles_to_failure=None,
        basis='elastic spring screen with assumed friction and prying; not a contact/fatigue qualification',physical_validation=False)


def _skew(d):
    x,y,z=d;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])


def beam_stiffness(a,b,section,young=210e9,poisson=.3):
    a=np.asarray(a);b=np.asarray(b);length=float(np.linalg.norm(b-a));x=(b-a)/length
    if length<=0:raise ValueError('zero beam length')
    reference=np.array([0.,0.,1.]) if abs(x[2])<.9 else np.array([0.,1.,0.])
    y=np.cross(reference,x);y/=np.linalg.norm(y);z=np.cross(x,y)
    rotation=np.array([x,y,z]);T=np.zeros((12,12))
    for i in range(4):T[i*3:i*3+3,i*3:i*3+3]=rotation
    k=np.zeros((12,12));ea=young*section['area_m2']/length;gj=young/(2*(1+poisson))*section['j_torsion_m4']/length
    for ids,v in [([0,6],ea),([3,9],gj)]:k[np.ix_(ids,ids)]+=v*np.array([[1,-1],[-1,1]])
    for ids,ei,sign in [([1,5,7,11],young*section['iz_m4'],1),([2,4,8,10],young*section['iy_m4'],-1)]:
        l=length;k[np.ix_(ids,ids)]+=ei/l**3*np.array([[12,sign*6*l,-12,sign*6*l],[sign*6*l,4*l*l,-sign*6*l,2*l*l],[-12,-sign*6*l,12,-sign*6*l],[sign*6*l,2*l*l,-sign*6*l,4*l*l]])
    return T.T@k@T


def interface_modes(contract):
    """Modal basis of this interface assembly, never of the whole train.

    Each physical CG/inertia contributes an exact rigid-body kinetic transform.
    Sills retain actual hollow properties; drilled sections use gross stiffness.
    Battery carriers/fasteners are rigidly attached inertia, not extra stiffness.
    """
    from scipy.linalg import eigh
    from osr_mech.section_contract import rhs
    from osr_mech.automated_geometry import aggregate,primitive_volume
    from copy import deepcopy
    parts={p['id']:p for p in contract['parts']};points=[[x,y,0]for y in (-.45,.45)for x in (-1,-.75,0,.75,1)]
    nodes=np.array(points);n=len(nodes);K=np.zeros((6*n,6*n));M=np.zeros_like(K)
    edges=[]
    for i in (0,5):
        sec=parts[f'sill-{i//5}']['analysis']['section']
        edges.extend((i+j,i+j+1,sec)for j in range(4))
    # Bolster plates have an explicit net-area rectangular bending reduction.
    plate=rhs(.5,.016,.004,density_kg_m3=7850)
    plate.update(area_m2=.5*.016,iy_m4=.5*.016**3/12,iz_m4=.016*.5**3/12,j_torsion_m4=.5*.016**3/3)
    edges.extend((i,i+5,plate)for i in (1,3))
    for a,b,sec in edges:
        ids=list(range(6*a,6*a+6))+list(range(6*b,6*b+6));K[np.ix_(ids,ids)]+=beam_stiffness(nodes[a],nodes[b],sec)
    for i in (1,3,6,8):
        for dof,v in enumerate((100000,200000,2000000)):K[6*i+dof,6*i+dof]+=v
    distribution=[]
    for p in contract['parts']:
        prop=p['properties'];cg=np.array(prop['cg_m']);mass=prop['mass_kg'];inertia=np.array(prop['inertia_tensor_kg_m2'])
        # Extended manufactured members distribute inertia among tributary nodes;
        # slice manufactured walls into actual tributary regions, including bolt bores.
        group=list(range(5))if p['id']=='sill-0'else list(range(5,10))if p['id']=='sill-1'else [int(np.argmin(np.linalg.norm(nodes-cg,axis=1)))]
        for position,node in enumerate(group):
            own_mass=mass/len(group);own_cg=cg;own_inertia=inertia/len(group)
            if p['id'].startswith('sill-'):
                boundaries=[-1,-.875,-.375,.375,.875,1];left,right=boundaries[position:position+2];pieces=[]
                for primitive in p['manufacturing']['primitives']:
                    q=deepcopy(primitive);old_x=q['centre_m'][0];q['centre_m'][0]=(left+right)/2;q['dimensions_m'][0]=right-left
                    if q['kind']=='plate':
                        holes=[[x+old_x-q['centre_m'][0],y]for x,y in q['holes_xy_m']if left<x+old_x<right]
                        if holes:q['holes_xy_m']=holes;q['kind']='perforated-plate'
                        else:q['kind']='box';q.pop('holes_xy_m');q.pop('hole_radius_m')
                    pieces.append(q)
                props=aggregate(pieces,[primitive_volume(q)*contract['materials'][p['material']]['density_kg_m3']for q in pieces])
                own_mass=props['mass_kg'];own_cg=np.asarray(props['cg_m']);own_inertia=np.asarray(props['inertia_tensor_kg_m2'])
            offset=own_cg-nodes[node];S=_skew(offset)
            block=np.block([[own_mass*np.eye(3),-own_mass*S],[own_mass*S,own_inertia+own_mass*(S.T@S)]])
            M[6*node:6*node+6,6*node:6*node+6]+=block
        distribution.append(dict(physical_part_id=p['id'],nodes=group,mass_kg=mass,rigid_offset_m=cg.tolist()))
    # No fabricated numerical mass: every node gets a portion of a physical sill.
    eigenvalues,phi=eigh(K,M);positive=np.where(eigenvalues>1e-6)[0][:12]
    frequencies=np.sqrt(eigenvalues[positive])/(2*math.pi);modes=phi[:,positive]
    orthogonality=float(np.max(np.abs(modes.T@M@modes-np.eye(len(positive)))))
    # Rigid-body kinetic reconciliation against independently summed part integrals.
    R=np.zeros((6*n,6))
    for i,x in enumerate(nodes):R[6*i:6*i+3,:3]=np.eye(3);R[6*i:6*i+3,3:]=-_skew(x);R[6*i+3:6*i+6,3:]=np.eye(3)
    rigid=R.T@M@R;tot=summary(contract);cg=np.asarray(tot['cg_m']);S=_skew(cg);mass=tot['mass_kg']
    expected=np.block([[mass*np.eye(3),-mass*S],[mass*S,np.asarray(tot['inertia_tensor_kg_m2'])+mass*S.T@S]])
    relative=float(np.linalg.norm(rigid-expected)/np.linalg.norm(expected))
    if relative>1e-10 or orthogonality>1e-8:raise ValueError('modal mass/inertia transfer differs')
    return dict(schema='osr-assembled-interface-modes/1',configuration_sha256=fingerprint(contract),nodes_m=points,
        frequencies_hz=frequencies.tolist(),mass_normalised_modes=modes.T.reshape(-1,n,6).tolist(),
        physical_part_distribution=distribution,rigid_mass_inertia_relative_error=relative,mass_orthogonality_error=orthogonality,
        damping_ratios=None,whole_vehicle_transfer_accepted=False,
        stiffness_assumptions=['gross sills despite local bolt holes','beam-reduced bolster plates','rigid carrier/bolt attachment','design-seed suspension springs'],
        mandatory_checks={'joint_compliance_calibration':'unknown','equipment_supplier_inventory':'unknown','measured_modes':'unknown','whole_vehicle_basis':'unknown'},physical_validation=False)


def civil_stages(contract,trace,*,prestress_n=1000000,loss_fraction=.2,ground_layers=None):
    """Full moving axle envelope + declared lifting/jacking stages, elastic bound.

    Reinforcement, cracking, shear, torsion, losses and foundation law are not
    implicitly qualified by this global gross-section response.
    """
    deck=next(p for p in contract['parts']if p['id']=='deck');sec=deck['analysis']['section']
    length=max(p['dimensions_m'][2]for p in deck['manufacturing']['primitives']);mass=sum(p['properties']['mass_kg']for p in contract['parts']if p['id']=='deck'or p['id'].startswith(('deck-rebar-','tendon-')))
    q=mass*9.80665/length;young=contract['materials']['concrete']['young_pa'];ei=young*sec['iy_m4']
    pattern=trace['reference']['axle_pattern'];offsets=np.array([p['x_m']for p in pattern]);offsets-=offsets[0]
    forces=np.array([p['static_load_kn']*1000 for p in pattern]);xs=np.linspace(0,length,161)
    maxmoment=0.;maxreaction=0.;maxdef=0.;governing=None
    for nose in np.linspace(-offsets[-1],length,321):
        positions=nose+offsets;inside=(positions>=0)&(positions<=length);p=positions[inside];f=2*forces[inside]
        ra=q*length/2+float(np.sum(f*(length-p)/length));rb=q*length/2+float(np.sum(f*p/length))
        moment=ra*xs-q*xs*xs/2-np.sum(f[:,None]*np.maximum(0,xs[None,:]-p[:,None]),axis=0)
        maxreaction=max(maxreaction,ra,rb)
        if moment.max()>maxmoment:maxmoment=float(moment.max());governing=float(nose)
        # Simply supported point-load Green function, two tracks simultaneous.
        deflection=q*xs*(length**3-2*length*xs**2+xs**3)/(24*ei)
        for a,force in zip(p,f):
            b=length-a
            deflection+=np.where(xs<=a,force*b*xs/(6*length*ei)*(length**2-b**2-xs**2),force*a*(length-xs)/(6*length*ei)*(length**2-a**2-(length-xs)**2))
        maxdef=max(maxdef,float(deflection.max()))
    stress=maxmoment*(sec['height_m']/2)/sec['iy_m4'];effective=prestress_n*(1-loss_fraction)
    if not 0<=loss_fraction<1 or prestress_n<0:raise ValueError('invalid prestress/loss sensitivity')
    service=dict(maximum_bending_moment_nm=maxmoment,maximum_support_reaction_n=maxreaction,maximum_deflection_m=maxdef,
        governing_train_origin_m=governing,maximum_gross_fibre_bending_stress_pa=stress,
        effective_prestress_force_n=effective,prestress_compression_pa=effective/sec['area_m2'],
        prestress_basis='straight tendon seed; eccentricity, anchors, transfer/loss history and bonded resistance unresolved',
        installed_deck_assembly_mass_kg=mass,train_axle_count=len(pattern),simultaneous_tracks=2,complete_axle_sweep=True)
    # Overhanging deck with supports at 0.2/0.8 L: exact UDL moment envelope.
    a=.2*length;r=1.3*q*length/2
    moments=r*np.maximum(0,xs-a)+r*np.maximum(0,xs-(length-a))-1.3*q*xs**2/2
    lifting=dict(support_positions_m=[a,length-a],dynamic_factor=1.3,reaction_n_each=r,maximum_absolute_moment_nm=float(np.max(np.abs(moments))),local_insert_capacity=None,lateral_stability=None)
    ground={'status':'unknown','layers':None,'pile_group_response_accepted':False}
    if ground_layers is not None:
        if not ground_layers:raise ValueError('nonempty ordered ground layers required')
        top=0
        for layer in ground_layers:
            if layer['top_m']!=top or layer['bottom_m']<=top or layer['lateral_stiffness_n_m2']<=0:raise ValueError('contiguous positive-depth/stiffness layers required')
            top=layer['bottom_m']
            if not layer.get('source_sha256'):raise ValueError('ground layer needs a controlled source hash')
        ground['layers']=ground_layers # Hash alone is not survey acceptance.
    checks={'global_elastic_deflection':'passed'if maxdef<=length/1000 else'failed','reinforcement_and_cracking':'unknown',
        'anchorage_and_losses':'unknown','shear_torsion_fatigue':'unknown','ground_calibration':'unknown',
        'lifting_insert_capacity':'unknown','temporary_lateral_stability':'unknown','bearing_replacement_local_capacity':'unknown'}
    return dict(schema='osr-common-civil-stages/1',configuration_sha256=fingerprint(contract),service=service,lifting=lifting,
        bearing_replacement=dict(dead_load_reaction_n_each=q*length/2,jack_capacity_n=None,local_capacity=None),
        ground=ground,checks=checks,status=mandatory_status(checks),physical_validation=False,production_released=False)
