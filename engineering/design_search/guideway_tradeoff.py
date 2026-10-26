"""Counted concrete/steel alternatives around the selected onboard PM geometry.

This is a bounded necessary-screen study, not a replacement force map, civil
approval or price quotation. Thin faces never inherit the 35 mm coupon force.
"""
from copy import deepcopy
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import json
import math
import tomllib

ROOT=Path(__file__).resolve().parents[2]
CODE='engineering/design_search/guideway_tradeoff.py'
SELECTOR='engineering/development-baseline.toml'
MAGNETS='docs/design-engine/halbach-scaling/comparison.json'
FINITE='docs/design-engine/halbach-scaling/finite.json'
MU0=4*math.pi*1e-7
G=9.80665
RHO_STEEL=7850.
RHO_CONCRETE=2500.
E_STEEL=200e9
E_CONCRETE=30e9
FLAGS=dict(configuration_adopted=False,engineering_accepted=False,physical_accepted=False,
           installed_mass_complete=False,manufacturing_release=False,operating_release=False)


def encoded(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def identity(value):return sha256(encoded(value)).hexdigest()
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()


def positive(value,name):
    if type(value) not in (int,float) or not math.isfinite(value) or value<=0:
        raise ValueError('finite positive '+name+' required')
    return float(value)


def maxwell_bounds(force_N,active_area_m2,length_m,field_cap_T=1.6):
    """Conditional necessary bounds, not a uniform-field force prediction.

    Fz <= integral(Bn^2)/(2mu0) <= Bcap*integral(abs(Bn))/(2mu0).
    A closed two-lobe circuit has equal positive/negative flux, so each lobe
    needs at least mu0*Fz/Bcap. If one steel return section closes that flux,
    Bsteel<=Bcap implies t>=mu0*Fz/(Bcap^2*length). Leakage/end returns and
    different topologies invalidate that last premise; a full FEM must resolve it.
    """
    force_N=positive(force_N,'force');area=positive(active_area_m2,'area')
    length=positive(length_m,'length');cap=positive(field_cap_T,'field cap')
    return dict(force_N=force_N,working_area_m2=area,declared_field_cap_T=cap,
        maximum_ideal_normal_stress_N_m2=cap**2/(2*MU0),
        minimum_effective_working_area_m2=2*MU0*force_N/cap**2,
        required_RMS_normal_field_T=math.sqrt(2*MU0*force_N/area),
        minimum_absolute_normal_flux_Wb=2*MU0*force_N/cap,
        closed_two_lobe_minimum_return_flux_Wb=MU0*force_N/cap,
        conditional_one_section_minimum_thickness_m=MU0*force_N/(cap**2*length),
        assumptions=['No current/force credit; Maxwell stress necessary inequality only',
            'Declared field cap applies to both working normal field and steel return',
            'Two equal lobes close through one thickness x module-length steel section',
            'End, leakage and neighbouring steel paths unresolved; topology premise must be checked'],
        field_cap_is_a_qualified_material_limit=False,force_is_a_qualified_collapse_bound=False,
        predicts_actual_force=False)


def plate_fixture(force_N,pitch_m,thickness_m,effective_width_m=.4):
    """Simply supported longitudinal strip, central load distributed across width."""
    P=positive(force_N,'force');p=positive(pitch_m,'pitch');t=positive(thickness_m,'thickness')
    b=positive(effective_width_m,'effective width');I=b*t**3/12;Z=b*t*t/6
    return dict(model='Simply supported elastic strip; central longitudinal load',
        moment_Nm=P*p/4,stress_Pa=P*p/(4*Z),deflection_m=P*p**3/(48*E_STEEL*I),I_m4=I)


def rhs_properties(width,height,wall):
    if min(width,height)<=2*wall or wall<=0:raise ValueError('positive hollow section required')
    return dict(area_m2=width*height-(width-2*wall)*(height-2*wall),
        I_m4=(width*height**3-(width-2*wall)*(height-2*wall)**3)/12)


def _stock(uid,quantity,volume,material='steel'):
    rho=RHO_STEEL if material=='steel' else RHO_CONCRETE
    return dict(id=uid,quantity=quantity,unit_volume_m3=volume,material=material,
                density_kg_m3=rho,counted_mass_kg=quantity*volume*rho)


def _parent(root):
    root=Path(root).resolve();selector=tomllib.loads((root/SELECTOR).read_text())
    receipt_path=root/selector['source_manifest'];receipt=json.loads(receipt_path.read_bytes())
    if digest(receipt_path)!=selector['source_manifest_sha256']:raise ValueError('selected physical manifest differs')
    design_path=root/selector['source_design']
    if digest(design_path)!=receipt['files_sha256'][design_path.name]:raise ValueError('selected physical dossier differs')
    dossier=json.loads(gzip.decompress(design_path.read_bytes()));car=dossier['vehicle'];baseline=dossier['interfaces']['civil']
    ids=dict(candidate_id=car['candidate_id'],body_candidate_id=car['body_candidate_id'],magnet_component_id=car['magnet_component_id'])
    if any(ids[k]!=selector[s] for k,s in [('candidate_id','vehicle_candidate_id'),('body_candidate_id','body_candidate_id'),('magnet_component_id','magnet_component_id')]):
        raise ValueError('selected vehicle/component identity differs')
    if (selector['vehicle']['cars'],selector['vehicle']['normal_passengers_per_car'],len(car['physical_definition']['module_mounts']))!=(6,46,24):
        raise ValueError('study requires explicit six-car comfort parent and24mounts')
    if baseline['civil_interface_id']!=identity({k:v for k,v in baseline.items() if k!='civil_interface_id'}):
        raise ValueError('retained civil physical identity differs')
    magnetic=json.loads((root/MAGNETS).read_bytes())
    component=next(v for v in magnetic['magnetic_candidates'] if v['candidate_id']==ids['magnet_component_id'])
    if (component['length_x_m'],component['parameters']['width_m'],component['interface']['facing_width_m'],component['interface']['facing_thickness_m'])!=(1.,.4,.5,.035):
        raise ValueError('magnetic geometry requires a new facing study')
    if digest(root/MAGNETS)!=dossier['source_sha256'][MAGNETS]:raise ValueError('magnetic input differs from selected evidence')
    finite=json.loads((root/FINITE).read_bytes());sample=next(r for r in finite['rows'] if r['candidate_id']==ids['magnet_component_id'])
    own=Path(__file__).read_bytes()
    if not (root/CODE).is_file() or (root/CODE).read_bytes()!=own:
        raise ValueError('integrate executing producer into the declared source root before running')
    names=(SELECTOR,selector['source_manifest'],selector['source_design'],MAGNETS,FINITE,CODE)
    sources={n:digest(root/n) for n in names}
    return dict(**ids,selection_id=identity(selector),vehicle=car,baseline=baseline,
        magnet=component,retained_component_sample=dict(gap_m=sample['gap_m'],
            steel_B_peak_T=sample['analysis']['steel_B_peak_T'],
            Fz_contours_N=[r['force_N'][2] for r in sample['analysis']['air_contour_results']],
            numerical_force_convergence_established=False),source_sha256=sources)


def definition(family,face_thickness,pitch,head_depth,rebar_pitch,parent,rib_width_x_m=None):
    if family not in ('concrete-ledges','embedded-edge-stiffeners','dual-use-steel-box'):
        raise ValueError('unknown physical guideway family')
    for value,name in [(face_thickness,'face thickness'),(pitch,'anchor pitch'),(head_depth,'head depth'),(rebar_pitch,'rebar pitch')]:positive(value,name)
    # Preserve beam/face datums. Raising a wide box through the PM/brake volume
    # is not free clearance: add a narrow stem and explicit protection channels.
    value=dict(schema='osr-guideway-alternative/1',family=family,
        parent_vehicle_candidate_id=parent['candidate_id'],parent_body_candidate_id=parent['body_candidate_id'],
        magnet_component_id=parent['magnet_component_id'],parent_civil_interface_id=parent['baseline']['civil_interface_id'],
        span_m=25.,facing_width_m=.5,facing_thickness_m=face_thickness,
        face_centres_y_m=[-.88,.88],working_face_bottom_z_m=-1.16,
        retained_box_width_m=.8,retained_box_depth_m=2.5,retained_box_top_z_m=-1.6,
        new_head_width_m=2.26,new_head_depth_m=head_depth,new_stem_width_m=.72,
        anchor_pitch_m=pitch,anchor_diameter_m=.024,anchor_embedment_m=.35,
        transverse_rebar_diameter_m=.016,transverse_rebar_pitch_m=rebar_pitch,
        protection_channel_abs_y_m=[.36,.60],protection_channel_top_z_m=-.90,
        protection_pedestal_width_m=1.0,protection_pedestal_height_m=.22,
        face_stock_segments_m=5.,reference_coupon_gap_m=.012,operating_gap_m=None,
        selected_material_limits_qualified=False,
        reserve_includes_complete_load_and_faults=False)
    if family=='embedded-edge-stiffeners':value['edge_RHS_m']=[.075,.15,.006]
    if family=='dual-use-steel-box':value['steel_box_top_thickness_m']=.008;value['steel_box_web_height_m']=.15;value['steel_box_web_thickness_m']=.006
    if rib_width_x_m is not None:
        rib_width_x_m=positive(rib_width_x_m,'integral crosshead width')
        n=math.ceil(25./pitch)+1
        value.update(integral_crosshead_width_x_m=rib_width_x_m,
            integral_crosshead_centres_x_m=[rib_width_x_m/2+i*(25.-rib_width_x_m)/(n-1) for i in range(n)],
            rib_transverse_bar_count=max(0,math.floor((rib_width_x_m-2*.04-2*.01+.016)/(.016+.016)+1e-9)),
            rib_closed_tie_diameter_m=.010,rib_closed_tie_pitch_m=.075,
            independent_protection_nibs=dict(count=102,length_x_m=.20,width_y_m=.20,height_z_m=.22,
                centres_abs_y_m=.46,bottom_z_m=-1.60,post_base_z_m=-1.38),
            end_overhang_and_adjacent_span_interface_qualified=False)
    value['guideway_candidate_id']=identity(value)
    return value


def evaluate_variant(value,parent,force_N=40000.):
    if value.get('guideway_candidate_id')!=identity({k:v for k,v in value.items() if k!='guideway_candidate_id'}):
        raise ValueError('guideway physical identity differs')
    if value['magnet_component_id']!=parent['magnet_component_id'] or value['parent_vehicle_candidate_id']!=parent['candidate_id']:
        raise ValueError('guideway belongs to another train or magnet')
    P=positive(force_N,'local module force');s=value['span_m'];t=value['facing_thickness_m'];p=value['anchor_pitch_m'];d=value['new_head_depth_m']
    n=math.ceil(s/p)+1;rib_width=value.get('integral_crosshead_width_x_m')
    bars=math.ceil(s/value['transverse_rebar_pitch_m'])+1 if rib_width is None else n*value['rib_transverse_bar_count']
    faces=2*s*.5*t;top=-1.16+t+d;stem_height=(-1.16+t)-(-1.6)
    channel_height=max(0.,min(-.90,top)-(-1.16+t))
    new_concrete_volume=s*(.72*stem_height+2.26*d-2*(.60-.36)*channel_height+(1.-.72)*.22)
    if new_concrete_volume<=0:raise ValueError('positive new concrete material required')
    rows=[_stock('working-face/continuous-plate',2,s*.5*t),
        _stock('new-head-stem-pedestal/net-concrete',1,new_concrete_volume,'concrete'),
        _stock('facing-anchor/24mm-shank',4*n,math.pi*.024**2/4*.35),
        _stock('facing-anchor/head-nut-stock',4*n,math.pi*.04**2/4*.04),
        _stock('facing-anchor/washer',4*n,math.pi*(.06**2-.026**2)/4*.005),
        _stock('head/transverse-top-bar',bars,math.pi*.016**2/4*2.56),
        _stock('head/longitudinal-distribution-bar',12,math.pi*.012**2/4*s),
        _stock('protection-post/new-baseplate',102,.20*.20*.020),
        _stock('protection-post/new-anchor-shank',204,math.pi*.020**2/4*.25)]
    for stock in parent['baseline']['stock']:
        if stock['id'].startswith('protection/'):
            rows.append(dict(id='retained/'+stock['id'],quantity=stock['quantity'],unit_volume_m3=stock['volume_m3'],
                             material='steel',density_kg_m3=stock['density_kg_m3'],counted_mass_kg=stock['counted_mass_kg']))
    plate=plate_fixture(P,p,t);longitudinal_delta=plate['deflection_m'];plate_stress=plate['stress_Pa'];weld_m=0.
    family=value['family']
    if family=='embedded-edge-stiffeners':
        w,h,wall=value['edge_RHS_m'];rhs=rhs_properties(w,h,wall)
        rows.append(_stock('embedded/continuous-edge-RHS',4,s*rhs['area_m2']))
        # RHS replaces concrete, not an extra invisible overlapping solid.
        displaced=4*s*w*h
        rows[1]['unit_volume_m3']-=displaced;rows[1]['counted_mass_kg']=rows[1]['unit_volume_m3']*RHO_CONCRETE
        transverse_span=.425;plate_I=1.*t**3/12
        longitudinal_delta=P*p**3/(48*E_STEEL*2*rhs['I_m4'])
        plate_delta=5*P*transverse_span**3/(384*E_STEEL*plate_I)
        plate_stress=6*(P*transverse_span/8)/(1.*t*t)
        stiffener_stress=(P*p/8)/(rhs['I_m4']/(h/2))
        weld_m=8*s
    elif family=='dual-use-steel-box':
        h=value['steel_box_web_height_m'];web=value['steel_box_web_thickness_m'];tt=value['steel_box_top_thickness_m'];width=.5
        rows.extend([_stock('dual-use/box-top-steel',2,s*width*tt),_stock('dual-use/box-side-webs',4,s*h*web),
                     _stock('dual-use/diaphragms',2*n,width*h*.008)])
        displaced=2*s*width*(h+tt)
        rows[1]['unit_volume_m3']-=displaced;rows[1]['counted_mass_kg']=rows[1]['unit_volume_m3']*RHO_CONCRETE
        areas=[width*t,width*tt,2*web*h];zs=[t/2,t+h+tt/2,t+h/2]
        z=sum(a*z for a,z in zip(areas,zs))/sum(areas)
        I=width*t**3/12+areas[0]*(zs[0]-z)**2+width*tt**3/12+areas[1]*(zs[1]-z)**2+2*web*h**3/12+areas[2]*(zs[2]-z)**2
        longitudinal_delta=P*p**3/(48*E_STEEL*I)
        transverse_span=.5;plate_I=1.*t**3/12
        plate_delta=5*P*transverse_span**3/(384*E_STEEL*plate_I)
        plate_stress=6*(P*transverse_span/8)/(1.*t*t)
        stiffener_stress=P*p/4/(I/max(z,t+h+tt-z));weld_m=8*s+2*n*2*(width+h)
    else:plate_delta=plate['deflection_m'];stiffener_stress=plate_stress;longitudinal_delta=0.
    if rib_width is not None:
        # Discrete heads/stems, with separate102small cast protection feet.
        # Feet abut the narrow stem at |y|=.36 and lie below the head, so
        # no overlapping material volume is credited twice.
        coverage=n*rib_width/s
        old_pedestal_overhang=s*(1.-.72)*.22
        feet_volume=102*.20*.20*.22
        rows[1]['unit_volume_m3']=(rows[1]['unit_volume_m3']-old_pedestal_overhang)*coverage+feet_volume
        rows[1]['counted_mass_kg']=rows[1]['unit_volume_m3']*RHO_CONCRETE
        distribution=next(r for r in rows if r['id']=='head/longitudinal-distribution-bar')
        distribution['quantity']=12*n;distribution['unit_volume_m3']=math.pi*.012**2/4*(rib_width+.24)
        distribution['counted_mass_kg']=distribution['quantity']*distribution['unit_volume_m3']*RHO_STEEL
        rows.extend([_stock('protection-nib/U16-rebar',204,math.pi*.016**2/4*1.20),
                     _stock('protection-nib/closed10-tie',204,math.pi*.010**2/4*.66)])
    # Root of each RC cantilever is narrowed by the explicit brake/capture slot.
    depth=max(0.,top-(-.90));effective_depth=depth-.040
    fixture_width=1. if rib_width is None else rib_width
    As=math.pi*.016**2/4/value['transverse_rebar_pitch_m'] if rib_width is None else value['rib_transverse_bar_count']*math.pi*.016**2/4
    fy=400e6;fc=30e6
    M=P*(.88-.36);force_tension=As*fy
    compression_block=force_tension/(.85*fc*fixture_width)
    moment_capacity=0. if effective_depth<=0 else force_tension*(effective_depth-compression_block/2)
    gross_I=fixture_width*depth**3/12
    concrete_delta=None if gross_I<=0 else 3*P*(.88-.36)**3/(3*E_CONCRETE*gross_I)
    shear_stress=None if effective_depth<=0 else P/(fixture_width*effective_depth)
    combined=None if concrete_delta is None else plate_delta+longitudinal_delta+concrete_delta
    stiffness_ok=combined is not None and combined<=.001
    flexure_ok=effective_depth>0 and compression_block<=.4*effective_depth and M<=moment_capacity
    tie_yield_bound=None;strut_bound=None
    if rib_width is not None:
        tie_pitch=value['rib_closed_tie_pitch_m'];tie_area=2*math.pi*.010**2/4
        tie_yield_bound=tie_area/tie_pitch*fy*max(0.,effective_depth)
        strut_bound=.2*fc*fixture_width*max(0.,effective_depth)
        tie_length=2*(max(0.,rib_width-.08)+max(0.,depth-.08))+.20
        rows.append(_stock('head/rib-closed10-yield-truss-ties',2*n*(math.ceil(.73/tie_pitch)+1),math.pi*.010**2/4*tie_length))
    shear_ok=shear_stress is not None and (shear_stress<=.4e6 or (tie_yield_bound is not None and min(tie_yield_bound,strut_bound)>=P))
    steel_ok=max(plate_stress,stiffener_stress)<=237e6
    # At least one neighbouring station can share a 1m load; no such sharing
    # is credited to the anchor fixture: two anchors carry one module force.
    anchor_stress=P/2/(math.pi*.024**2/4)
    bounds=[maxwell_bounds(P,.35,1.,cap) for cap in (1.4,1.6,1.8)]
    magnetic_ok=t>=bounds[1]['conditional_one_section_minimum_thickness_m'] and .35>=bounds[1]['minimum_effective_working_area_m2']
    checks=dict(local_steel_stress=steel_ok,local_elastic_deflection=stiffness_ok,
                RC_fixture_flexure=flexure_ok,RC_fixture_shear=shear_ok,
                rib_cage_fit=rib_width is None or value['rib_transverse_bar_count']>=1,
                anchor_shank_stress=anchor_stress<=237e6,anchor_shank_top_cover_fit=d>=.35+.04,conditional_single_return_flux_capacity=magnetic_ok)
    rows=[r for r in rows if r['quantity']>0]
    steel=sum(r['counted_mass_kg'] for r in rows if r['material']=='steel')
    added_concrete=sum(r['counted_mass_kg']/RHO_CONCRETE for r in rows if r['material']=='concrete')
    baseline=parent['baseline'];saved=baseline['complete_counted_steel_stock_kg_per_span']-steel
    result=dict(schema='osr-guideway-necessary-evaluation/1',guideway_candidate_id=value['guideway_candidate_id'],physical_definition=value,
        parent_vehicle_candidate_id=parent['candidate_id'],body_candidate_id=parent['body_candidate_id'],magnet_component_id=parent['magnet_component_id'],
        stock=rows,steel_kg_per25m=steel,steel_tonnes_per_direction_km=steel/25,
        additional_concrete_m3_per25m=added_concrete,
        retained_prismatic_concrete_m3_per25m=baseline['reference_prismatic_concrete_volume_m3'],
        concrete_kg_per25m=baseline['reference_prismatic_concrete_mass_kg']+added_concrete*RHO_CONCRETE,
        saved_counted_steel_kg_per25m=saved,
        facing_anchors_per25m=4*n,additional_protection_base_anchors_per25m=204,
        all_support_anchors_per25m=4*n+204,baseline_support_anchors_per25m=baseline['anchors_per_span'],
        retained_protection_wear_fasteners_per25m=204,
        full_width_RHS_crossmembers_per25m=0,internal_steel_box_diaphragms_per25m=2*n if family=='dual-use-steel-box' else 0,
        integral_concrete_crossheads_per25m=0 if rib_width is None else n,
        discrete_head_coverage_fraction=1. if rib_width is None else n*rib_width/s,
        transverse_rebar_occurrences_per25m=bars,longitudinal_distribution_bar_occurrences_per25m=12 if rib_width is None else 12*n,
        working_face_factory_panels_per25m=10,working_face_internal_joints_per25m=8,
        declared_longitudinal_and_diaphragm_weld_m_per25m=weld_m,
        local_fixture=dict(module_force_N_hypothesis=P,force_is_a_qualified_limit=False,
            effective_longitudinal_load_width_m=1.,plate_elastic_deflection_m=plate_delta,
            anchor_total_shank_length_m=.35,concrete_embedment_after_steel_depth_m=.35-(0.15 if family!='concrete-ledges' else 0.),
            longitudinal_stiffener_deflection_m=longitudinal_delta,RC_gross_deflection_times3_m=concrete_delta,
            total_elastic_component_deflection_m=combined,deflection_screen_m=.001,
            steel_stress_Pa=max(plate_stress,stiffener_stress),steel_screen_Pa=237e6,
            RC_effective_root_depth_m=effective_depth,RC_effective_longitudinal_width_m=fixture_width,RC_As_m2_in_fixture=As,RC_demand_moment_Nm=M,
            RC_fixture_moment_capacity_Nm=moment_capacity,RC_shear_stress_Pa=shear_stress,
            RC_shear_screen_Pa_hypothesis=.4e6,RC_tie_yield_bound_N=tie_yield_bound,
            RC_concrete_strut_bound_N_hypothesis=strut_bound,
            actual_shear_cracking_anchorage_and_fatigue_qualified=False,anchor_shank_stress_Pa=anchor_stress,
            RC_strength_properties_and_cracked_creep_factor_qualified=False),
        magnetic_capacity_bounds=bounds,necessary_screens={k:'pass' if ok else 'fail' for k,ok in checks.items()},
        engineering_screen='conditional-necessary-survivor' if all(checks.values()) else 'failed-necessary-screen',
        field_map=dict(changed_steel_geometry=True,actual_changed_interface_force_N=None,
            retained35mm_coupon_force_transferred=False,
            required_coupon_facing_width_m=.5,required_coupon_facing_thickness_m=t,
            extra_steel_or_rebar_needs_separate_installed_field_model=True,
            complete_multiaxis_current_temperature_map_available=False),
        assembly=dict(factory_operations=dict(plate_panels=10,facing_anchor_placements=4*n,
            protection_anchor_placements=204,transverse_bar_placements=bars,distribution_bar_placements=12 if rib_width is None else 12*n,
            continuous_weld_length_m=weld_m),field_operations=dict(span_lifts=1,working_face_joint_locations=8,
            actual_site_bolts_torque_tasks_and_alignment=None),
            actual_fabrication_hours=None,actual_erection_hours=None,
            thermal_joints_and_anchor_longitudinal_slip_qualified=False),
        cost_break_even=dict(installed_price_per_direction_km=None,
            actual_prices_available=False,saved_steel_kg=saved,added_concrete_m3=added_concrete,
            changed_facing_anchor_count=4*n-baseline['anchors_per_span'],new_protection_base_anchors=204,
            minimum_steel_price_per_kg_over_concrete_price_per_m3_ignoring_all_other_costs=None if saved<=0 else added_concrete/saved,
            formula='DeltaC=-savedSteelKg*Cs+addedConcreteM3*Cc+changedFacingAnchors*Ca+newProtectionAnchors*Cp+newWeldM*Cw+unpricedOtherChanges',
            omitted_from_simple_ratio=['Steelgrade-specific prices','Newformwork','Prestress/globalrebar','Welds/anchors/QA','Heaviertransport/piers/foundations','Protection/joints/replacement','Magnetic/current/coolingchanges']),
        numerical_validity='Analytical fixture only; gross/cracked stiffness and reinforcement capacities are hypotheses',
        evidence_maturity='analytical',physical_screen='unknown',
        unclosed=['Concretebreakout/anchorprying/fatigue','Rebarcovers/anchorage/cracks/creep','Globalprestress/torsion/movingloads',
            'Pier/foundation/liftingmass','Fullnativevehicle/protectionclash','Steelgrade/DCBH/joints/eddycurrentloss',
            'Actualinstalledfieldforcesandfaults','Completebrake/captureattachments','Factory/sitehoursandprices'],**FLAGS)
    result['evaluation_id']=identity(result);return result


def pareto(rows):
    survivors=[r for r in rows if r['engineering_screen']=='conditional-necessary-survivor']
    fields=('steel_kg_per25m','additional_concrete_m3_per25m','facing_anchors_per25m','declared_longitudinal_and_diaphragm_weld_m_per25m')
    return [r['guideway_candidate_id'] for r in survivors if not any(
        all(other[k]<=r[k] for k in fields) and any(other[k]<r[k] for k in fields)
        for other in survivors if other is not r)]


def build(root=ROOT):
    parent=_parent(root);rows=[]
    definitions=[]
    for family,t,p,d,r in product(('concrete-ledges','embedded-edge-stiffeners','dual-use-steel-box'),
        (.012,.020,.028,.035),(.25,.5,1.,1.5),(.35,.45,.55),(.15,.30)):
        definitions.append(definition(family,t,p,d,r,parent))
    for family,t,p,d,w in product(('concrete-ledges','embedded-edge-stiffeners','dual-use-steel-box'),
        (.020,.035),(.5,.75,1.,1.5),(.45,.55),(.10,.15,.20)):
        definitions.append(definition(family,t,p,d,.30,parent,rib_width_x_m=w))
    for value in definitions:
        nominal=evaluate_variant(value,parent,40000.);fault=evaluate_variant(value,parent,70000.)
        nominal.pop('evaluation_id')
        nominal['nominal40kN_screen']=nominal['engineering_screen'];nominal['fault70kN_screen']=fault['engineering_screen']
        nominal['force_case_evaluations']=[{k:row[k] for k in ('local_fixture','magnetic_capacity_bounds','necessary_screens','engineering_screen')} for row in (nominal,fault)]
        nominal['engineering_screen']='conditional-necessary-survivor' if all(row['engineering_screen']=='conditional-necessary-survivor' for row in (nominal,fault)) else 'failed-necessary-screen'
        nominal['evaluation_id']=identity(nominal);rows.append(nominal)
    front=pareto(rows);eligible=[r for r in rows if r['guideway_candidate_id'] in front]
    ranked=sorted(eligible,key=lambda r:(r['steel_kg_per25m'],r['facing_anchors_per25m'],r['guideway_candidate_id']))
    tare=parent['vehicle']['mass']['accounted_tare_kg_per_car']
    loads=[dict(passengers_per_car=p,accounted_kg_per_car=tare+75*p,
         uniform_static_module_N=(tare+75*p)*G/24,uniform1p3_module_N=1.3*(tare+75*p)*G/24)
         for p in (0,46,160)]
    value=dict(schema='osr-guideway-tradeoff-campaign/1',selection_id=parent['selection_id'],
        parent_vehicle_candidate_id=parent['candidate_id'],body_candidate_id=parent['body_candidate_id'],magnet_component_id=parent['magnet_component_id'],
        source_sha256=parent['source_sha256'],baseline=deepcopy(parent['baseline']),load_cases=loads,
        retained35mm_component_sample=parent['retained_component_sample'],
        declared_stock_density_steel_kg_m3=RHO_STEEL,retained_electrical_proxy_density_kg_m3=parent['magnet']['materials']['steel']['density_kg_m3'],
        density_or_grade_equivalence_established=False,
        cases=rows,counts=dict(executed=len(rows),conditional_necessary_survivors=sum(r['engineering_screen']=='conditional-necessary-survivor' for r in rows),
            pareto=len(front),joint_physical_survivors=0),pareto_candidate_ids=front,
        shortlist_candidate_ids=[r['guideway_candidate_id'] for r in ranked[:6]],
        installed_cost_ranking=None,selected_replacement_candidate_id=None,
        scope='Counted physical stock and declared necessary load/flux fixtures; no new field map, full civil qualification or economic default selection',**FLAGS)
    value['campaign_id']=identity(value);return value


def publish(output,root=ROOT):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);result=build(root)
    raw=encoded(result);(output/'result.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    summary={k:v for k,v in result.items() if k not in ('cases','baseline')}
    summary['shortlist']=[{k:r[k] for k in ('guideway_candidate_id','physical_definition','steel_kg_per25m','steel_tonnes_per_direction_km','additional_concrete_m3_per25m','facing_anchors_per25m','additional_protection_base_anchors_per25m','all_support_anchors_per25m','engineering_screen','cost_break_even')}
        for r in result['cases'] if r['guideway_candidate_id'] in result['shortlist_candidate_ids']]
    (output/'summary.json').write_bytes(encoded(summary))
    manifest=dict(schema='osr-guideway-tradeoff-publication/1',campaign_id=result['campaign_id'],source_sha256=result['source_sha256'],
        files_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()},**FLAGS)
    (output/'manifest.json').write_bytes(encoded(manifest));verify(output,root)
    return summary


def verify(output,root=ROOT,replay=True):
    output=Path(output);m=json.loads((output/'manifest.json').read_bytes())
    for name,h in m['source_sha256'].items():
        if digest(Path(root)/name)!=h:raise ValueError('source differs '+name)
    for name,h in m['files_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or digest(output/name)!=h:raise ValueError('payload differs '+name)
    result=json.loads(gzip.decompress((output/'result.json.gz').read_bytes()))
    if result['campaign_id']!=identity({k:v for k,v in result.items() if k!='campaign_id'}):raise ValueError('campaign identity differs')
    if any(result.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('research cannot grant physical acceptance')
    if replay and result!=build(root):raise ValueError('guideway campaign replay differs')
    return dict(verified=True,replayed=replay,campaign_id=result['campaign_id'],counts=result['counts'],**FLAGS)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['run','verify']);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True);a=p.parse_args(argv)
    value=publish(a.output,a.root) if a.action=='run' else verify(a.output,a.root)
    print(json.dumps(value,sort_keys=True,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
