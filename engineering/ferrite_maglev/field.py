"""2D magnetostatic development solver and manufactured-solution controls.

A_z is solved on a Cartesian grid with zero exterior potential. B=(dA/dy,-dA/dx).
Material values below are explicit hypotheses, not adopted supplier B-H/recoil
curves. This is no 3D, loss, demagnetisation or vehicle-force qualification.
"""
import math
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.interpolate import RegularGridInterpolator

MU0=4*math.pi*1e-7


def solve(x,y,reluctivity,source,boundary=None):
    """Conservative five-point variable-reluctivity elliptic solve, SI units."""
    x=np.asarray(x);y=np.asarray(y);nu=np.asarray(reluctivity);rhs=np.asarray(source)
    if len(x)<5 or len(y)<5 or nu.shape!=(len(y),len(x)) or rhs.shape!=nu.shape:
        raise ValueError('matching rectangular mesh/material/source arrays required')
    dx=x[1]-x[0];dy=y[1]-y[0]
    if dx<=0 or dy<=0 or not np.allclose(np.diff(x),dx) or not np.allclose(np.diff(y),dy):raise ValueError('uniform ordered grid required')
    if not np.isfinite(nu).all() or (nu<=0).any() or not np.isfinite(rhs).all():raise ValueError('finite positive reluctivity and finite source required')
    ny,nx=nu.shape;ny0=ny-2;nx0=nx-2
    values=np.zeros_like(nu) if boundary is None else np.array(boundary,dtype=float,copy=True)
    if values.shape!=nu.shape or not np.isfinite(values).all():raise ValueError('finite boundary field required')
    ids=np.arange(nx0*ny0).reshape(ny0,nx0);rows=[];cols=[];data=[];diagonal=np.zeros_like(ids,dtype=float);b=rhs[1:-1,1:-1].copy()
    centre=nu[1:-1,1:-1]
    for axis,step,spacing in [(1,-1,dx),(1,1,dx),(0,-1,dy),(0,1,dy)]:
        sy=slice(1+step,ny-1+step) if axis==0 else slice(1,ny-1)
        sx=slice(1+step,nx-1+step) if axis==1 else slice(1,nx-1)
        neighbour=nu[sy,sx];face=2*centre*neighbour/(centre+neighbour)/spacing**2;diagonal+=face
        shifted=np.roll(ids,-step,axis=axis)
        valid=np.ones_like(ids,dtype=bool)
        if axis==1:valid[:,0 if step==-1 else -1]=False
        else:valid[0 if step==-1 else -1,:]=False
        rows.extend(ids[valid].ravel());cols.extend(shifted[valid].ravel());data.extend((-face[valid]).ravel())
        edge=~valid;b[edge]+=face[edge]*values[sy,sx][edge]
    rows.extend(ids.ravel());cols.extend(ids.ravel());data.extend(diagonal.ravel())
    matrix=coo_matrix((data,(rows,cols)),shape=(ids.size,ids.size)).tocsr()
    answer=spsolve(matrix,b.ravel());values[1:-1,1:-1]=answer.reshape(ids.shape)
    residual=np.linalg.norm(matrix@answer-b.ravel())/max(np.linalg.norm(b.ravel()),1e-30)
    if not np.isfinite(values).all() or residual>1e-8:raise ValueError('field solve did not converge')
    return values,float(residual)


def manufactured_controls():
    records=[]
    for count in (21,41,81):
        x=np.linspace(0,1,count);y=x.copy();xx,yy=np.meshgrid(x,y)
        exact=np.sin(math.pi*xx)*np.sin(math.pi*yy)
        actual,residual=solve(x,y,np.ones_like(exact),2*math.pi**2*exact)
        records.append(dict(mesh_nodes=count**2,error_linf=float(np.max(abs(actual-exact))),linear_residual=residual))
    ratios=[records[i]['error_linf']/records[i+1]['error_linf'] for i in range(2)]
    return dict(method='manufactured sine solution of -Laplacian(A)=J; not magnet/rail validation',
                refinements=records,error_reduction_ratios=ratios,second_order_control=all(3.8<r<4.2 for r in ratios))


def coupon(*,count=81,gap_m=.008,temperature_c=20,coil_ampere_turns=0,nonlinear=True):
    if type(count) is not int or not 31<=count<=201 or gap_m<=0 or not math.isfinite(gap_m):raise ValueError('bounded mesh and positive gap required')
    if not math.isfinite(temperature_c) or not math.isfinite(coil_ampere_turns):raise ValueError('finite temperature/excitation required')
    x=np.linspace(-.15,.15,count);y=np.linspace(-.10,.15,count);xx,yy=np.meshgrid(x,y)
    # Symmetric boundaries must include both representationally equal grid
    # coordinates; binary roundoff at +/-25mm must not invent a lateral force.
    eps=1e-12
    magnet=(abs(xx)<=.025+eps)&(yy>=-.05-eps)&(yy<=eps)
    iron=(abs(xx)<=.10+eps)&(yy>=gap_m-eps)&(yy<=gap_m+.02+eps)
    left=(xx>=-.045-eps)&(xx<=-.03+eps)&(yy>=-.04-eps)&(yy<=-.01+eps)
    right=np.fliplr(left)
    mur=np.ones_like(xx);mur[magnet]=1.05;mur[iron]=400
    br_y=np.zeros_like(xx);br_y[magnet]=.43*(1-.002*(temperature_c-20))
    # Return-current legs have equal integral by construction/symmetric grid.
    current=np.zeros_like(xx);area=(x[1]-x[0])*(y[1]-y[0])
    for mask,sign in [(left,1),(right,-1)]:
        if not mask.any():raise ValueError('mesh does not resolve coil region')
        current[mask]=sign*coil_ampere_turns/(mask.sum()*area)
    nu=1/(MU0*mur);converged=False;changes=[]
    for iteration in range(60 if nonlinear else 1):
        source=current+np.gradient(nu*br_y,x,axis=1)
        potential,residual=solve(x,y,nu,source)
        by=np.gradient(potential,y,axis=0);bz=-np.gradient(potential,x,axis=1)
        if not nonlinear:converged=True;break
        magnitude=np.hypot(by,bz)
        # Explicit artificial monotonic saturation hypothesis, not a steel grade.
        target=mur.copy();target[iron]=1+399/(1+(magnitude[iron]/1.5)**8)
        new=1/(MU0*target);change=float(np.max(abs(new[iron]/nu[iron]-1))) if iron.any() else 0
        changes.append(change)
        if change<1e-5:converged=True;break
        nu=.6*nu+.4*new
    if not converged:raise ValueError('nonlinear coupon iteration remains unconverged')
    # Maxwell contour entirely in air around the iron plate. Per axial metre.
    ib=RegularGridInterpolator((y,x),by);iz=RegularGridInterpolator((y,x),bz)
    def contour(margin):
        xmin,xmax=-.10-margin,.10+margin;ymin=gap_m/2;ymax=gap_m+.02+margin
        force=np.zeros(2)
        for p0,p1,normal in [((xmin,ymin),(xmax,ymin),(0,-1)),((xmax,ymin),(xmax,ymax),(1,0)),
                            ((xmax,ymax),(xmin,ymax),(0,1)),((xmin,ymax),(xmin,ymin),(-1,0))]:
            q=np.linspace(0,1,400);points=np.array(p0)[None,:]+q[:,None]*(np.array(p1)-p0)
            points_yx=points[:,::-1];bfield=np.column_stack((ib(points_yx),iz(points_yx)));n=np.array(normal)
            traction=(np.sum(bfield*n,axis=1)[:,None]*bfield-.5*np.sum(bfield*bfield,axis=1)[:,None]*n)/MU0
            force+=np.trapezoid(traction,q,axis=0)*np.linalg.norm(np.array(p1)-p0)
        return force.tolist()
    contours=[contour(m) for m in (.008,.015)]
    return dict(schema='osr-maglev-2d-coupon/1',mesh_nodes=count**2,gap_m=gap_m,temperature_c=temperature_c,
                coil_ampere_turns=coil_ampere_turns,nonlinear_hypothesis=nonlinear,nonlinear_iterations=iteration+1,
                linear_residual=residual,nonlinear_last_relative_change=changes[-1] if changes else 0,
                max_flux_density_t=float(np.hypot(by,bz).max()),net_free_current_a=float(current.sum()*area),
                iron_force_contours_n_per_m=contours,force_contour_relative_difference=abs(contours[0][1]-contours[1][1])/max(abs(contours[0][1]),1e-20),
                magnetic_force_map_validated=False,vehicle_lift_capacity_n=None,
                material_basis='Br 0.43 T sensitivity and assumed recoil 1.05; artificial 400-relative-permeability/1.5T saturation law, no supplier grade adopted',
                scope='2D finite-difference coupon; finite exterior boundary; no 3D ends, actual winding geometry, eddy/hysteresis loss or demagnetisation',
                grid=dict(x_m=x.tolist(),y_m=y.tolist(),potential_wb_m=potential.tolist(),b_horizontal_t=by.tolist(),b_vertical_t=bz.tolist()),
                sources=['https://www.femm.info/Archives/doc/manual.pdf','https://www.femm.info/doku/doku.php?id=FAQ'])


def study():
    controls=manufactured_controls()
    if not controls['second_order_control']:raise ValueError('field backend failed manufactured control')
    results=[coupon(count=n) for n in (61,81,121)]
    cases=[coupon(gap_m=g,temperature_c=t,coil_ampere_turns=i) for g,t,i in [(.004,20,0),(.012,20,0),(.008,80,0),(.008,20,500),(.008,20,-500)]]
    forces=[r['iron_force_contours_n_per_m'][0][1] for r in results]
    changes=[abs(forces[i+1]-forces[i])/abs(forces[i+1]) for i in range(len(forces)-1)]
    return dict(schema='osr-maglev-field-study/1',controls=controls,mesh_refinement=results,sensitivity_cases=cases,
                force_refinement_relative_changes=changes,force_mesh_converged=False,
                force_mesh_state='hold: staircase geometry/force extraction requires independently converged mesh and boundary studies',
                verified_scope='PDE manufactured solution and residuals only; vehicle force qualification remains open',
                nonlinear_3d_solver='not implemented',physical_validation=False,manufacturing_release=False)
