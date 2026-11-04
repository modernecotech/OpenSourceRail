"""Actual-wall Saint-Venant torsion through a conforming P1 warping FEM.

The scalar Neumann problem minimizes integral((w_y-z)^2+(w_z+y)^2).
Only one additive scalar gauge is fixed; outer and hole boundaries retain their
natural zero-traction condition. Material G and structural qualification are
separate from this geometry-only cross-section calculation.
"""
from __future__ import annotations

from math import ceil, isfinite
import platform
import os
from pathlib import Path
import sys

import numpy as np
import scipy
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

from engineering.station_rail import common
from engineering.station_rail.common import digest, identity

PRODUCER = "engineering/design_search/section_torsion.py"
LOADED = digest(__file__)
COMMON_SOURCE = digest(common.__file__)
MAX_NODES = 25_000
MAX_TRIANGLES = 50_000
FLAGS = dict(physical_accepted=False, engineering_accepted=False, configuration_adopted=False,
             manufacturing_release=False, operating_release=False, installed_mass_complete=False)
REFERENCES = ["https://sectionproperties.readthedocs.io/en/latest/user_guide/theory.html#torsion-constant",
              "https://link.springer.com/article/10.1186/s10033-018-0214-9"]


def _positive(value, name):
    try:
        valid = type(value) in (int, float) and isfinite(value) and value > 0
    except (OverflowError, ValueError):
        valid = False
    if not valid:
        raise ValueError("Positive finite geometry required: " + name)
    return float(value)


def _bounds(nodes, triangles):
    if nodes > MAX_NODES or triangles > MAX_TRIANGLES:
        raise ValueError("Cross-section mesh exceeds 25000-node/50000-triangle resource domain before allocation")


def _patch(iy0, iy1, iz0, iz1, nz):
    iy, iz = np.meshgrid(np.arange(iy0, iy1), np.arange(iz0, iz1), indexing="ij")
    ll = (iy*(nz+1)+iz).ravel()
    lr = ll+nz+1
    return np.vstack((np.column_stack((ll, lr, lr+1)), np.column_stack((ll, lr+1, ll+1))))


def _mesh(y, z, patches):
    nz = len(z)-1
    triangles = np.vstack([_patch(*patch, nz) for patch in patches])
    indices, inverse = np.unique(triangles, return_inverse=True)
    points = np.column_stack((y[indices//(nz+1)], z[indices % (nz+1)]))
    triangles = inverse.reshape((-1, 3))
    _bounds(len(points), len(triangles))
    return points, triangles


def _grid(outer, wall, n, interior):
    return np.concatenate((np.linspace(-outer/2, -outer/2+wall, n+1)[:-1],
        np.linspace(-outer/2+wall, outer/2-wall, interior+1)[:-1],
        np.linspace(outer/2-wall, outer/2, n+1)))


def _integrate(points, triangles, *, geometry, request, expected, gauge_node, saved_warping=None):
    if digest(__file__) != LOADED or digest(common.__file__) != COMMON_SOURCE:
        raise ValueError("Executing section torsion source changed")
    count = len(points)
    if type(gauge_node) is not int or not 0 <= gauge_node < count:
        raise ValueError("One explicit valid scalar gauge node required")
    p = points[triangles]
    twice_area = (p[:,1,0]-p[:,0,0])*(p[:,2,1]-p[:,0,1])-(p[:,2,0]-p[:,0,0])*(p[:,1,1]-p[:,0,1])
    if not np.all(np.isfinite(twice_area)) or np.any(twice_area <= 0):
        raise ValueError("Positive finite conforming triangle areas required")
    area = twice_area/2
    gradient = np.stack((np.column_stack((p[:,1,1]-p[:,2,1],p[:,2,1]-p[:,0,1],p[:,0,1]-p[:,1,1])),
                         np.column_stack((p[:,2,0]-p[:,1,0],p[:,0,0]-p[:,2,0],p[:,1,0]-p[:,0,0]))),axis=2)/twice_area[:,None,None]
    centroid = p.mean(axis=1)
    local_k = area[:,None,None]*np.einsum("tik,tjk->tij",gradient,gradient)
    local_f = area[:,None]*(gradient[:,:,0]*centroid[:,1,None]-gradient[:,:,1]*centroid[:,0,None])
    row = np.repeat(triangles, 3, axis=1).ravel()
    column = np.tile(triangles, (1,3)).ravel()
    matrix = coo_matrix((local_k.ravel(),(row,column)),shape=(count,count)).tocsr()
    force = np.bincount(triangles.ravel(),weights=local_f.ravel(),minlength=count)
    free = np.arange(count)!=gauge_node
    if saved_warping is None:
        warping = np.zeros(count)
        warping[free] = spsolve(matrix[free][:,free].tocsc(),force[free])
    else:
        if (not isinstance(saved_warping,list) or len(saved_warping)!=count
                or any(type(v) not in (int,float) or not isfinite(v) for v in saved_warping)):
            raise ValueError("Explicit finite saved nodal warping field required")
        warping=np.array(saved_warping,dtype=float)
        if warping[gauge_node]!=0.:
            raise ValueError("Saved nodal warping differs from its scalar gauge")
    if not np.all(np.isfinite(warping)):
        raise ValueError("Non-finite warping solution; no torsion value available")
    # Exact degree-two integrals on each straight triangle, not centroid squares.
    def quadratic(axis):
        v=p[:,:,axis]
        return area*(np.sum(v*v,axis=1)+v[:,0]*v[:,1]+v[:,0]*v[:,2]+v[:,1]*v[:,2])/6
    iy, iz = float(sum(quadratic(1))), float(sum(quadratic(0)))
    ip = iy+iz
    grad_w = np.einsum("ti,tik->tk",warping[triangles],gradient)
    energy = ip+float(np.sum(area*(np.sum(grad_w*grad_w,axis=1)-2*centroid[:,1]*grad_w[:,0]+2*centroid[:,0]*grad_w[:,1])))
    torque = ip+float(np.sum(area*(centroid[:,0]*grad_w[:,1]-centroid[:,1]*grad_w[:,0])))
    stationary = ip-float(force@warping)
    residual = matrix@warping-force
    if not 0 < energy <= ip*(1+1e-10) or not all(isfinite(v) for v in (energy,torque,stationary)):
        raise ValueError("Torsion result violates positive-energy/polar-inertia numerical bounds")
    quantity = dict(area_m2=float(sum(area)),I_y_m4=iy,I_z_m4=iz,polar_inertia_m4=ip)
    relative = {key:abs(quantity[key]-expected[key])/expected[key] for key in expected}
    if max(relative.values()) > 1e-10:
        raise ValueError("Actual material mesh area/inertia differs from declared section")
    sources={PRODUCER:LOADED,"engineering/station_rail/common.py":COMMON_SOURCE}
    mesh_id=identity(dict(points=points.tolist(),triangles=triangles.tolist()))
    value=dict(schema="osr-section-warping-torsion/1",execution="completed",
        numerical_validity="Single-mesh diagnostics reported; refinement convergence is not established",
        geometry=geometry,geometry_id=identity(geometry),
        model_id=identity(dict(geometry=geometry,request=request,method="single-valued-P1-Neumann-warping/1")),request=request,
        mesh_id=mesh_id,warping_m2=warping.tolist(),
        mesh=dict(node_count=count,triangle_count=len(triangles),mesh_id=mesh_id,
            material_domain="actual four-wall ring with a hole" if geometry["kind"]=="rhs" else "solid rectangle independent control",
            maximum_nodes=MAX_NODES,maximum_triangles=MAX_TRIANGLES),
        J_energy_m4=energy,J_torque_m4=torque,J_stationary_m4=stationary,quantities=quantity,
        exact_geometry_quantities=expected,quantity_relative_errors=relative,
        numerical=dict(weak_residual_relative=float(np.linalg.norm(residual))/max(float(np.linalg.norm(force)),1e-300),
            gauge_node=gauge_node,gauge_value_m2=0.,gauge_is_not_a_physical_boundary_restraint=True,
            load_compatibility_residual=float(abs(sum(force))),
            energy_torque_relative_difference=abs(energy-torque)/energy,
            stationary_energy_relative_difference=abs(energy-stationary)/energy),
        boundary_condition="Natural zero traction on both outer and inner boundaries; one scalar additive-warping gauge only",
        material_scope="J is geometry only; no E/G, anisotropic material law or structural acceptance is inferred",
        discretization_scope="Conforming P1 warping energy; nested-refinement energies approach from above, without a certified lower bound",
        source_sha256=sources,runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,implementation=platform.python_implementation(),
            python_executable_sha256=digest(Path(sys.executable).resolve()),
            numerical_thread_environment={name:os.environ.get(name) for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")}),
        references=REFERENCES,integrated_selection=None,**FLAGS)
    if digest(__file__) != LOADED or digest(common.__file__) != COMMON_SOURCE:
        raise ValueError("Section torsion sources changed during solve")
    value["evaluation_id"]=identity(value)
    return value


def _rhs(section, *, through_wall=1, gauge_node=0, saved_warping=None):
    if not isinstance(section,dict) or set(section)!={"width_m","height_m","wall_m"}:
        raise ValueError("Explicit width_m, height_m and wall_m geometry only required")
    b,h,t=[_positive(section[k],k) for k in ("width_m","height_m","wall_m")]
    if 2*t>=min(b,h):
        raise ValueError("Actual hollow RHS requires a positive hole; solid controls use rectangle()")
    if type(through_wall) is not int or through_wall not in (1,2,4,8):
        raise ValueError("Through-wall resolution must be one, two, four or eight")
    n=through_wall
    ratios=((b-2*t)/t,(h-2*t)/t)
    if not all(isfinite(r) for r in ratios):
        raise ValueError("Section aspect ratio exceeds finite mesh domain")
    my,mz=[max(1,ceil(r))*n for r in ratios]
    ny,nz=my+2*n,mz+2*n
    nodes=(ny+1)*(nz+1)-(my-1)*(mz-1)
    cells=2*n*nz+2*n*my
    _bounds(nodes,2*cells)
    points,triangles=_mesh(_grid(b,t,n,my),_grid(h,t,n,mz),
        [(0,n,0,nz),(n+my,ny,0,nz),(n,n+my,0,n),(n,n+my,n+mz,nz)])
    expected=dict(area_m2=b*h-(b-2*t)*(h-2*t),
        I_y_m4=(b*h**3-(b-2*t)*(h-2*t)**3)/12,I_z_m4=(h*b**3-(h-2*t)*(b-2*t)**3)/12)
    return _integrate(points,triangles,geometry=dict(kind="rhs",width_m=b,height_m=h,wall_m=t),
        request=dict(through_wall=n,gauge_node=gauge_node),expected=expected,gauge_node=gauge_node,saved_warping=saved_warping)


def _rectangle(width_m,height_m,*,divisions=32,gauge_node=0,saved_warping=None):
    b,h=_positive(width_m,"width_m"),_positive(height_m,"height_m")
    if type(divisions) is not int or not 1<=divisions<=128:
        raise ValueError("Independent solid rectangle resolution must be 1..128")
    ny,nz=divisions,divisions
    _bounds((ny+1)*(nz+1),2*ny*nz)
    points,triangles=_mesh(np.linspace(-b/2,b/2,ny+1),np.linspace(-h/2,h/2,nz+1),[(0,ny,0,nz)])
    return _integrate(points,triangles,geometry=dict(kind="solid-rectangle-control",width_m=b,height_m=h),
        request=dict(divisions=divisions,gauge_node=gauge_node),
        expected=dict(area_m2=b*h,I_y_m4=b*h**3/12,I_z_m4=h*b**3/12),gauge_node=gauge_node,saved_warping=saved_warping)


def evaluate(section, *, through_wall=1, gauge_node=0):
    return _rhs(section,through_wall=through_wall,gauge_node=gauge_node)


def rectangle(width_m,height_m,*,divisions=32,gauge_node=0):
    return _rectangle(width_m,height_m,divisions=divisions,gauge_node=gauge_node)


def verify_result(result, *, expected_runtime=None):
    """Reassemble and replay a saved nodal field without performing a solve.

    The 1e-8 checks concern floating-point equation/energy consistency only.
    Refinement convergence and material/structural acceptance remain separate.
    """
    if (not isinstance(result,dict) or result.get("schema")!="osr-section-warping-torsion/1"
            or result.get("evaluation_id")!=identity({k:v for k,v in result.items() if k!="evaluation_id"})):
        raise ValueError("Saved torsion result identity differs")
    if not isinstance(result.get("warping_m2"),list):
        raise ValueError("Saved nodal warping field is required for solve-free verification")
    geometry,request=result.get("geometry",{}),result.get("request",{})
    if geometry.get("kind")=="rhs":
        expected=_rhs({k:geometry[k] for k in ("width_m","height_m","wall_m")},
            through_wall=request.get("through_wall"),gauge_node=request.get("gauge_node"),saved_warping=result.get("warping_m2"))
    elif geometry.get("kind")=="solid-rectangle-control":
        expected=_rectangle(geometry["width_m"],geometry["height_m"],divisions=request.get("divisions"),
            gauge_node=request.get("gauge_node"),saved_warping=result.get("warping_m2"))
    else:
        raise ValueError("Unknown saved torsion geometry")
    if expected_runtime is not None:
        current=expected["runtime"]
        if (not isinstance(expected_runtime,dict) or set(expected_runtime)!=set(current)
                or any(expected_runtime[key]!=value for key,value in current.items() if key!="numerical_thread_environment")
                or expected_runtime.get("numerical_thread_environment")!={name:"1" for name in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS")}):
            raise ValueError("Expected worker runtime must match current executable/libraries and explicit one-thread worker policy")
        expected["runtime"]=dict(expected_runtime)
        expected["evaluation_id"]=identity({k:v for k,v in expected.items() if k!="evaluation_id"})
    if result!=expected:
        raise ValueError("Saved torsion field, mesh, quantities, source/runtime or numerical summary differs")
    numerical=expected["numerical"]
    if any(not isfinite(numerical[key]) or numerical[key]>1e-8 for key in (
            "weak_residual_relative","energy_torque_relative_difference","stationary_energy_relative_difference")):
        raise ValueError("Saved warping fails the declared 1e-8 numerical equation/energy consistency checks")
    return dict(verified=True,evaluation_id=result["evaluation_id"],mesh_id=result["mesh_id"],
        verification="Saved nodal field replay; no sparse solve or refinement-convergence claim",**FLAGS)


def verify(section,result,*,expected_runtime=None):
    geometry=dict(kind="rhs",**section)
    if result.get("geometry")!=geometry:
        raise ValueError("Saved torsion result belongs to another actual wall section")
    return verify_result(result,expected_runtime=expected_runtime)
