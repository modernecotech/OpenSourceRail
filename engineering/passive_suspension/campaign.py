"""Bounded physical alternatives, immutable calculations and honest publication.

The common design-search contracts are reused unchanged. A two-dimensional
linear-material field is a numerical experiment, never a completed suspension.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import tomllib

from engineering.design_search.contracts import (
    FLAGS, encoded, identity, make_candidate, make_evaluation_request, make_result,
    PHYSICAL_KEYS, mass_properties, validate_candidate, validate_result,
)
from engineering.design_search.registry import ImmutableRegistry
from engineering.design_search.selection import select
from engineering.design_search.storage import atomic_immutable
from engineering.ferrite_maglev import candidate_magnetics as canonical
from . import geometry, fields, controls

ROOT = Path(__file__).resolve().parents[2]
SPEC = Path(__file__).with_name('campaign.toml')
G = 9.80665
ROTATION = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]


def sources():
    paths = set(Path(__file__).parent.glob('*.py')) | {SPEC}
    paths.update((ROOT/'engineering/design_search').glob('*.py'))
    paths.update(ROOT/p for p in (
        'engineering/ferrite_maglev/candidate-magnetics.toml',
        'engineering/ferrite_maglev/candidate_magnetics.py',
        'engineering/ferrite_maglev/configuration.py',
        'engineering/factory_examples/native.py',
        'engineering/factory_examples/models.py',
    ) if (ROOT/p).is_file())
    # Mass replacement imports the canonical candidate. Bind its declared input
    # files too; do not mistake its existing receipt for a new installed design.
    paths.update((ROOT/'engineering/ferrite_maglev').glob('*.toml'))
    paths.update(canonical.source_paths())
    return {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def environment():
    return dict(python=platform.python_version(), numpy=importlib.metadata.version('numpy'),
                scipy=importlib.metadata.version('scipy'), platform=platform.platform(),
                numerical_workers=1, blas_threads=os.environ.get('OPENBLAS_NUM_THREADS','library-default'))


def common_candidate(value, requirements, *, parent_ids=None):
    """Stock/count contracts, with unresolved installed distribution explicit."""
    geometry._validate(value)
    for region in value['regions']:
        if region['group']=='guideway' and (region['material']!='steel' or region.get('circuit_id')
                or region.get('J_x_A_m2',0.) or region.get('Br_y_T',0.) or region.get('Br_z_T',0.)):
            raise ValueError('Ordinary guideway may contain only passive steel magnetic facings')
        if region.get('circuit_id') and region['group']!='train':
            raise ValueError('Suspension/guidance coils must be onboard')
    mats = [dict(id=key, density_kg_m3=data['density_kg_m3'],
                 grade=data.get('id', key),
                 basis='Named retained stock proxy in candidate-magnetics.toml; actual material certification pending')
            for key, data in sorted(value['materials'].items())]
    parts, stock = [], []
    for q in value['stock_parts']:
        if q['group'] != 'train':
            continue
        part = {key: deepcopy(q[key]) for key in ('id', 'kind', 'size_m', 'at_m')}
        part.update(frame_id='module', material_id=q['material'], role=q['role'])
        if 'Br_y_T' in q:
            magnitude = math.hypot(q['Br_y_T'], q['Br_z_T'])
            part['magnetisation_direction_yz'] = [q['Br_y_T']/magnitude, q['Br_z_T']/magnitude]
        parts.append(part)
        stock.append(dict(id=q['id'], status='known', quantity=value['units_per_car'],
                          scope='vehicle-per-car', basis='Repeated exact stock; packing poses in architecture; installed distribution unresolved',
                          unit_mass_kg=q['mass_kg'], geometry_id=q['id'], frame_id='module',
                          cg_m=None, inertia_kg_m2=None))
    p = value['parameters']
    for bank, cy in enumerate(value['packing']['bank_centres_y_m']):
        name = f'guideway/facing-bank-{bank}'
        size = [p['beam_span_m'], p['facing_width_m'], p['facing_thickness_m']]
        parts.append(dict(id=name, kind='box', size_m=size,
                          at_m=[-size[0]/2, cy-size[1]/2, 0.],
                          frame_id='module', material_id='steel', role='passive-steel-facing'))
        stock.append(dict(id=name, status='known', quantity=1, scope='guideway-per-span',
                          basis='Full selected span, two passive steel facing banks',
                          unit_mass_kg=math.prod(size)*value['materials']['steel']['density_kg_m3'],
                          geometry_id=name, frame_id='module', cg_m=None, inertia_kg_m2=None))
    for q in value['unknown_installed_inventory']:
        per_module = q['scope'] == 'per-module'
        stock.append(dict(id=q['id'], status='unknown', quantity=value['units_per_car'] if per_module else 1,
                          scope='guideway-per-span' if q['scope']=='per-beam-span' else 'vehicle-per-car',
                          basis=q['reason']+'; count pending' if q['quantity'] is None else q['reason'],
                          unit_mass_kg=None, geometry_id=None, frame_id='module', cg_m=None, inertia_kg_m2=None))
    circuits = [{k: deepcopy(q[k]) for k in ('id','turns','conductor_area_m2','conductor_length_m','topology')}
                for q in value['circuits']]
    return make_candidate(requirement_revision=requirements,
        architecture=dict(family=value['label'], packing=value['packing'], winding_circuits=circuits,
                          separate_guidance_reference=value['separate_guidance_reference'],
                          reference_gap_m=value['reference_gap_m']),
        frames=[dict(id='module', parent_id=None, origin_m=[0.,0.,0.], rotation_matrix=ROTATION)],
        materials=mats, geometry=parts,
        interfaces=[dict(id='ordinary-guideway', materials=['concrete','passive-steel'],
                         permanent_magnets='train-only', suspension_guidance_actuators='train-only',
                         station_propulsion='separate finite powered zones'),
                    dict(id='working-facing', gap_datum_m=value['reference_gap_m'],
                         force_frame='x travel, y right, z up', attachments='Unresolved tensile load path to concrete')],
        installed_inventory=stock,
        lineage=dict(parent_candidate_ids=parent_ids or [], operation='bounded-physical-proposal'),
        label=value.get('sample_id', value['label']), source_bindings={'geometry_source':sources()})


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = encoded(value)
    atomic_immutable(path,data)


def _record(registry, candidate, evaluator, run, *, src, scenario=None, settings=None, hypothesis=None):
    request = make_evaluation_request(candidate, evaluator_id=evaluator, evaluator_sources=src,
        scenario=scenario or {}, settings=settings or {}, hypothesis=hypothesis or {},
        environment=environment(), purpose='next-experiment')
    cached = registry.cached(request)
    if cached is not None:
        return cached
    registry.store('evaluation-request', request)
    result = run(request)
    registry.store('evaluation', result)
    return result


def mechanical_report(value,candidate):
    mass=geometry.replacement_mass_comparison(value)
    load=mass['material_subtotal_aw3_kg_per_car']*G/value['units_per_car']
    reserve=1.3*load
    curves=[geometry.curve_screen(value,R) for R in (150.,250.,500.,1000.)]
    result=dict(candidate_id=candidate['candidate_id'],sample_id=value['sample_id'],
        units_per_car=value['units_per_car'],
        stock=value['stock'],mass_comparison=mass,curves=curves,
        attachment=geometry.attachment_screen(value,reserve),factory_datums=geometry.factory_datums(value),
        support_load_material_floor_N_per_module=load,support_reserve_floor_N_per_module=reserve,
        complete_installed_mass_kg=None,native_scope='one local module and passive facing coupon',**FLAGS)
    if value['label']=='D':
        result['flexure']=geometry.flexure_screen(value,curves[0]['independently_required_yaw_rad'],
            lateral_translation_m=curves[0]['independently_required_centre_slide_m'])
    return result


def run(output, *, spec_path=SPEC, run_map=True):
    """Restart by exact request identity. Budget failure never becomes a pass."""
    output = Path(output)
    spec = tomllib.loads(Path(spec_path).read_text())
    if spec['schema'] != 'osr-passive-suspension-campaign/1' or spec['purpose'] != 'next-experiment':
        raise ValueError('Bounded next-experiment specification required')
    src = sources()
    # Custom specifications participate in the evaluation identity and run ID.
    campaign_id = identity(dict(spec=spec, sources=src, environment=environment(), run_map=run_map))
    registry = ImmutableRegistry(output/'registry')
    benchmark_path=output/'method-benchmarks.json'
    if benchmark_path.exists():
        benchmark=json.loads(benchmark_path.read_bytes())
        if benchmark.get('source_sha256')!=fields.sources():raise ValueError('Method benchmark sources differ')
    else:
        benchmark=fields.benchmarks()
        _write(benchmark_path,benchmark)
    if benchmark.get('numerical_method_benchmark_pass') is not True:
        raise ValueError('Independent analytical method benchmarks failed; candidate campaign refused')
    definitions = geometry.bounded_variants()
    # A declared revision tests the facing-overlap compromise and a longer
    # coupon. It does not silently change car length, passenger load or route.
    revisions = [geometry.candidate('B', {'facing_width_m':.40}),
                 geometry.candidate('B', {'facing_width_m':.40, 'length_x_m':1.2}),
                 geometry.candidate('B', {'facing_width_m':.50, 'length_x_m':1.2,
                                         'pole_width_m':.16, 'pm_thickness_m':.08})]
    for i, value in enumerate(revisions):
        value['sample_id'] = ('B/revised-overlap', 'B/revised-longer-module','B/revised-area-and-ferrite')[i]
    definitions += revisions
    if len(definitions) > spec['maximum_physical_candidates']:
        raise ValueError('Physical candidate budget exceeded')
    candidates, results, reports = [], [], []
    parent = None
    for value in definitions:
        candidate = common_candidate(value, spec['requirement_revision'],
            parent_ids=[parent] if 'revised' in value['sample_id'] and parent else [])
        if value['sample_id'] == 'B/edge-facing':
            parent = candidate['candidate_id']
        candidates.append(candidate)
        registry.store('candidate', candidate)
        _write(output/'candidates'/(candidate['candidate_id']+'.json'),candidate)
        _write(output/'geometry'/(candidate['candidate_id']+'.json'),value)
        report=mechanical_report(value,candidate)
        mass=report['mass_comparison'];reserve=report['support_reserve_floor_N_per_module']
        def calculate(request):
            try:
                point = fields.solve(value, gap_m=value['reference_gap_m'], temperature_C=20., settings=spec['fields'])
            except ValueError as exc:
                return make_result(request,execution_status='error',numerical_status='invalid',screen_status='unknown',
                    metrics=dict(negative_reference_support_ratio=None,
                        known_train_stock_tonnes_per_car=value['stock']['train_known_mass_kg_per_car']/1000),
                    diagnostics=[dict(kind='field-refusal',reason=str(exc))])
            usable = point['interpolation_usable']
            lift = point['F_z_N']
            # These are zero-current reference-gap results, not an authority or
            # integrated acceptance screen at every possible controlled gap.
            constraint_state = 'fail' if usable and lift < reserve else 'unknown'
            return make_result(request,execution_status='executed',
                numerical_status='converged' if usable else 'nonconverged',
                screen_status='fail' if constraint_state=='fail' else 'unknown', maturity='numerical-screen',
                metrics=dict(reference_F_z_N=lift, reference_F_y_N=point['F_y_N'],
                             negative_reference_support_ratio=-lift/reserve if usable else None,
                             known_train_stock_tonnes_per_car=value['stock']['train_known_mass_kg_per_car']/1000),
                constraints=[dict(id='reference-zero-current-reserve', state=constraint_state, value_N=lift, required_floor_N=reserve),
                             dict(id='installed-coupled-3D-qualified',state='unknown')],
                diagnostics=[dict(kind='field-point',value=point)])
        result = _record(registry,candidate,'transverse-reference',calculate,src=src,
            scenario=dict(gap_m=value['reference_gap_m'],temperature_C=20.,currents_A={},lateral_m=0.,roll_rad=0.,
                          load_reserve_floor_N_per_module=reserve,mass_comparison_sha256=identity(mass)),
            settings=spec['fields'],hypothesis=dict(material='linear-steel-mur1000-bound',spatial='infinite-travel-2D'))
        results.append(result)
        report['reference_evaluation_id']=result['evaluation_id']
        report['reference_field']=result['diagnostics'][0].get('value')
        report['reference_execution_status']=result['execution_status']
        report['reference_numerical_status']=result['numerical_status']
        reports.append(report)
    policy = {k:spec['selection'][k] for k in ('policy_id','objectives')}
    next_selection = select(candidates,results,purpose='next-experiment',policy=policy)
    integrated = select(candidates,results,purpose='integrated-baseline',policy=dict(policy,
        critical_evaluators=['transverse-reference','coupled-installed-system'], minimum_maturity='coupled-numerical'))
    registry.store('selection',next_selection); registry.store('selection',integrated)
    selected_id = next_selection['selected_candidate_id']
    selected_index = next((i for i,c in enumerate(candidates) if c['candidate_id']==selected_id),None)
    if selected_index is not None:
        value=definitions[selected_index]
        primary=next(r for r in results if r['candidate_id']==selected_id)
        check_request=make_evaluation_request(candidates[selected_index],evaluator_id='transverse-additional-points',
            evaluator_sources=src,purpose='confirmation',environment=environment(),
            hypothesis=dict(material='linear-steel-mur1000-bound',spatial='infinite-travel-2D'),
            settings=dict(spec['fields'],confirmation_of=primary['evaluation_id'],
                          verification_scope='additional-points-same-evaluator'),
            scenario=dict(points=[dict(gap_m=.004,lateral_m=0.,temperature_C=20.),
                                  dict(gap_m=.012,lateral_m=-.006,temperature_C=50.),
                                  dict(gap_m=.012,lateral_m=.006,temperature_C=50.)]))
        checked=registry.cached(check_request)
        if checked is None:
            registry.store('evaluation-request',check_request)
            points=[fields.solve(value,settings=spec['fields'],**p) for p in check_request['scenario']['points']]
            checked=make_result(check_request,execution_status='executed',
                numerical_status='converged' if all(p['interpolation_usable'] for p in points) else 'nonconverged',
                screen_status='unknown',maturity='numerical-screen',
                diagnostics=[dict(kind='additional-points',points=points,
                    scope='Same evaluator/material model at additional scenarios; not independent domain confirmation')])
            registry.store('evaluation',checked)
        results.append(checked)
        nonlinear_settings=dict(spec['fields'],steel_model='nonlinear_repo_proxy')
        def nonlinear(request):
            point=fields.solve(value,gap_m=value['reference_gap_m'],temperature_C=20.,settings=nonlinear_settings)
            return make_result(request,execution_status='executed',
                numerical_status='converged' if point['interpolation_usable'] else 'nonconverged',
                screen_status='unknown',maturity='numerical-screen',
                diagnostics=[dict(kind='nonlinear-material-sensitivity',value=point,
                    scope='Same physical geometry; retained material-curve proxy lacks measured solid-facing DC correlation')])
        results.append(_record(registry,candidates[selected_index],'transverse-material-sensitivity',nonlinear,src=src,
            settings=nonlinear_settings,scenario=dict(gap_m=value['reference_gap_m'],temperature_C=20.,currents_A={}),
            hypothesis=dict(material='retained-nonlinear-proxy-unqualified-for-solid-facing-DC',spatial='infinite-travel-2D')))
    selected_map, control_report = None, dict(execution_status='not-run',reason='Map explicitly disabled')
    if run_map and selected_index is not None:
        value = definitions[selected_index]
        map_settings = dict(spec['fields'], max_solves=spec['maximum_map_solves'])
        map_request = make_evaluation_request(candidates[selected_index], evaluator_id='transverse-map', evaluator_sources=src,
            hypothesis=dict(material='linear-steel-mur1000-bound',spatial='infinite-travel-2D',
                common_current_port={'damping--1':1.,'damping-1':1.},
                electrical_scope='Equivalent series-terminal perturbation; installed wiring/converter topology unresolved'),
            settings=map_settings,scenario=spec['map'],environment=environment(),purpose='next-experiment')
        map_path=output/'maps'/(map_request['evaluation_id']+'.json')
        registry.store('evaluation-request',map_request)
        if map_path.exists():
            selected_map=json.loads(map_path.read_bytes())
            _validate_map(selected_map,map_request,value)
            cached_map=registry.cached(map_request)
            if cached_map is not None and cached_map['diagnostics'][0]['sha256']!=sha256(map_path.read_bytes()).hexdigest():
                raise ValueError('Cached map lacks its exact immutable evaluation receipt')
        else:
            selected_map=fields.field_map(value,**spec['map'],settings=map_settings,
                series_circuits={'damping--1':1.,'damping-1':1.}, circuit_id='lift-series')
            _write(map_path, selected_map)
        map_result=make_result(map_request,execution_status='executed',
            numerical_status='converged' if selected_map['interpolation_usable'] else 'nonconverged',
            screen_status='unknown',maturity='numerical-screen',
            diagnostics=[dict(kind='map-artifact',path=map_path.relative_to(output).as_posix(),
                              sha256=sha256(map_path.read_bytes()).hexdigest(),map_id=selected_map['map_id'])],
            constraints=[dict(id='integrated-coupled-qualification',state='unknown')])
        registry.store('evaluation',map_result);results.append(map_result)
        control_report = analyse_controls(selected_map,reports[selected_index])
    if sources()!=src:
        raise ValueError('Campaign source changed; retained numerical cache remains identity-bound, publication refused')
    summary=dict(schema='osr-passive-suspension-campaign-result/1',campaign_id=campaign_id,
        specification=spec,source_sha256=src,environment=environment(),source_unchanged=True,
        execution_options=dict(run_map=run_map),
        candidate_ids=[c['candidate_id'] for c in candidates],evaluation_ids=[r['evaluation_id'] for r in results],
        reports=reports,next_experiment=next_selection,integrated_selection=integrated,
        numerical_method_benchmarks=benchmark,
        map_id=selected_map['map_id'] if selected_map else None,controls=control_report,
        solved_physical_candidates=len(candidates), selection_is_global_optimum=False,
        complete_journey_executed=False,passive_static_levitation_established=False,
        travel_drag_N=None,installed_cost=None,physical_tests_executed=False,**FLAGS)
    summary['result_sha256']=identity(summary)
    _write(output/'summary.json',summary)
    return summary


def analyse_controls(field_map, report):
    """No extrapolation, stable-pass invention or unknown-zero substitutions."""
    result=dict(execution_status='held',map_id=field_map['map_id'], map_interpolation_usable=field_map['interpolation_usable'],
                service_context=controls.SERVICE_CONTEXT, equilibrium=[],loss_statistics=None,
                closed_loop_simulation=None,passive_shunt_damping=None,
                reason='Missing converged map, demonstrated authority or installed thermal/control equipment',**FLAGS)
    # Bracket necessary zero-current force balance using checked POINT forces.
    # An unresolved derivative still blocks interpolation, equilibrium and all
    # controller credit. These intervals do not imply stable levitation.
    records={p['result_id']:p for p in field_map['solve_records']}
    brackets=[]
    for temperature in field_map['axes']['temperature_C']:
        rows=sorted((row for row in field_map['rows'] if row['current_A']==0 and row['lateral_m']==0
                     and row['temperature_C']==temperature and records[row['result_id']]['interpolation_usable']),
                    key=lambda row:row['gap_m'])
        loads=[('tare-material-floor',report['mass_comparison']['material_subtotal_tare_kg_per_car']*G/report['units_per_car']),
               ('AW3-material-floor',report['support_load_material_floor_N_per_module']),
               ('1.3-AW3-material-floor',report['support_reserve_floor_N_per_module'])]
        for name,load in loads:
            pairs=[dict(gaps_m=[a['gap_m'],b['gap_m']],forces_N=[a['F_z_N'],b['F_z_N']])
                   for a,b in zip(rows,rows[1:]) if (a['F_z_N']-load)*(b['F_z_N']-load)<=0]
            brackets.append(dict(temperature_C=temperature,load_case=name,load_N=load,intervals=pairs,
                                 scope='Checked point-force brackets only; no equilibrium, stability, control or installed-mass acceptance'))
    result['force_only_load_brackets']=brackets
    try:
        controls.FieldMap(field_map)
    except controls.MapUnavailable as exc:
        result['reason']=str(exc)
        return result
    for temperature in field_map['axes']['temperature_C']:
        for factor in (1.,1.3):
            load=report['support_load_material_floor_N_per_module']*factor
            equilibrium=controls.zero_current_equilibria(field_map,load,temperature_C=temperature)
            result['equilibrium'].append(dict(temperature_C=temperature,load_factor=factor,load_N=load,result=equilibrium))
    result['execution_status']='executed'
    result['reason']='Equilibrium search completed inside conditional 2D map; installed and coupled fault qualification remain open'
    return result


def _validate_map(data,request,value):
    if data['map_id']!=fields._digest({k:v for k,v in data.items() if k!='map_id'}):
        raise ValueError('Field map internal identity differs')
    if data['source_sha256']!=fields.sources() or data['geometry_id']!=fields._digest(value):
        raise ValueError('Field map source or physical geometry differs')
    axes=dict(zip(controls.AXES,(request['scenario'][key] for key in ('gaps_m','laterals_m','currents_A','temperatures_C'))))
    if data['axes']!=axes:raise ValueError('Field map scenario axes differ')
    if data['series_circuits']!=request['hypothesis']['common_current_port']:
        raise ValueError('Equivalent current-port connection differs')
    expected_settings=fields._settings(request['settings'])
    for record in data['solve_records']:
        observed=record['diagnostics'].get('requested_settings',record['settings'])
        if observed!=expected_settings or record['source_sha256']!=fields.sources() or record['geometry_id']!=fields._digest(value):
            raise ValueError('Field map constituent settings/source/geometry differ')


def verify(output):
    output=Path(output);summary=json.loads((output/'summary.json').read_bytes())
    if summary['result_sha256']!=identity({k:v for k,v in summary.items() if k!='result_sha256'}):
        raise ValueError('Campaign summary payload differs')
    if summary['source_sha256']!=sources():raise ValueError('Retained campaign evaluator sources differ')
    if any(summary.get(flag) is not False for flag in FLAGS):raise ValueError('Campaign cannot assert acceptance')
    if any(summary.get(flag) is not False for flag in ('complete_journey_executed','passive_static_levitation_established','physical_tests_executed')):
        raise ValueError('Unexecuted physical or integrated evidence cannot be promoted')
    expected_id=identity(dict(spec=summary['specification'],sources=summary['source_sha256'],
        environment=summary['environment'],run_map=summary['execution_options']['run_map']))
    if expected_id!=summary['campaign_id']:raise ValueError('Campaign context identity differs')
    for candidate_id in summary['candidate_ids']:
        candidate=json.loads((output/'candidates'/(candidate_id+'.json')).read_bytes())
        validate_candidate(candidate)
        if candidate['candidate_id']!=candidate_id:raise ValueError('Mixed candidate package')
        value=json.loads((output/'geometry'/(candidate_id+'.json')).read_bytes())
        expected=common_candidate(value,candidate['requirement_revision'],parent_ids=candidate['lineage']['parent_candidate_ids'])
        if expected!=candidate:raise ValueError('Physical geometry, mass, candidate or source package differs')
    registry=ImmutableRegistry(output/'registry')
    benchmark=json.loads((output/'method-benchmarks.json').read_bytes())
    if benchmark!=summary['numerical_method_benchmarks'] or benchmark.get('source_sha256')!=fields.sources():
        raise ValueError('Retained numerical method benchmark differs')
    if benchmark.get('numerical_method_benchmark_pass') is not True:raise ValueError('Method benchmark is not passed')
    results=[registry.read('evaluation',key) for key in summary['evaluation_ids']]
    candidates=[json.loads((output/'candidates'/(key+'.json')).read_bytes()) for key in summary['candidate_ids']]
    for candidate in candidates:
        physical=registry.read('candidate',candidate['candidate_id'])
        if any(physical[key]!=candidate[key] for key in PHYSICAL_KEYS):raise ValueError('Registered physical candidate differs')
        if registry.read_context(identity(candidate))!=candidate:raise ValueError('Registered candidate context differs')
    for result in results:
        if registry.read('evaluation-request',result['evaluation_id'])!=result['request']:
            raise ValueError('Retained request and evaluation differ')
        if result['request']['evaluator_sources']!=sources():raise ValueError('Evaluation source epoch differs')
        if result['request']['environment']!=summary['environment']:raise ValueError('Mixed numerical environments')
        if result['candidate_id'] not in summary['candidate_ids']:raise ValueError('Evaluation belongs to a different candidate')
        if result['request']['evaluator_id']=='transverse-map':
            artifact=result['diagnostics'][0]
            path=output/artifact['path']
            if Path(artifact['path']).is_absolute() or '..' in Path(artifact['path']).parts or path.is_symlink():
                raise ValueError('Ordinary owned map artifact required')
            data=json.loads(path.read_bytes())
            if sha256(path.read_bytes()).hexdigest()!=artifact['sha256'] or data['map_id']!=artifact['map_id'] or data['map_id']!=summary['map_id']:
                raise ValueError('Retained field map content differs')
            value=json.loads((output/'geometry'/(result['candidate_id']+'.json')).read_bytes())
            _validate_map(data,result['request'],value)
            if summary['controls']!=analyse_controls(data,next(row for row in summary['reports'] if row['candidate_id']==result['candidate_id'])):
                raise ValueError('Controls do not derive from selected field map')
    primary=[r for r in results if r['request']['evaluator_id']=='transverse-reference']
    for name,purpose in (('next_experiment','next-experiment'),('integrated_selection','integrated-baseline')):
        expected=select(candidates,primary,purpose=purpose,policy=summary[name]['policy'])
        if expected!=summary[name] or registry.read('selection',expected['selection_id'])!=expected:
            raise ValueError('Selection does not derive from retained candidates and evaluations')
    for report in summary['reports']:
        candidate=next(c for c in candidates if c['candidate_id']==report['candidate_id'])
        value=json.loads((output/'geometry'/(candidate['candidate_id']+'.json')).read_bytes())
        expected=mechanical_report(value,candidate)
        if any(report.get(key)!=item for key,item in expected.items()):
            raise ValueError('Mechanical/stock/load report differs from physical definition')
        if report['mass_comparison']!=geometry.replacement_mass_comparison(value):raise ValueError('Retained mass replacement differs')
        if report['stock']!=value['stock']:raise ValueError('Retained stock subtotal differs')
        load=report['mass_comparison']['material_subtotal_aw3_kg_per_car']*G/value['units_per_car']
        if report['support_load_material_floor_N_per_module']!=load or report['support_reserve_floor_N_per_module']!=1.3*load:
            raise ValueError('Load reserve differs from counted vehicle material floor')
        field=registry.read('evaluation',report['reference_evaluation_id'])['diagnostics'][0].get('value')
        if report['reference_field']!=field:raise ValueError('Reference field differs from evaluation')
    if summary['integrated_selection']['selected_candidate_id'] is not None:
        raise ValueError('Incomplete campaign cannot publish an integrated design')
    return dict(verified=True,campaign_id=summary['campaign_id'],physical_accepted=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['run','verify'])
    parser.add_argument('--output',type=Path,default=ROOT/'build/passive-suspension/campaign')
    parser.add_argument('--skip-map',action='store_true')
    args=parser.parse_args()
    value=run(args.output,run_map=not args.skip_map) if args.action=='run' else verify(args.output)
    print(json.dumps({k:value[k] for k in ('campaign_id','verified','solved_physical_candidates') if k in value},indent=2))


if __name__=='__main__':main()
