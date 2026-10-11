"""Bound compact expansion while reserving candidates for underserved sectors."""
from copy import deepcopy
import math
import numpy as np
import residential_route_expansion as expansion
from mapping_evidence import coverage,radial_distances,sector_members


def plan(routes, stations, grid, mask, buildable, population, old_population, cfg, mapping_cfg):
    """Sector phases rank real resident counts, then fill the remaining budget.

    Sector quotas allocate investigation effort; they are not automatic coverage
    acceptance. Earlier selected stop circles are excluded from subsequent gains.
    Actual native station placement is audited after synthesis.
    """
    result=deepcopy(routes);stops=deepcopy(stations);added=[];phases=[];rejected=[];used=0.
    def length(line):return math.fsum(math.dist(a,b)*grid['cell_m'] for a,b in zip(line['cells'],line['cells'][1:]))
    original_length=math.fsum(length(line) for line in routes['lines'])
    budget=min(cfg['maximum_added_route_m'],original_length*cfg['maximum_added_route_fraction'])
    year=mapping_cfg['population_year'];radius=cfg['station_radius_m']
    true_counts=population['counts'];initial=radial_distances(population,stations)<=radius+1e-7;covered=initial.copy()
    total=math.fsum(map(float,true_counts))
    sectors=mapping_cfg['sectors']
    for sector in [*sectors,dict(id='city',reserved_added_lines=cfg['maximum_added_lines'])]:
        count=min(sector['reserved_added_lines'],cfg['maximum_added_lines']-len(added))
        if count<=0:break
        region=np.ones(len(true_counts),dtype=bool) if sector['id']=='city' else sector_members(population,sector)
        remaining=region&~covered&(true_counts>0)
        if not remaining.any():
            phases.append(dict(sector=sector['id'],added_lines=0,outcome='no unserved positive population'));continue
        data={k:population[k][region].copy() for k in ('lat','lon','counts')}
        phase=deepcopy(cfg);phase.update(maximum_added_lines=count,maximum_added_route_m=budget-used,
                                       maximum_added_route_fraction=1.,target_station_radial_fraction=1.)
        candidate,report=expansion.plan(result,stops,grid,mask,buildable,data,phase)
        for row in report['added_lines']:
            # Recover source-year-independent gain from the full native union,
            # rather than summing overlapping sector-only phase totals.
            line=next(line for line in candidate['lines'] if line['name']==row['line'])
            cells=[line['cells'][0],line['cells'][-1],*row['priority_cells']]
            positions=expansion.cell_lonlat(cells,grid)
            new_stops=[dict(lat=float(lat),lon=float(lon),line=row['line']) for lon,lat in positions]
            new=radial_distances(population,new_stops)<=radius+1e-7
            gain=math.fsum(map(float,true_counts[new&~covered]));sector_gain=math.fsum(map(float,true_counts[new&~covered&region]))
            covered|=new;stops.extend(new_stops)
            row=deepcopy(row);row.pop('incremental_residents_2020',None)
            row.update(selection_sector=sector['id'],incremental_residents=round(gain,3),population_year=year,
                       incremental_sector_residents=round(sector_gain,3))
            added.append(row)
        used+=report['added_route_m'];result=candidate;rejected.extend(report['rejected_priority_areas'])
        phases.append(dict(sector=sector['id'],reserved_lines=count,added_lines=report['added_line_count'],
                           added_route_m=report['added_route_m'],outcome=report['outcome']))
    if len(added)>cfg['maximum_added_lines'] or used>budget+.01:raise ValueError('Regional expansion exceeded total compact budget')
    old=dict(old_population,valid=np.ones(len(old_population['counts']),dtype=bool))
    current=dict(population,valid=np.ones(len(true_counts),dtype=bool))
    old_baseline=coverage(old,stations,sectors,radius)['sectors'][0]['radial_fraction']
    fraction=math.fsum(map(float,true_counts[covered]))/total
    report=dict(population_year=year,bbox_population=round(total,3),population_dataset=mapping_cfg['selected_population'],
                baseline_population_year=2020,baseline_actual_station_radial_fraction=old_baseline,
                selected_population_baseline_station_radial_fraction=round(math.fsum(map(float,true_counts[initial]))/total,8),
                original_line_count=len(routes['lines']),added_line_count=len(added),final_line_count=len(result['lines']),
                original_route_m=round(original_length,3),added_route_m=round(used,3),added_route_limit_m=round(budget,3),
                target_radial_fraction=cfg['target_station_radial_fraction'],proposed_station_sample_radial_fraction=round(fraction,8),
                target_met_in_proposed_station_sample=fraction>=cfg['target_station_radial_fraction'],actual_regenerated_station_coverage=None,
                planned_stop_cells_by_line={line['name']:expansion.station_samples(line['cells'],mask,cfg['maximum_ordinary_station_gap_m'],grid['cell_m']) for line in result['lines']},
                sector_selection_phases=phases,sector_baseline=coverage(current,stations,sectors,radius),sector_proposed_stop_screen=coverage(current,stops,sectors,radius),
                added_lines=added,rejected_priority_areas=rejected,
                outcome='Compact investigation candidate; actual emitted sector coverage and pedestrian topology must be audited separately')
    return result,report
