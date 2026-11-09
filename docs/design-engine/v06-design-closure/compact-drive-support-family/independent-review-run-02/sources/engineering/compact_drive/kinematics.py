"""Track/contact, wheelset, primary frame and secondary body transforms.

Wheelset contact never receives primary/secondary vertical travel. Gear swing
is about its actual transverse output shaft (Y), not an unexplained X roll.
The finite samples are diagnostics; conservative continuous padding remains a
separate screen and may overpredict a clash. No sampled-only clearance pass.
"""
from itertools import product
from math import sin,cos,sqrt
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]

def mul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def rotation(yaw=0.,roll=0.,pitch=0.):
    z=[[cos(yaw),-sin(yaw),0.],[sin(yaw),cos(yaw),0.],[0.,0.,1.]]
    x=[[1.,0.,0.],[0.,cos(roll),-sin(roll)],[0.,sin(roll),cos(roll)]]
    y=[[cos(pitch),0.,sin(pitch)],[0.,1.,0.],[-sin(pitch),0.,cos(pitch)]]
    return mul(mul(z,x),y)

def apply(T,p):return [sum(T[i][j]*p[j] for j in range(3))+T[i][3] for i in range(3)]
def pivot(R,at,translation):
    return [[*R[i],at[i]-sum(R[i][j]*at[j] for j in range(3))+translation[i]] for i in range(3)]+[[0.,0.,0.,1.]]

def frame_tree(bogie_x,axle_local_x,pose,lift,*,gear_pitch=0.):
    """Nominal input coordinates are railhead SI at radius0.38m.

    Cant changes the contact plane and shared unsprung frame. Primary heave/
    frame roll move sprung motor/frame. Secondary heave moves the body only.
    Body lift is already present in nominal physical geometry, never applied
    twice here. Wheelset yaw uses the declared bogie relative yaw as a bounded
    packaging hypothesis, not an asserted curved-track contact solution.
    """
    wear=pose['wheel_radius_m']-.38
    cant=pose['cant_rad'];yaw=pose['yaw_rad'];roll=pose['frame_roll_rad']
    contact=[bogie_x,0.,0.];axis=[bogie_x+axle_local_x,0.,.38]
    unsprung=pivot(rotation(yaw,cant),contact,[0.,0.,wear])
    frame=pivot(rotation(yaw,cant+roll),[bogie_x,0.,.41],
                [0.,pose['lateral_m'],wear+pose['primary_m']])
    body=pivot(I,[bogie_x,0.,0.],[0.,0.,wear+pose['primary_m']+pose['secondary_m']])
    # Gear output is rigidly carried by wheelset, with explicit case swing.
    gear_local=pivot(rotation(pitch=gear_pitch),axis,[0.,0.,0.])
    gear=[[*[sum(unsprung[i][k]*gear_local[k][j] for k in range(3)) for j in range(3)],
           sum(unsprung[i][k]*gear_local[k][3] for k in range(3))+unsprung[i][3]] for i in range(3)]+[[0.,0.,0.,1.]]
    return dict(wheelset=unsprung,bogie=frame,body=body,gear=gear,
        contact_geometry='Declared yaw/cant contact-plane envelope only; exact flange/tread/curve dynamics not established',body_lift_already_in_nominal_geometry_m=lift)

def poses(policy):
    m=policy['movement'];out=[]
    #24diagnostic states; continuous paddings cover independently variable signs.
    for j,(wear,sy,sp,ss) in enumerate(product(policy['wheel_diameter_m'],(-1,1),(-1,1),(-1,1))):
        out.append(dict(wheel_radius_m=wear/2,yaw_rad=sy*m['yaw_rad'],
            cant_rad=(-1 if j%2 else 1)*m['track_cant_rad'],frame_roll_rad=(-1 if j%3 else 1)*m['frame_roll_rad'],
            primary_m=sp*m['primary_heave_m'],secondary_m=ss*m['secondary_heave_m'],lateral_m=(-1 if j%2 else 1)*m['lateral_m']))
    for sign in (-1,1):
        for wear in policy['wheel_diameter_m']:
            out.append(dict(wheel_radius_m=wear/2,yaw_rad=0.,cant_rad=sign*m['track_cant_rad'],frame_roll_rad=0.,primary_m=0.,secondary_m=0.,lateral_m=0.))
    assert len(out)<=policy['limits']['maximum_pose_samples'];return out

def continuous_padding(size,relative,policy,uncertainty=0.):
    """Conservative radius*angle bound, used only to preserve a HOLD.

    This is not a contact/rail dynamics proof. Ground uses wheelset wear/cant/
    actual local case swing separately, with no sprung-body jounce allocation.
    """
    m=policy['movement'];radius=sqrt(sum((s/2)**2 for s in size))
    angle=m['yaw_rad']+m['frame_roll_rad']+m['track_cant_rad']
    vertical=m['secondary_heave_m']+(m['primary_heave_m'] if relative=='body-gear' else 0.)
    return [radius*angle+m['lateral_m']+uncertainty]*2+[radius*(m['frame_roll_rad']+m['track_cant_rad'])+vertical+uncertainty]
