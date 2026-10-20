"""Constrained route-shape and whole-network connectivity planning.

Common route cells are proposed interchange sites, not accepted switches,
platforms or pedestrian transfers. Native station generation and the independent
geographic audit must subsequently verify the actual platform pairs.
"""
from copy import deepcopy
import math

import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString


def components(lines,mask=None):
    shapes={line['name']:LineString(line['cells']) for line in lines}
    remaining=set(shapes); groups=[]
    while remaining:
        group={min(remaining)};remaining-=group;pending=list(group)
        while pending:
            first=pending.pop()
            for other in sorted(remaining):
                intersection=shapes[first].intersection(shapes[other])
                def dry_contact(value):
                    if value.is_empty:return False
                    if mask is None:return True
                    if value.geom_type=='Point':
                        r,c=(math.floor(x+.5) for x in value.coords[0])
                        return 0<=r<mask.shape[0] and 0<=c<mask.shape[1] and mask[r,c]==0
                    if value.geom_type=='LineString':
                        from shapely.geometry import Point
                        return any(dry_contact(Point(c)) for c in value.coords)
                    return any(dry_contact(v) for v in value.geoms)
                if dry_contact(intersection):
                    remaining.remove(other);group.add(other);pending.append(other)
        groups.append(sorted(group))
    return sorted(groups)


def length(cells,cell_m):
    return math.fsum(math.dist(a,b)*cell_m for a,b in zip(cells,cells[1:]))


def reverse_excursion(cells,cell_m):
    delta=np.subtract(cells[-1],cells[0]);norm=float(np.linalg.norm(delta))
    if norm==0:return 0.
    progress=np.dot(np.subtract(cells,cells[0]),delta/norm)*cell_m
    return float(np.max(np.maximum.accumulate(progress)-progress))


def remove_small_knots(cells,cell_m,mask,buildable,*,maximum_removed_m=200.,required_cells=()):
    """Remove bounded raster micro-loops, preserving endpoints and ring closure.

    Larger loops require another corridor decision. A diagonal crossing can
    be resolved along one side of its own raster cell only on known buildable
    land. This is a planning realignment, never an issued curve detail.
    """
    result=[list(c) for c in cells];changes=[];closed=result[0]==result[-1]
    while not LineString(result).is_simple:
        seen={};diagonals={};proposals=[]
        for j,c in enumerate(result):
            key=tuple(c)
            if key in seen and not (closed and seen[key]==0 and j==len(result)-1):
                i=seen[key];proposals.append((i,j,result[:i+1]+result[j+1:],'repeated-cell-loop'))
            seen[key]=j
        for j,(a,b) in enumerate(zip(result,result[1:])):
            if abs(a[0]-b[0])!=1 or abs(a[1]-b[1])!=1:continue
            key=(min(a[0],b[0]),min(a[1],b[1]));rising=(a[0]<b[0])==(a[1]<b[1])
            if (key,not rising) in diagonals:
                i=diagonals[(key,not rising)]
                proposals.append((i,j,result[:i+1]+result[j+1:],'crossed-unit-diagonals'))
            diagonals[(key,rising)]=j
        accepted=[]
        for i,j,candidate,kind in proposals:
            if len(candidate)<(4 if closed else 2) or candidate[0]!=result[0] or candidate[-1]!=result[-1]:continue
            if not set(map(tuple,required_cells))<=set(map(tuple,candidate)):continue
            removed=length(result,cell_m)-length(candidate,cell_m)
            if not 0<removed<=maximum_removed_m-sum(c['removed_route_m'] for c in changes):continue
            a,b=candidate[i],candidate[min(i+1,len(candidate)-1)]
            if max(abs(a[0]-b[0]),abs(a[1]-b[1]))>1:continue
            if any(mask[tuple(c)]!=0 or not buildable[tuple(c)] for c in (a,b)):continue
            accepted.append((removed,i,j,kind,candidate))
        if not accepted:raise ValueError('Self-intersecting route requires a larger controlled realignment')
        removed,i,j,kind,result=min(accepted,key=lambda v:(v[0],v[1],v[2]))
        changes.append(dict(kind=kind,removed_route_m=removed,source_from_index=i,source_to_index=j,
                            local_curve_and_site_accepted=False))
    return result,changes


def connect_network(routes,mask,buildable,cell_m,route,*,maximum_extension_m=4000.,
                    maximum_added_m=5000.,maximum_reverse_m=750.,protected_by_line=None):
    """Join components by bounded continuous extensions or through diversions.

    Preserve line inventory, ring closure and existing connected components.
    Reject self-intersections, out-and-back spurs, excessive added scope and
    paths that cannot be routed through the supplied land/water constraints.
    """
    result=deepcopy(routes);changes=[];initial=components(result['lines'],mask)
    while len(before:=components(result['lines'],mask))>1:
        group={name:i for i,names in enumerate(before) for name in names}
        candidates=[]
        for line in result['lines']:
            if line['shape'].lower()=='ring':continue
            original=list(map(tuple,line['cells']));old_length=length(original,cell_m)
            old_shape=LineString(original)
            targets=sorted({tuple(c) for other in result['lines'] if group[other['name']]!=group[line['name']]
                            for c in other['cells'] if mask[tuple(c)]==0 and buildable[tuple(c)]})
            if not targets:continue
            tree=cKDTree(targets)
            proposals=[]
            for at_start in (True,False):
                end=original[0] if at_start else original[-1]
                distances,indices=tree.query(end,k=min(8,len(targets)))
                # Different targets must be spatially distinct, not eight
                # adjacent cells offering the same blocked approach.
                chosen=[]
                for distance,index in zip(np.atleast_1d(distances),np.atleast_1d(indices)):
                    target=targets[int(index)]
                    if distance*cell_m>maximum_extension_m:continue
                    if any(math.dist(target,p)*cell_m<200 for p in chosen):continue
                    chosen.append(target)
                    try:path=route(end,target,None)
                    except ValueError:continue
                    if length(path,cell_m)>maximum_extension_m:continue
                    revised=list(reversed(path))+original[1:] if at_start else original+path[1:]
                    proposals.append((revised,target,'terminal-extension'))
            # A middle approach may need a continuous through diversion.
            distances,indices=tree.query(original);slot=int(np.argmin(distances))
            target=targets[int(indices[slot])]
            if distances[slot]*cell_m<=maximum_extension_m:
                chain=np.r_[0.,np.cumsum([math.dist(a,b)*cell_m for a,b in zip(original,original[1:])])]
                for window in (1000.,2000.,3000.):
                    left=int(np.searchsorted(chain,max(0.,chain[slot]-window)))
                    right=min(len(original)-1,int(np.searchsorted(chain,chain[slot]+window)))
                    if left==right:continue
                    try:
                        first=route(original[left],target,None)
                        second=route(target,original[right],set(first[:-1]))
                    except ValueError:continue
                    proposals.append((original[:left]+first+second[1:]+original[right+1:],target,'through-diversion'))
            for revised,target,kind in proposals:
                revised=[list(c) for i,c in enumerate(revised) if i==0 or c!=revised[i-1]]
                shape=LineString(revised)
                if not shape.is_simple:continue
                required=set(map(tuple,(protected_by_line or {}).get(line['name'],[])))
                if not required<=set(map(tuple,revised)):continue
                new_length=length(revised,cell_m);added=new_length-old_length
                if added>maximum_added_m or new_length<old_length*.75:continue
                # A monotone progress screen prevents a new hairpin spur.
                delta=np.subtract(revised[-1],revised[0]);norm=float(np.linalg.norm(delta))
                if norm>0:
                    progress=np.dot(np.subtract(revised,revised[0]),delta/norm)*cell_m
                    if float(np.max(np.maximum.accumulate(progress)-progress))>maximum_reverse_m:continue
                trial=deepcopy(result)
                next(l for l in trial['lines'] if l['name']==line['name'])['cells']=revised
                after=components(trial['lines'],mask)
                if len(after)>=len(before):continue
                # Every previously connected component must remain connected.
                if any(not any(set(c)<=set(n) for n in after) for c in before):continue
                changed_m=old_shape.difference(shape).length*cell_m
                candidates.append((max(0.,added)+.1*changed_m,line['name'],kind,target,trial,
                                   dict(line=line['name'],kind=kind,contact_cell=list(target),
                                        original_route_m=old_length,final_route_m=new_length,
                                        added_route_m=added,components_before=before,components_after=after,
                                        platforms_and_transfer_access_accepted=False)))
        if not candidates:
            raise ValueError('No bounded compliant connection for network components: '+str(before))
        chosen=min(candidates,key=lambda v:(v[0],v[1],v[2],v[3]))
        result=chosen[4];changes.append(chosen[5])
    return result,dict(initial_components=initial,final_components=components(result['lines'],mask),changes=changes,
                       engineering_release=False,physical_release=False)
