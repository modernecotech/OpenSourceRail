"""Single-patch nonconformal Hertz/Mindlin contact with explicit validity checks.

Supplied wheel/rail profiles locate the patch; no circular pressure assumption is
substituted for an elliptical patch. Conformal/flange/multiple-patch contact is
outside this adapter and requires CONTACT or another qualified formulation.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, minimize_scalar


def finite(value, name, minimum=None):
    if type(value) not in (int,float) or not math.isfinite(value) or (minimum is not None and value<minimum):
        raise ValueError('invalid contact '+name)
    return float(value)


@lru_cache(maxsize=128)
def hertz_coefficients(curvature_x,curvature_y,effective_modulus):
    """Half-space ellipse integrals; unit load fixes force/penetration scaling."""
    for v in (curvature_x,curvature_y,effective_modulus):finite(v,'curvature/modulus',1e-12)
    def integrals(ratio):
        def denominator(t):return math.sqrt((1+t*t)*(ratio*ratio+t*t))
        i0=2*quad(lambda t:1/denominator(t),0,np.inf,epsabs=1e-10)[0]
        ix=2*quad(lambda t:1/((1+t*t)*denominator(t)),0,np.inf,epsabs=1e-10)[0]
        iy=2*quad(lambda t:1/((ratio*ratio+t*t)*denominator(t)),0,np.inf,epsabs=1e-10)[0]
        return i0,ix,iy
    target=curvature_x/curvature_y
    low,high=.02,50.
    if not integrals(low)[1]/integrals(low)[2]<=target<=integrals(high)[1]/integrals(high)[2]:
        raise ValueError('contact aspect ratio is outside nonconformal ellipse domain')
    ratio=brentq(lambda r:math.log(integrals(r)[1]/integrals(r)[2]/target),low,high,xtol=1e-11)
    i0,ix,_=integrals(ratio)
    a=(3*ix/(2*math.pi*effective_modulus*curvature_x))**(1/3);b=ratio*a
    penetration=3*i0/(4*math.pi*effective_modulus*a)
    return dict(a_per_load_cuberoot_m=a,b_per_load_cuberoot_m=b,coefficient_n_m32=penetration**-1.5,
                curvature_x_m_inv=curvature_x,curvature_y_m_inv=curvature_y,effective_modulus_pa=effective_modulus)


def patch(force,coefficients):
    force=finite(force,'normal force',0.)
    if force==0:return dict(semi_axis_x_m=0.,semi_axis_y_m=0.,maximum_pressure_pa=0.,penetration_m=0.)
    a=coefficients['a_per_load_cuberoot_m']*force**(1/3);b=coefficients['b_per_load_cuberoot_m']*force**(1/3)
    return dict(semi_axis_x_m=a,semi_axis_y_m=b,maximum_pressure_pa=3*force/(2*math.pi*a*b),
                penetration_m=(force/coefficients['coefficient_n_m32'])**(2/3))


def normal_force(penetration,coefficients):
    penetration=finite(penetration,'penetration')
    return coefficients['coefficient_n_m32']*max(penetration,0.)**1.5


class ProfilePair:
    def __init__(self,wheel,rail,rolling_radius_m,effective_modulus_pa):
        def spline(points):
            array=np.asarray(points,dtype=float)
            if array.ndim!=2 or array.shape[1]!=2 or len(array)<5 or not np.isfinite(array).all() or np.any(np.diff(array[:,0])<=0):
                raise ValueError('contact profile needs five sorted finite y/z points')
            return CubicSpline(array[:,0],array[:,1],extrapolate=False),(array[0,0],array[-1,0])
        self.wheel,self.wheel_range=spline(wheel);self.rail,self.rail_range=spline(rail)
        self.radius=finite(rolling_radius_m,'rolling radius',1e-6);self.modulus=finite(effective_modulus_pa,'modulus',1.)

    def locate(self,lateral_shift_m,roll_rad=0.):
        shift=finite(lateral_shift_m,'lateral shift');roll=finite(roll_rad,'roll')
        low=max(self.rail_range[0],self.wheel_range[0]+shift)
        high=min(self.rail_range[1],self.wheel_range[1]+shift)
        if low>=high:raise ValueError('wheel/rail profile overlap lost')
        def gap(y):return float(self.wheel(y-shift)+roll*(y-shift)-self.rail(y))
        result=minimize_scalar(gap,bounds=(low,high),method='bounded',options={'xatol':1e-12})
        y=float(result.x);curvature=float(self.wheel(y-shift,2)-self.rail(y,2))
        if not result.success or min(y-low,high-y)<1e-5 or curvature<=0:
            raise ValueError('flange/conformal contact needs another contact adapter')
        grid=np.linspace(low,high,65);derivative=self.wheel(grid-shift,1)+roll-self.rail(grid,1)
        if np.count_nonzero((derivative[:-1]<0)&(derivative[1:]>=0))!=1:
            raise ValueError('multiple contact patches are outside this adapter')
        slope=float(self.rail(y,1));normal=np.asarray([0.,-slope,1.]);normal/=np.linalg.norm(normal)
        coefficient=hertz_coefficients(1/self.radius,curvature,self.modulus)
        return dict(contact_y_m=y,wheel_y_m=y-shift,relative_height_m=gap(y),normal_local=normal,
                    coefficients=coefficient,rolling_radius_m=self.radius-float(self.wheel(y-shift)))


@dataclass
class TangentialContact:
    displacement: np.ndarray | None = None
    dissipated_j: float = 0.

    def trial(self,velocity,dt,normal_n,stiffness_n_m,friction):
        """Elastic stick plus radial-return slip; does not mutate until committed."""
        v=np.asarray(velocity,dtype=float)
        if v.shape!=(2,) or not np.isfinite(v).all():raise ValueError('two finite tangential velocities required')
        for value,name,minimum in [(dt,'step',1e-12),(normal_n,'compression',0.),(stiffness_n_m,'tangential stiffness',1e-12),(friction,'friction',0.)]:finite(value,name,minimum)
        previous=np.zeros(2) if self.displacement is None else self.displacement
        if normal_n==0:
            lost=.5*stiffness_n_m*float(previous@previous)
            return dict(force_n=np.zeros(2),next_displacement=np.zeros(2),dissipation_j=lost,stored_energy_j=0.)
        trial=previous+v*dt;traction=stiffness_n_m*trial;limit=friction*normal_n
        magnitude=np.linalg.norm(traction)
        if magnitude>limit:traction*=limit/magnitude
        current=traction/stiffness_n_m;dissipation=max(0.,float(traction@(trial-current)))
        return dict(force_n=-traction,next_displacement=current,dissipation_j=dissipation,
                    stored_energy_j=.5*stiffness_n_m*float(current@current))

    def commit(self,result):
        self.displacement=result['next_displacement'].copy();self.dissipated_j+=result['dissipation_j']


def benchmarks():
    E=115e9;radius=.38;force=80000.
    c=hertz_coefficients(1/radius,1/radius,E);p=patch(force,c)
    a=(3*force*radius/(4*E))**(1/3);expected=4*E*math.sqrt(radius)/3
    state=TangentialContact();result=state.trial([.02,-.01],.01,force,1e8,.3)
    error=abs(c['coefficient_n_m32']/expected-1)
    return dict(schema='osr-wheel-contact-benchmarks/1',sphere_halfspace_relative_error=error,
        patch_radius_relative_error=abs(p['semi_axis_x_m']/a-1),unilateral_open_force_n=normal_force(-.001,c),
        friction_bound_n=.3*force,observed_tangent_n=float(np.linalg.norm(result['force_n'])),
        passed=bool(error<1e-8 and abs(p['semi_axis_x_m']/a-1)<1e-8 and np.linalg.norm(result['force_n'])<=.3*force*(1+1e-12)),
        physical_validation=False,contact_reference_comparison_performed=False)
