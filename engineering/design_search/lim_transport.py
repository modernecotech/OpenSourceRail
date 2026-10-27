"""Residual SUPG operators for the declared P1 moving-aluminium component.

The extra test function is tau*v*dN/dx. It weights the complete interior
residual sigma*(A_dot+v*A_x+u), including time and floating-potential terms.
For affine P1 cells and constant conductor reluctivity the interior diffusion
residual vanishes. Cut-cell moments integrate only the actual moving metal.
Numerical work is signed; it is never renamed copper or secondary Joule heat.
"""
import numpy as np
from engineering.station_rail.common import identity

CODE='engineering/design_search/lim_transport.py'
REFERENCE='https://thesis.caltech.edu/430/4/brooks_an_1981.pdf'
METHODS=('galerkin','supg-coth')


def method(name):
    if name not in METHODS:raise ValueError('Explicit Galerkin or independently checked residual-SUPG method required')
    value=dict(schema='osr-LIM-transport-method/1',name=name,
        formulation='unchanged Galerkin' if name=='galerkin' else 'P1 element-interior residual SUPG: tau*v*N_x*sigma*(A_dot+v*A_x+u)',
        parameter='zero' if name=='galerkin' else 'tau=h/(2*abs(v))*(coth(Pe)-1/Pe), Pe=abs(v)*h/(2*diffusivity), h=2/sum(abs(N_x))',
        source_and_time_terms_weighted=True,numerical_work_is_physical_heat=False,
        validation_scope='Manufactured scalar advection-diffusion and discrete work controls; full moving-field convergence and physical correlation remain open',
        primary_reference=REFERENCE,primary_sections='2.4, 3.2.3-3.2.5 and 3.3',
        operating_map_admitted=False,physical_accepted=False)
    value['method_id']=identity(value);return value


def parameter(gradient_x,speed,diffusivity):
    gradient_x=np.asarray(gradient_x,dtype=float)
    if gradient_x.ndim!=2 or not np.all(np.isfinite(gradient_x)) or not np.isfinite(speed) or not np.isfinite(diffusivity) or diffusivity<=0:raise ValueError('Finite streamline gradients/speed and positive diffusivity required')
    denominator=np.sum(abs(gradient_x),axis=1)
    h=np.divide(2.,denominator,out=np.zeros_like(denominator),where=denominator>0)
    Pe=abs(speed)*h/(2*diffusivity)
    if speed==0:return np.zeros_like(h),Pe
    factor=np.zeros_like(Pe);small=(Pe>0)&(Pe<1e-3);large=Pe>=1e-3
    q=Pe[small];factor[small]=q/3-q**3/45+2*q**5/945
    factor[large]=1/np.tanh(Pe[large])-1/Pe[large]
    return h/(2*abs(speed))*factor,Pe


def operators(m0,m1,gradient_x,*,sigma,speed,diffusivity,name):
    method(name);m0=np.asarray(m0,dtype=float);m1=np.asarray(m1,dtype=float);g=np.asarray(gradient_x,dtype=float)
    if m0.ndim!=1 or m1.shape!=g.shape or len(m0)!=len(g) or not np.all(np.isfinite(m0)) or not np.all(np.isfinite(m1)) or np.any(m0<0) or not np.isfinite(sigma) or sigma<=0:raise ValueError('Finite actual-conductor P1 moments and positive conductivity required')
    tau,Pe=parameter(g,speed,diffusivity)
    if name=='galerkin':tau[:]=0.
    a=sigma*tau*speed
    mass=a[:,None,None]*g[:,:,None]*m1[:,None,:]
    transport=(a*speed*m0)[:,None,None]*g[:,:,None]*g[:,None,:]
    floating=(a*m0)[:,None]*g
    return dict(mass=mass,transport=transport,floating=floating,tau_s=tau,streamline_Peclet=Pe)


def power(local_At,local_A,u,operators,height):
    """Actual SUPG field-equation work, including its possible negative sign."""
    At=np.asarray(local_At);A=np.asarray(local_A)
    residual=np.einsum('tij,tj->ti',operators['mass'],At)+np.einsum('tij,tj->ti',operators['transport'],A)+operators['floating']*u
    return float(height*np.einsum('ti,ti->',At,residual))
