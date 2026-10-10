"""Shared six-DOF bodies/bogies/wheelsets and nonlinear spatial rail contact.

Full sparse FE equations are solved monolithically. Rotations are perturbations
about the moving alignment; angular excursions outside the declared small-angle
domain are reported. Wheel spin is retained separately from its contact location.
"""
from __future__ import annotations
from copy import deepcopy
import math
import numpy as np
from scipy.sparse import csc_matrix,block_diag,coo_matrix
from scipy.sparse.linalg import splu
from scipy.spatial.transform import Rotation
from osr_mech.engineering_definition import validate,component_mass_records,fingerprint
from osr_mech.vehicle_mass_properties import combined_inertia
from .spatial_structure import SpatialStructure,Route,skew
from .wheel_contact import ProfilePair,TangentialContact,patch,normal_force,profile_normal_gap
from .joint_laws import response as joint_response


def loaded_model(model,case):
    """Derived gross body properties; original component/supplier records survive."""
    result=deepcopy(model);family=model['family_definition'];profile=family['profile']
    counts={'empty':0,'nominal':profile['passenger_capacity']/family['car_count'],
            'crush':profile['crush_capacity']/family['car_count'],
            'uneven':profile['passenger_capacity']/family['car_count']}
    if case['id'] not in counts:raise ValueError('unknown passenger loading state')
    for field in ('passenger_mass_kg','longitudinal_offset_m','lateral_offset_m','passenger_cg_height_m','mass_uncertainty_fraction'):
        if type(case[field]) not in (int,float) or not math.isfinite(case[field]):raise ValueError('finite passenger loading input required: '+field)
    if case['passenger_mass_kg']<0 or (counts[case['id']]>0 and case['passenger_mass_kg']==0) or not 0<=case['mass_uncertainty_fraction']<=1:raise ValueError('positive loaded passenger mass and bounded loading uncertainty required')
    if abs(case['longitudinal_offset_m'])>family['car_length_m']/2:raise ValueError('passenger offset outside the frozen car module')
    for row in result['instances']:
        if row['body'] and row['part_id']=='LM3-CAR-A900':
            count=counts[case['id']];mass=count*case['passenger_mass_kg']
            original=row['properties'][row['property_source']]
            if original is None:raise ValueError('passenger loading requires the base body mass record')
            x=case['longitudinal_offset_m'] if case['id']=='uneven' else 0.
            y=case['lateral_offset_m'] if case['id']=='uneven' else 0.
            payload=dict(id='passengers',mass_kg=mass,x_m=x,y_m=y,z_m=case['passenger_cg_height_m'],inertia_tensor_kg_m2=np.diag([mass*.1,mass*.1,mass*.1]).tolist())
            base=dict(id=row['id'],mass_kg=original['mass_kg'],**{k+'_m':original['cg_m'][i] for i,k in enumerate(('x','y','z'))},inertia_tensor_kg_m2=original['inertia_tensor_kg_m2'])
            total=base['mass_kg']+mass;cg={k:(base['mass_kg']*base[k+'_m']+mass*payload[k+'_m'])/total for k in ('x','y','z')}
            props=deepcopy(original);props['mass_kg']=total;props['cg_m']=[cg[k] for k in ('x','y','z')]
            props['inertia_tensor_kg_m2']=combined_inertia([base,payload],cg,None)['inertia_tensor_kg_m2']
            props['basis']='derived passenger case '+case['id']+' from retained base configuration '+fingerprint(model)
            props['evidence']=None;props['uncertainty_kg']+=mass*case['mass_uncertainty_fraction'];row['property_source']='design';row['properties']['design']=props
    return result


class SpatialVehicle:
    def __init__(self,model,joint_laws):
        definition=validate(model);self.model=model;self.groups={};self.instances={r['id']:r for r in model['instances']};records=component_mass_records(model)
        if any(r.get('mass_kg') is None or r.get('inertia_tensor_kg_m2') is None for r in records):raise ValueError('spatial vehicle requires complete component mass/inertia')
        index=0
        def rigid(key,rows,wheel=False,kind='bogie'):
            nonlocal index
            mass=sum(r['mass_kg'] for r in rows)
            if mass<=0:raise ValueError('positive spatial body mass required')
            cg={a:sum(r['mass_kg']*r[a+'_m'] for r in rows)/mass for a in ('x','y','z')}
            inertia=np.asarray(combined_inertia(rows,cg,None)['inertia_tensor_kg_m2'])
            if np.linalg.eigvalsh(inertia).min()<=0:raise ValueError('positive full rigid-body inertia required')
            self.groups[key]=dict(id=key,index=index,mass=mass,cg=np.array(list(cg.values())),inertia=inertia,wheel=wheel,kind=kind);index+=6
        for body in definition['cars']:
            rows=[r for r in records if r['body']==body['id']]
            if rows:rigid(body['id'],rows,kind='carbody')
        for bogie in definition['bogies']:
            rows=[r for r in records if r['bogie']==bogie['id'] and self.instances[r['id']]['axle'] is None]
            if not rows:continue
            rigid(bogie['id'],rows)
            for axle in (1,2):
                wheels=[r for r in records if r['bogie']==bogie['id'] and self.instances[r['id']]['axle']==axle]
                if not wheels:raise ValueError('spatial bogie needs both wheelset identities')
                rigid(f"{bogie['id']}/axle-{axle}",wheels,True,kind='wheelset')
                self.groups[f"{bogie['id']}/axle-{axle}"]['powered']=bogie['kind']=='powered'
        self.size=index;self.joints=[]
        for joint in model['joints']:
            if joint['connection']=='fixed':continue
            if joint['id'] not in joint_laws:raise ValueError('six-direction mechanical law missing: '+joint['id'])
            law=joint_laws[joint['id']];K=np.asarray(law['stiffness_si'],dtype=float);C=np.asarray(law['damping_si'],dtype=float)
            for a in (K,C):
                if a.shape!=(6,6) or not np.isfinite(a).all() or not np.allclose(a,a.T) or np.linalg.eigvalsh(a).min()<-1e-7:
                    raise ValueError('passive symmetric six-DOF joint matrices required')
            endpoints=[]
            for e in joint['endpoints']:
                instance=self.instances[e['instance']];group=instance['body'] or instance['bogie']
                if instance['axle'] is not None:group=f"{instance['bogie']}/axle-{instance['axle']}"
                r=self.groups[group];t=instance['transform'];d=instance['datums'][e['datum']]
                world=np.asarray(t['translation_m'])+np.asarray(t['rotation'])@d['translation_m']
                endpoints.append(dict(group=r,offset=world-r['cg']))
            self.joints.append(dict(id=joint['id'],endpoints=endpoints,K=K,C=C,law=law))
        K,_,_,_=self.matrices(Route(dict(radius_m=0.,cant_rad=0.,cant_start_m=0.,cant_end_m=1.,grade_rad=0.,basis='static initial equilibrium')),0.,0.)
        gravity=np.zeros(self.size)
        for g in self.groups.values():gravity[g['index']+2]=-g['mass']*9.81
        fixed={d for g in self.groups.values() if g['wheel'] for d in range(g['index'],g['index']+6)};free=[i for i in range(self.size) if i not in fixed]
        static=np.zeros(self.size);static[free]=np.linalg.solve(K[np.ix_(free,free)],gravity[free])
        reactions=K@static-gravity;self.contacts=[]
        for g in self.groups.values():
            if not g['wheel']:continue
            vertical=reactions[g['index']+2];moment=reactions[g['index']+3]
            for side in (-1,1):
                N=(vertical+side*moment/(1.435/2))/2
                if N<=0:raise ValueError('initial spatial wheel contact unloads; explicit restraint/load case needed')
                self.contacts.append(dict(group=g,side=side,static_n=float(N),state=TangentialContact()))
        for joint in self.joints:
            J=joint['straight_J'];joint['preload_extension']=J@static
        self.total_mass=sum(g['mass'] for g in self.groups.values())

    def matrices(self,route,advance,track_y):
        K=np.zeros((self.size,self.size));C=np.zeros_like(K);M=np.zeros_like(K);poses={}
        for g in self.groups.values():
            s=advance+g['cg'][0];R=route.frame(s);i=g['index']
            M[i:i+3,i:i+3]=np.eye(3)*g['mass'];M[i+3:i+6,i+3:i+6]=R@g['inertia']@R.T
            poses[g['id']]=dict(s=s,R=R,position=route.position(s,track_y+g['cg'][1],g['cg'][2]))
        plans=[]
        for joint in self.joints:
            J=np.zeros((6,self.size));points=[];Rs=[]
            for sign,endpoint in zip((1.,-1.),joint['endpoints']):
                g=endpoint['group'];p=poses[g['id']];r=p['R']@endpoint['offset'];i=g['index']
                J[:3,i:i+3]+=np.eye(3)*sign;J[:3,i+3:i+6]-=sign*skew(r);J[3:,i+3:i+6]+=np.eye(3)*sign
                points.append(p['position']+r);Rs.append(p['R'])
            frame=Rs[0];G=np.zeros((6,6));G[:3,:3]=frame;G[3:,3:]=frame
            localJ=G.T@J;K+=localJ.T@joint['K']@localJ;C+=localJ.T@joint['C']@localJ
            error=np.concatenate([frame.T@(points[0]-points[1]),-Rotation.from_matrix(Rs[0].T@Rs[1]).as_rotvec()])
            plans.append(dict(joint=joint,J=localJ,error=error))
            if 'preload_extension' not in joint:joint['straight_J']=localJ
        return K,C,M,(poses,plans)


def run_spatial(model,configuration,*,dt=.002,duration_s=1.,deck_mesh=4,rail_step=1.,sample_callback=None):
    """Implicit sparse monolithic integration, contact opening and return mapping."""
    if not .0000625<=dt<=.005 or not 0<duration_s<=30. or math.ceil(duration_s/dt)>200000:raise ValueError('spatial time/budget outside domain')
    maximum_iterations=configuration.get('newton_max_iterations',50)
    if type(maximum_iterations) is not int or not 2<=maximum_iterations<=100:raise ValueError('bounded integer Newton iteration limit required')
    bridge=deepcopy(model['bridge']);condition=configuration.get('infrastructure_condition',{})
    for key,field in [('foundation_stiffness_factor','ground_scenarios'),('bearing_stiffness_factor','bearing')]:
        factor=condition.get(key,1.)
        if type(factor) not in (int,float) or not np.isfinite(factor) or not 0<factor<=2:raise ValueError('invalid infrastructure condition factor')
        if field=='ground_scenarios':
            for ground in bridge['study'][field]:
                for k in ('axial_stiffness_n_m','lateral_stiffness_n_m','rotational_stiffness_nm_rad'):ground[k]*=factor
            if 'foundation_stiffness_si' in bridge:bridge['foundation_stiffness_si']=(np.asarray(bridge['foundation_stiffness_si'])*factor).tolist()
        else:
            for k in ('horizontal_stiffness_n_m','vertical_stiffness_n_m','rotational_stiffness_nm_rad'):
                if k in bridge['study'][field]:bridge['study'][field][k]*=factor
    route=Route(configuration['route']);structure=SpatialStructure(bridge,route,deck_mesh=deck_mesh,rail_step=rail_step,modes=12)
    trains=[];nb=structure.K.shape[0];size=nb
    for entry in configuration['traffic']:
        if entry['track'] not in (0,1):raise ValueError('traffic requires track 0/1')
        vehicle=SpatialVehicle(loaded_model(model,entry['load_case']),configuration['joint_laws'])
        trains.append(dict(vehicle=vehicle,entry=entry,start=size));size+=vehicle.size
    if len({r['entry']['id'] for r in trains})!=len(trains) or not 1<=len(trains)<=4:raise ValueError('unique bounded train identities required')
    unconstrained=np.asarray([i for i in range(size) if i not in structure.fixed])
    material=configuration['contact'];E=material['effective_modulus_pa'];radius=material['rolling_radius_m']
    profiles={side:ProfilePair(material['wheel_profiles'][str(side)],material['rail_profile'],radius,E) for side in (-1,1)}
    reference_profiles={side:profiles[side].locate(0.,0.) for side in (-1,1)}
    q=np.zeros(size);q[:nb]=structure.dead_displacement;v=np.zeros(size);acc=np.zeros(size)
    beta=.25;gamma=.5;omega1=structure.omega[0];omega2=max(omega1*2,2*math.pi*12);damp=configuration['bridge_damping_ratio']
    alpha=2*damp*omega1*omega2/(omega1+omega2);beta_R=2*damp/(omega1+omega2)
    CB=alpha*structure.M+beta_R*structure.K
    massblocks=[structure.M];Kblocks=[structure.K];Cblocks=[CB]
    history=[];iterations=[];minimum=math.inf;maximum=0.;work_error=0.;domain=[]
    for step in range(1,math.ceil(duration_s/dt)+1):
        t=step*dt;pred=q+dt*v+dt*dt*(.5-beta)*acc;predv=v+dt*(1-gamma)*acc
        plans=[];massblocks=[structure.M];Kblocks=[structure.K];Cblocks=[CB]
        for train in trains:
            e=train['entry'];elapsed=t-e['arrival_time_s'];speed=max(0.,e['speed_m_s']+e['acceleration_m_s2']*elapsed)
            drive_acceleration=e['acceleration_m_s2']
            if e['acceleration_m_s2']<0 and elapsed>=-e['speed_m_s']/e['acceleration_m_s2']:
                elapsed=-e['speed_m_s']/e['acceleration_m_s2'];speed=0.;drive_acceleration=0.
            train['drive_acceleration']=drive_acceleration
            advance=e['initial_advance_m']+e['speed_m_s']*elapsed+.5*e['acceleration_m_s2']*elapsed**2
            K,C,M,geometry=train['vehicle'].matrices(route,advance,structure.tracks[e['track']]);massblocks.append(csc_matrix(M));Kblocks.append(csc_matrix(K));Cblocks.append(csc_matrix(C))
            train['poses']=geometry[0]
            for group in train['vehicle'].groups.values():
                p=geometry[0][group['id']];s=p['s'];h=.01;y=structure.tracks[e['track']]+group['cg'][1];z=group['cg'][2]
                plus=route.position(s+h,y,z);minus=route.position(s-h,y,z);centre=p['position']
                derivative=(plus-minus)/(2*h);second=(plus-2*centre+minus)/(h*h)
                p['reference_velocity']=derivative*speed
                p['reference_acceleration']=second*speed*speed+derivative*drive_acceleration
                def angular(station):return Rotation.from_matrix(route.frame(station+h)@route.frame(station-h).T).as_rotvec()/(2*h)
                rate=angular(s);p['reference_omega']=rate*speed
                p['reference_alpha']=(angular(s+h)-angular(s-h))/(2*h)*speed*speed+rate*drive_acceleration
            for plan in geometry[1]:
                joint=plan['joint'];velocities=[];omegas=[]
                for endpoint in joint['endpoints']:
                    pg=geometry[0][endpoint['group']['id']];lever=pg['R']@endpoint['offset']
                    velocities.append(pg['reference_velocity']+np.cross(pg['reference_omega'],lever));omegas.append(pg['reference_omega'])
                first=geometry[0][joint['endpoints'][0]['group']['id']]
                plan['reference_rate']=np.concatenate([first['R'].T@(velocities[0]-velocities[1])-np.cross(first['R'].T@first['reference_omega'],plan['error'][:3]),first['R'].T@(omegas[0]-omegas[1])])
            plans.append((train,speed,advance,geometry))
        M=block_diag(massblocks,format='csc');K=block_diag(Kblocks,format='csc');C=block_diag(Cblocks,format='csc')
        A=M/(beta*dt*dt)+C*gamma/(beta*dt)+K
        current=pred.copy();contact_rows=[];joint_rows=[];last_states=[]
        for iteration in range(maximum_iterations):
            av=(current-pred)/(beta*dt*dt);vv=predv+gamma*dt*av;external=np.zeros(size);external[:nb]=structure.dead_load
            kr=[];kc=[];kv=[];contact_rows=[];joint_rows=[];last_states=[];step_domain=[]
            for train,speed,advance,(poses,joint_plans) in plans:
                vehicle=train['vehicle'];offset=train['start'];uq=current[offset:offset+vehicle.size];vq=vv[offset:offset+vehicle.size];e=train['entry']
                wheel_groups=[g for g in vehicle.groups.values() if g['wheel']]
                driven=[g for g in wheel_groups if g['powered']] if train['drive_acceleration']>0 else wheel_groups
                if train['drive_acceleration']>0 and not driven:raise ValueError('positive traction demand requires powered wheelsets')
                effective_mass=vehicle.total_mass+sum(g['inertia'][1,1]/radius**2 for g in wheel_groups)
                for g in vehicle.groups.values():
                    p=poses[g['id']];i=offset+g['index'];R=p['R'];a_ref=p['reference_acceleration']
                    external[i:i+3]+=g['mass']*(np.array([0.,0.,-9.81])-a_ref)
                    wref=p['reference_omega'].copy()
                    reference_alpha=p['reference_alpha'].copy()
                    if g['wheel']:
                        spin=R[:,1]*speed/radius;wref+=spin
                        reference_alpha+=R[:,1]*train['drive_acceleration']/radius+np.cross(p['reference_omega'],spin)
                    inertia=R@g['inertia']@R.T;w=wref+vq[g['index']+3:g['index']+6]
                    external[i+3:i+6]-=np.cross(w,inertia@w)+inertia@reference_alpha
                    if g['wheel'] and any(g is drive for drive in driven):
                        torque=train['drive_acceleration']*effective_mass*radius/len(driven)
                        external[i+3:i+6]+=R[:,1]*torque
                for plan in joint_plans:
                    joint=plan['joint'];J=plan['J'];law=joint['law']
                    extension=plan['error']+joint['preload_extension'];external[offset:offset+vehicle.size]-=J.T@joint['K']@extension
                    displacement=extension+J@uq
                    jrate=plan['reference_rate']
                    jvelocity=J@vq+jrate
                    external[offset:offset+vehicle.size]-=J.T@joint['C']@jrate
                    force,kt,ct=joint_response(law,displacement,jvelocity)
                    linear=joint['K']@displacement+joint['C']@jvelocity
                    external[offset:offset+vehicle.size]-=J.T@(force-linear)
                    delta=J.T@(kt-joint['K']+(ct-joint['C'])*gamma/(beta*dt))@J
                    for ia,ib in zip(*np.nonzero(delta)):
                        kr.append(offset+int(ia));kc.append(offset+int(ib));kv.append(float(delta[ia,ib]))
                    limits=np.asarray(law['motion_bounds_si'])
                    if np.any(displacement<limits[:,0]) or np.any(displacement>limits[:,1]):step_domain.append('joint-motion:'+joint['id'])
                    joint_rows.append(dict(train=e['id'],joint=joint['id'],relative_pose_si=displacement.tolist(),force_moment_si=force.tolist()))
                for contact in vehicle.contacts:
                    g=contact['group'];side=contact['side'];p=poses[g['id']];R=p['R'];gi=g['index'];s=p['s'];r=R@np.array([0.,side*structure.gauge/2,-radius])
                    Jv=np.zeros((3,vehicle.size));Jv[:,gi:gi+3]=np.eye(3);Jv[:,gi+3:gi+6]=-skew(r)
                    # Wheel spin rotates material, not the geometric circular patch.
                    Jposition=Jv.copy();Jposition[:,gi+3:gi+6]=Jv[:,gi+3:gi+6]@(np.eye(3)-np.outer(R[:,1],R[:,1]))
                    port=structure.rail_port(s,e['track'],side)
                    # Alignment elevations include the dead-load equilibrium.
                    d_vehicle=Jposition@uq;d_bridge=np.zeros(3) if port is None else (port['H']@(current[port['dofs']]-structure.dead_displacement[port['dofs']]))[:3]
                    shift=float(R[:,1]@(d_vehicle-d_bridge));roll=float(R[:,0]@uq[gi+3:gi+6])
                    try:location=profiles[side].locate(shift,roll)
                    except ValueError as error:
                        step_domain.append(str(error));location=profiles[side].locate(0.,0.)
                    reference=reference_profiles[side];normal=R@location['normal_local'];coefficient=location['coefficients']
                    d0=patch(contact['static_n']/float(reference['normal_local'][2]),reference['coefficients'])['penetration_m']
                    rough=configuration['irregularity']['amplitude_m']*math.sin(2*math.pi*s/configuration['irregularity']['wavelength_m'])
                    if configuration['wheel_defect']['depth_m']:
                        rough+=configuration['wheel_defect']['depth_m']*math.cos(speed*t/radius)
                    penetration=d0-profile_normal_gap(float(R[:,2]@(d_vehicle-d_bridge)),location,reference,rough)
                    N=normal_force(penetration,coefficient);patch_values=patch(N,coefficient)
                    if patch_values['semi_axis_x_m']>radius*.1 or patch_values['semi_axis_y_m']>.025:step_domain.append('contact-patch-validity')
                    r_material=R@np.array([0.,side*structure.gauge/2,-location['rolling_radius_m']])
                    velocity=p['reference_velocity']+np.cross(p['reference_omega'],r_material)+(Jv@vq)
                    velocity+=np.cross(R@np.array([0.,speed/radius,0.]),r_material)
                    if port is not None:velocity-=(port['H']@vv[port['dofs']])[:3]
                    tangents=np.column_stack([R[:,0],np.cross(normal,R[:,0])]);tangent_velocity=tangents.T@velocity
                    state=contact['state'];tangent=state.trial(tangent_velocity,dt,N,material['tangential_stiffness_n_m'],material['friction_coefficient'])
                    F=N*normal+tangents@tangent['force_n'];external[offset:offset+vehicle.size]+=Jv.T@F
                    bridge_map=None
                    if port is not None:
                        Hb=port['H'][:3];external[port['dofs']]-=Hb.T@F;bridge_map=(port['dofs'],Hb)
                    columns=list(range(offset,offset+vehicle.size));G=Jposition;Gt=Jv
                    if bridge_map is not None:
                        columns=bridge_map[0]+columns;G=np.hstack([-bridge_map[1],Jposition]);Gt=np.hstack([-bridge_map[1],Jv])
                    active=np.any(np.abs(G)+np.abs(Gt)>0,axis=0);columns=np.asarray(columns)[active];G=G[:,active];Gt=Gt[:,active]
                    normal_tangent=1.5*coefficient['coefficient_n_m32']*math.sqrt(max(penetration,0.))
                    effective_normal=normal-tangents@tangent['restoring_normal_derivative']
                    jac=Gt.T@(normal_tangent*np.outer(effective_normal,normal))@G
                    jac+=Gt.T@(gamma/beta*tangents@tangent['restoring_tangent_n_m']@tangents.T)@Gt
                    for ia,ib in zip(*np.nonzero(jac)):kr.append(int(columns[ia]));kc.append(int(columns[ib]));kv.append(float(jac[ia,ib]))
                    vehicle_power=F@(Jv@vq);bridge_power=0. if port is None else F@((port['H']@vv[port['dofs']])[:3])
                    relative_power=F@(Jv@vq-(np.zeros(3) if port is None else (port['H']@vv[port['dofs']])[:3]))
                    work_error=max(work_error,abs(vehicle_power-bridge_power-relative_power))
                    vertical_force=float(R[:,2]@F)
                    contact_rows.append(dict(train=e['id'],wheelset=g['id'],side=side,station_m=float(s),normal_n=N,vertical_n=vertical_force,lateral_n=float(R[:,1]@F),
                        longitudinal_n=float(R[:,0]@F),lateral_vertical_ratio=float(abs(R[:,1]@F)/max(vertical_force,1e-9)),
                        unloading_ratio=1-vertical_force/contact['static_n'],contact_closed=N>0,creep_velocity_m_s=tangent_velocity.tolist(),
                        contact_y_m=location['contact_y_m'],wheel_y_m=location['wheel_y_m'],
                        patch=patch_values,friction_dissipation_j=tangent['dissipation_j']))
                    last_states.append((state,tangent))
            residual=M@av+C@vv+K@current-external
            norm=float(np.max(np.abs(residual[unconstrained])))
            if norm<configuration['newton_force_tolerance_n']:break
            tangent=A+coo_matrix((kv,(kr,kc)),shape=(size,size)).tocsc()
            increment=np.zeros(size)
            increment[unconstrained]=splu(tangent[unconstrained][:,unconstrained]).solve(-residual[unconstrained])
            if not np.isfinite(increment).all():raise RuntimeError('nonfinite spatial Newton increment')
            # Bounded relaxation helps when contact opens/returns to the surface.
            factor=min(1.,.02/max(np.max(np.abs(increment)),.02));current+=factor*increment
        else:raise RuntimeError(f'spatial nonlinear step did not converge at {t:g}s: residual {norm:g} N')
        domain.extend(step_domain)
        minimum=min(minimum,min(row['normal_n'] for row in contact_rows));maximum=max(maximum,max(row['normal_n'] for row in contact_rows))
        for state,result in last_states:state.commit(result)
        q=current;acc=(q-pred)/(beta*dt*dt);v=predv+gamma*dt*acc;iterations.append(iteration+1)
        for train in trains:
            for group in train['vehicle'].groups.values():
                i=train['start']+group['index'];angles=q[i+3:i+6].copy()
                if group['wheel']:
                    spin=train['poses'][group['id']]['R'][:,1];angles-=spin*(spin@angles)
                if np.max(np.abs(angles))>.15:domain.append('small-angle-body-domain')
        body_rows=[]
        for train in trains:
            for group in train['vehicle'].groups.values():
                if group['kind']!='carbody':continue
                i=train['start']+group['index'];pose=train['poses'][group['id']];R=pose['R']
                # Specific force is excluded: these are kinematic acceleration
                # histories at the rigid CG, not seat/body-interface measurements.
                linear=pose['reference_acceleration']+acc[i:i+3]
                angular=pose['reference_alpha']+acc[i+3:i+6]
                body_rows.append(dict(train=train['entry']['id'],body=group['id'],reference_station_m=pose['s'],
                    frame_to_global=R.tolist(),displacement_global_m=q[i:i+3].tolist(),
                    rotation_perturbation_global_rad=q[i+3:i+6].tolist(),
                    angular_velocity_global_rad_s=(pose['reference_omega']+v[i+3:i+6]).tolist(),
                    velocity_global_m_s=(pose['reference_velocity']+v[i:i+3]).tolist(),
                    acceleration_global_m_s2=linear.tolist(),acceleration_body_m_s2=(R.T@linear).tolist(),
                    angular_acceleration_body_rad_s2=(R.T@angular).tolist(),
                    reference_point='rigid-body centre of gravity; flexible seat transfer not represented'))
        history.append(dict(time_s=t,contacts=contact_rows,joints=joint_rows,bodies=body_rows,
            peak_structure_displacement_m=float(np.max(np.abs(q[:nb].reshape(-1,6)[:,:3]))),
            peak_structure_acceleration_m_s2=float(np.max(np.abs(acc[:nb].reshape(-1,6)[:,:3]))),
            peak_vehicle_acceleration_m_s2=float(np.max(np.abs(acc[nb:].reshape(-1,6)[:,:3]))),
            peak_carbody_acceleration_m_s2=max(float(np.max(np.abs(acc[train['start']+g['index']:train['start']+g['index']+3])))
                for train in trains for g in train['vehicle'].groups.values() if g['kind']=='carbody'),
            peak_total_carbody_acceleration_m_s2=max(max(abs(v) for v in body['acceleration_body_m_s2']) for body in body_rows),
            structural_member_demands=structure.full_member_demands(q[:nb]),
            foundation_reactions_si=[(s['K']@(s['J']@q[s['dofs']])).tolist() for s in structure.springs if s['kind']=='foundation'],
            newton_residual_n=norm,newton_iterations=iteration+1))
        if sample_callback is not None:sample_callback(deepcopy(history[-1]))
    return dict(schema='osr-spatial-train-track-bridge/1',configuration_sha256=fingerprint(configuration),hardware_definition_sha256=fingerprint(model),
        dofs=size,full_sparse_fem=True,modal_truncation_used=False,tracks=2,span_count=model['bridge']['span_count'],
        trains=[dict(id=t['entry']['id'],body_groups=len(t['vehicle'].groups),mass_kg=t['vehicle'].total_mass,load_case=t['entry']['load_case']) for t in trains],
        time_step_s=dt,duration_s=duration_s,steps=len(history),maximum_newton_iterations=max(iterations),
        contact_power_balance_residual_w=work_error,minimum_wheel_contact_n=minimum,maximum_wheel_contact_n=maximum,
        peak_lateral_vertical_ratio=max(c['lateral_vertical_ratio'] for r in history for c in r['contacts']),
        maximum_wheel_unloading=max(c['unloading_ratio'] for r in history for c in r['contacts']),
        peak_structure_displacement_m=max(r['peak_structure_displacement_m'] for r in history),
        peak_ride_acceleration_m_s2=max(r['peak_carbody_acceleration_m_s2'] for r in history),
        peak_total_carbody_acceleration_m_s2=max(r['peak_total_carbody_acceleration_m_s2'] for r in history),
        peak_unsprung_and_vehicle_acceleration_m_s2=max(r['peak_vehicle_acceleration_m_s2'] for r in history),
        initial_condition='dead-equilibrated structure and gravity-preloaded vehicle; live load startup transient included',
        within_adapter_domain=not domain,domain_exceedances=sorted(set(domain)),history=history,
        physical_validation=False,engineering_released=False,contact_reference_comparison_performed=False,
        limitations=['single nonconformal Hertz patch; flange/multiple patch contact rejected','small perturbation rotations; finite alignment/cant prescribed',
                     'forces use nominal contact ports; finite patch motion/rail roll needs a dedicated geometry adapter',
                     'equivalent powered-axle traction/all-axle braking; supplier control and torque limits not represented',
                     'six-DOF equivalent joint laws need supplier/calibration evidence','linear Timoshenko structure; nonlinear material capacity evaluated separately'])
