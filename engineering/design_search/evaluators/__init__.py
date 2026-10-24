"""Candidate-bound adapters to current native structures and nonlinear magnetics."""
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import platform
from pathlib import Path
import sys

import numpy as np

from .. import contracts, coupling, families

ROOT=Path(__file__).resolve().parents[3]
IDS=('definition','mechanical','civil','magnetic','coupling')
DEPENDENCIES={'definition':[],'mechanical':['definition'],'civil':['mechanical'],
              'magnetic':['definition','civil'],'coupling':['civil','magnetic']}


def evaluator_ids():return list(IDS)


def evaluator_catalogue():
    return [dict(id=name,dependencies=DEPENDENCIES[name],maximum_maturity='numerical-screen',
        physical_accepted=False,uses_current_candidate_stock=True,ideal_force_channel=False) for name in IDS]


def source_snapshot(evaluator_id):
    if evaluator_id not in IDS:raise ValueError('unknown evaluator')
    from engineering.ferrite_maglev import candidate_magnetics as magnetic, candidate_structures as structures
    paths={Path(__file__),Path(contracts.__file__),Path(families.__file__),Path(coupling.__file__),*magnetic.source_paths(),
           Path(structures.__file__),structures.INPUT}
    if evaluator_id in ('mechanical','civil'):
        paths.add(ROOT/'engineering/design_search/geometry.py')
    if evaluator_id=='mechanical':paths.add(ROOT/'engineering/maglev_research/carrier_geometry.py')
    return {path.relative_to(ROOT).as_posix():sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def request_for(candidate,evaluator_id,*,purpose='diagnostic',hypothesis=None,settings=None,scenario=None,mesh=None,environment=None):
    env=dict(python=sys.version.split()[0],numpy=np.__version__,system=platform.system(),machine=platform.machine())
    if environment is not None:
        if not isinstance(environment,dict):raise ValueError('explicit environment mapping required')
        if any(key in environment and environment[key]!=value for key,value in env.items()):raise ValueError('declared evaluator environment differs from actual runtime')
        env.update(deepcopy(environment))
    defaults=dict(flux_allocation='original-branch-flux')
    if hypothesis is not None:defaults.update(deepcopy(hypothesis))
    return contracts.make_evaluation_request(candidate,evaluator_id=evaluator_id,evaluator_sources=source_snapshot(evaluator_id),
        hypothesis=defaults,settings=settings,mesh=mesh,scenario=scenario,environment=env,purpose=purpose)


def _definition(candidate,request):
    vehicle=contracts.mass_properties(candidate);beam=contracts.mass_properties(candidate,'guideway-per-span')
    complete=vehicle['complete_installed_distribution'] and beam['complete_installed_distribution']
    return dict(numerical_status='converged',screen_status='pass' if complete else 'unknown',
        metrics=dict(vehicle_mass_lower_bound_kg=vehicle['known_mass_subtotal_kg'],constraint_violation=0. if complete else 1.,
            unknown_vehicle_stock_count=len(vehicle['unknown_stock_ids']),unlocated_vehicle_stock_count=len(vehicle['unlocated_stock_ids']),
            guideway_known_mass_lower_bound_kg=beam['known_mass_subtotal_kg']),
        constraints=[dict(id='complete-installed-inventory',state='pass' if complete else 'unknown',vehicle=vehicle,guideway=beam)],
        diagnostics=['All stock scopes are separate. Unknown installed mass/CG/inertia is not zero.'])


def _mechanical(candidate,request):
    from engineering.ferrite_maglev import candidate_structures as structures
    native=families.materialize(candidate,allow_incomplete=True)
    height=request['settings'].get('unlocated_equipment_height_m',1.)
    mass=families.known_mass_state(candidate,unlocated_height_m=height);a=structures.load()
    loads=structures.load_cases(native,mass,a);response=structures.mechanical(native,mass,loads,a)
    # Current physical hardpoints/stringers/capture remain actual source stock;
    # newly proposed bearings/slides cannot replace those missing load paths.
    ratios=[response['hardpoint']['worst']['utilisation'],response['collector_splice']['utilisation'],
            response['body_spine']['combined_screen_pa']/response['body_spine']['stress_limit_pa']]
    load_ratio=max(row['peak_module_resultant_n']/row['module_force_screen_n'] for row in loads['cases'])
    violation=max([load_ratio,*ratios]);failed=violation>1
    from engineering.maglev_research import carrier_geometry
    carrier=candidate['architecture']['carrier'];radius=request['scenario'].get('curve_radius_m',150.)
    tolerance=request['scenario'].get('tolerance_reserve_m',.002)
    bounds=carrier_geometry.stock_bounds(native['module']['parts']);positions=carrier['module_centres_x_m']
    small,extra=divmod(len(positions),carrier['count_per_car']);start=0;groups=[]
    for index in range(carrier['count_per_car']):
        size=small+(index<extra);groups.append(positions[start:start+size]);start+=size
    layout=dict(id=candidate['candidate_id'],stock_bounds=bounds,row_centres_y_m=carrier['rows_y_m'],module_centres_x_m=positions,
        module_count=len(native['module_placements']),body_length_m=17.,body_end_clearance_m=.5,
        proposed_underbody_clearance_width_m=2.65,current_body_width_m=2.65)
    geometry=carrier_geometry.evaluate(layout,groups,radius,tolerance,
        'yaw-and-lateral-slide' if carrier['mode']=='yaw-and-lateral-slide' else 'yaw-only-fixed-pivots')
    curve_ratio=(geometry['maximum_finite_stock_radial_mismatch_m']+tolerance)/(.008-.002)
    violation=max(violation,curve_ratio);failed=failed or not geometry['conditional_stock_geometry_screen_pass']
    return dict(numerical_status='converged',screen_status='fail' if failed else 'unknown',
        metrics=dict(vehicle_mass_lower_bound_kg=mass['laden']['mass_kg'],constraint_violation=violation,
            mechanical_maximum_utilisation=violation),
        constraints=[dict(id='source-native-hardpoints-and-loads',state='fail' if failed else 'unknown',ratio=violation),
            dict(id='finite-stock-carrier-curve',state='pass' if geometry['conditional_stock_geometry_screen_pass'] else 'fail',scope='Finite stock at declared curve; installed joints/slides remain unknown.'),
            dict(id='new-carrier-joints-and-installed-stock',state='unknown')],
        diagnostics=[dict(loads=loads,mechanical=response,carrier_geometry=geometry,mass_state=mass,scope='Diagnostic known-stock loading; unknown carrier interfaces prevent a complete mechanical pass.')])


def _civil(candidate,request):
    selected=families.selected_beam(candidate);beam=selected['beam']
    ratio=beam['deflection']['live_m']/beam['deflection']['limit_m']
    passed=beam['passed_implemented_screens']
    return dict(numerical_status='converged',screen_status='unknown' if passed else 'fail',
        metrics=dict(vehicle_mass_lower_bound_kg=contracts.mass_properties(candidate)['known_mass_subtotal_kg'],constraint_violation=max(ratio,1. if passed else 1.000001),
            selected_beam_gross_mass_kg=beam['gross_mass_kg'],selected_beam_live_deflection_m=beam['deflection']['live_m']),
        constraints=[dict(id='selected-beam-current-moving-loads',state='pass' if passed else 'fail',
            candidate_id=candidate['candidate_id'],section_id=selected['section_id'],span_m=selected['span_m']),
            dict(id='installed-stock-materials-joints-soil',state='unknown')],
        diagnostics=[dict(selected_beam=selected,scope='Current nonlinear-stock candidate load distribution and selected real section; no old ideal-force search plant.')])


@contextmanager
def _network(module,hypothesis):
    from engineering.ferrite_maglev import candidate_magnetics as magnetic
    original=magnetic._runtime;context=deepcopy(original(module['variant_id']))
    allocation=hypothesis.get('flux_allocation','original-branch-flux')
    if allocation=='useful-only-poles-sensitivity':
        branch=[];moved=[]
        for path in context[2]['core_paths']['branch']:
            if path['id'] in ('core/lift-pole','core/guide-pole'):moved.append(dict(path,id='useful-only/'+path['id']))
            else:branch.append(path)
        context[2]['core_paths']['branch']=branch;context[2]['core_paths']['stationary_return']+=moved
    elif allocation!='original-branch-flux':raise ValueError('unsupported flux-allocation hypothesis')
    magnetic._runtime=lambda _:context
    try:yield magnetic
    finally:magnetic._runtime=original


def _magnetic(candidate,request):
    native=families.materialize(candidate,allow_incomplete=True);mass=contracts.mass_properties(candidate)['known_mass_subtotal_kg']
    scenario=request['scenario'];gap=scenario.get('gap_m',.008);temperature=scenario.get('temperature_c',40.)
    factor=scenario.get('load_factor',1.3);contracts.finite(gap,'gap',True);contracts.finite(temperature,'temperature');contracts.finite(factor,'load factor',True)
    target=factor*mass*9.80665/len(native['module_placements'])
    with _network(native,request['hypothesis']) as magnetic:
        current=magnetic.load()['current_limit_a'];raw=magnetic.evaluate_batch([[gap]*4],[[current,0.]],temperature)
        inverse=magnetic.inverse_current([target],[0.],[[gap]*4],temperature)
    actual=float(raw['upward_n'][0]);converged=bool(raw['converged'][0]);valid=bool(raw['valid'][0]);support=actual>=target
    failed=not (valid and support)
    ratio=target/max(actual,1e-12)
    return dict(numerical_status='converged' if converged else 'nonconverged',screen_status='fail' if failed else 'unknown',
        metrics=dict(vehicle_mass_lower_bound_kg=mass,constraint_violation=max(ratio,1.000001 if not valid else 0.),
            magnetic_actual_peak_sample_lift_n=actual,magnetic_required_support_n=target),
        constraints=[dict(id='actual-magnetic-capacity-at-current-limit',state='fail' if failed else 'pass',
            actual_n=actual,required_n=target,current_a=current,field_domain_valid=valid),
            dict(id='independent-spatial-map-and-thermal-duty',state='unknown')],
        diagnostics=[dict(candidate_id=candidate['candidate_id'],flux_allocation=request['hypothesis']['flux_allocation'],
            current_inverse_converged=bool(inverse['converged'][0]),required_inverse_current_a=inverse['current_a'].tolist(),
            unknown_installed_stock=native['unknown_installed_stock_ids'],field_converged=converged,
            scope='Actual nonlinear four-flux reluctance evaluator, including both physical current circuits; conditional maps are not spatial/physical validation.')])


def _coupling(candidate,request):
    properties=contracts.mass_properties(candidate)
    if not properties['complete_installed_distribution']:
        return dict(numerical_status='unknown',screen_status='unknown',metrics=dict(vehicle_mass_lower_bound_kg=properties['known_mass_subtotal_kg'],constraint_violation=1.),
            constraints=[dict(id='mass-heat-deformation-gap-closure',state='unknown',unknown_stock_ids=properties['unknown_stock_ids'],unlocated_stock_ids=properties['unlocated_stock_ids'])],
            diagnostics=['No nominal mass/CG/inertia is invented for installed stock. The coupling iteration waits for a complete candidate and candidate-specific heat/elastic maps.'])
    return dict(numerical_status='unknown',screen_status='unknown',metrics=dict(vehicle_mass_lower_bound_kg=properties['known_mass_subtotal_kg'],constraint_violation=1.),
        constraints=[dict(id='candidate-specific-electrothermal-deformation-map',state='unknown')],
        diagnostics=['Complete stock alone supplies no calibrated thermal/deformation response. Use coupling.iterate with explicit real maps, residuals and limits.'])


ADAPTERS=dict(definition=_definition,mechanical=_mechanical,civil=_civil,magnetic=_magnetic,coupling=_coupling)


def evaluate(candidate,evaluator_id,*,purpose='diagnostic',hypothesis=None,settings=None,scenario=None,mesh=None,environment=None):
    request=request_for(candidate,evaluator_id,purpose=purpose,hypothesis=hypothesis,settings=settings,scenario=scenario,mesh=mesh,environment=environment)
    before=source_snapshot(evaluator_id)
    try:
        if before!=request['evaluator_sources']:raise ValueError('evaluator sources changed after request identity was created')
        response=ADAPTERS[evaluator_id](candidate,request)
        response.setdefault('metrics',{}).update(known_vehicle_mass_kg=contracts.mass_properties(candidate)['known_mass_subtotal_kg'],
            known_guidebeam_mass_kg=contracts.mass_properties(candidate,'guideway-per-span')['known_mass_subtotal_kg'])
        if before!=source_snapshot(evaluator_id):raise ValueError('evaluator sources changed during execution')
        return contracts.make_result(request,execution_status='executed',maturity='numerical-screen',**response)
    except (ValueError,RuntimeError,KeyError,TypeError) as error:
        return contracts.make_result(request,execution_status='error',numerical_status='invalid',screen_status='unknown',
            diagnostics=[dict(error_type=type(error).__name__,message=str(error))])
