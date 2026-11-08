"""Counted, C3 station track spreading inside explicitly reserved straights.

This is a horizontal track and platform interface. It grants no capacity to the
running-span bearings, widened pier caps, station floors or turnouts. The parent
alignment must already contain the entire spread; this module cannot straighten
a curved route by relabelling it or silently extend an authority.
"""
from copy import deepcopy
from math import fsum, hypot, isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from .civil import sealed, source_union
from .route import FLAGS

PRODUCER='engineering/railway_project/station_tracks.py'


def transition(u, length, delta):
    """Septic smoothstep and derivatives with respect to longitudinal metres."""
    y=delta*(35*u**4-84*u**5+70*u**6-20*u**7)
    first=delta*(140*u**3-420*u**4+420*u**5-140*u**6)/length
    second=delta*(420*u**2-1680*u**3+2100*u**4-840*u**5)/length**2
    third=delta*(840*u-5040*u**2+8400*u**3-4200*u**4)/length**3
    return y,first,second,third


def metrics(length, delta, subdivisions):
    rows=[]
    for i in range(subdivisions+1):
        y,dy,ddy,dddy=transition(i/subdivisions,length,delta)
        speed=hypot(1.,dy)
        curvature=ddy/speed**3
        derivative=dddy/speed**4-3*dy*ddy**2/speed**6
        rows.append((speed,abs(curvature),abs(derivative)))
    integrated=length*fsum(r[0]*(1 if i in (0,subdivisions) else 4 if i%2 else 2)
                           for i,r in enumerate(rows))/(3*subdivisions)
    return dict(length_m=integrated,maximum_curvature_per_m=max(r[1] for r in rows),
                maximum_curvature_derivative_per_m2=max(r[2] for r in rows))


def generate(alignment, station, *, running_track_centres_y_m, transition_length_m,
             lateral_sway_bound_m, requested_speed_m_s, longitudinal_acceleration_bound_m_s2,
             lateral_acceleration_target_m_s2, lateral_jerk_target_m_s3, root=ROOT):
    """Two symmetric tracks, preserved physical +Y boarding and no turnouts.

    Every intermediate station has two transitions per track; a terminal has
    one. The modeled corridor includes the two terminal half-platforms, counted
    once. A common civil standard span is not claimed to support this spread.
    """
    sealed(alignment);sealed(station)
    if (alignment.get('schema')!='osr-station-straight-alignment/1' or
        station.get('schema')!='osr-project-station-interfaces/1' or
        station['alignment_candidate_id']!=alignment['candidate_id'] or
        station['alignment_evaluation_id']!=alignment['evaluation_id'] or
        any(v['candidate_id']!=identity(v['physical_definition']) for v in (alignment,station))):
        raise ValueError('Exact same-alignment station interfaces required')
    inputs=dict(transition_length_m=transition_length_m,lateral_sway_bound_m=lateral_sway_bound_m,
        requested_speed_m_s=requested_speed_m_s,longitudinal_acceleration_bound_m_s2=longitudinal_acceleration_bound_m_s2,
        lateral_acceleration_target_m_s2=lateral_acceleration_target_m_s2,lateral_jerk_target_m_s3=lateral_jerk_target_m_s3)
    if any(type(v) not in (int,float) or not isfinite(v) or v<=0 for v in inputs.values()):
        raise ValueError('Explicit positive track geometry and performance inputs required')
    centres=running_track_centres_y_m;wide=station['physical_definition']['track_centres_y_m']
    if (not isinstance(centres,list) or len(centres)!=2 or
        any(type(v) not in (int,float) or not isfinite(v) for v in centres+wide) or
        not centres[0]<0<centres[1] or abs(centres[0]+centres[1])>1e-12 or
        abs(wide[0]+wide[1])>1e-12 or wide[1]<=centres[1]):
        raise ValueError('Explicit symmetric running and wider station track centres required')
    p=station['physical_definition'];sites=p['stations'];n=len(sites)
    if n<2 or [s['id'] for s in sites]!=[s['id'] for s in alignment['physical_definition']['stations']]:
        raise ValueError('All retained station identities required')
    length=sites[0]['boarding_faces'][0]['platform_polygon_local_xy_m'][1][0]*2
    if any(abs(f['platform_polygon_local_xy_m'][1][0]*2-length)>1e-9
           for s in sites for f in s['boarding_faces']):
        raise ValueError('Common explicit boarding length required by this track family')
    if length+2*transition_length_m>alignment['physical_definition']['platform_straight_m']+1e-9:
        raise ValueError('Actual parent straight does not contain boarding and both transitions')
    width=p['train_width_m'];gap=p['nominal_boarding_gap_m']
    clearance=(wide[1]-wide[0])-width-p['platform_width_m']-2*gap-2*lateral_sway_bound_m
    running_clearance=centres[1]-centres[0]-width-2*lateral_sway_bound_m
    if min(clearance,running_clearance)<0:
        raise ValueError('Declared swept train envelopes conflict at running track or inner platform')
    delta=wide[1]-centres[1]
    coarse=metrics(transition_length_m,delta,128);fine=metrics(transition_length_m,delta,256)
    spread=[]
    half=length/2
    for i,site in enumerate(sites):
        c=site['chainage_m']
        for side in (-1,1):
            if (i==0 and side==-1) or (i==n-1 and side==1):continue
            start=c+side*(half+transition_length_m);end=c+side*half
            spread.append(dict(station_id=site['id'],start_chainage_m=min(start,end),end_chainage_m=max(start,end),
                direction='widening' if side==-1 else 'narrowing',
                track_lateral_polynomials=[dict(track=j,start_y_m=centres[j] if side==-1 else wide[j],
                    end_y_m=wide[j] if side==-1 else centres[j],degree=7,
                    basis='35u^4-84u^5+70u^6-20u^7') for j in range(2)]))
    for left,right in zip(sorted(spread,key=lambda r:r['start_chainage_m']),sorted(spread,key=lambda r:r['start_chainage_m'])[1:]):
        if left['end_chainage_m']>right['start_chainage_m']+1e-9:
            raise ValueError('Station track transitions overlap')
    physical=dict(schema='osr-station-track-spread-geometry/1',alignment_candidate_id=alignment['candidate_id'],
        station_geometry_candidate_id=station['candidate_id'],running_track_centres_y_m=deepcopy(centres),
        station_track_centres_y_m=deepcopy(wide),boarding_length_m=length,transition_length_m=transition_length_m,
        modeled_chainage_domain_m=[-half,alignment['route_m']+half],transitions=spread,
        platforms=deepcopy(sites),turnouts=[],turnback_definition_complete=False)
    extra_per_track_transition=fine['length_m']-transition_length_m
    total_track=2*(alignment['route_m']+length)+2*len(spread)*extra_per_track_transition
    k=fine['maximum_curvature_per_m'];dk=fine['maximum_curvature_derivative_per_m2']
    a=requested_speed_m_s**2*k
    jerk=requested_speed_m_s**3*dk+2*requested_speed_m_s*longitudinal_acceleration_bound_m_s2*k
    checks=dict(parent_alignment_screen=alignment['calculated_alignment_screen_passed'],
        sampled_spread_acceleration=a<=lateral_acceleration_target_m_s2,
        sampled_spread_jerk=jerk<=lateral_jerk_target_m_s3,
        transition_length_refinement=abs(fine['length_m']-coarse['length_m'])<.001)
    result=dict(schema='osr-station-track-spread-evaluation/1',candidate_id=identity(physical),physical_definition=physical,
        alignment_candidate_id=alignment['candidate_id'],alignment_evaluation_id=alignment['evaluation_id'],
        station_candidate_id=station['candidate_id'],station_evaluation_id=station['evaluation_id'],requirements=inputs,
        quantities=dict(transition_pairs=len(spread),individual_track_transitions=2*len(spread),
            station_plateau_track_m=2*n*length,terminal_extension_track_m=2*length,
            spread_additional_track_m=2*len(spread)*extra_per_track_transition,
            total_track_m=total_track,total_rail_m=2*total_track),
        numerical=dict(**fine,length_refinement_residual_m=abs(fine['length_m']-coarse['length_m']),
            swept_inner_platform_clearance_m=clearance,swept_running_train_clearance_m=running_clearance,
            lateral_acceleration_m_s2=a,lateral_jerk_upper_estimate_m_s3=jerk,interval_enclosure_verified=False),
        checks=checks,calculated_horizontal_screen_passed=all(checks.values()),installed_station_complete=False,
        holds=['Track widening changes bearing spacing, transverse caps, pier torsion, foundations and station support quantities; running-span FEM is not inherited.',
            'Sampled horizontal geometry excludes cant, suspension dynamics, vehicle end sweep, vertical profiles and actual site obstacles.',
            'Terminal authority/overrun, crossovers and reversal routes require counted physical geometry before a service can be accepted.',
            'Platform supports, accessibility, gap bridging, guards, roofing, drainage, egress and electrical installation require their own parts and analyses.'],
        source_sha256=source_union(alignment,station,root=root),**FLAGS)
    result['source_sha256'][PRODUCER]=digest(Path(root)/PRODUCER)
    result['evaluation_id']=identity(result)
    return result
