"""Work-conjugate flexible carbody attachment matrices for the spatial vehicle.

The vertical Euler-Bernoulli basis is a reduced research model with uniformly
represented body mass. Shell/solid and measured modal bases are separate gates.
No new equipment mass is introduced by changing generalized coordinates.
"""
import math
import numpy as np
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle
from engineering.civil_exploration.spatial_structure import Route
from engineering.industrialisation.common import finite
from .flexible import beam_modes, attachment_shape


def attachment_slope(model,station_m):
    x=finite(station_m,'attachment station',0.);L=model['length_m'];n=model['elements']
    if x>L:raise ValueError('modal attachment outside carbody')
    h=L/n;i=min(n-1,int(x/h));s=(x-i*h)/h
    N=np.array([(-6*s+6*s*s)/h,1-4*s+3*s*s,(6*s-6*s*s)/h,-2*s+3*s*s])
    return N@np.asarray(model['shapes_mass_normalized'])[2*i:2*i+4]


class FlexibleVehicle(SpatialVehicle):
    def __init__(self,model,joint_laws,*,ei_nm2=3e8,mode_count=6,damping_ratio=.02,equipment_mounts=None):
        self.modal={};self.damping_ratio=finite(damping_ratio,'modal damping',0.)
        if self.damping_ratio>.2:raise ValueError('research modal damping outside bounds')
        super().__init__(model,joint_laws,equipment_mounts=equipment_mounts);self.rigid_size=self.size;self.static_coordinates=None
        for car in model['family_definition']['cars']:
            if car['id'] not in self.groups:continue
            body=self.groups[car['id']];basis=beam_modes(car['length_m'],body['mass']/car['length_m'],ei_nm2,modes=mode_count)
            self.modal[car['id']]=dict(index=self.size,basis=basis,centre_x_m=car['centre_x_m']);self.size+=mode_count
        # Recalculate preload against the coupled coordinates, preserving gravity
        # and wheel restraint. Old static extensions are not carried into a new K.
        route=Route(dict(radius_m=0.,cant_rad=0.,cant_start_m=0.,cant_end_m=1.,grade_rad=0.,basis='straight static modal verification'))
        K,_,_,(_,plans)=self.matrices(route,0.,0.);gravity=np.zeros(self.size)
        for g in self.groups.values():gravity[g['index']+2]=-g['mass']*9.81
        fixed={i for g in self.groups.values() if g['wheel'] for i in range(g['index'],g['index']+6)};free=[i for i in range(self.size) if i not in fixed]
        q=np.zeros(self.size);q[free]=np.linalg.solve(K[np.ix_(free,free)],gravity[free]);reactions=K@q-gravity
        for contact in self.contacts:
            g=contact['group'];i=g['index'];contact['static_n']=float((reactions[i+2]+contact['side']*reactions[i+3]/(.7175))/2)
            if contact['static_n']<=0:raise ValueError('flexible static model unloads a wheel')
        for plan in plans:plan['joint']['preload_extension']=plan['J']@q
        self.static_coordinates=q
        self.intrinsic_preload=np.zeros(self.size)
        for record in self.modal.values():
            i=record['index'];n=len(record['basis']['frequencies_hz'])
            self.intrinsic_preload[i:i+n]=np.asarray(record['basis']['modal_stiffness'])@q[i:i+n]

    def matrices(self,route,advance,track_y):
        K,C,M,(poses,plans)=super().matrices(route,advance,track_y)
        if not self.modal:return K,C,M,(poses,plans)
        for record in self.modal.values():
            i=record['index'];basis=record['basis'];n=len(basis['frequencies_hz']);ix=np.arange(i,i+n);omega=2*math.pi*np.asarray(basis['frequencies_hz'])
            M[np.ix_(ix,ix)]=basis['modal_mass'];K[np.ix_(ix,ix)]+=basis['modal_stiffness'];C[ix,ix]+=2*self.damping_ratio*omega
        for plan in plans:
            joint=plan['joint'];old=plan['J'];J=old.copy()
            for sign,end in zip((1.,-1.),joint['endpoints']):
                g=end['group'];record=self.modal.get(g['id'])
                if record is None:continue
                x=float(g['cg'][0]+end['offset'][0]-record['centre_x_m']+record['basis']['length_m']/2)
                shape=attachment_shape(record['basis'],x);slope=attachment_slope(record['basis'],x);n=len(shape);i=record['index']
                local=np.zeros((6,n));local[2]=shape;local[4]=-slope
                first_frame=poses[joint['endpoints'][0]['group']['id']]['R'];body_frame=poses[g['id']]['R'];R=first_frame.T@body_frame
                transform=np.zeros((6,6));transform[:3,:3]=R;transform[3:,3:]=R
                J[:,i:i+n]+=sign*transform@local
            K+=J.T@joint['K']@J-old.T@joint['K']@old;C+=J.T@joint['C']@J-old.T@joint['C']@old;plan['J']=J
        # Analytical assembly is symmetric. Remove only the rounding asymmetry
        # of dense products/subtractions before the coupled static solve.
        return (K+K.T)/2,(C+C.T)/2,(M+M.T)/2,(poses,plans)

    def modal_observation(self,body,station_m,q,v,a):
        record=self.modal[body];i=record['index'];shape=attachment_shape(record['basis'],station_m);n=len(shape)
        return dict(body=body,station_m=station_m,flexible_displacement_m=float(shape@(q[i:i+n]+self.static_coordinates[i:i+n])),flexible_velocity_m_s=float(shape@v[i:i+n]),flexible_acceleration_m_s2=float(shape@a[i:i+n]),reference='flexible transfer relative to rigid body',static_modal_preload_included=True,physical_validation=False)
