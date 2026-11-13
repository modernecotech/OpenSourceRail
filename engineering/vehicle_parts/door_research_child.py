"""Small proposed two-pulley door-header family with distinct physical children.

The ideal belt pitch-length equation is a research hypothesis. A 5.8 m cut
length, pulley envelope and sampled route do not establish an installed belt,
shaft fit, tension, header mount or moving-door clearance.
"""
import argparse
import json
from math import cos, dist, fsum, isfinite, pi, sin
from pathlib import Path

from engineering.station_rail.common import digest, identity
from engineering.vehicle_parts import ROOT
from engineering.vehicle_parts import door_mating

PRODUCER='engineering/vehicle_parts/door_research_child.py'
_LOADED_SHA=digest(__file__)
SAMPLES_M=(.025,.03,.035)
HALF_WRAP_SEGMENTS=16


def _loop(x0,y0,z0,centres,radius):
    left=x0-centres/2;right=x0+centres/2
    point=lambda x,z:[x,y0,z]
    route=[point(left,z0+radius),point(right,z0+radius)]
    for i in range(1,HALF_WRAP_SEGMENTS+1):
        angle=pi/2-pi*i/HALF_WRAP_SEGMENTS
        route.append(point(right+radius*cos(angle),z0+radius*sin(angle)))
    route.append(point(left,z0-radius))
    for i in range(1,HALF_WRAP_SEGMENTS+1):
        angle=-pi/2-pi*i/HALF_WRAP_SEGMENTS
        route.append(point(left+radius*cos(angle),z0+radius*sin(angle)))
    route[-1]=route[0]
    return route


def _geometry(radius,centre_distance,request,parts):
    if type(radius) not in (float,int) or not isfinite(radius) or radius<=0:
        raise ValueError('Finite positive provisional pitch radius required')
    pulley_ids=('body/door-drive-pulley','body/door-idler-pulley')
    max_radius=min(min(parts[n]['stock']['size_m'][:2])/2 for n in pulley_ids)
    header_length=parts['body/door-header-backplate']['stock']['size_m'][0]
    guide_length=parts['body/door-guide-rail']['stock']['length_m']
    belt_cut=parts['body/door-belt']['stock']['length_m']
    assumes_pitch_equals_cut=centre_distance is None
    if centre_distance is None:
        centre_distance=(belt_cut-2*pi*radius)/2
    if type(centre_distance) not in (float,int) or not isfinite(centre_distance) or centre_distance<=0:
        raise ValueError('Finite positive proposed pulley centre distance required')
    controls=request['nominal_motion_control']
    bounds=dict(pulley_pitch_radius_m=radius,pulley_envelope_radius_upper_bound_m=max_radius,
        ideal_centre_distance_m=centre_distance,proposed_centre_distance_m=centre_distance,
        cut_equals_pitch_centre_distance_m=(belt_cut-2*pi*radius)/2,
        belt_stock_cut_length_m=belt_cut,
        ideal_belt_pitch_length_hypothesis_m=belt_cut if assumes_pitch_equals_cut else None,
        ideal_pitch_length_residual_m=2*centre_distance+2*pi*radius-belt_cut,
        proposed_ideal_pitch_path_length_m=2*centre_distance+2*pi*radius,
        projected_pulley_span_m=centre_distance+2*radius,
        header_span_arithmetic_margin_m=header_length-centre_distance-2*radius,
        counted_pulley_radius_arithmetic_margin_m=max_radius-radius,
        header_stock_length_m=header_length,guide_stock_length_m=guide_length,
        nominal_opening_plus_slides_m=controls['opening_plus_two_slides_m'],
        guide_motion_arithmetic_margin_m=guide_length-controls['opening_plus_two_slides_m'],
        guide_header_arithmetic_margin_m=header_length-guide_length,
        pitch_equals_cut_length_unverified=assumes_pitch_equals_cut,
        belt_cut_pitch_relationship_unverified=True)
    failures=[]
    if radius>max_radius:failures.append('Pitch radius exceeds counted pulley envelope')
    if centre_distance<=2*radius:failures.append('Proposed pitch circles overlap')
    if centre_distance+2*radius>header_length:failures.append('Ideal pulley span exceeds header stock length')
    if guide_length>header_length:failures.append('Full guide stock exceeds header stock length')
    if controls['opening_plus_two_slides_m']>guide_length:
        failures.append('Nominal opening and slides exceed full guide stock length')
    return bounds,failures


def evaluate_geometry(radius_m,centre_distance_m=None):
    """Screen a proposed radius and spacing, never an installed belt fit."""
    if digest(ROOT/PRODUCER)!=_LOADED_SHA:
        raise ValueError('Loaded door research child changed; restart caller')
    handoff,request,_,_=door_mating._current_inputs(ROOT)
    parts={p['part_id']:p for p in handoff['parts']}
    bounds,failures=_geometry(radius_m,centre_distance_m,request,parts)
    origin=[request['frame']['proposed_centre_x_m'],1.315,3.25]
    x0,y0,z0=origin;guide_length=bounds['guide_stock_length_m']
    centre_distance=bounds['ideal_centre_distance_m']
    definition=dict(schema='osr-v07-door-header-research-physical/1',
        parent_physical_candidate_id=request['physical_candidate_id'],
        parent_installed_candidate_id=request['installed_candidate_id'],
        opening=request['opening'],
        part_definitions={n:parts[n]['component_definition_id'] for n in sorted(parts)},
        parts_per_opening={n:parts[n]['quantity_per_opening'] for n in sorted(parts)},
        proposed_car_local_header_frame=dict(translation_m=origin,
            rotation_matrix=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]),
        guide=dict(stock_cut_length_m=guide_length,
            proposed_endpoints_car_m=[[x0-guide_length/2,y0,z0],[x0+guide_length/2,y0,z0]]),
        belt=dict(stock_cut_length_m=parts['body/door-belt']['stock']['length_m'],
            proposed_route_kind='two equal-radius pulleys, two straight tangents and two semicircular wraps',
            proposed_pitch_plane='car-local x-z',
            equal_pitch_radius_hypothesis_m=radius_m,
            proposed_centre_distance_m=centre_distance,
            drive_axis_origin_car_m=[x0-centre_distance/2,y0,z0],
            idler_axis_origin_car_m=[x0+centre_distance/2,y0,z0],
            axes_unit_car=[0.,1.,0.]))
    child_id=identity(definition)
    sources={**handoff['source_sha256'],
        'docs/design-engine/v07-execution/door-interface-handoff.json':digest(ROOT/'docs/design-engine/v07-execution/door-interface-handoff.json'),
        'docs/design-engine/v07-execution/door-route-request.json':digest(ROOT/'docs/design-engine/v07-execution/door-route-request.json'),
        'engineering/vehicle_parts/door_mating.py':digest(door_mating.__file__),
        PRODUCER:_LOADED_SHA}
    row=dict(schema='osr-v07-door-header-research-evaluation/1',
        physical_definition=definition,physical_candidate_id=child_id,
        parent_physical_candidate_id=request['physical_candidate_id'],
        parent_installed_candidate_id=request['installed_candidate_id'],
        parent_installed_evaluation_id=request['installed_evaluation_id'],
        source_route_request_id=request['request_id'],
        geometry_basis='Existing generic anchor y=1.315 m and header-local z=2.25 m above z=1 m; unaccepted placement',
        pitch_equals_cut_length_hypothesis=centre_distance_m is None,
        selection_id=None,source_sha256=sources,necessary_bounds=bounds,
        necessary_bound_failures=failures,disposition='infeasible-necessary-bound' if failures else 'held-research-geometry',
        sampled_belt_polyline_m=None,polyline_approximation_error_m=None,
        stock_cut_to_sampled_path_difference_m=None,
        parent_route_proposal=None,parent_mating_assessment_id=None,
        unresolved_inputs=['Belt cut length is not authenticated pitch length or rated tension range',
            'Actual header-to-body mount and guide/stop/carriage fit are unknown',
            'Drive/idler shafts, tooth count, wrap, torque and thermal duty are unknown',
            'Finite leaf, seal, harness, tool and removal sweeps are unverified',
            'No supplier, inspection or physical-test limits are authenticated'],
        candidate_adopted=False,parent_installed_child_relabelled=False,
        installed_geometry_verified=False,ready_for_native_assembly=False,
        engineering_accepted=False,physical_accepted=False,manufacturing_release=False)
    if not failures:
        path=_loop(x0,y0,z0,centre_distance,radius_m)
        axes=[dict(part_id=n,origin_car_m=[x0+sign*centre_distance/2,y0,z0],
                   axis_unit_car=[0.,1.,0.],pitch_radius_m=radius_m)
              for n,sign in (('body/door-drive-pulley',-1),('body/door-idler-pulley',1))]
        proposal=dict(schema='osr-v07-one-opening-route-proposal/1',
            request_id=request['request_id'],physical_candidate_id=request['physical_candidate_id'],
            installed_candidate_id=request['installed_candidate_id'],
            installed_evaluation_id=request['installed_evaluation_id'],opening=request['opening'],
            guide=dict(geometry='straight-full-guide',extent_m=guide_length,
                installed_start_m=definition['guide']['proposed_endpoints_car_m'][0],
                installed_end_m=definition['guide']['proposed_endpoints_car_m'][1],
                mounting_datums=None,removal_path=None),
            belt=dict(geometry='closed-loop',closed_pitch_path_m=path,
                pulley_axis_datums=axes,tensioner_range_m=None,removal_path=None),
            ready_for_native_assembly=False,installed_geometry_verified=False,
            manufacturing_release=False,engineering_accepted=False,physical_accepted=False)
        screen=door_mating.evaluate(proposal=proposal)
        polyline_length=fsum(dist(a,b) for a,b in zip(path,path[1:]))
        row.update(sampled_belt_polyline_m=polyline_length,
            polyline_approximation_error_m=bounds['proposed_ideal_pitch_path_length_m']-polyline_length,
            stock_cut_to_sampled_path_difference_m=bounds['belt_stock_cut_length_m']-polyline_length,
            parent_route_proposal=proposal,
            parent_mating_assessment_id=screen['assessment_id'],
            parent_route_intake_holds=screen['route_intake_holds'])
    row['evaluation_id']=identity(row)
    return row


def evaluate_radius(radius_m):
    """Preserve the original radius-only pitch-equals-cut hypothesis."""
    return evaluate_geometry(radius_m)


def evaluate_family(radii_m=SAMPLES_M):
    if (not isinstance(radii_m,(tuple,list)) or not 1<=len(radii_m)<=12
            or len(set(radii_m))!=len(radii_m)):
        raise ValueError('One to twelve distinct explicit radius samples required')
    rows=[evaluate_radius(r) for r in radii_m]
    family=dict(schema='osr-v07-door-header-research-family/1',
        parent_physical_candidate_id=rows[0]['parent_physical_candidate_id'],
        radius_samples_m=list(radii_m),rows=rows,selected_candidate_id=None,
        physical_accepted=False,engineering_accepted=False)
    family['family_id']=identity(family)
    return family


def evaluate_variations(radii_m=SAMPLES_M,centre_offsets_m=(-.02,0.,.02)):
    """Small bounded grid and provisional tradeoffs; no child is selected.

    Offsets shift pulley axes from the centre distance implied by treating the
    belt cut length as pitch length. That equality is unauthenticated, so its
    residual is a diagnostic axis rather than an engineering acceptance limit.
    """
    if (not isinstance(radii_m,(tuple,list)) or not isinstance(centre_offsets_m,(tuple,list))
            or not 1<=len(radii_m)<=12 or not 1<=len(centre_offsets_m)<=7
            or len(radii_m)*len(centre_offsets_m)>48
            or any(type(v) not in (float,int) or not isfinite(v) for v in (*radii_m,*centre_offsets_m))
            or len(set(radii_m))!=len(radii_m)
            or len(set(centre_offsets_m))!=len(centre_offsets_m)):
        raise ValueError('One to 48 distinct finite radius/centre-offset combinations required')
    rows=[]
    for radius in radii_m:
        base=evaluate_radius(radius)
        nominal=base['necessary_bounds']['ideal_centre_distance_m']
        for offset in centre_offsets_m:
            row=base if offset==0 else evaluate_geometry(radius,nominal+offset)
            rows.append(row)
    comparisons=[]
    for row in rows:
        bounds=row['necessary_bounds']
        comparisons.append(dict(physical_candidate_id=row['physical_candidate_id'],
            evaluation_id=row['evaluation_id'],disposition=row['disposition'],
            pulley_pitch_radius_m=bounds['pulley_pitch_radius_m'],
            centre_distance_m=bounds['proposed_centre_distance_m'],
            header_span_arithmetic_margin_m=bounds['header_span_arithmetic_margin_m'],
            counted_pulley_radius_arithmetic_margin_m=bounds['counted_pulley_radius_arithmetic_margin_m'],
            absolute_pitch_cut_residual_m=abs(bounds['ideal_pitch_length_residual_m']),
            necessary_bound_failures=row['necessary_bound_failures']))
    eligible=[r for r in comparisons if r['disposition']=='held-research-geometry']
    objectives=('header_span_arithmetic_margin_m',
                'counted_pulley_radius_arithmetic_margin_m')
    def dominates(a,b):
        better_or_equal=(all(a[k]>=b[k] for k in objectives)
                         and a['absolute_pitch_cut_residual_m']<=b['absolute_pitch_cut_residual_m'])
        strictly_better=(any(a[k]>b[k] for k in objectives)
                         or a['absolute_pitch_cut_residual_m']<b['absolute_pitch_cut_residual_m'])
        return better_or_equal and strictly_better
    frontier=[r['physical_candidate_id'] for r in eligible
              if not any(dominates(other,r) for other in eligible if other is not r)]
    family=dict(schema='osr-v07-door-header-variation-grid/1',
        parent_physical_candidate_id=rows[0]['parent_physical_candidate_id'],
        radius_samples_m=list(radii_m),centre_offsets_m=list(centre_offsets_m),
        rows=rows,comparison=comparisons,provisional_nondominated_physical_ids=frontier,
        comparison_basis='Three arithmetic proxies only: header span margin, counted pulley radius margin, and pitch-path versus cut-length residual; cut length is not authenticated pitch length',
        selected_candidate_id=None,selection_id=None,candidate_adopted=False,
        installed_geometry_verified=False,engineering_accepted=False,physical_accepted=False)
    family['family_id']=identity(family)
    return family


def _millimetres(value):
    try:
        result=tuple(float(part)/1000 for part in value.split(','))
    except ValueError as error:
        raise argparse.ArgumentTypeError('Comma-separated millimetres required') from error
    if not result or any(not isfinite(v) for v in result):
        raise argparse.ArgumentTypeError('Finite millimetres required')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--radii-mm',type=_millimetres,default=SAMPLES_M)
    parser.add_argument('--centre-offsets-mm',type=_millimetres,default=(-.02,0.,.02))
    args=parser.parse_args()
    family=evaluate_variations(args.radii_mm,args.centre_offsets_mm)
    print(json.dumps(dict(family_id=family['family_id'],
        evaluated_children=len(family['rows']),
        necessary_bound_failures=sum(bool(r['necessary_bound_failures']) for r in family['rows']),
        provisional_nondominated_physical_ids=family['provisional_nondominated_physical_ids'],
        comparison=family['comparison'],selected_candidate_id=None,
        engineering_accepted=False,physical_accepted=False),sort_keys=True))


if __name__=='__main__':main()
