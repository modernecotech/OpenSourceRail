"""Monolithic vertical car/bogie pitch, wheelset, rail and multi-span coupling.

Displacements are perturbations about vehicle equilibrium on a rigid approach.
The linear contact model reports loss of compression as outside its domain.
This numerical research adapter supplies no lateral/contact or material release.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.linalg import cho_factor, cho_solve, eigh
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import splu

from osr_mech.civil.exploration import geometry
from osr_mech.engineering_definition import validate, component_mass_records, model_mass_properties, fingerprint, number
from osr_mech.vehicle_mass_properties import combined_inertia
from .model import deck_physics, pier_physics, cement_area


def beam_matrices(length, EI, mass_per_m):
    """Euler–Bernoulli bending with consistent translational/rotational mass."""
    l = length
    K = EI/l**3 * np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])
    M = mass_per_m*l/420 * np.array([[156,22*l,54,-13*l],[22*l,4*l*l,13*l,-3*l*l],[54,13*l,156,-22*l],[-13*l,-3*l*l,-22*l,4*l*l]])
    return M, K


def hermite(x, start, length):
    s = (x-start)/length
    shape = np.array([1-3*s*s+2*s**3, length*(s-2*s*s+s**3), 3*s*s-2*s**3, length*(-s*s+s**3)])
    derivative = np.array([(-6*s+6*s*s)/length, 1-4*s+3*s*s, (6*s-6*s*s)/length, -2*s+3*s*s])
    return shape, derivative


def _spring(K, C, vector, stiffness, damping=0.):
    K += stiffness*np.outer(vector, vector)
    C += damping*np.outer(vector, vector)


class Bridge:
    def __init__(self, specification, mesh):
        required = {'candidate', 'study', 'span_count', 'track', 'contact_n_m'}
        if set(specification) != required or type(mesh) is not int or not 2 <= mesh <= 32:
            raise ValueError('invalid shared bridge/discretisation fields')
        candidate, study = specification['candidate'], specification['study']
        count = specification['span_count']
        if type(count) is not int or not 1 <= count <= 8:
            raise ValueError('bounded multi-span structure required')
        self.geo = geometry(candidate['definition'])
        span = candidate['definition']['deck']['span_m']; self.length = span*count
        track = specification['track']
        if set(track) != {'EI_nm2', 'mass_kg_m', 'pad_stiffness_n_m', 'pad_damping_ns_m', 'basis'} or not track['basis']:
            raise ValueError('explicit flexible track properties required')
        for key in ('EI_nm2', 'mass_kg_m', 'pad_stiffness_n_m', 'pad_damping_ns_m'):
            number(track[key], key, minimum=0)
        if min(track['EI_nm2'], track['mass_kg_m'], track['pad_stiffness_n_m']) <= 0:
            raise ValueError('positive rail mass, stiffness and pad stiffness required')
        number(specification['contact_n_m'], 'contact stiffness', minimum=1)
        local = sorted({*np.linspace(0., span, mesh+1), *(s['start_m'] for s in self.geo['deck']), *(s['end_m'] for s in self.geo['deck'])})
        self.elements = []; deck_nodes = []; dof = 0; ends = []
        for index in range(count):
            nodes = [(index*span+x, dof+2*j) for j, x in enumerate(local)]
            dof += 2*len(nodes); deck_nodes.extend(nodes); ends.append((nodes[0][1], nodes[-1][1]))
            for (start, first), (end, second) in zip(nodes, nodes[1:]):
                section = next(s for s in self.geo['deck'] if s['start_m']-1e-8 <= (start+end)/2-index*span < s['end_m'])
                properties = deck_physics(candidate, section)
                # Explicit nonstructural dead load mass; rail mass remains separate.
                allowance = candidate['mass_allowances']
                mass = (properties['mass_kg_m'] + allowance['reinforcement_kg_m3']*cement_area(section) +
                        allowance['prestress_kg_m'] + allowance['superimposed_dead_kg_m_per_track'])
                if section is not self.geo['deck'][1]:
                    mass += allowance['embedded_kg_per_beam']/(2*self.geo['deck'][0]['end_m'])
                self.elements.append(dict(start=start, length=end-start, dofs=[first,first+1,second,second+1], EI=properties['effective_EI_nm2'], EA=properties['effective_EA_n'], mass=mass))
        self.deck_dof_count=dof
        # Continuous rail approaches prevent an artificial displacement jump
        # between a moving bridge support and an infinitely rigid outside track.
        self.approach = 5.
        # Resolve rail-on-pad bending independently of the much coarser deck.
        # Its characteristic length is (EI/k_pad)^(1/4).
        rail_step=(track['EI_nm2']/track['pad_stiffness_n_m'])**.25/2
        rail_count=math.ceil((self.length+2*self.approach)/rail_step)
        if rail_count>1000:raise ValueError('rail bending mesh exceeds adapter budget')
        global_x = sorted({round(x,10) for x in np.linspace(-self.approach,self.length+self.approach,rail_count+1)} | {round(x,10) for x,_ in deck_nodes})
        self.rail_nodes = [(x, dof+2*j) for j, x in enumerate(global_x)]; dof += 2*len(global_x)
        self.supports = [(dof+2*j, dof+2*j+1) for j in range(count+1)]; dof += 2*(count+1)
        self.M = np.zeros((dof,dof)); self.K = np.zeros_like(self.M); self.C = np.zeros_like(self.M)
        self.constrained = [self.rail_nodes[0][1],self.rail_nodes[0][1]+1,self.rail_nodes[-1][1],self.rail_nodes[-1][1]+1]
        self.approach_ground_pads=[]
        for e in self.elements:
            m,k = beam_matrices(e['length'],e['EI'],e['mass']); ix=np.ix_(e['dofs'],e['dofs'])
            self.M[ix] += m; self.K[ix] += k
        self.rail_elements=[]
        for (x,a),(end,b) in zip(self.rail_nodes,self.rail_nodes[1:]):
            indices=[a,a+1,b,b+1]; m,k=beam_matrices(end-x,track['EI_nm2'],track['mass_kg_m']); ix=np.ix_(indices,indices)
            self.M[ix]+=m; self.K[ix]+=k
            self.rail_elements.append(dict(start=x,length=end-x,dofs=indices))
        # Distributed pad stiffness is integrated with nodal tributary lengths.
        for i,(x,rail) in enumerate(self.rail_nodes):
            matches=[e for e in self.elements if e['start']-1e-8 <= x <= e['start']+e['length']+1e-8]
            tributary=((global_x[i+1]-x) if i+1<len(global_x) else 0)+((x-global_x[i-1]) if i else 0)
            if not matches:
                v=np.zeros(dof);v[rail]=1.
                _spring(self.K,self.C,v,track['pad_stiffness_n_m']*tributary/2,track['pad_damping_ns_m']*tributary/2)
                self.approach_ground_pads.append((rail,track['pad_stiffness_n_m']*tributary/2))
            for element in matches:
                v=np.zeros(dof);v[rail]=1.
                n,_=hermite(x,element['start'],element['length']);v[element['dofs']]=-n
                _spring(self.K,self.C,v,track['pad_stiffness_n_m']*tributary/2/len(matches),track['pad_damping_ns_m']*tributary/2/len(matches))
        compliance=sum((s['end_m']-s['start_m'])/pier_physics(candidate,s)['effective_EA_n'] for s in self.geo['pier'])
        pier_mass=sum((s['end_m']-s['start_m'])*pier_physics(candidate,s)['mass_kg_m'] for s in self.geo['pier'])
        foundation=candidate['foundation'];cap_mass=foundation['cap_depth_m']*foundation['cap_length_m']*foundation['cap_width_m']*candidate['material']['density_kg_m3']
        ground=study['ground_scenarios'][0]['axial_stiffness_n_m']
        bearing=study['bearing']['vertical_stiffness_n_m']
        for i,(top,base) in enumerate(self.supports):
            self.M[top,top]+=pier_mass/2;self.M[base,base]+=pier_mass/2+cap_mass
            v=np.zeros(dof);v[top]=1.;v[base]=-1.;_spring(self.K,self.C,v,1/compliance)
            v=np.zeros(dof);v[base]=1.;_spring(self.K,self.C,v,ground)
            attached=[]
            if i:attached.append(ends[i-1][1])
            if i<count:attached.append(ends[i][0])
            for deck in attached:
                v=np.zeros(dof);v[deck]=1.;v[top]=-1.;_spring(self.K,self.C,v,bearing)
        damping=study['analysis']['damping_ratio'];number(damping,'bridge damping',minimum=0)
        free=[i for i in range(dof) if i not in self.constrained]
        first=math.sqrt(eigh(self.K[np.ix_(free,free)],self.M[np.ix_(free,free)],subset_by_index=[0,0],eigvals_only=True)[0])
        self.C+=2*damping*first*self.M
        self.bearing_stiffness=bearing;self.ground_stiffness=ground;self.ends=ends
        self.pier_axial_stiffness=1/compliance

    def rail_shape(self,x):
        if not -self.approach <= x <= self.length+self.approach: return None
        e=next((e for e in self.rail_elements if e['start'] <= x < e['start']+e['length']),self.rail_elements[-1])
        n,derivative=hermite(x,e['start'],e['length'])
        return e,n,derivative


def native_deck_benchmark(specification, mesh=4):
    """Independent native OpenSees replay of the finite-support deck subsystem.

    Track/contact coupling is deliberately excluded from this equation check;
    their load/moment/work and refinement benchmarks are independent checks.
    """
    import openseespy.opensees as ops
    bridge=Bridge(specification,mesh)
    selected=list(range(bridge.deck_dof_count))+[d for support in bridge.supports for d in support]
    lookup={d:i for i,d in enumerate(selected)};K=np.zeros((len(selected),len(selected)));F=np.zeros(len(selected))
    nodes={}
    ops.wipe();ops.model('basic','-ndm',2,'-ndf',3);ops.geomTransf('Linear',1)
    tag=0;link=0;material=0
    for element in bridge.elements:
        for x,dof in [(element['start'],element['dofs'][0]),(element['start']+element['length'],element['dofs'][2])]:
            if dof not in nodes:
                tag+=1;nodes[dof]=tag;ops.node(tag,x,0.);ops.fix(tag,1,0,0)
        link+=1
        ops.element('elasticBeamColumn',link,nodes[element['dofs'][0]],nodes[element['dofs'][2]],element['EA']/30e9,30e9,element['EI']/30e9,1)
        _,k=beam_matrices(element['length'],element['EI'],element['mass']);indices=[lookup[d] for d in element['dofs']]
        K[np.ix_(indices,indices)]+=k
    span=specification['candidate']['definition']['deck']['span_m']
    def spring(a,b,stiffness):
        nonlocal link,material
        link+=1;material+=1;ops.uniaxialMaterial('Elastic',material,stiffness)
        ops.element('zeroLength',link,nodes[a],nodes[b],'-mat',material,'-dir',2)
        vector=np.zeros(len(K));vector[lookup[a]]=1.
        if b in lookup:vector[lookup[b]]=-1.
        K[:]+=stiffness*np.outer(vector,vector)
    for i,(top,base) in enumerate(bridge.supports):
        for dof in (top,base):
            tag+=1;nodes[dof]=tag;ops.node(tag,i*span,0.);ops.fix(tag,1,0,1)
        ground=max(selected)+i+1;tag+=1;nodes[ground]=tag;ops.node(tag,i*span,0.);ops.fix(tag,1,1,1)
        spring(top,base,bridge.pier_axial_stiffness);spring(base,ground,bridge.ground_stiffness)
        attached=([bridge.ends[i-1][1]] if i else [])+([bridge.ends[i][0]] if i<len(bridge.ends) else [])
        for deck in attached:spring(deck,top,bridge.bearing_stiffness)
    # Same nonuniform deck, actual node positions and finite support chain.
    midpoint=span/2
    node=next(e['dofs'][0] for e in bridge.elements if abs(e['start']-midpoint)<1e-8)
    F[lookup[node]]=100000.
    ops.timeSeries('Linear',1);ops.pattern('Plain',1,1);ops.load(nodes[node],0.,100000.,0.)
    ops.constraints('Plain');ops.numberer('RCM');ops.system('BandGeneral');ops.test('NormUnbalance',1e-7,10)
    ops.algorithm('Linear');ops.integrator('LoadControl',1.);ops.analysis('Static')
    if ops.analyze(1)!=0:raise ValueError('native OpenSees shared deck benchmark failed to solve')
    reference=np.linalg.solve(K,F);observed=np.zeros(len(selected))
    for dof,n in nodes.items():
        if dof in lookup:
            observed[lookup[dof]]=ops.nodeDisp(n,2)
            if dof<bridge.deck_dof_count:observed[lookup[dof+1]]=ops.nodeDisp(n,3)
    scale=max(np.max(np.abs(reference)),1e-12);error=float(np.max(np.abs(observed-reference))/scale)
    version=ops.version();ops.wipe()
    return dict(schema='osr-native-shared-deck-benchmark/1',native_library='OpenSeesPy',native_version=version,
        relative_displacement_error=error,numerical_benchmark_passed=error<1e-6,
        point_load_n=100000.,finite_bearings_piers_foundations=True,
        model_scope='linear vertical Euler–Bernoulli deck/support subsystem; separate from rail/contact',
        physical_validation=False,engineering_released=False)


class Vehicle:
    def __init__(self, model):
        definition=validate(model);mass=model_mass_properties(model)
        if mass['total_mass_kg'] is None or mass['inertia_tensor_kg_m2'] is None:
            raise ValueError('coupled dynamics requires complete instance mass and inertia')
        self.records=component_mass_records(model);self.instances={r['id']:r for r in model['instances']}
        self.group={};self.wheels=[];self.static=mass;dof=0
        for body in definition['cars']:
            records=[r for r in self.records if r['body']==body['id']]
            if records:
                self.group[body['id']]=self._rigid(records,dof);dof+=2
        for bogie in definition['bogies']:
            instances=[r for r in model['instances'] if r['bogie']==bogie['id']]
            if not instances:continue
            frames=[r for r in self.records if r['bogie']==bogie['id'] and self.instances[r['id']]['axle'] is None]
            if not frames:raise ValueError('a coupled bogie needs a separate rigid-frame mass')
            self.group[bogie['id']]=self._rigid(frames,dof);dof+=2
            for i,x in enumerate(bogie['axle_x_m']):
                wheel_records=[r for r in self.records if r['bogie']==bogie['id'] and self.instances[r['id']]['axle']==i+1]
                if not wheel_records:raise ValueError('each bogie needs two identified unsprung wheelset masses')
                wheel_mass=sum(r['mass_kg'] for r in wheel_records)
                if wheel_mass<=0:raise ValueError('positive unsprung mass required')
                key=f"{bogie['id']}/axle-{i+1}"
                self.group[key]=dict(dofs=[dof],mass=wheel_mass,x=x)
                static=next(r['static_load_kn']*1000 for r in mass['axle_pattern'] if r['bogie']==bogie['id'] and r['axle']==i+1)
                self.wheels.append(dict(id=key,dof=dof,mass=wheel_mass,x=x,static_n=static));dof+=1
        self.M=np.zeros((dof,dof));self.K=np.zeros_like(self.M);self.C=np.zeros_like(self.M);self.joints=[]
        for rigid in self.group.values():
            self.M[rigid['dofs'][0],rigid['dofs'][0]]=rigid['mass']
            if len(rigid['dofs'])==2:self.M[rigid['dofs'][1],rigid['dofs'][1]]=rigid['pitch_inertia']
        primary=set();secondary=set()
        for joint in model['joints']:
            if joint['connection'] not in ('primary','secondary','articulation'):continue
            p=joint['properties'][joint['property_source']]
            if p is None or p['stiffness_n_m']<=0:raise ValueError('coupled joints require positive evidenced/study stiffness')
            vector=np.zeros(dof)
            endpoint_groups=[]
            for sign,endpoint in zip((1.,-1.),joint['endpoints']):
                instance=self.instances[endpoint['instance']]
                group=instance['body'] or instance['bogie']
                if instance['axle'] is not None:group=f"{instance['bogie']}/axle-{instance['axle']}"
                endpoint_groups.append(group)
                rigid=self.group[group];datum=instance['datums'][endpoint['datum']];transform=instance['transform']
                location=np.asarray(transform['translation_m'])+np.asarray(transform['rotation'])@datum['translation_m']
                # Only straight, nominal vertical joints are within this adapter.
                if not np.allclose(transform['rotation'],np.eye(3)) or not np.allclose(datum['rotation'],np.eye(3)):
                    raise ValueError('vertical adapter requires nominal straight joint frames')
                vector[rigid['dofs'][0]]+=sign
                if len(rigid['dofs'])==2:vector[rigid['dofs'][1]]+=sign*(location[0]-rigid['x'])
            _spring(self.K,self.C,vector,p['stiffness_n_m'],p['damping_ns_m'])
            if joint['connection']=='primary':
                wheel_groups=[g for g in endpoint_groups if '/axle-' in g]
                if len(wheel_groups)!=1 or wheel_groups[0] in primary or wheel_groups[0].rsplit('/axle-',1)[0] not in endpoint_groups:
                    raise ValueError('primary joint must connect each wheelset once to its own bogie')
                primary.add(wheel_groups[0])
            if joint['connection']=='secondary':
                bogie_groups=[g for g in endpoint_groups if '/bogie-' in g]
                if len(bogie_groups)!=1 or bogie_groups[0] in secondary or bogie_groups[0].split('/bogie-')[0] not in endpoint_groups:
                    raise ValueError('secondary joint must connect each bogie once to its parent car')
                secondary.add(bogie_groups[0])
            self.joints.append(dict(id=joint['id'],vector=vector,properties=p))
        if primary!={w['id'] for w in self.wheels} or secondary!={g for g in self.group if '/bogie-' in g and '/axle-' not in g}:
            raise ValueError('each wheelset needs primary suspension and each bogie a secondary joint')

    @staticmethod
    def _rigid(records,dof):
        mass=sum(r['mass_kg'] for r in records)
        if mass<=0:raise ValueError('positive rigid-body mass required')
        cg={k:sum(r['mass_kg']*r[k+'_m'] for r in records)/mass for k in ('x','y','z')}
        tensor=combined_inertia(records,cg,None)['inertia_tensor_kg_m2']
        if tensor is None or tensor[1][1]<=0:raise ValueError('positive evidenced/study pitch inertia required')
        return dict(dofs=[dof,dof+1],mass=mass,x=cg['x'],pitch_inertia=tensor[1][1])


def run(model, *, speed=20., dt=.005, mesh=4, irregularity_amplitude=0., irregularity_wavelength=10., moving_forces=False):
    """Both-way monolithic Newmark coupling; moving_forces is an independent limit."""
    for value,name in ((speed,'speed'),(dt,'timestep'),(irregularity_wavelength,'roughness wavelength')):
        number(value,name,minimum=1e-9)
    number(irregularity_amplitude,'roughness amplitude',minimum=0)
    if not .00025 <= dt <= .02 or speed>60:raise ValueError('coupling outside bounded temporal domain')
    vehicle=Vehicle(model);bridge=Bridge(model['bridge'],mesh)
    nb=len(bridge.M);nv=0 if moving_forces else len(vehicle.M);size=nb+nv
    M=np.zeros((size,size));K0=np.zeros_like(M);C=np.zeros_like(M)
    M[:nb,:nb]=bridge.M;K0[:nb,:nb]=bridge.K;C[:nb,:nb]=bridge.C
    if nv:M[nb:,nb:]=vehicle.M;K0[nb:,nb:]=vehicle.K;C[nb:,nb:]=vehicle.C
    q=np.zeros(size);v=np.zeros(size);acc=np.zeros(size)
    lead=max(w['x'] for w in vehicle.wheels)
    offsets=[lead-w['x'] for w in vehicle.wheels]
    # Small approach clearance gives all vehicle DOFs a compatible equilibrium.
    duration=(bridge.length+2*bridge.approach+max(offsets)+1.)/speed
    steps=math.ceil(duration/dt)
    if steps>80000 or size>1000:raise ValueError('coupling execution budget exceeded')
    beta=.25;gamma=.5;contact_k=model['bridge']['contact_n_m'];history=[]
    minimum=math.inf;peak=0.;force_error=0.;moment_error=0.;work_error=0.;outside_stops=set()
    observation=min(bridge.rail_nodes,key=lambda row:abs(row[0]-bridge.length/2))[1]
    free=[i for i in range(size) if i not in bridge.constrained];ix=np.ix_(free,free)
    for step in range(1,steps+1):
        time=step*dt;positions=[speed*time-bridge.approach-.5-offset for offset in offsets]
        K=K0.copy();F=np.zeros(size);contacts=[]
        for wheel,x in zip(vehicle.wheels,positions):
            sample=bridge.rail_shape(x);shape=np.zeros(size);derivative=np.zeros(size)
            if sample:
                e,n,dn=sample;shape[e['dofs']]=n;derivative[e['dofs']]=dn
                F+=shape*wheel['static_n']
            if not moving_forces:
                b=-shape;b[nb+wheel['dof']]=1.
                taper=math.sin(math.pi/2*min(1.,max(0.,x/2.)))**2*math.sin(math.pi/2*min(1.,max(0.,(bridge.length-x)/2.)))**2
                rough=irregularity_amplitude*math.sin(2*math.pi*x/irregularity_wavelength)*taper if sample else 0.
                active=np.flatnonzero(b);local=b[active]
                K[np.ix_(active,active)]+=contact_k*np.outer(local,local);F+=contact_k*b*rough
                contacts.append((wheel,x,sample,shape,derivative,b,rough))
        predicted=q+dt*v+dt*dt*(.5-beta)*acc;predicted_v=v+dt*(1-gamma)*acc
        effective=M+gamma*dt*C+beta*dt*dt*K
        rhs=F-C@predicted_v-K@predicted;acc=np.zeros(size)
        acc[free]=splu(csc_matrix(effective[ix])).solve(rhs[free])
        q=predicted+beta*dt*dt*acc;v=predicted_v+gamma*dt*acc
        contact_rows=[]
        for wheel,x,sample,shape,derivative,b,rough in contacts:
            dynamic=contact_k*(b@q-rough);force=wheel['static_n']+dynamic
            if sample:
                minimum=min(minimum,force);peak=max(peak,force)
                rail_force=shape[:nb]*force
                translations=[d for _,d in bridge.rail_nodes]
                force_error=max(force_error,abs(rail_force[translations].sum()-force))
                rail_moment=sum(rail_force[d]*p+rail_force[d+1] for p,d in bridge.rail_nodes)
                moment_error=max(moment_error,abs(rail_moment-force*x))
                # Independently computed nodal and point powers, including the
                # moving interpolation velocity and prescribed irregularity work.
                rail_velocity=shape@v+speed*(derivative@q)
                wheel_velocity=v[nb+wheel['dof']]
                nodal_power=rail_force@v[:nb]-force*wheel_velocity
                sliding_power=force*speed*(derivative@q)
                gap_power=force*(wheel_velocity-rail_velocity)
                work_error=max(work_error,abs(nodal_power+sliding_power+gap_power))
            contact_rows.append(dict(axle=wheel['id'],x_m=x,on_structure=0<=x<=bridge.length,on_modelled_track=sample is not None,force_n=force,
                                     unloading_ratio=1-force/wheel['static_n']))
        joint_rows=[]
        if nv:
            for joint in vehicle.joints:
                displacement=joint['vector']@q[nb:];relative_v=joint['vector']@v[nb:];p=joint['properties']
                if (p['lower_stop_m'] is not None and displacement<p['lower_stop_m']) or (p['upper_stop_m'] is not None and displacement>p['upper_stop_m']):outside_stops.add(joint['id'])
                joint_rows.append(dict(joint=joint['id'],relative_displacement_m=float(displacement),force_n=float(p['stiffness_n_m']*displacement+p['damping_ns_m']*relative_v)))
        deck_acc=max(abs(acc[e['dofs'][0]]) for e in bridge.elements)
        bearings=[]
        for index,(top,base) in enumerate(bridge.supports):
            attached=([bridge.ends[index-1][1]] if index else [])+([bridge.ends[index][0]] if index<len(bridge.ends) else [])
            bearings.extend(dict(support=index,deck_dof=d,force_n=float(bridge.bearing_stiffness*(q[d]-q[top]))) for d in attached)
        history.append(dict(time_s=time,rail_displacement_m=float(q[observation]),deck_acceleration_m_s2=float(deck_acc),
            vehicle_acceleration_m_s2=float(max((abs(acc[nb+g['dofs'][0]]) for k,g in vehicle.group.items() if '/bogie-' not in k),default=0.)) if nv else None,
            contacts=contact_rows,joints=joint_rows,bearing_reactions=bearings,
            foundation_reactions_n=[float(bridge.ground_stiffness*q[base]) for top,base in bridge.supports]))
    return dict(schema='osr-train-track-bridge/1',model_sha256=fingerprint(model),
        adapter='moving-forces' if moving_forces else 'vertical-heave-pitch-rail-multispan',
        speed_m_s=speed,time_step_s=dt,mesh_per_span=mesh,steps=steps,dofs=size,
        total_mass_kg=vehicle.static['total_mass_kg'],axle_pattern=vehicle.static['axle_pattern'],
        peak_rail_displacement_m=max(abs(r['rail_displacement_m']) for r in history),
        peak_deck_acceleration_m_s2=max(r['deck_acceleration_m_s2'] for r in history),
        peak_vehicle_acceleration_m_s2=max((r['vehicle_acceleration_m_s2'] or 0 for r in history),default=0) if nv else None,
        peak_bearing_force_n=max(abs(b['force_n']) for r in history for b in r['bearing_reactions']),
        minimum_contact_n=minimum if math.isfinite(minimum) else None,maximum_contact_n=peak if nv else None,
        contact_force_balance_residual_n=force_error,contact_moment_balance_residual_nm=moment_error,
        contact_power_balance_residual_w=work_error,joints_outside_linear_stops=sorted(outside_stops),
        within_adapter_domain=bool(minimum>=0 and not outside_stops) if nv else True,
        physical_validation=False,engineering_released=False,history=history,
        limitations=['vertical linear heave/pitch only; straight single track','Euler–Bernoulli rail/deck; shear and 3D response require other adapters',
                    'vertical axial pier/foundation motion; no lateral soil interaction','no contact loss/recontact, creepage, wear or nonlinear wheel–rail contact',
                    'research mechanical/material parameters require calibration','no material, connection strength, fatigue or project acceptance inferred'])
