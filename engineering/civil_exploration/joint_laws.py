"""Six-axis nonlinear force curves, damping and unilateral bump stops."""
import numpy as np


def curve(points, x):
    data=np.asarray(points,dtype=float)
    if data.ndim!=2 or data.shape[1]!=2 or len(data)<2 or not np.isfinite(data).all() or np.any(np.diff(data[:,0])<=0) or np.any(np.diff(data[:,1])<0):
        raise ValueError('joint curve requires ordered abscissae and passive monotone forces')
    if not data[0,0]<=x<=data[-1,0]:raise ValueError('joint curve outside supplied displacement/velocity range')
    i=min(len(data)-2,max(0,int(np.searchsorted(data[:,0],x)-1)))
    slope=(data[i+1,1]-data[i,1])/(data[i+1,0]-data[i,0])
    return float(data[i,1]+slope*(x-data[i,0])),float(slope)


def response(law, displacement, velocity):
    q=np.asarray(displacement,dtype=float);v=np.asarray(velocity,dtype=float)
    K=np.asarray(law['stiffness_si']);C=np.asarray(law['damping_si'])
    if q.shape!=(6,) or v.shape!=(6,) or not np.isfinite(np.concatenate([q,v])).all():raise ValueError('six finite joint coordinates required')
    force=K@q+C@v;kt=K.copy();ct=C.copy()
    for key,values,matrix,is_displacement in [('force_displacement_curves',q,kt,True),('damping_curves',v,ct,False)]:
        curves=law.get(key,[None]*6)
        if len(curves)!=6:raise ValueError('six joint axis curve slots required')
        for axis,points in enumerate(curves):
            if points is None:continue
            value,slope=curve(points,values[axis]);base=K if is_displacement else C
            if np.any(np.delete(base[axis],axis)!=0) or np.any(np.delete(base[:,axis],axis)!=0):
                raise ValueError('independent nonlinear axis curves cannot replace a coupled joint matrix; supply a passive coupled potential')
            if not is_displacement:
                zero,_=curve(points,0.)
                if abs(zero)>1e-12 or value*values[axis]<-1e-12:
                    raise ValueError('damping curve must vanish at rest and dissipate energy')
            force[axis]+=value-base[axis]@values
            matrix[axis,:]=0.;matrix[axis,axis]=slope
    stops=law.get('bump_stops',[None]*6)
    if len(stops)!=6:raise ValueError('six bump-stop slots required')
    for axis,stop in enumerate(stops):
        if stop is None:continue
        lo,hi,k,c=[stop[x] for x in ('lower_si','upper_si','stiffness_si','damping_si')]
        if not np.isfinite([lo,hi,k,c]).all() or lo>=hi or min(k,c)<0:raise ValueError('invalid joint stop')
        over=q[axis]-np.clip(q[axis],lo,hi)
        if over:
            force[axis]+=k*over;kt[axis,axis]+=k
            if over*v[axis]>0:force[axis]+=c*v[axis];ct[axis,axis]+=c
    return force,kt,ct
