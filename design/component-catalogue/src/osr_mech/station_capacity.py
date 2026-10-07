"""Shared-layout station area, circulation and lift-out capacity screens.

No default people density or equipment throughput is presented as a standard.
Surveyed demand and reviewed evacuation/rescue criteria remain separate inputs.
"""
import math
from osr_mech.provenance import stable_sum as sum
from .station.circulation import continuous_path,continuous_clear_width


def footprint_screen(platform,length_m,equipment):
    x0,x1=-length_m/2,length_m/2;y0=(platform['y_mm']-platform['width_mm']/2)/1000;y1=y0+platform['width_mm']/1000
    rectangles=[]
    for e in equipment:
        if platform['level'] not in e['served_levels']:continue
        a=(e['x_mm']-e['length_mm']/2)/1000;b=(e['x_mm']+e['length_mm']/2)/1000
        c=(e['y_mm']-e['width_mm']/2)/1000;d=(e['y_mm']+e['width_mm']/2)/1000
        if d<=y0 or c>=y1:continue  # Equipment on another platform at this level.
        if not x0<=a<b<=x1 or not y0<=c<d<=y1:
            raise ValueError('equipment footprint extends outside platform support envelope')
        if a<b and c<d:rectangles.append((a,b,c,d))
    cuts=sorted({x0,x1,*(a for a,b,c,d in rectangles),*(b for a,b,c,d in rectangles)})
    occupied=0;minimum_gap=y1-y0
    for a,b in zip(cuts,cuts[1:]):
        segments=sorted((c,d) for left,right,c,d in rectangles if left<(a+b)/2<right)
        merged=[]
        for c,d in segments:
            if merged and c<=merged[-1][1]:merged[-1][1]=max(d,merged[-1][1])
            else:merged.append([c,d])
        occupied+=(b-a)*sum(d-c for c,d in merged)
        edges=[y0,*[v for pair in merged for v in pair],y1]
        gaps=[edges[i+1]-edges[i] for i in range(0,len(edges)-1,2)]
        minimum_gap=min(minimum_gap,max(gaps,default=0))
    gross=length_m*(y1-y0)
    return dict(gross_platform_area_m2=gross,equipment_union_area_m2=occupied,unoccupied_envelope_area_m2=gross-occupied,
        narrowest_largest_contiguous_lane_m=minimum_gap,
        continuous_longitudinal_clear_width_m=continuous_clear_width((x0,x1,y0,y1),rectangles),
        basis='contained footprint union and connected longitudinal clearance; site obstacles, entrance routes and crowd dynamics remain separate')


def station_capacity_screen(station,length_m,criteria=None):
    criteria=criteria or {};layout=station['layout'];demand=station.get('passenger_demand',{})
    platforms=[]
    for platform in layout['platforms']:
        area=footprint_screen(platform,length_m,layout['equipment'])
        waiting=criteria.get('waiting_pax_by_platform',{}).get(platform['id'])
        if waiting is None and len(layout['platforms'])==1:waiting=demand.get('peak_waiting_accumulation_pax')
        rate=criteria.get('pedestrian_flow_pax_per_m_min')
        if rate is not None and (not math.isfinite(rate) or rate<=0):raise ValueError('positive sourced circulation rate required')
        density=waiting/area['unoccupied_envelope_area_m2'] if waiting is not None and area['unoccupied_envelope_area_m2']>0 else None
        platforms.append(dict(platform_id=platform['id'],**area,waiting_pax=waiting,waiting_density_pax_m2=density,
            circulation_capacity_pax_hour=area['continuous_longitudinal_clear_width_m']*rate*60 if rate is not None else None,
            crowding_criterion_pax_m2=criteria.get('crowding_criterion_pax_m2'),criteria_accepted=False))
    lift_ids=[e['id'] for e in layout['equipment'] if e['kind']=='lift']
    capacities=criteria.get('lift_capacity_pax_hour',{})
    if any(k not in lift_ids or not math.isfinite(v) or v<=0 for k,v in capacities.items()):
        raise ValueError('lift throughput must identify actual layout lifts with positive sourced rates')
    outages=[dict(unavailable_lift=k,remaining_station_lift_capacity_pax_hour=sum(capacities[j] for j in lift_ids if j!=k)
        if all(j in capacities for j in lift_ids) else None,capacity_acceptance=False) for k in lift_ids]
    return dict(station=station['id'],platforms=platforms,one_lift_out_cases=outages,
        measured_criteria_source=criteria.get('source_record'),passenger_demand_complete=demand.get('demand_coverage_complete',False),
        evacuation_seconds=None,assisted_rescue_accepted=False,street_crossings_accepted=False,
        accessible_entrance_walkshed_population=None,station_structure_and_launcher_passage_accepted=False,
        engineering_qualified=False)
