"""Unselected 20 m reference-box moving-load analytical research control.

Gross uncracked beam theory is not local deck, bearing, reinforced-concrete,
foundation, handling or installed railway qualification.
"""
from copy import deepcopy
from math import fsum,isfinite
from pathlib import Path
from engineering.station_rail.common import identity,digest
from engineering.development_baseline import selection
from engineering.design_search import civil_shape_geometry as geometry
from engineering.design_search.craft_backends import viaduct_cases

PRODUCER='engineering/design_search/craft_backends/civil_moving_load.py'
G=9.80665


def positive(value,label,zero=False):
    if type(value) not in (int,float) or not isfinite(value) or (value<0 if zero else value<=0):
        raise ValueError('Finite '+label+' required')
    return value


def axle_positions(vehicle):
    """Axle stations from the declared first body start, never a CG inference."""
    v=vehicle['physical_definition']['vehicle'];s=vehicle['physical_definition']['support']
    length=positive(v['body_length_m'],'body length');gap=positive(v['coupling_gap_m'],'gap',True)
    wheelbase=positive(s['bogie_wheelbase_m'],'wheelbase')
    centers=s['bogie_centres_x_m']
    if v['cars']!=6 or len(centers)!=2:raise ValueError('Explicit six-car two-bogie control required')
    return [i*(length+gap)+length/2+center+offset
            for i in range(v['cars']) for center in centers for offset in (-wheelbase/2,wheelbase/2)]


def dead_segments(case):
    rows=[]
    for e in case['entities']:
        g=e['geometry'];a=g['at_m'][0];b=a+g['length_m']
        mass=case['expected']['part_nominal_material_masses_kg'][e['id']]
        rows.append(dict(part_id=e['id'],a_m=a,b_m=b,q_N_m=mass*G/(b-a)))
    return rows


def dead_response(length,x,segments):
    left=fsum(s['q_N_m']*(s['b_m']-s['a_m'])*(1-(s['a_m']+s['b_m'])/(2*length)) for s in segments)
    total=fsum(s['q_N_m']*(s['b_m']-s['a_m']) for s in segments)
    subtract=[]
    for s in segments:
        u=min(x,s['b_m'])-s['a_m']
        if u>0:subtract.append(s['q_N_m']*((x-s['a_m'])*u-u*u/2))
    return left,total-left,left*x-fsum(subtract)


def response(length,x,shift,axles,axle_N,segments=()):
    """Exact influence ordinates for centered point loads and prism dead loads."""
    positive(length,'span');positive(axle_N,'axle load')
    if not 0<=x<=length or not isfinite(shift):raise ValueError('Section and train placement within finite domain required')
    z=[shift+a for a in axles if 0<=shift+a<=length]
    dl,dr,dm=dead_response(length,x,segments)
    left=fsum(axle_N*(length-a)/length for a in z)
    right=fsum(axle_N*a/length for a in z)
    moment=fsum(axle_N*(a*(length-x)/length if a<=x else x*(length-a)/length) for a in z)
    total=fsum(s['q_N_m']*(s['b_m']-s['a_m']) for s in segments)+len(z)*axle_N
    return dict(left_N=dl+left,right_N=dr+right,moment_Nm=dm+moment,
                balance_residual_N=(dl+left+dr+right)-total,axles_on_span=len(z))


def envelope(length,axles,axle_N,segments,step_m):
    positive(step_m,'section sample spacing')
    if not axles or len(axles)>100 or any(type(a) not in (int,float) or not isfinite(a) for a in axles):raise ValueError('Bounded explicit axle stations required')
    n=round(length/step_m)
    if not 2<=n<=400 or abs(n*step_m-length)>1e-10:raise ValueError('Bounded exact section grid required')
    peak=None;left=right=0.;residual=0.
    for i in range(n+1):
        x=length*i/n
        # For a fixed section, each influence function is piecewise linear in
        # train shift. Its maximum lies at an axle entry, section or exit event.
        shifts=sorted({station-a for a in axles for station in (0.,x,length)})
        for shift in shifts:
            r=response(length,x,shift,axles,axle_N,segments)
            residual=max(residual,abs(r['balance_residual_N']))
            left=max(left,r['left_N']);right=max(right,r['right_N'])
            if peak is None or r['moment_Nm']>peak['moment_Nm']:
                peak=dict(x_m=x,train_shift_m=shift,**r)
    return dict(section_step_m=step_m,section_count=n+1,max_moment=peak,
                max_left_reaction_N=left,max_right_reaction_N=right,
                maximum_balance_residual_N=residual,
                shift_search='Exact influence breakpoints at axle entry/section/exit; section maximum sampled')


def midpoint_deflection(length,axles,axle_N,segments,shift,EI,step_m):
    """Virtual work midpoint response; trapezoid integration diagnostic."""
    n=round(length/step_m);values=[]
    for i in range(n+1):
        x=length*i/n;unit_moment=min(x,length-x)/2
        m=response(length,x,shift,axles,axle_N,segments)['moment_Nm']
        values.append(m*unit_moment/EI*(.5 if i in (0,n) else 1.))
    return fsum(values)*length/n


def crane_at_radius(*,installed_lift_mass_kg,rigging_mass_kg,radius_m,hoist_factor,chart,configuration):
    """Compare only the supplied exact chart radius/configuration; no interpolation."""
    missing=[k for k,v in dict(installed_lift_mass_kg=installed_lift_mass_kg,
        rigging_mass_kg=rigging_mass_kg,radius_m=radius_m,hoist_factor=hoist_factor,
        chart=chart,configuration=configuration).items() if v is None]
    if missing:return dict(execution='held',missing=missing,required_capacity_kg=None,physical_accepted=False)
    mass=positive(installed_lift_mass_kg,'installed lift mass');rigging=positive(rigging_mass_kg,'rigging mass')
    radius=positive(radius_m,'installation radius');factor=positive(hoist_factor,'hoist factor')
    if factor<1 or not isinstance(configuration,str) or not configuration:raise ValueError('Declared hoist factor and crane configuration required')
    if not isinstance(chart,list):raise ValueError('Exact manufacturer chart rows required')
    rows=[r for r in chart if r.get('radius_m')==radius and r.get('configuration')==configuration]
    if len(rows)!=1:raise ValueError('Exact radius and configuration chart entry required; no rated-tonnage substitution')
    capacity=positive(rows[0]['capacity_kg'],'chart capacity');demand=(mass+rigging)*factor
    return dict(execution='calculated-unqualified',radius_m=radius,configuration=configuration,
        required_capacity_kg=demand,chart_capacity_kg=capacity,capacity_screen_pass=capacity>=demand,
        chart_authentication_and_ground_outrigger_wind_review_required=True,physical_accepted=False)


def build(root,steps=(.5,.25),*,producer_source=None):
    root=Path(root);producer_source=Path(producer_source) if producer_source is not None else root/PRODUCER
    if digest(producer_source)!=digest(__file__):raise ValueError('Loaded analytical producer source required')
    if len(steps)!=2 or not steps[1]<steps[0]:raise ValueError('Two ordered coarse/fine section grids required')
    selected=selection.load(root);vehicle=selected['vehicle']
    case=viaduct_cases.build('reference_box','reference',root=root)
    cells=case['physical_definition']['cells']
    if len(cells)!=1:raise ValueError('This analytical control requires the explicitly uniform reference box')
    sections=[geometry._properties(s['polygon_yz_m']) for s in cells[0]['sections']]
    area=fsum(s['area_m2'] for s in sections)
    center=fsum(s['area_m2']*s['centroid_yz_m'][1] for s in sections)/area
    inertia=fsum(s['I_y_m4']+s['area_m2']*(s['centroid_yz_m'][1]-center)**2 for s in sections)
    zs=[p[1] for s in cells[0]['sections'] for p in s['polygon_yz_m']]
    extreme=max(abs(z-center) for z in zs);L=case['span_m'];axles=axle_positions(vehicle);dead=dead_segments(case)
    v=vehicle['physical_definition']['vehicle'];tare=vehicle['mass']['accounted_tare_kg_per_car']
    cases={}
    for label,people in [('normal',v['normal_people_per_car']),('crowd-160-control',v['crowd_control_people_per_car'])]:
        mass=tare+people*v['passenger_mass_kg'];load=mass*G/4
        samples=[envelope(L,axles,load,dead,h) for h in steps]
        for e in samples:
            m=e['max_moment'];m['gross_uncracked_extreme_fibre_stress_Pa']=m['moment_Nm']*extreme/inertia
            e['midpoint_deflection_at_peak_moment_shift_m']=midpoint_deflection(L,axles,load,dead,m['train_shift_m'],35e9*inertia,e['section_step_m'])
        delta=abs(samples[-1]['max_moment']['moment_Nm']-samples[0]['max_moment']['moment_Nm'])
        cases[label]=dict(people_per_car=people,accounted_mass_kg_per_car=mass,axle_force_N=load,
            levels=samples,relative_moment_change=delta/samples[-1]['max_moment']['moment_Nm'],
            convergence_scope='Section sampling diagnostic, not native or engineering convergence',
            diagnostic_trigger=.01,diagnostic_trigger_is_not_engineering_limit=True)
    sources={**selected['source_sha256'],**vehicle['source_sha256'],**case['source_sha256'],
        'engineering/development_baseline/selection.py':digest(root/'engineering/development_baseline/selection.py'),
        'engineering/station_rail/vehicle.py':digest(root/'engineering/station_rail/vehicle.py'),
        PRODUCER:digest(producer_source)}
    config=dict(vehicle_candidate_id=vehicle['candidate_id'],civil_candidate_id=case['candidate_id'],
        component_geometry_id=case['component_geometry_id'],load_policy='accounted-tare/equal-four-axles/static/no-dynamic-factor',
        support='bilateral simply supported gross uniform box',steps_m=list(steps),young_Pa=35e9)
    result=dict(schema='osr-v07-civil-moving-load/1',research_configuration_id=identity(config),configuration=config,
        execution='completed',numerical_validity='valid-for-declared-analytical-model',engineering_screen='held',
        evidence_maturity='analytical-research-control',selection_purpose='method-check-and-next-task-ranking',
        selected_reference_changed=False,physical_candidate_selected=False,vehicle_reference_ids={k:vehicle[k] for k in ('candidate_id','body_candidate_id','support_component_id','propulsion_component_id')},
        civil_case_id=case['case_id'],civil_case_definition_id=case['case_definition_id'],span_m=L,
        axle_stations_m=axles,dead_stock_mass_kg=case['expected']['total_nominal_stock_mass_kg'],dead_segments=dead,
        section=dict(gross_area_m2=area,centroid_z_m=center,gross_I_y_m4=inertia,young_Pa_hypothesis=35e9),
        cases=cases,unlocated_accounted_mass_kg_per_car=vehicle['mass']['unlocated_or_reference_account_kg'],
        complete_installed_mass_kg_per_car=None,unknown_additional_installed_mass_kg=None,
        accounted_mass_is_not_a_guaranteed_installed_bound=True,
        vehicle_residual_overlap_unresolved=vehicle['residual_overlap_unresolved'],
        unresolved_civil_installed_items=deepcopy(case['unresolved_installed_items']),
        route_quantities=dict(span_count=None,support_count=None,transport_cycles=None,erection_cycles=None,installed_cost=None),
        ideal_centered_static_torsion_Nm=0.,actual_torsion_envelope_Nm=None,
        crane=crane_at_radius(installed_lift_mass_kg=None,rigging_mass_kg=None,radius_m=None,hoist_factor=None,chart=None,configuration=None),
        open_findings=[
          'Accounted tare includes positive unlocated allowances; actual CG/axle distribution and complete installed mass remain unknown.',
          'No dynamic amplification, braking/curving/lateral load, unequal rail loading, deck local wheel stress or train-bridge interaction is admitted.',
          'Uncracked homogeneous concrete E35GPa is a research stiffness hypothesis; no reinforcement, prestress transfer, cracking, fatigue or resistance qualification.',
          'Bilateral simple supports do not establish compression-only bearings, contact, uplift, anchorage or station/joint restraint.',
          'Foundation reactions need actual soil/settlement/lateral/overturning checks; no foundation capacity is assigned.',
          'Transport supports, lifting anchors, erection sequence, temporary bracing/wind and handling torsion remain unanalysed.',
          'Actual crane capacity requires installed lift mass, rigging, radius and authenticated configuration-specific load chart plus ground/outrigger review.',
          'Midpoint gross-beam deflection is not a magnetic-gap prediction: wheel/vehicle/wayside relative motion and actual interface/gap budgets are missing.',
          'City quantities/costs, support spacing, erection cycle and supplier prices are not inherited by this unselected component combination.'],
        source_sha256=sources,command='build(root, steps=(0.5,0.25))',native_solver_jobs=0,
        physical_accepted=False,engineering_accepted=False,manufacturing_release=False)
    result['evaluation_id']=identity(result);return result


def main(argv=None):
    """Write a fresh immutable external analytical package without native solves."""
    import argparse,json,sys,time,resource,shutil,subprocess
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv);root=args.root.resolve();out=args.output.absolute();source=Path(__file__).resolve()
    if out.exists() or out.resolve().is_relative_to(root) or out.resolve().is_relative_to(source.parents[3]):
        raise ValueError('Fresh external result directory required')
    if any(path.is_symlink() for path in (out,*out.parents)):raise ValueError('Ordinary result path required')
    out.parent.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(out.parent).free<21*1024**3:raise ValueError('20 GiB reserve plus 1 GiB request unavailable')
    out.mkdir();started=time.perf_counter()
    try:
        result=build(root,producer_source=source)
        for name,sha in result['source_sha256'].items():
            if digest(source if name==PRODUCER else root/name)!=sha:raise ValueError('Analytical source changed during execution')
        raw=(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
        (out/'result.json').write_bytes(raw)
        receipt=dict(schema='osr-v07-civil-analytical-run/1',evaluation_id=result['evaluation_id'],
            result_sha256=__import__('hashlib').sha256(raw).hexdigest(),command=[sys.executable,*sys.argv],
            producer_source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source.parents[3],text=True).strip(),
            runtime_source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
            runtime_dirty_state=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True),
            wall_seconds=time.perf_counter()-started,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
            source_sha256=result['source_sha256'],native_solver_jobs=0,
            resource_enforcement='Host disk admission and bounded sample grid; no OS sandbox or aggregate quota',physical_accepted=False)
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'evaluation_id':result['evaluation_id'],'output':str(out),'wall_seconds':receipt['wall_seconds']}))
    except BaseException as exc:
        (out/'failure.json').write_text(json.dumps({'type':type(exc).__name__,'reason':str(exc)})+'\n');raise


if __name__=='__main__':main()
