"""Bounded Q4 plane-stress/SIMP method experiment, with exact binary replay.

This implementation assembles 2x2 Gauss-integrated isoparametric elements from
their shape derivatives; it does not copy a closed-form educational element or
optimizer listing. SIMP, density filtering and the OC update follow the equations
in Andreassen et al., Structural and Multidisciplinary Optimization (2011):
https://www.topopt.mek.dtu.dk/-/media/subsites/topopt/apps/dokumenter-og-filer-til-apps/topopt88.pdf

All coordinates, forces and elastic inputs are SI. Densities are numerical
proposal variables, never physical geometry or qualified material properties.
Loads are FIXED during optimisation; candidate-dependent gravity belongs in a
separate binary replay. No strength, buckling, fatigue or railway admission is
provided. Time guards act between solves, not during a sparse factorisation.
There is no process memory limit or operating-system sandbox in this module.
"""
from math import ceil, isfinite, sqrt
import time

import numpy as np
import scipy
from scipy.sparse import bmat, coo_matrix, csr_matrix, diags
from scipy.sparse.linalg import splu

from engineering.station_rail.common import identity

PRODUCER = 'engineering/design_search/topology_optimisation.py'
METHOD_REFERENCE = 'https://www.topopt.mek.dtu.dk/-/media/subsites/topopt/apps/dokumenter-og-filer-til-apps/topopt88.pdf'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    manufacturing_release=False, operating_release=False,
    current_evaluator_admission=False, configuration_adopted=False,
    selected_reference_changed=False)


class NumericalFailure(RuntimeError):
    """The specified elastic calculation could not establish numerical validity."""


def _positive(value, name):
    try:valid=type(value) in (int, float) and isfinite(value) and value > 0
    except OverflowError:valid=False
    if not valid:
        raise ValueError('Finite positive '+name+' required')
    return float(value)


def q4_stiffness(coordinates, E_Pa, poisson, thickness_m):
    """Return the 8x8 full-material plane-stress stiffness of a CCW Q4."""
    xy = np.asarray(coordinates, dtype=float)
    if xy.shape != (4, 2) or not np.isfinite(xy).all():
        raise ValueError('Four finite counterclockwise Q4 coordinates required')
    E = _positive(E_Pa, 'Young modulus'); t = _positive(thickness_m, 'thickness')
    try:valid=type(poisson) in (int, float) and isfinite(poisson) and -1 < poisson < .5
    except OverflowError:valid=False
    if not valid:
        raise ValueError('Poisson ratio must be strictly between -1 and 0.5')
    D = E/(1-poisson**2)*np.array([[1., poisson, 0.], [poisson, 1., 0.], [0., 0., (1-poisson)/2]])
    K = np.zeros((8, 8))
    for xi in (-1/sqrt(3), 1/sqrt(3)):
        for eta in (-1/sqrt(3), 1/sqrt(3)):
            natural = .25*np.array([[-(1-eta), -(1-xi)], [1-eta, -(1+xi)],
                [1+eta, 1+xi], [-(1+eta), 1-xi]])
            J = xy.T @ natural; determinant = float(np.linalg.det(J))
            if not isfinite(determinant) or determinant <= 0:
                raise ValueError('Strictly positive Q4 Gauss-point Jacobians required')
            gradient = natural @ np.linalg.inv(J)
            B = np.zeros((3, 8)); B[0, 0::2] = gradient[:, 0]; B[1, 1::2] = gradient[:, 1]
            B[2, 0::2] = gradient[:, 1]; B[2, 1::2] = gradient[:, 0]
            K += t*determinant*(B.T @ D @ B)
    if not np.isfinite(K).all():
        raise ValueError('Finite Q4 stiffness required')
    return (K+K.T)/2


def mesh(specification):
    """Regular rectangle; node=j*(nx+1)+i, element=j*nx+i, z in [0,H].

    `specification` requires nx, nz, length_m, height_m, thickness_m, E_Pa,
    poisson. The numerical construction cap is not an engineering constraint.
    Arrays belong to this invocation and must not be mutated while solving.
    """
    s = dict(specification)
    for key in ('nx', 'nz'):
        if type(s.get(key)) is not int or s[key] < 1:
            raise ValueError('Positive integer mesh subdivisions required')
    nx, nz = s['nx'], s['nz']
    if nx*nz > 32768:
        raise ValueError('Bounded Q4 construction requires at most 32768 elements')
    for key in ('length_m', 'height_m', 'thickness_m', 'E_Pa'):
        s[key] = _positive(s.get(key), key)
    x = np.linspace(0., s['length_m'], nx+1); z = np.linspace(0., s['height_m'], nz+1)
    nodes = np.array([(a, b) for b in z for a in x])
    elements = np.array([(j*(nx+1)+i, j*(nx+1)+i+1,
        (j+1)*(nx+1)+i+1, (j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)], dtype=np.int64)
    edofs = (2*elements[:, :, None]+np.array([0, 1])).reshape(-1, 8)
    ke = q4_stiffness(nodes[elements[0]], s['E_Pa'], s.get('poisson'), s['thickness_m'])
    dx, dz = s['length_m']/nx, s['height_m']/nz
    return dict(specification=s, problem_id=identity(s), nodes=nodes, elements=elements,
        edofs=edofs, element_centres=nodes[elements].mean(axis=1),
        element_stiffness=ke, element_volume_m3=dx*dz*s['thickness_m'],
        ndof=2*len(nodes), nelements=len(elements),
        assembly_rows=np.repeat(edofs, 8, axis=1).ravel(),
        assembly_columns=np.tile(edofs, (1, 8)).ravel())


def _densities(problem, values):
    result = np.array(values, dtype=float, copy=True)
    if result.shape != (problem['nelements'],) or not np.isfinite(result).all() or np.any((result < 0) | (result > 1)):
        raise ValueError('One finite density in [0,1] per element required')
    return result


def _loads(problem, forces, fixed_dofs, *, allow_empty_fixed=False):
    F = np.asarray(forces, dtype=float)
    if F.ndim != 2 or F.shape[0] != problem['ndof'] or not 1 <= F.shape[1] <= 128 or not np.isfinite(F).all():
        raise ValueError('Finite force matrix (ndof, 1..128 cases) required')
    fixed = np.asarray(fixed_dofs)
    if fixed.ndim == 1 and not len(fixed) and allow_empty_fixed:fixed=np.array([],dtype=np.int64)
    if fixed.ndim != 1 or fixed.dtype.kind not in 'iu' or (not len(fixed) and not allow_empty_fixed) or len(np.unique(fixed)) != len(fixed) or np.any((fixed < 0) | (fixed >= problem['ndof'])):
        raise ValueError('Unique in-range integer homogeneous fixed DOFs required')
    return F.copy(), np.sort(fixed.astype(np.int64))


def _constraints(problem, constraint_matrix):
    if constraint_matrix is None:return np.zeros((0,problem['ndof']))
    C=np.array(constraint_matrix,dtype=float,copy=True)
    if (C.ndim!=2 or C.shape[1]!=problem['ndof'] or C.shape[0]>16
            or not np.isfinite(C).all() or np.any(np.max(np.abs(C),axis=1)==0)):
        raise ValueError('Finite homogeneous constraint matrix (0..16, ndof) with nonzero rows required')
    return C


def _simp(penalty, min_stiffness_ratio):
    p = _positive(penalty, 'SIMP exponent')
    e = _positive(min_stiffness_ratio, 'numerical minimum stiffness ratio')
    if p < 1 or not e < 1:
        raise ValueError('SIMP exponent >=1 and minimum stiffness ratio in (0,1) required')
    return p, e


def assemble_stiffness(problem, densities, *, penalty=3., min_stiffness_ratio=1e-9):
    rho = _densities(problem, densities); p, e = _simp(penalty, min_stiffness_ratio)
    scale = e+(1-e)*rho**p
    values = (scale[:, None, None]*problem['element_stiffness']).ravel()
    return coo_matrix((values, (problem['assembly_rows'], problem['assembly_columns'])),
        shape=(problem['ndof'], problem['ndof'])).tocsr()


def _support_rank(problem, fixed, constraints, active_dofs):
    xy = problem['nodes']; length = max(problem['specification']['length_m'], problem['specification']['height_m'])
    modes=np.zeros((problem['ndof'],3));modes[0::2,0]=1.;modes[1::2,1]=1.
    modes[0::2,2]=-xy[:,1]/length;modes[1::2,2]=xy[:,0]/length
    rows=np.vstack((modes[fixed],constraints[:,active_dofs]@modes[active_dofs]))
    if not len(rows):return 0
    scale=np.max(np.abs(rows),axis=1);rows=rows[scale>0]/scale[scale>0,None]
    return int(np.linalg.matrix_rank(rows,tol=1e-10)) if len(rows) else 0


def _analyse(problem, K, F, fixed, active_dofs, constraints):
    if _support_rank(problem, fixed, constraints, active_dofs) != 3:
        raise NumericalFailure('Supports do not remove all three planar rigid-body modes')
    free = np.setdiff1d(active_dofs, fixed)
    U = np.zeros_like(F);multipliers=np.zeros((len(constraints),F.shape[1]))
    stiffness_scale=1.;constraint_scales=np.ones(len(constraints))
    if len(free):
        try:
            if len(constraints):
                Cf=constraints[:,free];constraint_scales=np.max(np.abs(Cf),axis=1)
                if np.any(constraint_scales==0):raise NumericalFailure('Constraint has no free active DOFs')
                normalised=Cf/constraint_scales[:,None]
                if np.linalg.matrix_rank(normalised,tol=1e-10)!=len(constraints):
                    raise NumericalFailure('Dependent homogeneous constraints after fixed DOF elimination')
                Kf=K[free][:,free].tocsc();stiffness_scale=float(np.max(np.abs(Kf.diagonal())))
                if not isfinite(stiffness_scale) or stiffness_scale<=0:raise NumericalFailure('Invalid stiffness scaling')
                saddle=bmat([[Kf/stiffness_scale,csr_matrix(normalised.T)],
                    [csr_matrix(normalised),None]],format='csc')
                right=np.vstack((F[free]/stiffness_scale,np.zeros((len(constraints),F.shape[1]))))
                solution=splu(saddle).solve(right)
                U[free]=solution[:len(free)]
                multipliers=solution[len(free):]*stiffness_scale/constraint_scales[:,None]
            else:U[free] = splu(K[free][:, free].tocsc()).solve(F[free])
        except NumericalFailure:raise
        except (RuntimeError, ValueError) as exc:
            raise NumericalFailure('Singular or unsuccessful sparse factorisation') from exc
    elif len(constraints):raise NumericalFailure('Constraint has no free active DOFs')
    if not np.isfinite(U).all() or not np.isfinite(multipliers).all():
        raise NumericalFailure('Nonfinite elastic displacement')
    constraint_reactions=-(constraints.T@multipliers)
    internal = K @ U; residual = internal-F-constraint_reactions
    constraint_residual=constraints@U
    scaled_constraint_residual=constraint_residual/constraint_scales[:,None]
    constraint_displacement_scale=np.sum(np.abs(constraints[:,free]),axis=1)[:,None]*np.max(np.abs(U),axis=0)
    constraint_relative=np.abs(constraint_residual)/np.maximum(1e-30,constraint_displacement_scale)
    if (np.any(np.abs(scaled_constraint_residual)>1e-9*np.maximum(1.,np.max(np.abs(U),axis=0)))
            or np.any(constraint_relative>1e-7)):
        raise NumericalFailure('Homogeneous constraint displacement residual failed')
    load_scale = np.maximum(1., np.max(np.abs(F), axis=0))
    free_residual = np.max(np.abs(residual[free]), axis=0) if len(free) else np.zeros(F.shape[1])
    relative = free_residual/load_scale
    compliance = np.sum(F*U, axis=0); work = np.sum(U*internal, axis=0)
    if (not np.isfinite(internal).all() or not np.isfinite(compliance).all() or not np.isfinite(work).all()
            or np.any(relative > 1e-7) or np.any(compliance < -1e-9)
            or np.any(np.abs(work-compliance) > 1e-7*np.maximum(1., np.abs(compliance)))):
        raise NumericalFailure('Elastic residual or energy check failed')
    fixed_reactions=np.zeros_like(F);fixed_reactions[fixed]=residual[fixed]
    reactions=constraint_reactions+fixed_reactions
    constraint_work=np.sum(U*constraint_reactions,axis=0)
    if np.any(np.abs(constraint_work)>1e-7*np.maximum(1.,np.abs(compliance))):
        raise NumericalFailure('Homogeneous constraint work is not zero')
    external = (F+reactions).reshape(-1, 2, F.shape[1])
    force_residual = external.sum(axis=0).T
    xy = problem['nodes']
    moment_residual = np.sum(xy[:, 0, None]*external[:, 1]-xy[:, 1, None]*external[:, 0], axis=0)
    resultant_scale=np.maximum(1.,np.sum(np.abs(F),axis=0))
    moment_scale=resultant_scale*max(1.,problem['specification']['length_m'],problem['specification']['height_m'])
    if (np.any(np.max(np.abs(force_residual),axis=1)>1e-7*resultant_scale)
            or np.any(np.abs(moment_residual)>1e-7*moment_scale)):
        raise NumericalFailure('Global force or moment equilibrium check failed')
    return dict(displacements=U, reactions=reactions, compliances=compliance,
        objective=float(compliance.sum()), strain_energy_J=.5*work,
        energy_residual_J=work-compliance, free_residual_max_N=free_residual,
        free_residual_relative=relative, force_equilibrium_residual_N=force_residual,
        moment_equilibrium_residual_Nm=moment_residual, active_dof_ids=active_dofs,
        constraint_multipliers=multipliers,constraint_residual=constraint_residual,
        constraint_residual_relative=constraint_relative,
        scaled_constraint_residual=scaled_constraint_residual,constraint_reactions=constraint_reactions,
        fixed_dof_reactions=fixed_reactions,constraint_work_J=constraint_work,
        saddle_stiffness_scale=stiffness_scale,constraint_row_scales=constraint_scales,
        execution='completed', numerical_validity='elastic-residual-and-energy-checked', **FLAGS)


def solve(problem, densities, forces, fixed_dofs, penalty=3., min_stiffness_ratio=1e-9, *, constraint_matrix=None):
    """Regularised density solve, sum-of-compliances objective, fixed multiple RHS.

    `density_gradient` differentiates the objective with respect to the densities
    supplied here. Apply the density-filter/passive-mask chain before OC updates.
    Artificial void stiffness belongs ONLY to this numerical proposal model.
    Optional homogeneous C@U=0 constraints use a scaled sparse saddle system;
    up to 16 rows and 128 load cases are supported. Empty fixed_dofs are then
    allowed. The convention is K@U+C.T@lambda=F, reactions=-C.T@lambda.
    """
    C=_constraints(problem,constraint_matrix)
    rho = _densities(problem, densities); F, fixed = _loads(problem, forces, fixed_dofs,allow_empty_fixed=bool(len(C)))
    p, e = _simp(penalty, min_stiffness_ratio)
    K = assemble_stiffness(problem, rho, penalty=p, min_stiffness_ratio=e)
    result = _analyse(problem, K, F, fixed, np.arange(problem['ndof']),C)
    ue = result['displacements'][problem['edofs']]
    element_work = np.einsum('eic,ij,ejc->ec', ue, problem['element_stiffness'], ue)
    gradient = -p*(1-e)*rho**(p-1)*element_work.sum(axis=1)
    if not np.isfinite(element_work).all() or not np.isfinite(gradient).all():
        raise NumericalFailure('Nonfinite element energy or sensitivity')
    result.update(element_full_material_work_J=element_work,
        density_gradient=gradient,
        densities=rho.copy(), min_stiffness_ratio=e, penalty=p,
        density_is_physical_geometry=False, tool_versions=dict(numpy=np.__version__, scipy=scipy.__version__))
    return result


def density_filter(problem, radius_m):
    """Row-normalised distance filter using metres, including boundary rows."""
    radius = _positive(radius_m, 'physical filter radius')
    s = problem['specification']; nx, nz = s['nx'], s['nz']
    dx, dz = s['length_m']/nx, s['height_m']/nz
    rx, rz = min(nx-1, ceil(radius/dx)), min(nz-1, ceil(radius/dz))
    if problem['nelements']*(2*rx+1)*(2*rz+1) > 4_000_000:
        raise ValueError('Density-filter construction exceeds the bounded neighbour budget')
    rows=[]; columns=[]; values=[]
    for j in range(nz):
        for i in range(nx):
            for b in range(max(0, j-rz), min(nz, j+rz+1)):
                for a in range(max(0, i-rx), min(nx, i+rx+1)):
                    value = radius-sqrt(((a-i)*dx)**2+((b-j)*dz)**2)
                    if value > 0:
                        rows.append(j*nx+i); columns.append(b*nx+a); values.append(value)
    H = coo_matrix((values, (rows, columns)), shape=(problem['nelements'],)*2).tocsr()
    sums=np.asarray(H.sum(axis=1)).ravel()
    if not np.isfinite(sums).all() or np.any(sums<=0):
        raise ValueError('Finite positive filter row weights required')
    operator=(diags(1/sums) @ H).tocsr()
    if not np.isfinite(operator.data).all():raise ValueError('Finite normalized density filter required')
    return operator


def _mask(problem, mask):
    result = np.asarray(mask)
    if result.dtype.kind != 'b' or result.shape != (problem['nelements'],):
        raise ValueError('Explicit boolean mask with one entry per element required')
    return result.copy()


def _filtered(problem, design, operator, passive):
    x = _densities(problem, design).copy(); x[passive] = 1.
    rho = np.asarray(operator @ x).ravel(); rho[passive] = 1.
    if np.any(rho < -1e-12) or np.any(rho > 1+1e-12):
        raise ValueError('Density filter must preserve [0,1]')
    return x, np.clip(rho, 0., 1.)


def filtered_objective(problem, design, forces, fixed_dofs, operator, passive_solid_mask,
        *, penalty=3., min_stiffness_ratio=1e-9, constraint_matrix=None):
    """Full density-filter chain; passive input and output derivatives are zero."""
    passive = _mask(problem, passive_solid_mask)
    x, rho = _filtered(problem, design, operator, passive)
    result = solve(problem, rho, forces, fixed_dofs, penalty, min_stiffness_ratio,constraint_matrix=constraint_matrix)
    dc = result['density_gradient'].copy(); dc[passive] = 0.
    gradient = np.asarray(operator.T @ dc).ravel(); gradient[passive] = 0.
    volume_gradient = np.asarray(operator.T @ (~passive).astype(float)).ravel()/problem['nelements']
    volume_gradient[passive] = 0.
    result.update(design_variables=x, design_gradient=gradient,
        volume_fraction=float(rho.mean()), volume_gradient=volume_gradient)
    return result


def _oc_step(x, gradient, volume_gradient, passive, volume_offset, target, move):
    active = ~passive; lo = np.maximum(0., x-move); hi = np.minimum(1., x+move)
    useful = active & (volume_gradient > 0)
    scale = np.zeros_like(x)
    scale[useful] = np.maximum(0., -gradient[useful])/volume_gradient[useful]
    def trial(multiplier):
        proposed = x.copy()
        proposed[useful] = np.clip(x[useful]*np.sqrt(scale[useful]/multiplier), lo[useful], hi[useful])
        proposed[passive] = 1.
        return proposed
    if not useful.any():return x.copy()
    lower, upper = 0., max(1., float(scale.max()))
    for _ in range(100):
        if volume_offset+float(volume_gradient @ trial(upper)) <= target+1e-12:break
        upper *= 2
    else:raise NumericalFailure('OC multiplier could not bracket the volume constraint')
    result = trial(upper)
    for _ in range(100):
        middle = (lower+upper)/2; proposed = trial(middle)
        if volume_offset+float(volume_gradient @ proposed) > target:
            lower = middle
        else:
            upper = middle; result = proposed
        if upper-lower <= 1e-11*max(1., upper):break
    return result


def optimise(problem, forces, fixed_dofs, passive_solid_mask, volume_fraction,
        filter_radius_m, max_iterations, change_tolerance, time_budget_s, *,
        move_limit=.2, penalty=3., min_stiffness_ratio=1e-9, initial_densities=None,
        constraint_matrix=None,iteration_callback=None):
    """OC minimisation of the fixed-load sum of compliances.

    `volume_fraction` bounds TOTAL FILTERED domain volume, including passive
    solids and filter leakage. Returned analysis always belongs to returned
    densities. A pending unevaluated proposal is separately named. Budget
    exhaustion is not convergence or failure of a physical design.
    Both forces and homogeneous constraints are snapshotted and fixed during
    the search; their derivatives therefore contribute no design terms.
    After every successful solve, iteration_callback receives an independent
    dictionary with copied design/density arrays and scalar iteration, objective,
    volume_fraction and free_residual_relative. It runs before the next OC step;
    callback errors propagate. No callback is invoked for an unsuccessful solve.
    """
    start = time.monotonic(); passive = _mask(problem, passive_solid_mask)
    if iteration_callback is not None and not callable(iteration_callback):
        raise ValueError('iteration_callback must be callable or None')
    constraints=_constraints(problem,constraint_matrix)
    forces, fixed_dofs = _loads(problem, forces, fixed_dofs,allow_empty_fixed=bool(len(constraints)))
    _simp(penalty, min_stiffness_ratio)
    target = _positive(volume_fraction, 'total volume fraction')
    if target > 1 or type(max_iterations) is not int or not 1 <= max_iterations <= 1000:
        raise ValueError('Volume fraction <=1 and 1..1000 iterations required')
    tolerance = _positive(change_tolerance, 'change tolerance'); budget = _positive(time_budget_s, 'time budget')
    move = _positive(move_limit, 'OC move limit')
    if move > 1:raise ValueError('Move limit must not exceed one')
    operator = density_filter(problem, filter_radius_m)
    zero = np.zeros(problem['nelements']); zero[passive] = 1.
    _, base = _filtered(problem, zero, operator, passive); minimum = float(base.mean())
    if target < minimum-1e-12:
        raise ValueError('Requested volume is below passive-solid/filter minimum')
    if initial_densities is None:
        x = zero.copy()
        x[~passive] = 0. if minimum == 1 else np.clip((target-minimum)/(1-minimum),0.,1.)
    else:x = _densities(problem, initial_densities).copy(); x[passive] = 1.
    _, rho = _filtered(problem, x, operator, passive)
    if rho.mean() > target+1e-10:
        raise ValueError('Initial filtered density exceeds the declared total volume')
    history=[]; last=None; next_design=None; termination='iteration-budget'
    for iteration in range(max_iterations):
        if time.monotonic()-start >= budget:
            termination='time-budget';break
        last = filtered_objective(problem, x, forces, fixed_dofs, operator, passive,
            penalty=penalty, min_stiffness_ratio=min_stiffness_ratio,constraint_matrix=constraints)
        history.append(dict(iteration=iteration+1, objective=last['objective'],
            volume_fraction=last['volume_fraction'], proposed_change=None,
            elapsed_seconds=time.monotonic()-start,
            free_residual_relative=float(last['free_residual_relative'].max())))
        if iteration_callback is not None:
            iteration_callback(dict(iteration=iteration+1,objective=last['objective'],
                volume_fraction=last['volume_fraction'],free_residual_relative=float(last['free_residual_relative'].max()),
                design_variables=last['design_variables'].copy(),densities=last['densities'].copy()))
        next_design = _oc_step(x, last['design_gradient'], last['volume_gradient'], passive,
            minimum, target, move)
        change = float(np.max(np.abs(next_design-x)))
        history[-1]['proposed_change']=change
        history[-1]['elapsed_seconds']=time.monotonic()-start
        if time.monotonic()-start >= budget:
            termination='time-budget';break
        if change <= tolerance:
            termination='change-tolerance';break
        if iteration+1 < max_iterations:x = next_design
    if last is not None:x=last['design_variables'];rho=last['densities']
    return dict(problem_id=problem['problem_id'], design_variables=x, densities=rho,
        last_analysis=last, next_design_variables=next_design, history=history,
        termination=termination, converged=termination=='change-tolerance',
        execution='completed' if last is not None else 'not-run',
        numerical_validity='last-evaluated-density-state-only' if last is not None else 'not-established',
        selection_purpose='next-experiment', global_optimum_proven=False,
        evaluated_iterations=len(history), elapsed_seconds=time.monotonic()-start,
        target_total_volume_fraction=target, minimum_filtered_volume_fraction=minimum,
        move_limit=move, penalty=penalty, min_stiffness_ratio=min_stiffness_ratio,
        filter_radius_m=filter_radius_m, density_is_physical_geometry=False,
        force_dependence='fixed during optimisation; realized structural gravity must be replayed separately',
        runtime_guard='between sparse solves and OC updates', memory_limit_enforced=False,
        operating_system_isolation=False, **FLAGS)


def solve_binary(problem, occupancy, forces, fixed_dofs, *, constraint_matrix=None):
    """Replay actual occupied elements, with void stiffness and void DOFs removed.

    No islands are pruned and no corner connections repaired. Invalid topology
    returns an explicit non-executed failure record with the complete occupancy.
    """
    C=_constraints(problem,constraint_matrix)
    occupied = _mask(problem, occupancy); F, fixed = _loads(problem, forces, fixed_dofs,allow_empty_fixed=bool(len(C)))
    active = np.flatnonzero(occupied)
    status = dict(problem_id=problem['problem_id'], occupancy=occupied.copy(),
        active_element_ids=active, void_stiffness_used=False, void_dofs_removed=True,
        repaired_geometry=False, execution='not-run', numerical_validity='not-established', **FLAGS)
    def fail(reason, **extra):return dict(status, failure_reason=reason, **extra)
    if not len(active):return fail('empty-material-domain', material_component_count=0)
    nx = problem['specification']['nx']; nz = problem['specification']['nz']
    remaining = set(active.tolist()); components=[]
    while remaining:
        stack=[remaining.pop()]; component=[]
        while stack:
            e=stack.pop();component.append(e);i,j=e%nx,e//nx
            for a,b in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
                other=b*nx+a
                if 0<=a<nx and 0<=b<nz and other in remaining:
                    remaining.remove(other);stack.append(other)
        components.append(sorted(component))
    if len(components)!=1:
        return fail('disconnected-or-corner-only-material', material_component_count=len(components),
            material_components=components)
    grid=occupied.reshape(nz,nx);corner_contacts=[]
    for j in range(nz-1):
        for i in range(nx-1):
            a,b,c,d=bool(grid[j,i]),bool(grid[j,i+1]),bool(grid[j+1,i]),bool(grid[j+1,i+1])
            if (a and d and not b and not c) or (b and c and not a and not d):
                corner_contacts.append([j*nx+i,j*nx+i+1,(j+1)*nx+i,(j+1)*nx+i+1])
    if corner_contacts:
        # Global edge connectivity does not legitimise a second, local point
        # connection. Shared Q4 nodes would otherwise transmit force there.
        return fail('corner-only-contact',material_component_count=1,
            corner_contact_element_blocks=corner_contacts)
    dofs = np.unique(problem['edofs'][active]); inactive = np.setdiff1d(np.arange(problem['ndof']),dofs)
    if np.any(F[inactive] != 0):return fail('load-on-void-node', inactive_loaded_dof_ids=inactive[np.any(F[inactive]!=0,axis=1)])
    if np.any(~np.isin(fixed,dofs)):return fail('support-on-void-node')
    if np.any(C[:,inactive]!=0):return fail('constraint-on-void-node')
    rows = np.repeat(problem['edofs'][active],8,axis=1).ravel()
    columns = np.tile(problem['edofs'][active],(1,8)).ravel()
    K = coo_matrix((np.tile(problem['element_stiffness'].ravel(),len(active)),(rows,columns)),
        shape=(problem['ndof'],problem['ndof'])).tocsr()
    try:result=_analyse(problem,K,F,fixed,dofs,C)
    except NumericalFailure as exc:return fail(str(exc),material_component_count=1)
    status.update(result,material_component_count=1,failure_reason=None,
        model_scope='Connected occupied Q4 plane-stress material under supplied loads; no 3D, strength or physical acceptance')
    return status
