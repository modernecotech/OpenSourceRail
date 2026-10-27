"""Independent scalar manufactured controls for residual SUPG transport."""
import numpy as np
import pytest
from engineering.design_search import lim_transport as t


def _one_dimensional(n,speed,diffusivity):
    h=1/n;g=np.tile([-1/h,1/h],(n,1));m0=np.full(n,h);m1=np.full((n,2),h/2)
    o=t.operators(m0,m1,g,sigma=1.,speed=speed,diffusivity=diffusivity,name='supg-coth')
    return h,g,m0,m1,o


@pytest.mark.parametrize('speed',[20.,-20.])
def test_steady_boundary_layer_is_nodally_exact_without_overwriting_physical_diffusion(speed):
    n=12;diff=.04;h,g,m0,m1,o=_one_dimensional(n,speed,diff);K=np.zeros((n+1,n+1))
    for k in range(n):
        element=diff*h*np.outer(g[k],g[k])+speed*np.outer(m1[k],g[k])+o['transport'][k]
        K[k:k+2,k:k+2]+=element
    b=np.zeros(n+1);K[0,:]=0;K[-1,:]=0;K[0,0]=K[-1,-1]=1;b[-1]=1
    result=np.linalg.solve(K,b);x=np.linspace(0,1,n+1);p=speed/diff
    exact=(np.exp(p*(x-1))-np.exp(-p))/(1-np.exp(-p)) if speed>0 else np.expm1(p*x)/np.expm1(p)
    assert np.max(abs(result-exact))<1e-12
    assert result.min()>-1e-12 and result.max()<1+1e-12
    assert np.max(o['streamline_Peclet'])>1
    # Reversal changes the nonsymmetric transient/floating operators' sign.
    assert np.sign(o['mass'][0,1,0])==np.sign(speed)
    assert np.all(o['tau_s']>=0)


def test_transient_and_floating_terms_are_present_and_match_exact_polynomial_residual():
    h,g,m0,m1,o=_one_dimensional(8,20.,.04);x=np.linspace(0,1,9);cells=np.array([[i,i+1] for i in range(8)])
    # A=x, A_dot=2+x and u=3: full residual D=25+x. The test is
    # independent of production assembly: integral D = h*(25+x_center).
    A=x[cells];At=2+x[cells];u=3.
    residual=np.einsum('tij,tj->ti',o['mass'],At)+np.einsum('tij,tj->ti',o['transport'],A)+o['floating']*u
    exact=o['tau_s'][:,None]*20*g*(h*(25+x[cells].mean(axis=1)))[:,None]
    assert residual==pytest.approx(exact,rel=1e-12,abs=1e-12)
    actual=t.power(At,A,u,o,.16)
    expected=.16*np.sum(At*exact)
    assert actual==pytest.approx(expected,rel=1e-12)
    assert t.method('supg-coth')['numerical_work_is_physical_heat'] is False


def test_manufactured_transient_linear_solution_includes_source_and_time_upwinding():
    # q(x,t)=(1+t)x solves q_t+v*q_x-d*q_xx=f=x+v*(1+t).
    # It is exactly P1 in space and linear in time. Consistently weighting the
    # source and time terms must preserve the solution at arbitrary Peclet.
    n=10;v=20.;d=.04;dt=.017;h,g,m0,m1,o=_one_dimensional(n,v,d)
    M=np.zeros((n+1,n+1));K=np.zeros_like(M);F=np.zeros(n+1);x=np.linspace(0,1,n+1)
    for k in range(n):
        mass=h/6*np.array([[2.,1.],[1.,2.]])+o['mass'][k]
        stiffness=d*h*np.outer(g[k],g[k])+v*np.outer(m1[k],g[k])+o['transport'][k]
        M[k:k+2,k:k+2]+=mass;K[k:k+2,k:k+2]+=stiffness
        # Exact Gauss integration of N*f and tau*v*N_x*f.
        for q in (-1/np.sqrt(3),1/np.sqrt(3)):
            N=np.array([(1-q)/2,(1+q)/2]);position=(k+(q+1)/2)*h;f=position+v*(1+dt)
            F[k:k+2]+=h/2*(N+o['tau_s'][k]*v*g[k])*f
    system=M/dt+K;rhs=M@x/dt+F
    system[0,:]=0;system[-1,:]=0;system[0,0]=system[-1,-1]=1;rhs[0]=0;rhs[-1]=1+dt
    assert np.linalg.solve(system,rhs)==pytest.approx((1+dt)*x,rel=1e-11,abs=1e-11)


def test_signed_numerical_work_can_be_negative_and_galerkin_is_exactly_unchanged():
    h,g,m0,m1,o=_one_dimensional(3,20.,.04)
    # A_dot decreasing along the streamline while D is positive gives signed
    # negative SUPG work. It cannot be added to physical positive Joule heat.
    At=np.tile([2.,1.],(3,1));A=np.zeros_like(At)
    assert t.power(At,A,3.,o,.16)<0
    zero=t.operators(m0,m1,g,sigma=1.,speed=20.,diffusivity=.04,name='galerkin')
    assert not np.any(zero['mass']) and not np.any(zero['transport']) and not np.any(zero['floating'])
    assert t.method('galerkin')['method_id']!=t.method('supg-coth')['method_id']


def test_unforced_transient_fourier_wave_converges_to_closed_form_decay_and_translation():
    # For periodic q_t+v*q_x-d*q_xx=0 a Fourier mode has the exact complex
    # amplitude exp[-(d*k^2+i*v*k)t]. This also checks positive decay rather
    # than relying on a source manufactured from the discretized operator.
    errors=[];rates=[];v=20.;d=.04;T=.016;k=2*np.pi
    for n in (12,24,48):
        h,g,m0,m1,o=_one_dimensional(n,v,d);M=np.zeros((n,n));K=np.zeros_like(M)
        for e in range(n):
            ix=np.array([e,(e+1)%n]);M[np.ix_(ix,ix)]+=h/6*np.array([[2.,1.],[1.,2.]])+o['mass'][e]
            K[np.ix_(ix,ix)]+=d*h*np.outer(g[e],g[e])+v*np.outer(m1[e],g[e])+o['transport'][e]
        mode=np.exp(1j*k*np.arange(n)/n);rate=np.vdot(mode,K@mode)/np.vdot(mode,M@mode)
        steps=20*n;dt=T/steps;actual=(1+dt*rate)**(-steps);exact=np.exp(-(d*k*k+1j*v*k)*T)
        assert rate.real>0 and abs(actual)<1
        errors.append(abs(actual-exact));rates.append(rate.real)
    assert errors[2]<errors[1]<errors[0] and errors[0]/errors[1]>2
    assert abs(rates[2]-d*k*k)<abs(rates[1]-d*k*k)<abs(rates[0]-d*k*k)


def test_small_peclet_zero_speed_and_invalid_operator_domains():
    tau,pe=t.parameter(np.array([[-1.,1.]]),1e-10,1.)
    assert tau[0]==pytest.approx(1/12,rel=1e-10)
    assert t.parameter(np.array([[-1.,1.]]),0.,1.)[0][0]==0
    for value in (0.,-1.,float('nan')):
        with pytest.raises(ValueError):t.parameter(np.array([[-1.,1.]]),1.,value)
    with pytest.raises(ValueError):t.method('ignore-Peclet')
