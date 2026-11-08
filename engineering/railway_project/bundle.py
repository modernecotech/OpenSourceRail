"""One corridor/vehicle/civil/station identity, separate from evaluations."""
from copy import deepcopy
from math import isfinite
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,identity
from .civil import sealed,source_union
from .route import FLAGS

PRODUCER='engineering/railway_project/bundle.py'


def stations(body,alignment,*,platform_width_m,track_centres_y_m,nominal_boarding_gap_m,
             stopping_tolerance_m,root=ROOT):
    """Explicit one-sided boarding interfaces; no mirror-image train assumption.

    All formations keep the same physical+route orientation after reversal.
    Both boarding faces are therefore on physical+Y: one between the tracks,
    one outside. Two generic outside platforms would give the wrong door side.
    Access structures and bridge mechanisms remain separate detailed assemblies.
    """
    sealed(body);sealed(alignment)
    if (body.get('schema')!='osr-vehicle-installation/1' or alignment.get('schema')!='osr-station-straight-alignment/1'
        or body['candidate_id']!=identity(body['physical_definition']) or alignment['candidate_id']!=identity(alignment['physical_definition'])):
        raise ValueError('Exact installed body and designed alignment required')
    layout=body['policy']['layout'];lift=body['compact_drive_contract']['body_lift_m']
    for v in (platform_width_m,nominal_boarding_gap_m,stopping_tolerance_m):
        if type(v) not in (int,float) or not isfinite(v) or v<=0:
            raise ValueError('Explicit positive station interface dimensions required')
    if (not isinstance(track_centres_y_m,list) or len(track_centres_y_m)!=2 or
        any(type(v) not in (int,float) or not isfinite(v) for v in track_centres_y_m) or
        track_centres_y_m[1]<=track_centres_y_m[0]):
        raise ValueError('Two ordered explicit track centres required')
    length=layout['cars']*layout['car_length_m']+(layout['cars']-1)*layout['intercar_gap_m']
    p=alignment['physical_definition']['platform_straight_m']
    if p<length+2*stopping_tolerance_m or abs(alignment['requirements']['train_length_m']-length)>1e-9:
        raise ValueError('Same formation must fit declared straight platform with stop tolerance')
    width=layout['car_width_m'];spacing=track_centres_y_m[1]-track_centres_y_m[0]
    if spacing<width+platform_width_m+2*nominal_boarding_gap_m:
        raise ValueError('One-sided inner platform conflicts with the other track vehicle envelope')
    door_x=[-length/2+layout['car_length_m']/2+i*(layout['car_length_m']+layout['intercar_gap_m'])+x
            for i in range(layout['cars']) for x in layout['door_centres_local_x_m']]
    if any(abs(x)+layout['door_clear_width_m']/2+stopping_tolerance_m>p/2 for x in door_x):
        raise ValueError('Door opening falls outside declared platform')
    sites=[]
    for stop in alignment['physical_definition']['stations']:
        faces=[]
        for i,y in enumerate(track_centres_y_m):
            near=y+width/2+nominal_boarding_gap_m
            faces.append(dict(track=i,boarding_side_body_y='+Y',vehicle_body_orientation='+route in both travel directions',
                platform_polygon_local_xy_m=[[-p/2,near],[p/2,near],[p/2,near+platform_width_m],[-p/2,near+platform_width_m]],
                nominal_platform_top_above_rail_m=layout['floor_top_m']+lift,
                door_landing_centres_local_xy_m=[[x,near] for x in door_x],door_clear_width_m=layout['door_clear_width_m']))
        sites.append(dict(id=stop['id'],longitude=stop['longitude'],latitude=stop['latitude'],
            chainage_m=stop['chainage_m'],tangent_xy=deepcopy(stop['tangent_xy']),boarding_faces=faces))
    physical=dict(schema='osr-project-station-geometry/1',alignment_candidate_id=alignment['candidate_id'],
        train_length_m=length,train_width_m=width,track_centres_y_m=deepcopy(track_centres_y_m),
        platform_width_m=platform_width_m,nominal_boarding_gap_m=nominal_boarding_gap_m,
        stations=sites,terminal_platform_extensions_m=dict(before_first=p/2,after_last=p/2))
    result=dict(schema='osr-project-station-interfaces/1',candidate_id=identity(physical),physical_definition=physical,
        body_candidate_id=body['candidate_id'],body_evaluation_id=body['evaluation_id'],
        alignment_candidate_id=alignment['candidate_id'],alignment_evaluation_id=alignment['evaluation_id'],
        stopping_tolerance_m=stopping_tolerance_m,
        quantities=dict(stations=len(sites),boarding_faces=2*len(sites),
            door_landing_interfaces=2*len(sites)*len(door_x),platform_floor_area_m2=2*len(sites)*p*platform_width_m,
            beyond_terminal_centre_main_track_m=2*p),
        interface_definition_complete=True,installed_station_assembly_complete=False,
        holds=['Footprints and nominal floor level are defined; sway, suspension travel and gap bridging require dynamic/accessibility checks.',
            'One-sided door orientation requires compatible bidirectional controls and turnback/point geometry; no reflected train or unused-side door is assumed.',
            'Platform supports, access/egress, lifts, evacuation, guards, bridge plates and terminal/crossover equipment need detailed parts and analysis.',
            'Terminal platform track is outside station-centre route length and must be counted once in civil, rails, power and construction.'],
        source_sha256=source_union(body,alignment,root=root),**FLAGS)
    result['source_sha256'][PRODUCER]=digest(Path(root)/PRODUCER)
    result['evaluation_id']=identity(result)
    return result


def combine(body,alignment,civil,station,*,root=ROOT):
    """Bind actual physical revisions; service/price/proof are evaluation context."""
    expected=('osr-vehicle-installation/1','osr-station-straight-alignment/1',
              'osr-project-civil-evaluation/1','osr-project-station-interfaces/1')
    for value,schema in zip((body,alignment,civil,station),expected):
        sealed(value)
        if value.get('schema')!=schema or value['candidate_id']!=identity(value['physical_definition']):
            raise ValueError('Physical component identity differs')
    if (civil['vehicle_candidate_id']!=body['candidate_id'] or civil['body_evaluation_id']!=body['evaluation_id'] or
        station['body_candidate_id']!=body['candidate_id'] or station['body_evaluation_id']!=body['evaluation_id']):
        raise ValueError('Civil/station belongs to a different body or mass revision')
    if any(v['alignment_candidate_id']!=alignment['candidate_id'] or v['alignment_evaluation_id']!=alignment['evaluation_id'] for v in (civil,station)):
        raise ValueError('Civil/station belongs to a different mapped alignment revision')
    track=body['policy']['track_interface'];declared=civil['physical_definition']['span_geometry']['track_interface']
    if any(declared[k]!=track[k] for k in declared) or civil['physical_definition']['track_centres_y_m']!=station['physical_definition']['track_centres_y_m']:
        raise ValueError('Vehicle, civil and station rail datums disagree')
    physical=dict(schema='osr-mapped-railway-project-physical/1',body_candidate_id=body['candidate_id'],
        alignment_candidate_id=alignment['candidate_id'],civil_layout_candidate_id=civil['candidate_id'],
        station_geometry_candidate_id=station['candidate_id'])
    result=dict(schema='osr-mapped-railway-project-bundle/1',candidate_id=identity(physical),physical_definition=physical,
        body_evaluation_id=body['evaluation_id'],alignment_evaluation_id=alignment['evaluation_id'],
        civil_evaluation_id=civil['evaluation_id'],station_evaluation_id=station['evaluation_id'],
        source_sha256=source_union(body,alignment,civil,station,root=root),
        purpose='Mapped integrated research candidate; no selected development-reference revision',
        installed_vehicle_complete=body['installed_mass_complete'] and body['layout_definition_complete'],
        installed_station_complete=station['installed_station_assembly_complete'],
        force_driven_project_replayed=False,complete_project_costed=False,**FLAGS)
    result['source_sha256'][PRODUCER]=digest(Path(root)/PRODUCER)
    result['evaluation_id']=identity(result)
    return result
