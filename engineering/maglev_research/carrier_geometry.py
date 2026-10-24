"""Finite-stock yaw carrier and curve research; no installed articulation credit.

Paired rows remain rigid on each carrier. A body can translate laterally as a
whole; yaw-only pivots cannot translate independently. The separate slide option
explicitly counts one lateral slide per carrier and reports its required travel.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT/'docs/design-engine/ferrite-maglev/research-closure'
RADII = (50.,75.,100.,150.,300.)
CARRIERS = (2,3,4,5)
TOLERANCES = (.001,.002)
FLAGS = dict(configuration_adopted=False, design_complete=False,
             physical_validation=False, manufacturing_release=False,
             physical_release=False, system_eligible=False)


def finite(value, name, positive=False):
    if type(value) not in (int,float) or not math.isfinite(value) or (positive and value<=0):
        raise ValueError('finite '+('positive ' if positive else '')+name+' required')
    return float(value)


def stock_bounds(parts):
    if not isinstance(parts,list) or not parts:
        raise ValueError('counted stock boxes required')
    lo = [math.inf]*3
    hi = [-math.inf]*3
    for part in parts:
        if len(part['at_m'])!=3 or len(part['size_m'])!=3:
            raise ValueError('three-dimensional stock boxes required')
        for axis in range(3):
            at = finite(part['at_m'][axis],'box origin')
            size = finite(part['size_m'][axis],'box size',True)
            lo[axis] = min(lo[axis],at)
            hi[axis] = max(hi[axis],at+size)
    return dict(minimum_m=lo,maximum_m=hi,size_m=[b-a for a,b in zip(lo,hi)])


def partitions(positions, count):
    """Balanced contiguous module assignments; at most two carrier lengths."""
    n = len(positions)
    if type(count) is not int or not 1<=count<=n:
        raise ValueError('bounded nonempty carriers required')
    small,extra = divmod(n,count)
    for longer in itertools.combinations(range(count),extra):
        sizes = [small+(index in longer) for index in range(count)]
        groups=[]
        first=0
        for size in sizes:
            groups.append(positions[first:first+size]);first+=size
        yield groups


def radial_error(u,v,shift,radius):
    """Exact radial mismatch to the concentric rail at transverse coordinate v."""
    base=radius-v
    distance=math.hypot(u,base-shift)
    return (u*u+shift*shift-2*shift*base)/(distance+base)


def extremes(group,bounds,rows,radius,shift):
    centre=sum(group)/len(group)
    intervals=[(x-centre+bounds['minimum_m'][0],x-centre+bounds['maximum_m'][0]) for x in group]
    umax=max(abs(x) for interval in intervals for x in interval)
    umin=0. if any(a<=0<=b for a,b in intervals) else min(abs(x) for interval in intervals for x in interval)
    vmin=min(rows)+bounds['minimum_m'][1]
    vmax=max(rows)+bounds['maximum_m'][1]
    if radius<=vmax or radius-shift-vmax<=0:
        raise ValueError('carrier stock extends beyond the bounded circular domain')
    # Radial error rises with |u| and v for the positive radii/short carriers here.
    return (radial_error(umin,vmin,shift,radius),radial_error(umax,vmax,shift,radius))


def recenter(group,bounds,rows,radius):
    lo=0.
    hi=max(abs(error) for error in extremes(group,bounds,rows,radius,0.))*2+.001
    for _ in range(70):
        middle=(lo+hi)/2
        low,high=extremes(group,bounds,rows,radius,middle)
        if low+high>0:lo=middle
        else:hi=middle
    return (lo+hi)/2


def pose(groups,bounds,rows,radius,mechanism):
    centres=[sum(group)/len(group) for group in groups]
    if mechanism=='yaw-and-lateral-slide':
        shifts=[recenter(group,bounds,rows,radius) for group in groups]
        heights=[]
        for x,shift in zip(centres,shifts):
            if abs(x)>=radius-shift:
                raise ValueError('body pivot outside circle')
            root=math.sqrt((radius-shift)**2-x*x)
            heights.append((2*radius*shift-shift*shift+x*x)/(radius+root))
        body=(min(heights)+max(heights))/2
    elif mechanism=='yaw-only-fixed-pivots':
        # Body heading is tangent at its centre, matching the symmetric route
        # study. Optimise its one common lateral translation, never free pivots.
        lo,hi=-radius/4,radius/4
        for _ in range(70):
            body=(lo+hi)/2
            shifts=[radius-math.hypot(x,radius-body) for x in centres]
            errors=[extremes(group,bounds,rows,radius,shift) for group,shift in zip(groups,shifts)]
            if min(low for low,high in errors)+max(high for low,high in errors)>0:lo=body
            else:hi=body
        body=(lo+hi)/2
        heights=[body]*len(groups)
        shifts=[radius-math.hypot(x,radius-body) for x in centres]
    else:
        raise ValueError('explicit yaw-only or yaw/slide mechanism required')
    result=[]
    for group,x,height,shift in zip(groups,centres,heights,shifts):
        angle=math.atan2(x,radius-height)
        low,high=extremes(group,bounds,rows,radius,shift)
        result.append(dict(module_centres_body_x_m=group,pivot_body_x_m=x,
            pivot_body_y_m=height-body,normal_recentring_m=shift,yaw_rad=angle,
            radial_error_min_m=low,radial_error_max_m=high,
            modules_per_side=len(group),
            finite_longitudinal_stock_span_m=max(group)-min(group)+bounds['size_m'][0]))
    return body,result


def corners(x,y,angle,bounds,inflate=0.):
    lo,hi=bounds['minimum_m'],bounds['maximum_m']
    c,s=math.cos(angle),math.sin(angle)
    return [(x+c*u-s*v,y+s*u+c*v) for u,v in
            ((lo[0]-inflate,lo[1]-inflate),(hi[0]+inflate,lo[1]-inflate),
             (hi[0]+inflate,hi[1]+inflate),(lo[0]-inflate,hi[1]+inflate))]


def overlap(first,second):
    for polygon in (first,second):
        for edge in (0,1):
            dx=polygon[edge+1][0]-polygon[edge][0]
            dy=polygon[edge+1][1]-polygon[edge][1]
            axis=(-dy,dx)
            a=[x*axis[0]+y*axis[1] for x,y in first]
            b=[x*axis[0]+y*axis[1] for x,y in second]
            if max(a)<=min(b) or max(b)<=min(a):return False
    return True


def _distance(point,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    t=max(0.,min(1.,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return math.hypot(point[0]-a[0]-t*dx,point[1]-a[1]-t*dy)


def clearance(polygons):
    minimum=math.inf
    collisions=0
    boxes=[(min(x for x,y in p),max(x for x,y in p),min(y for x,y in p),max(y for x,y in p)) for p in polygons]
    for i,first in enumerate(polygons):
        for j in range(i+1,len(polygons)):
            second=polygons[j]
            a,b=boxes[i],boxes[j]
            lower=math.hypot(max(0.,a[0]-b[1],b[0]-a[1]),max(0.,a[2]-b[3],b[2]-a[3]))
            if lower>minimum:continue
            if overlap(first,second):
                collisions+=1;minimum=0.;continue
            distance=min(_distance(point,poly[edge],poly[(edge+1)%4])
                for points,poly in ((first,second),(second,first)) for point in points for edge in range(4))
            minimum=min(minimum,distance)
    return minimum,collisions


def evaluate(layout,groups,radius,tolerance,mechanism,*,nominal=.008,minimum=.002,maximum=.03):
    radius=finite(radius,'radius',True)
    tolerance=finite(tolerance,'tolerance',True)
    if not 0<minimum<nominal<maximum or tolerance>=min(nominal-minimum,maximum-nominal):
        raise ValueError('tolerance must leave a positive physical gap allowance')
    bounds=layout['stock_bounds']
    rows=layout['row_centres_y_m']
    expected=layout['module_centres_x_m']
    if (not groups or any(not group for group in groups) or
            sorted(x for group in groups for x in group)!=sorted(expected) or
            len(set(expected))!=len(expected) or len(set(rows))!=len(rows) or
            layout['module_count']!=len(expected)*len(rows)):
        raise ValueError('carriers must cover every declared finite module exactly once')
    body,carriers=pose(groups,bounds,rows,radius,mechanism)
    polygons=[]
    inflated=[]
    for carrier in carriers:
        angle=carrier['yaw_rad'];c,s=math.cos(angle),math.sin(angle)
        for module_x in carrier['module_centres_body_x_m']:
            u=module_x-carrier['pivot_body_x_m']
            for row in rows:
                x=carrier['pivot_body_x_m']+c*u-s*row
                y=carrier['pivot_body_y_m']+s*u+c*row
                polygons.append(corners(x,y,angle,bounds))
                inflated.append(corners(x,y,angle,bounds,tolerance))
    nominal_clear,nominal_collisions=clearance(polygons)
    _,tolerance_collisions=clearance(inflated)
    lower=min(carrier['radial_error_min_m'] for carrier in carriers)
    upper=max(carrier['radial_error_max_m'] for carrier in carriers)
    maxerror=max(abs(lower),abs(upper))
    gap=min(nominal-minimum,maximum-nominal)
    xmin=min(x for p in inflated for x,y in p);xmax=max(x for p in inflated for x,y in p)
    ymin=min(y for p in inflated for x,y in p);ymax=max(y for p in inflated for x,y in p)
    minimum_slide_pose_width=2*max(abs(ymin),abs(ymax))
    # One body translation is a real pose choice. If independent slides are
    # already counted, choose the smallest additional translation needed to fit
    # the declared underbody width; retain the extra stroke this consumes.
    package_shift=0.
    target_width=layout['proposed_underbody_clearance_width_m']
    if mechanism=='yaw-and-lateral-slide' and ymax-ymin<=target_width:
        low_shift,high_shift=ymax-target_width/2,ymin+target_width/2
        package_shift=max(low_shift,min(high_shift,0.))
        body+=package_shift
        ymin-=package_shift;ymax-=package_shift
        for carrier in carriers:carrier['pivot_body_y_m']-=package_shift
    bodyfit=max(abs(xmin),abs(xmax))<=layout['body_length_m']/2-layout['body_end_clearance_m']
    width_required=2*max(abs(ymin),abs(ymax))
    gap_pass=maxerror+tolerance<=gap+1e-12
    passing=gap_pass and tolerance_collisions==0 and bodyfit and width_required<=target_width
    return dict(layout=layout['id'],modules_per_car=layout['module_count'],carrier_count=len(groups),
        modules_per_side_by_carrier=[len(group) for group in groups],radius_m=radius,
        mechanism=mechanism,tolerance_reserve_m=tolerance,
        body_lateral_offset_m=body,carrier_poses=carriers,
        minimum_slide_pose_required_underbody_width_m=minimum_slide_pose_width,
        additional_body_translation_for_package_m=package_shift,
        peak_carrier_yaw_deg=max(abs(carrier['yaw_rad']) for carrier in carriers)*180/math.pi,
        required_one_sided_lateral_slide_travel_m=max(abs(carrier['pivot_body_y_m']) for carrier in carriers),
        maximum_finite_stock_radial_mismatch_m=maxerror,
        robust_minimum_gap_m=nominal-maxerror-tolerance,
        robust_maximum_gap_m=nominal+maxerror+tolerance,
        finite_gap_screen_pass=gap_pass,
        minimum_nominal_module_to_module_clearance_m=nominal_clear,
        nominal_module_collisions=nominal_collisions,tolerance_inflated_module_collisions=tolerance_collisions,
        modules_clear_with_tolerance=tolerance_collisions==0,
        stock_body_length_screen_pass=bodyfit,
        reserved_body_end_clearance_m=layout['body_end_clearance_m'],
        required_centred_underbody_width_m=width_required,
        current_body_width_m=layout['current_body_width_m'],
        current_body_width_screen_pass=width_required<=layout['current_body_width_m'],
        proposed_underbody_clearance_width_m=target_width,
        proposed_underbody_width_screen_pass=width_required<=target_width,
        yaw_joints_per_car=len(groups),lateral_slides_per_car=len(groups) if mechanism=='yaw-and-lateral-slide' else 0,
        joint_added_mass_kg=None,joint_installed_fit_verified=False,
        cooler_and_separate_guidance_installed_fit_verified=False,
        conditional_stock_geometry_screen_pass=passing,**FLAGS)


def study(root=ROOT):
    root=Path(root).resolve()
    from engineering.ferrite_maglev import candidate_magnetics
    from . import support_architecture
    candidate=candidate_magnetics.definition()
    support=support_architecture.study(root)
    if support['parent_configuration_sha256']!=candidate['configuration_sha256']:
        raise ValueError('support and carrier parent configurations differ')
    paths={*candidate['source_sha256'],
        'engineering/maglev_research/carrier_geometry.py',
        'engineering/maglev_research/support_architecture.py',
        'docs/design-engine/ferrite-maglev/research-closure/support-architecture.json'}
    source_snapshot={name:(root/name).read_bytes() for name in sorted(paths)}
    current=stock_bounds(candidate['module']['parts'])
    proposed=dict(minimum_m=[-.48,current['minimum_m'][1],current['minimum_m'][2]],
                  maximum_m=[.48,current['maximum_m'][1],current['maximum_m'][2]],
                  size_m=[.96,current['size_m'][1],current['size_m'][2]])
    # The frozen wide-stock extension is a96cm cover; current y/z stock limits
    # still dominate. No unpositioned cooler or separate-guidance envelope added.
    proposed_rows=[row for row in support['cases'] if row['hypothesis']['modules_per_car']==30]
    if not proposed_rows or any(not math.isclose(row['module_longitudinal_envelope_m'],.96,abs_tol=1e-12) for row in proposed_rows):
        raise ValueError('exact frozen96cm thirty-module stock envelope required')
    positions=sorted({position[0] for position in candidate['module_placements_m']})
    rows=sorted({position[1] for position in candidate['module_placements_m']})
    base=dict(body_length_m=17.,body_end_clearance_m=.5,current_body_width_m=2.65,
              proposed_underbody_clearance_width_m=3.,row_centres_y_m=rows)
    layouts=[dict(id='canonical24-stock',module_count=24,stock_bounds=current,module_centres_x_m=positions,**base),
        dict(id='proposed30-wide-stock',module_count=30,stock_bounds=proposed,
             module_centres_x_m=[(index-7)*1.01 for index in range(15)],**base)]
    a=tomllib.loads((root/'engineering/ferrite_maglev/candidate-magnetics.toml').read_text())
    cases=[]
    for layout,count,radius,tolerance,mechanism in itertools.product(layouts,CARRIERS,RADII,TOLERANCES,
            ('yaw-only-fixed-pivots','yaw-and-lateral-slide')):
        alternatives=[evaluate(layout,groups,radius,tolerance,mechanism,
            nominal=a['nominal_gap_m'],minimum=a['minimum_gap_m'],maximum=a['maximum_gap_m'])
            for groups in partitions(layout['module_centres_x_m'],count)]
        best=min(alternatives,key=lambda row:(not row['conditional_stock_geometry_screen_pass'],
            row['maximum_finite_stock_radial_mismatch_m'],row['required_centred_underbody_width_m'],
            row['required_one_sided_lateral_slide_travel_m'],row['modules_per_side_by_carrier']))
        best['balanced_partitions_evaluated']=len(alternatives)
        cases.append(best)
    recommendations=[]
    for layout,tolerance,radius in itertools.product(layouts,TOLERANCES,RADII):
        fitting=[row for row in cases if row['layout']==layout['id'] and row['tolerance_reserve_m']==tolerance
                 and row['radius_m']==radius and row['conditional_stock_geometry_screen_pass']]
        best=min(fitting,key=lambda row:(row['carrier_count'],row['lateral_slides_per_car'],row['required_one_sided_lateral_slide_travel_m'])) if fitting else None
        recommendations.append(dict(layout=layout['id'],radius_m=radius,tolerance_reserve_m=tolerance,
            least_carrier_count=best['carrier_count'] if best else None,
            mechanism=best['mechanism'] if best else None,
            yaw_joints_per_car=best['yaw_joints_per_car'] if best else None,
            lateral_slides_per_car=best['lateral_slides_per_car'] if best else None,
            required_one_sided_lateral_slide_travel_m=best['required_one_sided_lateral_slide_travel_m'] if best else None,
            required_centred_underbody_width_m=best['required_centred_underbody_width_m'] if best else None,
            stock_geometry_candidate=best is not None,system_eligible=False))
    if any((root/name).read_bytes()!=raw for name,raw in source_snapshot.items()):
        raise ValueError('carrier geometry sources changed during execution')
    return dict(schema='osr-finite-carrier-geometry-research/1',parent_configuration_sha256=candidate['configuration_sha256'],
        source_sha256={name:sha256(raw).hexdigest() for name,raw in source_snapshot.items()},
        source_unchanged_during_execution=True,
        assumptions=dict(nominal_gap_m=a['nominal_gap_m'],minimum_gap_m=a['minimum_gap_m'],maximum_gap_m=a['maximum_gap_m'],
            tolerance_reserves_m=list(TOLERANCES),carrier_counts=list(CARRIERS),curve_radii_m=list(RADII),
            body_heading='Tangent at body centre; global body lateral translation minimised, no independently floating yaw-only pivots.',
            stock_screen='Every point of the full finite stock box is conservatively required to remain in the radial gap envelope. This is stricter than a point-pole screen; a fitted spatial map still requires exact active pole faces.',
            underbody_width='3.0m is a revised package-clearance target, compared with current2.65m body width; it is not an approved city structure/clearance.',
            missing_installed_parts=['yaw bearings/frames/retention and lateral-slide guides/stops','newcooler/fan/pump andhoses','separateguidanceUcores','capture/brake articulation','wiring/insulation andfloor/guidewayclearance']),
        layouts=layouts,executed_geometry_cases=len(cases),cases=cases,
        recommendations=recommendations,
        yaw_only_geometry_survivors=sum(row['conditional_stock_geometry_screen_pass'] for row in cases if row['mechanism']=='yaw-only-fixed-pivots'),
        slide_geometry_survivors=sum(row['conditional_stock_geometry_screen_pass'] for row in cases if row['mechanism']=='yaw-and-lateral-slide'),
        complete_installed_carrier_fit=False,dynamics_rerun_ready=False,
        next_design='Compare150m terminal curves with counted four/five-carrier yaw/slide mechanisms and a3.0m underbody clearance target. Recount joints, coolers and separate guidance before force/control/route adoption.',
        **FLAGS)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUTPUT/'carrier-geometry.json')
    args=parser.parse_args()
    value=study()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps({key:value[key] for key in ('executed_geometry_cases','yaw_only_geometry_survivors','slide_geometry_survivors','dynamics_rerun_ready')}))


if __name__=='__main__':
    main()
