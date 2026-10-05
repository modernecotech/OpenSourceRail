"""Bounded water-aware repair of planning corridors, preserving dry geometry."""
from __future__ import annotations
import heapq
import math

import numpy as np


def sampled_cells(cells):
    """Sample every raster cell along segments, including sparse straight runs."""
    result = [tuple(round(value) for value in cells[0])]
    for a, b in zip(cells, cells[1:]):
        steps = max(1, math.ceil(2*math.hypot(b[0]-a[0],b[1]-a[1])))
        for index in range(1,steps+1):
            cell = (round(a[0]+(b[0]-a[0])*index/steps),round(a[1]+(b[1]-a[1])*index/steps))
            if cell != result[-1]:result.append(cell)
    return result


def water_runs(cells, mask, cell_m):
    samples = sampled_cells(cells)
    runs = []
    start = None; length = 0.0
    for index, cell in enumerate(samples):
        wet = int(mask[cell]) > 0
        step = math.dist(samples[index-1],cell)*cell_m if index else 0.0
        if wet:
            if start is None:start=index;length=step/2
            else:length+=step
        elif start is not None:
            length+=step/2
            runs.append(dict(start_index=start,end_index=index-1,length_m=length,
                             unknown=any(int(mask[c])==255 for c in samples[start:index])))
            start=None;length=0.0
    if start is not None:
        runs.append(dict(start_index=start,end_index=len(samples)-1,length_m=length,
                         unknown=any(int(mask[c])==255 for c in samples[start:])))
    return samples,runs


def water_budget_detour(start,goal,mask,blocked,cell_m,maximum_water_run_m,maximum_expansions):
    """Keep Pareto labels for cost and consecutive water distance.

    Each water step is rounded up to a metre, so the search budget is
    conservative. A cheaper path that has already used more of the crossing
    budget cannot erase a feasible shorter crossing from another shore.
    """
    start_state=(*start,0);costs={start_state:0.0};parents={};labels={start:[(0.0,0)]}
    queue=[(math.dist(start,goal),0.0,start_state)];count=0
    directions=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    while queue:
        _,travel,state=heapq.heappop(queue);row,col,budget=state
        if costs.get(state)!=travel or (travel,budget) not in labels.get((row,col),[]):continue
        if (row,col)==goal:
            path=[(row,col)]
            while state!=start_state:
                state=parents[state];path.append(state[:2])
            return list(reversed(path)),count
        count+=1
        if count>maximum_expansions:raise ValueError('Water-budget detour exceeds bounded search; review route')
        for dr,dc in directions:
            nr,nc=row+dr,col+dc
            if not 0<=nr<mask.shape[0] or not 0<=nc<mask.shape[1] or blocked[nr,nc]:continue
            if dr and dc and (blocked[row,nc] or blocked[nr,col]):continue
            step=math.hypot(dr,dc);metres=step*cell_m
            was_wet=mask[row,col]>0;wet=mask[nr,nc]>0
            next_budget=budget+math.ceil(metres) if was_wet and wet else (math.ceil(metres/2) if wet else 0)
            exit_budget=budget+math.ceil(metres/2) if was_wet and not wet else next_budget
            if exit_budget>maximum_water_run_m:continue
            candidate=travel+step*(100.0 if wet else 1.0)
            cell=(nr,nc);frontier=labels.get(cell,[])
            if any(cost<=candidate and used<=next_budget for cost,used in frontier):continue
            labels[cell]=[(cost,used) for cost,used in frontier if not(candidate<=cost and next_budget<=used)]
            labels[cell].append((candidate,next_budget));following=(*cell,next_budget)
            costs[following]=candidate;parents[following]=state
            heapq.heappush(queue,(candidate+math.dist(cell,goal),candidate,following))
    raise ValueError('No route within the controlled consecutive-water budget; review endpoints/crossing')


def detour(start, goal, mask, blocked, maximum_expansions=3_000_000,
           cell_m=20.0,maximum_water_run_m=1000.0):
    from scipy.ndimage import label
    land_components,_=label((mask==0)&~blocked)
    land_connected=land_components[start]!=0 and land_components[start]==land_components[goal]
    if land_connected:
        # Prefer an entirely dry route when both approaches share land. This
        # avoids searching costly shallow-water shortcuts around a peninsula.
        blocked=blocked|(mask>0)
    del land_components
    if not land_connected:
        label_limit=min(maximum_expansions,10_000) if mask.size>=1_000_000 else maximum_expansions
        try:
            return water_budget_detour(start,goal,mask,blocked,cell_m,maximum_water_run_m,label_limit)
        except ValueError as error:
            if 'exceeds bounded search' not in str(error):raise
            # A compiled minimum-cost search can find a narrow upstream
            # crossing without millions of resource-state labels. Accept its
            # actual geometry only after the same water budget and forbidden
            # corner checks; failure never waives the crossing limit.
            from skimage.graph import MCP_Geometric
            for diagonal in [True,False]:
                costs_grid=np.where(blocked,np.inf,np.where(mask>0,100.0,1.0))
                solver=MCP_Geometric(costs_grid,fully_connected=diagonal)
                costs,_=solver.find_costs([start],[goal])
                if not np.isfinite(costs[goal]):
                    raise ValueError('No permitted route connects these shores in the retained water/buildability constraints') from error
                path=solver.traceback(goal)
                visited_bound=int(np.count_nonzero(np.isfinite(costs)))
                del solver,costs,costs_grid
                _,runs=water_runs(path,mask,cell_m)
                forbidden_corner=any(a[0]!=b[0] and a[1]!=b[1]
                    and (blocked[a[0],b[1]] or blocked[b[0],a[1]]) for a,b in zip(path,path[1:]))
                if not forbidden_corner and all(not r['unknown'] and r['length_m']<=maximum_water_run_m for r in runs):
                    return path,label_limit+visited_bound
            if label_limit<maximum_expansions:
                path,count=water_budget_detour(start,goal,mask,blocked,cell_m,maximum_water_run_m,maximum_expansions)
                return path,label_limit+2*mask.size+count
            raise ValueError('Bounded fallback still requires an unapproved crossing; review alignment') from error
    height,width=mask.shape
    distances=np.full((height,width),np.inf)
    parent=np.full((height,width),-1,dtype=np.int32)
    distances[start]=0.0
    queue=[(math.dist(start,goal),0.0,start)]
    directions=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    count=0
    while queue:
        _,travel,cell=heapq.heappop(queue)
        if travel != distances[cell]:continue
        if cell==goal:
            path=[cell]
            while path[-1]!=start:
                previous=int(parent[path[-1]])
                path.append(divmod(previous,width))
            return list(reversed(path)),count
        count+=1
        if count>maximum_expansions:raise ValueError('Water detour exceeds bounded search; review route')
        row,col=cell
        for dr,dc in directions:
            nr,nc=row+dr,col+dc
            if not 0<=nr<height or not 0<=nc<width or blocked[nr,nc]:continue
            if dr and dc and (blocked[row,nc] or blocked[nr,col]):continue
            # A routing penalty, not a civil quotation. Large open-water runs
            # are blocked; narrow rivers may still receive priced bridges.
            penalty=100.0 if mask[nr,nc]>0 else 1.0
            candidate=travel+math.hypot(dr,dc)*penalty
            if candidate<distances[nr,nc]:
                distances[nr,nc]=candidate;parent[nr,nc]=row*width+col
                heapq.heappush(queue,(candidate+math.dist((nr,nc),goal),candidate,(nr,nc)))
    raise ValueError('No bounded land route around mapped water; review endpoints/crossing')


def crop_terminal_at_long_water(cells,mask,cell_m,at_start,maximum_crop_m,maximum_water_run_m=1000):
    """Apply a city's explicit exclusion of an offshore radial tail."""
    ordered=sampled_cells(cells)
    if not at_start:ordered.reverse()
    _,runs=water_runs(ordered,mask,cell_m)
    run=next((r for r in runs if r['unknown'] or r['length_m']>maximum_water_run_m),None)
    if run is None:raise ValueError('Controlled offshore-tail scope no longer matches a long water crossing')
    bank=run['end_index']+1
    if bank>=len(ordered)-1:raise ValueError('Offshore-tail scope would remove the whole line')
    removed=sum(math.dist(a,b)*cell_m for a,b in zip(ordered[:bank],ordered[1:bank+1]))
    if removed>maximum_crop_m:raise ValueError('Offshore-tail scope exceeds its controlled route-removal bound')
    retained=ordered[bank:]
    if not at_start:retained.reverse()
    return [list(c) for c in retained],dict(kind='controlled-offshore-tail-scope-reduction',
        from_cell=ordered[0],to_cell=ordered[bank],removed_original_route_m=removed,
        maximum_crop_m=maximum_crop_m,geometry_basis='shore-terminus-requires-catchment-access-and-curve-review')


def repair(cells, mask, cell_m, maximum_unapproved_crossing_m=1000.0, buildable=None,
           maximum_endpoint_trim_m=0.0, maximum_endpoint_relocation_m=0.0,
           maximum_approach_replacement_m=1000.0,minimum_shore_component_area_m2=0.0):
    """Unapproved kilometre-scale lake/sea crossings cannot silently be bridges.

    Short bridge candidates remain subject to civil/shoreline review. Unknown
    coverage is forbidden. Dry endpoints and all unrelated route fragments
    remain controlled inputs; wet endpoints require an explicit relocation.
    """
    from scipy.ndimage import distance_transform_edt
    changes=[]
    samples=sampled_cells(cells)
    usable_shore=(mask==0)&(buildable if buildable is not None else True)
    if minimum_shore_component_area_m2>0:
        from scipy.ndimage import label
        shore_labels,_=label(usable_shore)
        areas=np.bincount(shore_labels.ravel())*cell_m**2;areas[0]=0
        usable_shore &= areas[shore_labels]>=minimum_shore_component_area_m2
        del shore_labels,areas
    if samples[0]==samples[-1] and mask[samples[0]]>0:
        first=next((i for i,c in enumerate(samples[:-1]) if mask[c]==0),None)
        if first is None:raise ValueError('Closed ring has no dry platform origin')
        original=samples[0];unique=samples[:-1]
        samples=unique[first:]+unique[:first];samples.append(samples[0])
        changes.append(dict(kind='ring-chainage-origin-on-bank',from_cell=original,to_cell=samples[0],geometry_changed=False))
    elif maximum_endpoint_trim_m>0:
        for at_start in [True,False]:
            ordered=samples if at_start else list(reversed(samples))
            if usable_shore[ordered[0]]:continue
            index=next((i for i,c in enumerate(ordered) if usable_shore[c]),None)
            if index is None:raise ValueError('Water endpoint has no dry bank')
            removed=sum(math.dist(a,b)*cell_m for a,b in zip(ordered[:index],ordered[1:index+1]))
            if removed>maximum_endpoint_trim_m:
                if maximum_endpoint_relocation_m<=0:
                    raise ValueError(f'Water endpoint bank is {removed:.1f} m away, exceeding controlled {maximum_endpoint_trim_m:.0f} m crop; review alignment')
                origin=ordered[0];radius=math.floor(maximum_endpoint_relocation_m/cell_m)
                candidates=[]
                for r in range(max(0,origin[0]-radius),min(mask.shape[0],origin[0]+radius+1)):
                    for c in range(max(0,origin[1]-radius),min(mask.shape[1],origin[1]+radius+1)):
                        d=math.dist(origin,(r,c))*cell_m
                        if d<=maximum_endpoint_relocation_m and usable_shore[r,c]:
                            candidates.append((d,(r,c)))
                if not candidates:raise ValueError('Wet endpoint has no permitted dry bank within controlled relocation envelope')
                from scipy.ndimage import label
                land_components,_=label(usable_shore)
                connected=[candidate for candidate in candidates if land_components[candidate[1]]==land_components[ordered[index]]]
                if connected:candidates=connected
                del land_components
                shift,bank=min(candidates)
                depth=distance_transform_edt(mask>0)*cell_m
                blocked=(depth>maximum_unapproved_crossing_m/2)|(mask==255)
                if buildable is not None:blocked|=~buildable
                path,count=detour(bank,ordered[index],mask,blocked,cell_m=cell_m,maximum_water_run_m=maximum_unapproved_crossing_m)
                _,remaining=water_runs(path,mask,cell_m)
                if any(r['unknown'] or r['length_m']>maximum_unapproved_crossing_m for r in remaining):
                    raise ValueError('Relocated endpoint still requires an unapproved long water crossing')
                changes.append(dict(kind='bounded-endpoint-relocation-with-shore-route',from_cell=origin,to_cell=bank,
                    endpoint_shift_m=shift,maximum_relocation_m=maximum_endpoint_relocation_m,
                    removed_original_route_m=removed,detour_route_m=sum(math.dist(a,b)*cell_m for a,b in zip(path,path[1:])),
                    search_work_upper_bound=count,geometry_basis='shore-route-requires-survey-access-and-curve-review'))
                repaired=path+ordered[index+1:]
                samples=repaired if at_start else list(reversed(repaired))
                continue
            changes.append(dict(kind='bounded-water-endpoint-bank-crop',from_cell=ordered[0],to_cell=ordered[index],
                removed_route_m=removed,maximum_crop_m=maximum_endpoint_trim_m,geometry_changed=True))
            samples=samples[index:] if at_start else samples[:-index]
            if len(samples)<2:raise ValueError('Water endpoint crop would remove complete line')
    samples,runs=water_runs(samples,mask,cell_m)
    bad=[r for r in runs if r['unknown'] or r['length_m']>maximum_unapproved_crossing_m]
    if not bad:return ([list(c) for c in samples] if changes else cells),changes
    # Nearby open-water crossings separated by a short peninsula are one
    # detour problem. Repairing them separately can produce a needless
    # out-and-back excursion along an unserved peninsula or island.
    grouped=[]
    for run in bad:
        if grouped:
            previous=grouped[-1]
            gap=sum(math.dist(a,b)*cell_m for a,b in zip(
                samples[previous['end_index']:run['start_index']],
                samples[previous['end_index']+1:run['start_index']+1]))
            if gap<=maximum_unapproved_crossing_m:
                previous['end_index']=run['end_index']
                previous['length_m']+=run['length_m']
                previous['unknown']|=run['unknown']
                continue
        grouped.append(dict(run))
    bad=grouped
    wet=mask>0
    depth=distance_transform_edt(wet)*cell_m
    blocked=(depth>maximum_unapproved_crossing_m/2)|(mask==255)
    if buildable is not None:blocked|=~buildable
    output=[];position=0
    for run in bad:
        first=run['start_index']-1;last=run['end_index']+1
        if first<0 or last>=len(samples):
            raise ValueError('Long water tail ends over lake/sea; move endpoint explicitly before routing')
        # A dry shoreline cell may still lie in a forbidden protected area.
        # Extend the replacement onto permitted approach cells; never seed
        # the search inside that area or silently permit a blocked goal.
        old_first,old_last=first,last
        for backwards in [True,False]:
            moved=0.0
            while blocked[samples[first if backwards else last]] or not usable_shore[samples[first if backwards else last]]:
                current=first if backwards else last
                following=current-1 if backwards else current+1
                if not 0<=following<len(samples):raise ValueError('No permitted water-crossing approach inside controlled route')
                moved+=math.dist(samples[current],samples[following])*cell_m
                if moved>maximum_approach_replacement_m:raise ValueError('Forbidden shoreline approach exceeds bounded replacement envelope')
                if backwards:first=following
                else:last=following
        path,count=detour(samples[first],samples[last],mask,blocked,cell_m=cell_m,maximum_water_run_m=maximum_unapproved_crossing_m)
        _,remaining=water_runs(path,mask,cell_m)
        if any(r['unknown'] or r['length_m']>maximum_unapproved_crossing_m for r in remaining):
            raise ValueError('Water detour still requires an unapproved long crossing')
        output.extend(samples[position:first]);output.extend(path);position=last+1
        changes.append(dict(kind='land-detour-around-unapproved-open-water-crossing',
            from_cell=samples[first],to_cell=samples[last],removed_water_run_m=run['length_m'],
            detour_route_m=sum(math.dist(a,b)*cell_m for a,b in zip(path,path[1:])),
            protected_approach_extended=first!=old_first or last!=old_last,
            search_work_upper_bound=count,geometry_basis='water-constrained-raster-requires-curve-and-structure-review'))
    output.extend(samples[position:])
    return [list(c) for i,c in enumerate(output) if i==0 or c!=output[i-1]],changes
