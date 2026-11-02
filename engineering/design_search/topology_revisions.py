"""Explicit stock revisions of failed topology parents; no numerical admission.

The executor must authenticate the original trial, receipt and arrays package
BEFORE constructing a parent binding. This helper checks their supplied identity
and array consistency, not authenticity. It never edits or repairs a parent.
Every stock addition/removal creates a proposed physical child and a separate
proposal-evaluation identity. No FE, material resistance or manufacturing test
is executed. Time checks are cooperative between bounded operations.
"""
from collections import deque
from fractions import Fraction
from hashlib import sha256
import heapq
from math import isfinite
from pathlib import Path
import time

import numpy as np

from engineering.station_rail.common import identity, digest
from . import topology_geometry as geometry

PRODUCER='engineering/design_search/topology_revisions.py'
STRATEGIES=('retain-mandatory-component','connect-all-stock')
FLAGS=dict(physical_accepted=False,engineering_accepted=False,manufacturing_release=False,
    operating_release=False,configuration_adopted=False,selected_reference_changed=False,
    current_evaluator_admission=False)


def _sha(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value)
def _seal(value,key):value[key]=identity(value);return value


def _shape(values,maximum):
    if isinstance(values,np.ndarray):
        if values.ndim!=2:raise ValueError('Two-dimensional parent grid required')
        shape=values.shape
    elif isinstance(values,(list,tuple)) and values:
        if len(values)>maximum or not isinstance(values[0],(list,tuple)):
            raise ValueError('Bounded rectangular parent grid required')
        shape=(len(values),len(values[0]))
        if not shape[1] or any(not isinstance(row,(list,tuple)) or len(row)!=shape[1] for row in values):
            raise ValueError('Rectangular parent grid required')
    else:raise ValueError('Explicit two-dimensional parent grid required')
    if not all(shape) or shape[0]*shape[1]>maximum:
        raise ValueError('Parent grid exceeds explicit element budget')
    return shape


def _arrays(mask,rho,passive,maximum):
    shape=_shape(mask,maximum)
    if _shape(rho,maximum)!=shape or _shape(passive,maximum)!=shape:
        raise ValueError('Parent mask/density/passive grid shapes differ')
    mask=np.asarray(mask);passive=np.asarray(passive)
    if mask.dtype.kind!='b' or passive.dtype.kind!='b':
        raise ValueError('Explicit boolean parent occupancy and passive masks required')
    if np.asarray(rho).dtype.kind not in 'iuf':raise ValueError('Real numeric original density required')
    density=np.asarray(rho,dtype=float)
    if not np.isfinite(density).all() or np.any((density<0)|(density>1)):
        raise ValueError('Finite original density in [0,1] required')
    if not passive.any() or np.any(passive & ~mask):
        raise ValueError('All nonempty mandatory passive stock must exist in the parent')
    return mask.copy(),density.copy(),passive.copy()


def _fingerprint(values):
    return identity(dict(shape=list(values.shape),values=values.tolist()))


def _parent(parent,mask):
    p=parent.get('physical_definition',{}).get('webs',{}).get('rectangles_xz_m',[])
    if len(p)>mask.size:raise ValueError('Parent rectangle count exceeds grid budget')
    geometry.validate(parent)
    if geometry.realize(mask)!=parent:
        raise ValueError('Original occupancy does not reproduce exact parent geometry/source')


def make_parent_input(parent_geometry,occupancy,original_density,passive_solid_mask,*,
        parent_evaluation_id,parent_request_id,arrays_package_sha256,required_passive_cell_ids):
    """Bind explicitly observed, already authenticated parent inputs, without replay."""
    mask,rho,passive=_arrays(occupancy,original_density,passive_solid_mask,7680)
    _parent(parent_geometry,mask)
    if not all(_sha(x) for x in (parent_evaluation_id,parent_request_id,arrays_package_sha256)):
        raise ValueError('Exact parent evaluation/request/arrays-package SHA256 identities required')
    if not isinstance(required_passive_cell_ids,(list,tuple)) or len(required_passive_cell_ids)>mask.size:
        raise ValueError('Bounded explicit original mandatory cell list required')
    required=list(required_passive_cell_ids)
    if (not required or any(type(i) is not int or not 0<=i<mask.size for i in required)
            or len(required)!=len(set(required)) or sorted(required)!=np.flatnonzero(passive).tolist()):
        raise ValueError('Passive mask differs from explicit original mandatory cells')
    return _seal(dict(schema='osr-topology-revision-parent-input/1',
        parent_candidate_id=parent_geometry['candidate_id'],parent_geometry_id=parent_geometry['geometry_id'],
        parent_evaluation_id=parent_evaluation_id,parent_request_id=parent_request_id,
        original_arrays_package_sha256=arrays_package_sha256,shape=list(mask.shape),
        occupancy_sha256=_fingerprint(mask),original_density_sha256=_fingerprint(rho),
        passive_mask_sha256=_fingerprint(passive),required_passive_cell_ids=sorted(required),
        original_receipt_authenticated_by_this_helper=False,
        executor_must_first_verify_original_trial_receipt=True,**FLAGS),'parent_input_id')


class _BudgetExceeded(RuntimeError):pass


class _Budget:
    def __init__(self,maximum,seconds):
        self.maximum=maximum;self.seconds=seconds;self.started=time.monotonic();self.operations=0
    def tick(self):
        self.operations+=1
        if self.operations>self.maximum:raise _BudgetExceeded('operation-budget')
        if time.monotonic()-self.started>self.seconds:raise _BudgetExceeded('time-budget')


def _neighbors(index,nx,nz):
    j,i=divmod(index,nx)
    return sorted(b*nx+a for a,b in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)) if 0<=a<nx and 0<=b<nz)


def _components(mask,budget):
    nz,nx=mask.shape;remaining=set(np.flatnonzero(mask).tolist());groups=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);queue=deque([seed]);group={seed}
        while queue:
            budget.tick()
            for neighbor in _neighbors(queue.popleft(),nx,nz):
                if neighbor in remaining:remaining.remove(neighbor);group.add(neighbor);queue.append(neighbor)
        groups.append(group)
    return groups


def _mandatory_component(mask,passive,budget):
    required=set(np.flatnonzero(passive).tolist());groups=_components(mask,budget)
    return next((group for group in groups if required<=group),None),groups


def _connect(mask,rho,passive,budget,decisions):
    nz,nx=mask.shape;flat=mask.ravel();weights=[1-Fraction(str(float(v))) for v in rho.ravel()]
    while True:
        anchor,groups=_mandatory_component(mask,passive,budget)
        if anchor is None:
            first=int(np.flatnonzero(passive)[0]);anchor=next(group for group in groups if first in group)
        if len(groups)==1:return None
        foreign=set().union(*(group for group in groups if group is not anchor))
        distances={i:(0,Fraction(0),0) for i in anchor};previous={i:None for i in anchor}
        heap=[(0,Fraction(0),0,i) for i in sorted(anchor)];heapq.heapify(heap);target=None
        while heap:
            budget.tick();added,penalty,steps,current=heapq.heappop(heap)
            if distances[current]!=(added,penalty,steps):continue
            if current in foreign:target=current;break
            for neighbor in _neighbors(current,nx,nz):
                budget.tick();empty=not bool(flat[neighbor])
                score=(added+int(empty),penalty+(weights[neighbor] if empty else 0),steps+1)
                if neighbor not in distances or score<distances[neighbor]:
                    distances[neighbor]=score;previous[neighbor]=current
                    heapq.heappush(heap,(*score,neighbor))
        if target is None:return 'no-grid-path-to-original-stock'
        path=[];item=target
        while item is not None:path.append(item);item=previous[item]
        path.reverse();new=[i for i in path if not flat[i]]
        if not new:raise ValueError('Connecting path did not add material')
        flat[new]=True
        decisions.append(dict(kind='connect-original-stock',path_cell_ids=path,added_cell_ids=new,
            added_cell_count=len(new),density_penalty=str(distances[target][1])))


def _close_corners(mask,rho,budget,decisions):
    nz,nx=mask.shape;flat=mask.ravel();density=rho.ravel()
    blocks=[j*(nx-1)+i for j in range(nz-1) for i in range(nx-1)];heapq.heapify(blocks);pending=set(blocks)
    while blocks:
        budget.tick();index=heapq.heappop(blocks);pending.remove(index);j,i=divmod(index,nx-1)
        cells=[j*nx+i,j*nx+i+1,(j+1)*nx+i,(j+1)*nx+i+1]
        a,b,c,d=[bool(flat[k]) for k in cells]
        if not ((a and d and not b and not c) or (b and c and not a and not d)):continue
        choices=[k for k in cells if not flat[k]];chosen=min(choices,key=lambda k:(-float(density[k]),k));flat[chosen]=True
        decisions.append(dict(kind='close-corner-contact',block_cell_ids=cells,added_cell_ids=[chosen],
            original_density=float(density[chosen])))
        y,x=divmod(chosen,nx)
        for by in (y-1,y):
            for bx in (x-1,x):
                if 0<=by<nz-1 and 0<=bx<nx-1:
                    block=by*(nx-1)+bx
                    if block not in pending:heapq.heappush(blocks,block);pending.add(block)


def propose(parent_input,parent_geometry,occupancy,original_density,passive_solid_mask,*,strategy,
        maximum_elements=1920,maximum_operations=1_000_000,time_budget_s=2.):
    """Propose explicit physical stock changes; never modify/admit the parent.

    Shortest paths minimise added cells, then exact rational density penalty,
    then grid steps. Heap/neighbor row-major order deterministically breaks ties.
    Caller-provided element budgets may be 1920 or 7680; operation/time budgets
    are bounded construction controls, not physical design requirements.
    """
    if maximum_elements not in (1920,7680) or type(maximum_elements) is not int:
        raise ValueError('Explicit 1920/7680 element budget required')
    if type(maximum_operations) is not int or not 1<=maximum_operations<=20_000_000:
        raise ValueError('Bounded positive operation budget required')
    try:valid_time=type(time_budget_s) in (int,float) and isfinite(time_budget_s) and 0<time_budget_s<=30
    except OverflowError:valid_time=False
    if not valid_time:
        raise ValueError('Finite time budget in (0,30] seconds required')
    if strategy not in STRATEGIES:raise ValueError('Explicit physical revision strategy required')
    budget=_Budget(maximum_operations,time_budget_s)
    mask,rho,passive=_arrays(occupancy,original_density,passive_solid_mask,maximum_elements)
    if parent_input.get('parent_input_id')!=identity({k:v for k,v in parent_input.items() if k!='parent_input_id'}):
        raise ValueError('Sealed parent input required')
    expected=make_parent_input(parent_geometry,mask,rho,passive,
        parent_evaluation_id=parent_input['parent_evaluation_id'],parent_request_id=parent_input['parent_request_id'],
        arrays_package_sha256=parent_input['original_arrays_package_sha256'],required_passive_cell_ids=parent_input['required_passive_cell_ids'])
    if parent_input!=expected:raise ValueError('Parent geometry/evaluation or observed array binding differs')
    before=mask.copy();decisions=[];reason=None
    try:
        anchor,groups=_mandatory_component(mask,passive,budget)
        if anchor is None and strategy==STRATEGIES[0]:reason='mandatory-stock-spans-multiple-components'
        elif strategy==STRATEGIES[0]:
            remove=sorted(set(np.flatnonzero(mask).tolist())-anchor);mask.ravel()[remove]=False
            if remove:decisions.append(dict(kind='remove-disconnected-nonmandatory-islands',removed_cell_ids=remove))
        else:reason=_connect(mask,rho,passive,budget,decisions)
        if reason is None:_close_corners(mask,rho,budget,decisions)
        if np.any(passive & ~mask):raise ValueError('Revision removed mandatory stock')
        budget.tick()
    except _BudgetExceeded as exc:reason=str(exc)
    added=np.flatnonzero(mask & ~before).tolist();removed=np.flatnonzero(before & ~mask).tolist()
    child=None
    if reason is None:
        child=geometry.realize(mask)
        if child['candidate_id']==parent_geometry['candidate_id']:reason='physically-identical-no-change';child=None
        elif child['web_geometry']['corner_only_contacts'] or child['web_geometry']['finite_edge_components']!=1:
            reason='revision-topology-postcondition-failed';child=None
    value=dict(schema='osr-topology-physical-revision-proposal/1',strategy=strategy,
        parent_input_id=parent_input['parent_input_id'],parent_candidate_id=parent_geometry['candidate_id'],
        parent_geometry_id=parent_geometry['geometry_id'],parent_evaluation_id=parent_input['parent_evaluation_id'],
        parent_request_id=parent_input['parent_request_id'],original_arrays_package_sha256=parent_input['original_arrays_package_sha256'],
        proposed_geometry=child,proposed_candidate_id=None if child is None else child['candidate_id'],
        occupancy=mask.tolist(),added_cell_ids=added,removed_cell_ids=removed,decisions=decisions,
        input_shape=list(mask.shape),envelope_material_and_interfaces_unchanged=True,
        execution='proposal-generated' if child is not None else 'proposal-rejected',failure_reason=reason,
        resource_request=dict(maximum_elements=maximum_elements,maximum_operations=maximum_operations,time_budget_s=time_budget_s),
        operations=budget.operations,runtime_guard='between bounded grid operations; no process memory limit',
        operating_system_isolation=False,physical_stock_proposal_only=True,
        numerical_evaluation_execution='not-run',manufacturability_proved=False,installed_mass_complete=False,
        original_trial_authenticity_verified_by_this_helper=False,integrated_selection=None,
        source_sha256={PRODUCER:digest(__file__),**parent_geometry['source_sha256']},**FLAGS)
    value['revision_id']=identity(dict(parent_candidate_id=value['parent_candidate_id'],
        proposed_candidate_id=value['proposed_candidate_id'],strategy=strategy,added_cell_ids=added,removed_cell_ids=removed))
    return _seal(value,'evaluation_id')
