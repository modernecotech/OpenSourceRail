"""Compare actual stock at fixed passenger service; select experiments only."""
from copy import deepcopy
import math
from . import FLAGS,ROOT
from .common import identity

G=9.80665
RESERVE=1.3


def force_point(row):
    if row.get('execution_status')!='completed':return None
    execution=row.get('execution')
    if not isinstance(execution,dict) or execution.get('returncode')!=0 or execution.get('timed_out') is not False:
        raise ValueError('completed field point requires successful worker execution')
    raw=row['raw_result'];c=row['comparison']
    if raw['numerical_status']!='converged':return None
    return dict(force_N=c['conservative_contour_Fz_N'],demag_margin_A_per_m=c['demag_proxy_margin_A_per_m'],
                point_screen=c['next_experiment_sample_screen_pass'],
                contour_relative_difference=c['air_contour_relative_difference'],
                executed_evaluation_id=identity(dict(request_id=row['evaluation_id'],raw_result_id=raw['result_id'],
                                                     reported_environment=raw['environment'])))


def comparison_rows(magnets,bodies,screen_rows,*,root=ROOT):
    from . import candidates,vehicles,screen
    by_id={r['candidate_id']:r for r in screen_rows};rows=[]
    if len(by_id)!=len(screen_rows) or set(by_id)!={m['physical_id'] for m in magnets}:raise ValueError('unique complete magnetic result inventory required')
    for magnet in magnets:
        row=by_id[magnet['physical_id']]
        if row.get('execution_status')=='completed':
            try:screen.validate_point(row,magnet,root)
            except (KeyError,TypeError,ValueError) as error:raise ValueError('incompatible or altered field point') from error
    for magnet in magnets:
        candidates.validate(magnet,root)
        point=force_point(by_id[magnet['physical_id']])
        for body in bodies:
            full=vehicles.compose(body,magnet,root=root)
            nominal=full['support_requirements_by_unclosed_mass'][0]
            structure_failed=nominal['structure']['member_level_necessary_pass'] is False
            thermal=body['thermal'].get('comparisons') or []
            nominal_cooling_failure=any(c['nominal_capacity_margin_kWthermal']<0 for c in thermal)
            margins=[]
            for scenario in full['support_requirements_by_unclosed_mass']:
                margins.append(dict(unclosed_additional_mass_kg_per_car=scenario['unclosed_additional_mass_kg_per_car'],
                    comparison_aw3_kg_per_car=scenario['comparison_aw3_kg_per_car'],required_force_N_per_module=scenario['required_force_N_per_module'],
                    observed_2D_headroom_N=None if point is None else point['force_N']-scenario['required_force_N_per_module'],
                    conditional_capacity_screen=None if point is None else point['force_N']>=scenario['required_force_N_per_module'],
                    member_necessary_pass=scenario['structure']['member_level_necessary_pass']))
            row=dict(composition_id=full['candidate_id'],composition_result_id=full['evaluation_id'],
                body_candidate_id=body['candidate_id'],body_name=body['name'],magnet_component_id=magnet['physical_id'],recipe_id=magnet['recipe_id'],
                comparison_empty_kg_per_car=full['comparison_empty_kg_per_car'],comparison_aw3_kg_per_car=full['comparison_aw3_kg_per_car'],
                magnetic_known_stock_kg_per_car=full['magnetic_known_stock_kg_per_car'],force_point=point,
                support_sensitivities=margins,known_member_failure=structure_failed,nominal_hot_cooling_failure=nominal_cooling_failure,
                unknown_global_body_and_bracing=True,unknown_complete_HVAC_rating=True,unknown_installed_mass=True,
                nominal_thermal_margins_kW=[c['nominal_capacity_margin_kWthermal'] for c in thermal],
                next_capacity_experiment_eligible=(point is not None and point['point_screen'] and point['demag_margin_A_per_m']>=0
                    and not structure_failed and not nominal_cooling_failure),
                integrated_candidate_selected=False,**FLAGS)
            row['comparison_id']=identity(row);rows.append(row)
    return rows


def select_experiments(magnets,bodies,rows):
    """Prefer smaller counted arrays meeting +2t sensitivity, then body mass.

    No price or unknown equipment mass is set to zero. Unknown global body,
    thermal derating, dynamic control and force-map quality prevent adoption.
    """
    by_m={b['physical_id']:b for b in magnets};by_b={b['candidate_id']:b for b in bodies}
    eligible=[r for r in rows if r['next_capacity_experiment_eligible']
              and r['support_sensitivities'][2]['observed_2D_headroom_N']>=0
              and r['support_sensitivities'][2]['member_necessary_pass'] is not False]
    def order(row):
        m=by_m[row['magnet_component_id']]
        # Unknown baseline HVAC is kept for comparison; a known nominal-sized
        # proposal with explicit hot-load scenarios is a better next fixture.
        thermal_unknown_without_scenario=not by_b[row['body_candidate_id']]['thermal'].get('comparisons')
        return (thermal_unknown_without_scenario,m['stock']['magnet_volume_m3_per_module'],
                row['comparison_aw3_kg_per_car'],len([p for p in m['stock_parts'] if p['material']==m['grade_id']]),row['recipe_id'])
    selected=[]
    for kind,predicate in [('controlled',lambda m:m['parameters'].get('winding_layout')=='differential'),
                           ('topology-comparator',lambda m:m['parameters']['periods']==2)]:
        options=[r for r in eligible if predicate(by_m[r['magnet_component_id']])]
        fallback=False
        if not options:
            options=[r for r in rows if predicate(by_m[r['magnet_component_id']]) and r['force_point'] is not None and not r['known_member_failure']]
            fallback=True
        if options:
            row=min(options,key=order);selected.append(dict(purpose=kind,comparison_id=row['comparison_id'],
                magnet_component_id=row['magnet_component_id'],body_candidate_id=row['body_candidate_id'],
                failed_or_unknown_necessary_screen=fallback,adoption=False))
    return dict(policy='Next experiment only: explicit hot-load scenario, smallest PM volume meeting 1.3 AW3 plus 2t unclosed-mass sensitivity; then lower accounted car mass and fewer PM pieces. Separate differential and two-period families.',
                selected=selected,integrated_selection=None,all_unknown_costs_remain_unknown=True,**FLAGS)


def gap_profiles(operating_result,selection,comparisons):
    comparison_by={r['comparison_id']:r for r in comparisons};profiles=[]
    for selected in selection['selected']:
        mass=comparison_by[selected['comparison_id']];cid=selected['magnet_component_id']
        for temperature in (20.,80.):
            points=[]
            for row in operating_result['rows']:
                p=row['point']
                if p['candidate_id']!=cid or p['temperature_C']!=temperature or p['current_A']!=0:continue
                f=force_point(row['result'])
                if f is not None:points.append(dict(gap_m=p['gap_m'],force_N=f['force_N'],demag_margin_A_per_m=f['demag_margin_A_per_m'],
                                                   necessary_point_screen_pass=f['point_screen'] and f['demag_margin_A_per_m']>=0))
            points.sort(key=lambda p:p['gap_m']);loads=[]
            for load,name in [(mass['comparison_empty_kg_per_car'],'empty'),(mass['comparison_aw3_kg_per_car'],'AW3')]:
                weight=load*G/24;crossings=[]
                for a,b in zip(points,points[1:]):
                    if a['necessary_point_screen_pass'] and b['necessary_point_screen_pass'] and (a['force_N']-weight)*(b['force_N']-weight)<=0:crossings.append([a['gap_m'],b['gap_m']])
                loads.append(dict(load_case=name,comparison_mass_kg_per_car=load,mean_weight_N_per_module=weight,
                    sampled_zero_current_crossing_brackets_m=crossings,
                    gap_target_proven=False,stable_equilibrium_established=False))
            profiles.append(dict(candidate_id=cid,body_candidate_id=selected['body_candidate_id'],temperature_C=temperature,
                points=points,loads=loads,scope='Sampled zero-current crossing only; nominal weight is distinct from 1.3 reserve and no interpolated map or stable hover is accepted',**FLAGS))
    return profiles


def finite_plan(magnets,selection,comparisons,profiles):
    """One capacity reference and two independently computed operating points."""
    by_m={b['physical_id']:b for b in magnets};by_c={r['comparison_id']:r for r in comparisons};plan=[]
    for selected in selection['selected']:
        magnet=by_m[selected['magnet_component_id']]
        if selected['purpose']=='controlled':plan.append(dict(candidate=magnet,gap_m=.012,purpose='enlarged capacity reference'))
        profile=next((p for p in profiles if p['candidate_id']==magnet['physical_id'] and p['temperature_C']==80),None)
        load=by_c[selected['comparison_id']]['comparison_aw3_kg_per_car']*G/24;gap=.028
        if profile and profile['points']:
            points=[p for p in profile['points'] if p['necessary_point_screen_pass']]
            bracket=next(((a,b) for a,b in zip(points,points[1:]) if (a['force_N']-load)*(b['force_N']-load)<=0),None)
            if bracket:
                a,b=bracket
                # This is an explicit experiment proposal. A fresh3D solve
                # evaluates it; interpolation does not provide force credit.
                if min(a['force_N'],b['force_N'])>0 and a['force_N']!=b['force_N']:
                    gap=a['gap_m']+(b['gap_m']-a['gap_m'])*math.log(a['force_N']/load)/math.log(a['force_N']/b['force_N'])
                else:gap=(a['gap_m']+b['gap_m'])/2
            elif points:gap=min(points,key=lambda p:abs(p['force_N']-load))['gap_m']
        plan.append(dict(candidate=magnet,gap_m=round(gap,6),purpose=selected['purpose']+' exploratory AW3 state'))
    return plan[:3]
