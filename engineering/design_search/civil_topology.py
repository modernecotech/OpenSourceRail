"""Bounded civil material-distribution experiments with separate binary replay.

The optimizer's soft-void density field is numerical evidence. Only its explicit
binary realization defines stock. No selected railway or physical gate changes.
"""
from __future__ import annotations

import argparse
import importlib
from copy import deepcopy
import fcntl
import gzip
import json
from math import ceil, fsum, isfinite
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import tomllib

import numpy as np
import scipy

from engineering import mass_reserve_sensitivity
from engineering.development_baseline import selection
from engineering.station_rail import ROOT, civil
from engineering.station_rail.common import digest, encoded, identity
from . import civil_shape_mechanics, model_cost, portable_gzip
from . import topology_optimisation as kernel, topology_geometry as geometry, topology_cost

PRODUCER = 'engineering/design_search/civil_topology.py'
CAMPAIGN = 'campaigns/civil-topology.toml'
OUTPUT = 'docs/design-engine/civil-topology'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, selected_reference_changed=False,
    manufacturing_release=False, operating_release=False)


def _sealed(record, key):
    if record.get(key) != identity({k: v for k, v in record.items() if k != key}):
        raise ValueError('Topology identity differs: ' + key)


def _json(value):
    if isinstance(value, np.ndarray):
        return _json(value.tolist())
    if isinstance(value, np.generic):
        return _json(value.item())
    if isinstance(value, dict):
        return {key: _json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json(item) for item in value]
    if isinstance(value, float) and not isfinite(value):
        raise ValueError('Nonfinite topology result cannot be published')
    return value


def specification(root=ROOT):
    value = tomllib.loads((Path(root)/CAMPAIGN).read_text())
    if (value.get('schema') != 'osr-civil-topology-campaign/1'
            or value.get('purpose') != 'next-experiment'
            or value.get('reference_changes_allowed') is not False
            or value.get('maximum_trials') != 7 or value.get('maximum_optimized_trials') != 6
            or value.get('initial_fields') != ['uniform', 'longitudinal-wave']
            or value.get('realization_threshold') != .5
            or value.get('same_geometry_refinement_factor') != 2):
        raise ValueError('Explicit bounded non-promoting topology study required')
    for table, names in ((value['search'], ('filter_radius_m', 'passive_edge_band_m', 'passive_end_block_m',
            'wheel_load_patch_length_m', 'bearing_patch_length_m', 'penalty', 'move_limit',
            'physical_density_change_tolerance', 'minimum_stiffness_ratio', 'minimum_stiffness_check_ratio')),
            (value['elastic_hypotheses'], ('steel_E_Pa', 'steel_poisson', 'steel_density_kg_m3', 'concrete_density_kg_m3')),
            (value['replay'], ('relative_linear_residual_tolerance', 'relative_equilibrium_tolerance',
                'relative_energy_tolerance', 'two_mesh_compliance_change_target')),
            (value['publication'], ('replay_relative_tolerance', 'replay_absolute_tolerance'))):
        if any(type(table.get(name)) not in (int, float) or not isfinite(table[name]) for name in names):
            raise ValueError('Finite numeric topology parameters required')
    fixed = dict(geometry.FIXED)
    fixed['web_centres_y_m'] = list(fixed['web_centres_y_m'])
    if value.get('geometry') != fixed:
        raise ValueError('Topology study must retain its explicit paired-web/deck envelope')
    search = value['search']; limits = value['resources']; replay = value['replay']
    if (type(search['nx']) is not int or type(search['nz']) is not int
            or not 20 <= search['nx'] <= 320 or not 4 <= search['nz'] <= 24
            or search['nx']*search['nz'] > 7680
            or type(search['maximum_iterations']) is not int or not 1 <= search['maximum_iterations'] <= 200
            or search['pose_controls'] != ['quarter-span-moment', 'midspan-moment', 'left-support-reaction']
            or search['optimization_load_case'] != 'crowd_control'
            or search['optimization_dead_load'] != 'full-solid-web-and-upper-account-reserves-at-top-edge'
            or not 0 < search['filter_radius_m'] <= 1.
            or not 0 < search['passive_edge_band_m'] < .6
            or not 0 < search['passive_end_block_m'] < 10.
            or value['geometry']['web_height_m']/search['nz'] > search['passive_edge_band_m']+1e-12
            or value['geometry']['span_m']/search['nx'] > search['passive_end_block_m']+1e-12
            or not 0 < search['wheel_load_patch_length_m'] <= 1.
            or not 0 < search['bearing_patch_length_m'] <= search['passive_end_block_m']
            or not 1. <= search['penalty'] <= 8.
            or not 0 < search['move_limit'] <= 1.
            or not 0 < search['physical_density_change_tolerance'] <= .1
            or not 0 < search['minimum_stiffness_ratio'] <= search['minimum_stiffness_check_ratio'] < .01):
        raise ValueError('Topology grid, search/load or passive-material domain differs')
    if (len(value['volume_fractions']) != 3 or any(type(v) not in (int, float)
            or not isfinite(v) or not .2 <= v <= 1 for v in value['volume_fractions'])
            or sorted(set(value['volume_fractions'])) != value['volume_fractions']):
        raise ValueError('Three finite increasing total-volume targets required')
    if (any(type(limits[key]) is not int for key in ('workers', 'native_jobs', 'requested_blas_threads',
            'maximum_trial_wall_seconds', 'optimization_runtime_seconds', 'maximum_address_space_bytes', 'maximum_cpu_seconds',
            'maximum_rhs', 'replay_rhs'))
            or limits['workers'] != 1 or limits['native_jobs'] != 0 or limits['requested_blas_threads'] != 1
            or not 1 <= limits['optimization_runtime_seconds'] <= limits['maximum_trial_wall_seconds'] <= 300
            or not 256*1024**2 <= limits['maximum_address_space_bytes'] <= 2*1024**3
            or not 1 <= limits['maximum_cpu_seconds'] <= 300
            or limits['maximum_rhs'] != 128 or limits['replay_rhs'] != 81
            or replay['load_cases'] != ['empty', 'normal', 'crowd_control']
            or replay['mass_cases'] != ['low', 'base', 'high']
            or replay['void_stiffness_credited'] is not False
            or replay['physical_acceptance_limit_available'] is not False
            or value['elastic_hypotheses']['concrete_stiffness_credited'] is not False
            or value['elastic_hypotheses']['equal_web_load_sharing_qualified'] is not False):
        raise ValueError('Explicit resource, load/mass and unqualified model boundaries required')
    for table in (value['elastic_hypotheses'], search, replay, value['publication']):
        if any(type(v) in (int, float) and not isfinite(v) for v in table.values()):
            raise ValueError('Finite topology hypotheses required')
    elastic = value['elastic_hypotheses']
    if (not 1e3 <= elastic['steel_E_Pa'] <= 1e13 or not -1 < elastic['steel_poisson'] < .5
            or any(not 1 <= elastic[key] <= 1e6 for key in ('steel_density_kg_m3', 'concrete_density_kg_m3'))
            or any(not 0 < replay[key] <= 1e-3 for key in ('relative_linear_residual_tolerance',
                'relative_equilibrium_tolerance', 'relative_energy_tolerance'))
            or not 0 < replay['two_mesh_compliance_change_target'] < 1.
            or not 0 < value['publication']['replay_relative_tolerance'] <= 1e-6
            or not 0 < value['publication']['replay_absolute_tolerance'] <= 1e-6):
        raise ValueError('Elastic or numerical tolerance construction domain differs')
    return value


def load_context(root=ROOT):
    base = civil_shape_mechanics.load_context(root)
    reserve = mass_reserve_sensitivity.plan(root)
    selected = selection.load(root)['vehicle']
    if (base['vehicle_candidate_id'] != reserve['candidate_id']
            or base['selection_id'] != reserve['selection_id']
            or selected['candidate_id'] != base['vehicle_candidate_id']
            or selected['evaluation_id'] != base['vehicle_evaluation_id']):
        raise ValueError('Topology vehicle and mass-reserve candidates differ')
    cases = []
    passengers = dict(empty=0, normal=46, crowd_control=160)
    for mass in reserve['sensitivity_cases']:
        for case in base['cases']:
            loaded = mass['scenario_tare_mass_kg_per_car'] + 75.*passengers[case['name']]
            force = loaded*civil.G/4*base['dynamic_factor_hypothesis']
            cases.append(dict(name=case['name'], vehicle_mass_case=mass['name'],
                tare_kg_per_car=mass['scenario_tare_mass_kg_per_car'], loaded_kg_per_car=loaded,
                full_axle_force_N=force, offsets_m=deepcopy(case['offsets_m'])))
    value = dict(schema='osr-topology-train-load-context/1',
        selected_context_id=base['context_id'], vehicle_candidate_id=base['vehicle_candidate_id'],
        vehicle_evaluation_id=base['vehicle_evaluation_id'], selection_id=base['selection_id'],
        **{key: selected[key] for key in ('body_candidate_id', 'support_component_id', 'propulsion_component_id')},
        mass_reserve_result_id=reserve['result_id'], mass_cases_complete_installed=False,
        dynamic_factor_applied_once=base['dynamic_factor_hypothesis'], cases=cases,
        source_sha256={**base['source_sha256'], **reserve['source_sha256'],
            PRODUCER: digest(Path(root)/PRODUCER)}, **FLAGS)
    value['context_id'] = identity(value)
    return value


def sources(root=ROOT, context=None):
    root = Path(root); context = load_context(root) if context is None else context
    names = [PRODUCER, CAMPAIGN, 'engineering/design_search/topology_optimisation.py',
        'engineering/design_search/topology_geometry.py', 'engineering/design_search/topology_cost.py',
        'engineering/design_search/civil_shape_mechanics.py', 'engineering/station_rail/civil.py',
        'engineering/mass_reserve_sensitivity.py', 'engineering/station_rail/common.py',
        'engineering/design_search/portable_gzip.py']
    if (root/'engineering/design_search/topology_system_cost.py').is_file():
        names.append('engineering/design_search/topology_system_cost.py')
    result = {**context['source_sha256'], **model_cost.sources(root),
        **{name: digest(root/name) for name in names}}
    if any(digest(root/name) != expected for name, expected in result.items()):
        raise ValueError('Topology context contains stale producer bytes')
    return result


def critical_pose(span, offsets, objective):
    """Exact extrema of a piecewise-linear ideal support/moment influence."""
    if objective not in ('quarter-span-moment', 'midspan-moment', 'left-support-reaction'):
        raise ValueError('Explicit representative influence control required')
    section = span/4 if objective == 'quarter-span-moment' else span/2
    points = (0., span) if objective == 'left-support-reaction' else (0., section, span)
    candidates = sorted({round(x-offset, 12) for offset in offsets for x in points})
    def coefficient(x):
        if x < -1e-10 or x > span+1e-10:
            return 0.
        x = min(span, max(0., x))
        if objective == 'left-support-reaction':
            return (span-x)/span
        return ((span-section)*x/span if x <= section else section*(span-x)/span)
    scored = [(fsum(coefficient(offset+t) for offset in offsets), t) for t in candidates]
    score, translation = min(scored, key=lambda row: (-round(row[0], 12), row[1]))
    return dict(name=objective, translation_m=translation, influence_coefficient=score,
        scope='Representative ideal-beam influence pose only; not topology-critical compliance, stress or journey envelope')


def mesh(spec, factor=1):
    g = spec['geometry']; e = spec['elastic_hypotheses']; s = spec['search']
    return kernel.mesh(dict(nx=s['nx']*factor, nz=s['nz']*factor,
        length_m=g['span_m'], height_m=g['web_height_m'],
        thickness_m=2*g['web_thickness_m'], E_Pa=e['steel_E_Pa'], poisson=e['steel_poisson']))


def fixed_dofs(problem):
    # Finite mean bearing constraints supply the supports; no point node clamp.
    return np.array([], dtype=np.int64)


def line_weights(problem, lower, upper):
    """Integrate linear edge shape functions over a fixed physical interval."""
    nx = problem['specification']['nx']; span = problem['specification']['length_m']; dx = span/nx
    if not 0 <= lower < upper <= span:
        raise ValueError('Positive in-span edge interval required')
    result = np.zeros(nx+1)
    for i in range(nx):
        x0, x1 = i*dx, (i+1)*dx
        a, b = max(lower, x0), min(upper, x1)
        if b <= a:
            continue
        # Shift to the cell origin before integration to avoid cancellation.
        u, v = (a-x0)/dx, (b-x0)/dx
        right = dx*(v*v-u*u)/2
        result[i] += b-a-right; result[i+1] += right
    return result


def support_constraints(problem, spec):
    span = problem['specification']['length_m']; width = spec['search']['bearing_patch_length_m']
    left = line_weights(problem, 0., width)/width
    right = line_weights(problem, span-width, span)/width
    C = np.zeros((3, problem['ndof']))
    C[0, 2*np.arange(len(left))] = left
    C[1, 2*np.arange(len(left))+1] = left
    C[2, 2*np.arange(len(right))+1] = right
    return C


def top_load(problem, points, distributed_N_m=0.):
    """Consistent finite-patch loading preserves its force and first moment."""
    s = problem['specification']; nx = s['nx']; L = s['length_m']; dx = L/nx
    result = np.zeros(problem['ndof']); first = s['nz']*(nx+1)
    for point in points:
        x, force = float(point['x_m']), float(point['force_N'])
        if not isfinite(x) or not isfinite(force) or not 0 <= x <= L or force < 0:
            raise ValueError('Finite in-span downward axle loads required')
        if 'x_min_m' in point:
            weights = line_weights(problem, point['x_min_m'], point['x_max_m'])
            result[2*(first+np.arange(nx+1))+1] -= force*weights/(point['x_max_m']-point['x_min_m'])
            continue
        i = min(nx-1, int(x/dx)); fraction = (x-i*dx)/dx
        result[2*(first+i)+1] -= force*(1-fraction)
        result[2*(first+i+1)+1] -= force*fraction
    for i in range(nx):
        result[2*(first+i)+1] -= distributed_N_m*dx/2
        result[2*(first+i+1)+1] -= distributed_N_m*dx/2
    return result


def _points(case, pose, span, patch_length):
    values = []
    for offset in case['offsets_m']:
        x = offset+pose['translation_m']; lower, upper = max(0., x-patch_length/2), min(span, x+patch_length/2)
        if upper > lower:
            values.append(dict(x_m=(lower+upper)/2, x_min_m=lower, x_max_m=upper,
                axle_centre_x_m=x, force_N=case['full_axle_force_N']*(upper-lower)/patch_length,
                on_span_patch_fraction=(upper-lower)/patch_length))
    return values


def _rail_account(span):
    sets = 2*(ceil(span/.6)+1)
    return dict(rail_kg=2*60.21*span, complete_fastener_sets=sets,
        complete_fastener_account_kg=8.*sets, included_in_plate_cost=False,
        compatibility_qualified=False)


def support_demands(candidate, quantity, baseline, spec):
    """Conservative gravity sizing demands; no site or bearing resistance."""
    geometry.validate(candidate)
    _sealed(quantity, 'evaluation_id'); _sealed(baseline, 'baseline_id')
    context = baseline['load_context']; _sealed(context, 'context_id')
    span = spec['geometry']['span_m']; width = spec['search']['bearing_patch_length_m']
    rail = _rail_account(span)
    # The finite mean supports lie at width/2 and span-width/2. Scaling the
    # ideal triangular influence majorizes its positive part, including the
    # end overhangs. A uniform axle patch cannot exceed the point-train
    # translation supremum, because it is an average of translations.
    amplification = (span-width/2)/(span-width)
    cases = {name: dict(load_cases={}) for name in model_cost.CASES}
    for vehicle in context['cases']:
        live = civil.interior_pier_train_reaction(span, vehicle['offsets_m'], vehicle['full_axle_force_N'])
        live_bound = live['maximum_live_reaction_N']*amplification
        costs = {}
        for i, mass_case in enumerate(model_cost.CASES):
            mass = quantity['accounted_mass_kg_cases'][i]+rail['rail_kg']+rail['complete_fastener_account_kg']
            dead = mass*civil.G
            reaction = dead+live_bound
            costs[mass_case] = dict(accounted_span_mass_kg=mass,
                per_span_gravity_N=dead, adjacent_span_dead_reaction_N=dead,
                live_reaction_upper_N=live_bound,
                interior_support_vertical_reaction_N=reaction,
                minimum_gravity_bearing_area_m2_by_pressure_kpa={str(p): reaction/(p*1000.) for p in (300, 200, 100)},
                unknown_pier_selfweight=True, unknown_footing_selfweight=True,
                settlement_lateral_seismic_uplift_qualified=False,
                actual_footing_or_pile_quantity=None)
        cases[vehicle['vehicle_mass_case']]['load_cases'][vehicle['name']] = dict(financial_cases=costs)
    value = dict(schema='osr-topology-support-demands/1',
        candidate_id=candidate['candidate_id'], geometry_id=candidate['geometry_id'],
        quantity_evaluation_id=quantity['evaluation_id'], baseline_id=baseline['baseline_id'],
        selected_vehicle_candidate_id=context['vehicle_candidate_id'], load_context_id=context['context_id'],
        cases=cases, source_sha256=baseline['source_sha256'],
        finite_bearing_positive_influence_amplification=amplification,
        dead_reaction_basis='One complete span weight at an interior support between two identical adjacent spans, not two full span weights',
        area_basis='Necessary gravity area from provisional pressures only; excludes pier/footing weight, eccentricity, settlement, lateral and site actions',
        tracks_basis='One trackway support; shared two-track pier arrangement is undefined',
        physical_screen='provisional-gravity-sizing-only', **FLAGS)
    value['evaluation_id'] = identity(value)
    return value


def _passive(problem, spec):
    centres = problem['element_centres']; s = spec['search']; g = spec['geometry']
    return ((centres[:, 0] < s['passive_end_block_m'])
        | (centres[:, 0] > g['span_m']-s['passive_end_block_m'])
        | (centres[:, 1] < s['passive_edge_band_m'])
        | (centres[:, 1] > g['web_height_m']-s['passive_edge_band_m']))


def _initial(problem, passive, volume, radius, name):
    if name == 'uniform':
        return None
    operator = kernel.density_filter(problem, radius)
    centres = problem['element_centres']; s = problem['specification']
    shape = 1+.2*np.sin(2*np.pi*centres[:, 0]/s['length_m'])*np.cos(2*np.pi*centres[:, 1]/s['height_m'])
    low, high = 0., 2.
    for _ in range(70):
        level = (low+high)/2
        design = np.clip(level*shape, 0., 1.); design[passive] = 1.
        rho = operator@design; rho[passive] = 1.
        if float(rho.mean()) > volume:
            high = level
        else:
            low = level
    design = np.clip(low*shape, 0., 1.); design[passive] = 1.
    return design


def _summary_analysis(problem, result, rows, spec):
    if result['execution'] != 'completed':
        return _json(result)
    s = problem['specification']; displacements = result['displacements']
    summaries = []
    for i, row in enumerate(rows):
        force_scale = max(1., row['total_downward_force_N'])
        summaries.append(dict(row,
            compliance_J=float(result['compliances'][i]),
            strain_energy_J=float(result['strain_energy_J'][i]),
            maximum_absolute_displacement_m=float(np.max(np.abs(displacements[:, i]))),
            maximum_vertical_displacement_m=float(np.max(np.abs(displacements[1::2, i]))),
            free_residual_relative=float(result['free_residual_relative'][i]),
            constraint_residual_relative=float(np.max(np.abs(result['constraint_residual_relative'][:, i]))),
            relative_force_equilibrium_residual=float(np.max(np.abs(result['force_equilibrium_residual_N'][i]))/force_scale),
            relative_moment_equilibrium_residual=float(abs(result['moment_equilibrium_residual_Nm'][i])/(force_scale*s['length_m'])),
            relative_energy_residual=float(abs(result['energy_residual_J'][i])/max(1., abs(result['compliances'][i])))))
    policy = spec['replay']
    meets = all(row['free_residual_relative'] <= policy['relative_linear_residual_tolerance']
        and row['constraint_residual_relative'] <= policy['relative_linear_residual_tolerance']
        and row['relative_force_equilibrium_residual'] <= policy['relative_equilibrium_tolerance']
        and row['relative_moment_equilibrium_residual'] <= policy['relative_equilibrium_tolerance']
        and row['relative_energy_residual'] <= policy['relative_energy_tolerance'] for row in summaries)
    return dict(execution='completed', numerical_validity=(result['numerical_validity'] if meets else 'declared-numerical-residual-request-not-met'),
        cases=summaries, node_count=len(problem['nodes']), element_count=problem['nelements'],
        maximum_free_residual_relative=max(row['free_residual_relative'] for row in summaries),
        declared_residual_request_met=meets,
        constraint_residual_max=float(np.max(np.abs(result['constraint_residual']))),
        bearing_constraint='Three homogeneous finite-patch mean translations; end rotation and longitudinal expansion remain free',
        bearing_patch_m=spec['search']['bearing_patch_length_m'],
        contact_stiffness_and_load_sharing_qualified=False,
        void_stiffness_credited=False, physical_acceptance_limit_available=False, **FLAGS)


def replay(problem, occupancy, spec, context, quantities, poses):
    mask = np.asarray(occupancy, dtype=bool).ravel(); n = problem['ndof']
    rail = _rail_account(spec['geometry']['span_m']); steel_density = spec['elastic_hypotheses']['steel_density_kg_m3']
    steel_mass = float(mask.sum()*problem['element_volume_m3']*steel_density)
    if not np.isclose(steel_mass, quantities['quantities']['steel_net_mass_kg'], rtol=1e-12, atol=1e-8):
        raise ValueError('Binary FE and physical stock volumes differ')
    body_gravity = np.zeros(n)
    per_cell = problem['element_volume_m3']*steel_density*civil.G
    for nodes in problem['elements'][mask]:
        body_gravity[2*nodes+1] -= per_cell/4
    forces, labels = [], []
    for vehicle in context['cases']:
        for i, mass_case in enumerate(spec['replay']['mass_cases']):
            accounted = quantities['accounted_mass_kg_cases'][i]+rail['rail_kg']+rail['complete_fastener_account_kg']
            # Actual steel gravity follows occupied cells; all other accounted
            # gravity is an explicit top-edge UDL hypothesis, including reserves.
            top_weight = (accounted-steel_mass)*civil.G/spec['geometry']['span_m']
            for pose in poses:
                points = _points(vehicle, pose, spec['geometry']['span_m'], spec['search']['wheel_load_patch_length_m'])
                force = top_load(problem, points, top_weight)+body_gravity
                expected = accounted*civil.G+fsum(p['force_N'] for p in points)
                if not np.isclose(-force[1::2].sum(), expected, rtol=1e-12, atol=1e-7):
                    raise ValueError('Binary load/gravity accounting differs')
                nominal = quantities['quantities']['nominal_mass_kg']
                nominal_cg = quantities['quantities']['nominal_CG_m'][0]
                expected_moment = (nominal*nominal_cg+(accounted-nominal)*spec['geometry']['span_m']/2)*civil.G
                expected_moment += fsum(point['force_N']*point['x_m'] for point in points)
                actual_moment = float(np.sum(-force[1::2]*problem['nodes'][:, 0]))
                if not np.isclose(actual_moment, expected_moment, rtol=1e-12, atol=1e-6):
                    raise ValueError('Binary nodal first moment differs from physical stock CG and load patches')
                forces.append(force)
                labels.append(dict(load_case=vehicle['name'], vehicle_mass_case=vehicle['vehicle_mass_case'],
                    span_mass_case=mass_case, pose=pose['name'], accounted_span_mass_kg=accounted,
                    full_axle_force_N=vehicle['full_axle_force_N'], axle_count_on_span=len(points),
                    total_downward_force_N=expected, physical_downward_first_moment_Nm=expected_moment, live_points=points))
    result = kernel.solve_binary(problem, mask, np.column_stack(forces), fixed_dofs(problem),
        constraint_matrix=support_constraints(problem, spec))
    return result, _summary_analysis(problem, result, labels, spec)


def evaluate_trial(request, checkpoint=None, *, baseline=None):
    """Execute one explicit frozen request; process limits are set by _worker."""
    spec = request['specification']; context = request['load_context']; trial = request['trial']
    problem = mesh(spec); g = spec['geometry']; s = spec['search']
    cost_spec = request['cost_specification']; canonical = model_cost.assumptions(ROOT)
    full = geometry.realize(np.ones((s['nz'], s['nx']), dtype=bool), **g)
    densities = dict(steel=spec['elastic_hypotheses']['steel_density_kg_m3'],
        concrete=spec['elastic_hypotheses']['concrete_density_kg_m3'])
    full_q = geometry.quantities(full, densities, reserves_kg=cost_spec['reserve_mass_kg'], module_length_m=cost_spec['module_length_m'])
    rail = _rail_account(g['span_m'])
    upper_mass = full_q['accounted_mass_kg_cases'][2]+rail['rail_kg']+rail['complete_fastener_account_kg']
    selected_load = next(case for case in context['cases'] if case['name'] == 'crowd_control' and case['vehicle_mass_case'] == 'base')
    poses = [critical_pose(g['span_m'], selected_load['offsets_m'], name) for name in s['pose_controls']]
    fixed_forces = np.column_stack([top_load(problem, _points(selected_load, pose, g['span_m'], s['wheel_load_patch_length_m']), upper_mass*civil.G/g['span_m']) for pose in poses])
    if trial['kind'] == 'full-solid-reference':
        optimization = None; rho = np.ones(problem['nelements'])
    else:
        passive = _passive(problem, spec)
        optimization = kernel.optimise(problem, fixed_forces, fixed_dofs(problem), passive,
            trial['volume_fraction'], s['filter_radius_m'], s['maximum_iterations'],
            s['physical_density_change_tolerance'], spec['resources']['optimization_runtime_seconds'],
            move_limit=s['move_limit'], penalty=s['penalty'], min_stiffness_ratio=s['minimum_stiffness_ratio'],
            initial_densities=_initial(problem, passive, trial['volume_fraction'], s['filter_radius_m'], trial['initial_field']),
            constraint_matrix=support_constraints(problem, spec),
            iteration_callback=(lambda data: checkpoint('iteration-'+str(data['iteration']).zfill(4), data, {})) if checkpoint else None)
        if checkpoint:
            checkpoint('optimization', optimization, dict(density_field=optimization['densities'], design_variables=optimization['design_variables']))
        if optimization['last_analysis'] is None:
            return (dict(execution='not-run', optimization=_json(optimization), trial=trial,
                physical_geometry=None, numerical_validity='not-established', **FLAGS), {})
        rho = optimization['densities']
    mask = (rho >= spec['realization_threshold']).reshape(s['nz'], s['nx'])
    candidate = geometry.realize(mask, **g)
    quantity = geometry.quantities(candidate, densities, reserves_kg=cost_spec['reserve_mass_kg'], module_length_m=cost_spec['module_length_m'])
    cost = topology_cost.estimate(candidate, quantity, cost_spec, canonical)
    if checkpoint:
        checkpoint('realization', dict(candidate=candidate, quantities=quantity, span_cost=cost), dict(binary_occupancy=mask))
    coarse_raw, coarse = replay(problem, mask, spec, context, quantity, poses)
    if checkpoint:
        checkpoint('coarse', coarse, dict(displacements=coarse_raw.get('displacements')))
    finer = np.repeat(np.repeat(mask, 2, axis=0), 2, axis=1)
    if geometry.realize(finer, **g)['candidate_id'] != candidate['candidate_id']:
        raise ValueError('Mesh refinement changed the physical topology')
    fine_raw, fine = replay(mesh(spec, 2), finer, spec, context, quantity, poses)
    if checkpoint:
        checkpoint('fine', fine, dict(displacements=fine_raw.get('displacements')))
    changes = None
    if (coarse['execution'] == fine['execution'] == 'completed'
            and coarse['declared_residual_request_met'] and fine['declared_residual_request_met']):
        changes = [abs(a['compliance_J']-b['compliance_J'])/max(abs(b['compliance_J']), 1e-20)
            for a, b in zip(coarse['cases'], fine['cases'])]
    eps_check = []
    for epsilon in (s['minimum_stiffness_ratio'], s['minimum_stiffness_check_ratio']):
        try:
            elastic = kernel.solve(problem, rho, fixed_forces, fixed_dofs(problem), s['penalty'], epsilon,
                constraint_matrix=support_constraints(problem, spec))
            check = dict(minimum_stiffness_ratio=epsilon, execution='completed', compliance_J=elastic['compliances'].tolist(),
                maximum_linear_residual_relative=float(elastic['free_residual_relative'].max()))
        except kernel.NumericalFailure as exc:
            check = dict(minimum_stiffness_ratio=epsilon, execution='numerical-failure', reason=str(exc), physical_failure_inferred=False)
        eps_check.append(check)
        if checkpoint:
            checkpoint('epsilon-'+str(len(eps_check)), check, {})
    result = dict(schema='osr-civil-topology-trial/1', trial=trial, request_id=request['request_id'],
        load_context_id=context['context_id'], optimization=_json(optimization),
        density_field_is_physical_geometry=False, physical_geometry=candidate, quantities=quantity, span_cost=cost,
        fixed_search_dead_mass_kg_hypothesis=upper_mass, search_loads_are_density_independent=True,
        representative_poses=poses, rail_account=rail, density_minimum_stiffness_check=eps_check,
        boundary_model=dict(wheel_patch_length_m=s['wheel_load_patch_length_m'], bearing_patch_length_m=s['bearing_patch_length_m'],
            bearing_patch_intervals_m=[[0., s['bearing_patch_length_m']], [g['span_m']-s['bearing_patch_length_m'], g['span_m']]],
            ideal_equal_sharing_and_finite_mean_bearings=True, physical_contact_or_3D_admission=False),
        coarse_replay=coarse, fine_replay=fine, same_physical_geometry_refined=True,
        compliance_relative_changes=changes,
        numerical_refinement_status=('mesh-unresolved' if changes is None or max(changes) > spec['replay']['two_mesh_compliance_change_target'] else 'two-mesh-comparison-within-declared-target'),
        geometry_repaired=False, execution='completed',
        engineering_screen='unqualified-plane-model-geometry-and-cost-only',
        installed_mass_complete=False, available_propulsion_proven=False,
        material_strength_or_buckling_qualified=False, integrated_selection=None, **FLAGS)
    if baseline is not None:
        from . import topology_system_cost
        supports = support_demands(candidate, quantity, baseline, spec)
        system = topology_system_cost.compare(candidate, quantity, cost, baseline, supports, root=ROOT)
        result.update(system_cost=system, support_demands=supports,
            baseline_id=baseline['baseline_id'])
        if checkpoint:
            checkpoint('whole-system-cost', dict(system_cost=system, support_demands=supports), {})
    result['evaluation_id'] = identity(_json(result))
    raw = dict(coarse_displacements=coarse_raw.get('displacements'),
        fine_displacements=fine_raw.get('displacements'), density_field=rho.reshape(s['nz'], s['nx']),
        binary_occupancy=mask)
    return _json(result), raw


def _write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name+'.tmp')
    temporary.write_bytes(encoded(value)); temporary.replace(path)


def trials(spec):
    values = [dict(kind='full-solid-reference', volume_fraction=1., initial_field='full-solid')]
    values += [dict(kind='optimized-density', volume_fraction=volume, initial_field=initial)
        for volume in spec['volume_fractions'] for initial in spec['initial_fields']]
    for value in values:
        value['trial_id'] = identity(value)
    return values


def tool_context():
    """Observed binaries/versions; a changed tool creates another evaluation."""
    names = ('numpy._core._multiarray_umath', 'scipy.sparse.linalg._dsolve._superlu')
    files = dict(python=Path(sys.executable).resolve())
    for name in names:
        files[name] = Path(importlib.import_module(name).__file__).resolve()
    value = dict(schema='osr-civil-topology-tools/1', python_version=sys.version,
        python_implementation=sys.implementation.name, numpy_version=np.__version__, scipy_version=scipy.__version__,
        executable=str(Path(sys.executable).resolve()), environment_prefix=str(Path(sys.prefix).resolve()),
        binaries={name: dict(path=str(path), sha256=digest(path)) for name, path in files.items()},
        worker_environment=dict(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
            OPENBLAS_CORETYPE='NEHALEM', PYTHONHASHSEED='0'))
    value['tool_context_id'] = identity(value)
    return value


def plan(root=ROOT):
    root = Path(root); spec = specification(root); context = load_context(root)
    value = dict(schema='osr-civil-topology-plan/1', specification=spec,
        source_sha256=sources(root, context), load_context=context,
        tool_context=tool_context(),
        cost_specification=topology_cost.default_spec(), trials=trials(spec),
        numerical_method='Filtered fixed-load Q4 SIMP, followed by separate zero-void binary Q4 replay',
        selection_purpose='next-experiment', reference_replacement_selected=False, **FLAGS)
    value['campaign_id'] = identity(value)
    return value


def _request(configured, trial, baseline_ref=None):
    request = dict(schema='osr-civil-topology-request/1', campaign_id=configured['campaign_id'],
        trial=trial, specification=configured['specification'], load_context=configured['load_context'],
        cost_specification=configured['cost_specification'], source_sha256=configured['source_sha256'],
        tool_context=configured['tool_context'])
    if baseline_ref is not None:
        request['baseline'] = baseline_ref
    request['request_id'] = identity(request)
    return request


def _read_attempt(folder, row, configured, baseline_ref=None):
    """Completed state never substitutes for an intact immutable trial package."""
    _sealed(row, 'attempt_id')
    output = Path(folder)/'trials'/row['trial_id']
    if output.is_symlink() or not output.is_dir():
        raise ValueError('Topology completed trial directory is missing or linked')
    if json.loads((output/'attempt.json').read_bytes()) != row:
        raise ValueError('Topology state/attempt receipts differ')
    actual = {path.name: digest(path) for path in output.iterdir() if path.is_file() and path.name != 'attempt.json'}
    if (any(path.is_symlink() or not path.is_file() for path in output.iterdir())
            or actual != row['files_sha256']):
        raise ValueError('Topology completed trial payload differs')
    trial = next(t for t in configured['trials'] if t['trial_id'] == row['trial_id'])
    request = json.loads((output/'request.json').read_bytes())
    if request != _request(configured, trial, baseline_ref) or row['request_id'] != request['request_id']:
        raise ValueError('Topology completed request differs')
    for path in output.glob('checkpoint-*.json.gz'):
        data = json.loads(gzip.decompress(path.read_bytes())); _sealed(data, 'checkpoint_id')
        if data['request_id'] != request['request_id']:
            raise ValueError('Topology checkpoint belongs to another request')
    if row['returncode'] != 0:
        return None
    receipt = json.loads((output/'worker.json').read_bytes()); _sealed(receipt, 'receipt_id')
    if (row['worker_receipt_id'] != receipt['receipt_id'] or receipt['request_id'] != request['request_id']
            or receipt['tool_context'] != configured['tool_context']
            or receipt['source_sha256'] != configured['source_sha256']):
        raise ValueError('Topology worker/source/tool receipt differs')
    for name, expected in receipt['files_sha256'].items():
        if name not in actual or actual[name] != expected:
            raise ValueError('Topology worker output digest differs')
    result = json.loads(gzip.decompress((output/'result.json.gz').read_bytes()))
    if any(result.get(key) is not False for key in FLAGS):
        raise ValueError('Topology completed research cannot assert acceptance')
    if result['execution'] == 'completed':
        _sealed(result, 'evaluation_id')
        if result['request_id'] != request['request_id'] or result['trial'] != trial:
            raise ValueError('Topology result belongs to another trial')
        with np.load(output/'arrays.npz', allow_pickle=False) as arrays:
            expected_mask = arrays['density_field'] >= configured['specification']['realization_threshold']
            if not np.array_equal(expected_mask, arrays['binary_occupancy']):
                raise ValueError('Topology stored density/physical occupancy differs')
            physical = geometry.realize(arrays['binary_occupancy'], **configured['specification']['geometry'])
            if physical != result['physical_geometry']:
                raise ValueError('Topology saved arrays and physical candidate differ')
    return result


def _state(folder, root=ROOT):
    folder = Path(folder); current = plan(root); path = folder/'state.json'
    if not path.exists():
        folder.mkdir(parents=True, exist_ok=True)
        from . import topology_system_cost
        baseline = topology_system_cost.make_baseline(root, current['load_context'])
        if current != plan(root):
            raise ValueError('Topology source/tool epoch changed during baseline computation')
        baseline_path = folder/'baseline.json.gz'
        if baseline_path.exists():
            raise ValueError('Unindexed baseline exists; preserve and inspect before using another state')
        baseline_path.write_bytes(portable_gzip.compress(encoded(baseline)))
        state = dict(schema='osr-civil-topology-state/1', plan=current,
            baseline=dict(baseline_id=baseline['baseline_id'], file_sha256=digest(baseline_path)),
            pending_trial_ids=[trial['trial_id'] for trial in current['trials']], completed=[])
        _write(path, state)
    state = json.loads(path.read_bytes())
    if state.get('schema') != 'osr-civil-topology-state/1' or state.get('plan') != current:
        raise ValueError('Topology state belongs to another source/configuration; preserve it and choose a fresh directory')
    _baseline(folder, state['baseline'], root)
    expected = {trial['trial_id'] for trial in current['trials']}
    done = [row['trial_id'] for row in state['completed']]
    if (len(done) != len(set(done)) or len(state['pending_trial_ids']) != len(set(state['pending_trial_ids']))
            or set(done) & set(state['pending_trial_ids']) or set(done) | set(state['pending_trial_ids']) != expected):
        raise ValueError('Topology pending/completed trial coverage differs')
    for row in state['completed']:
        _read_attempt(folder, row, current, state['baseline'])
    return state


def _baseline(folder, reference, root=ROOT):
    from . import topology_system_cost
    path = Path(folder)/'baseline.json.gz'
    if path.is_symlink() or digest(path) != reference['file_sha256']:
        raise ValueError('Topology baseline payload differs')
    value = json.loads(gzip.decompress(path.read_bytes()))
    if value.get('baseline_id') != reference['baseline_id']:
        raise ValueError('Topology baseline identity differs')
    topology_system_cost.validate_baseline(value, root)
    return value


def _worker(request_path, output):
    request_path = Path(request_path); output = Path(output)
    request = json.loads(request_path.read_bytes()); _sealed(request, 'request_id')
    # This worker has no external solver subprocess. Resource limits apply to
    # this Python address space/CPU; they are not a filesystem/network sandbox.
    limits = request['specification']['resources']
    resource.setrlimit(resource.RLIMIT_AS, (limits['maximum_address_space_bytes'],)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (limits['maximum_cpu_seconds'],)*2)
    current = plan(ROOT)
    if {key: os.environ.get(key) for key in current['tool_context']['worker_environment']} != current['tool_context']['worker_environment']:
        raise ValueError('Topology worker thread/hash environment differs from its request')
    if (request['campaign_id'] != current['campaign_id']
            or request['source_sha256'] != current['source_sha256']
            or request['load_context'] != current['load_context']
            or request['specification'] != current['specification']
            or request['cost_specification'] != current['cost_specification']
            or request['tool_context'] != current['tool_context']
            or request['trial'] not in current['trials']):
        raise ValueError('Topology worker request differs from current exact inputs')
    started = time.monotonic()
    def checkpoint(phase, data, arrays):
        value = dict(schema='osr-civil-topology-checkpoint/1', request_id=request['request_id'], phase=phase,
            data=_json(data), **FLAGS)
        value['checkpoint_id'] = identity(value)
        path = output/('checkpoint-'+phase+'.json.gz')
        if path.exists():
            raise ValueError('Checkpoint already exists; preserve the prior phase')
        path.write_bytes(portable_gzip.compress(encoded(value)))
        values = {key: item for key, item in arrays.items() if item is not None}
        if values:
            np.savez_compressed(output/('checkpoint-'+phase+'.npz'), **values)
    baseline = _baseline(request_path.parent.parent.parent, request['baseline'])
    result, raw = evaluate_trial(request, checkpoint, baseline=baseline)
    if request['source_sha256'] != sources(ROOT, request['load_context']):
        raise ValueError('Topology source changed during the trial')
    if raw:
        np.savez_compressed(output/'arrays.npz', **{key: value for key, value in raw.items() if value is not None})
    (output/'result.json.gz').write_bytes(portable_gzip.compress(encoded(result)))
    receipt = dict(schema='osr-civil-topology-worker/1', request_id=request['request_id'],
        trial_id=request['trial']['trial_id'], campaign_id=current['campaign_id'],
        source_sha256=current['source_sha256'], elapsed_seconds=time.monotonic()-started,
        tool_context=current['tool_context'], observed_worker_environment={key: os.environ.get(key) for key in current['tool_context']['worker_environment']},
        observed_threads_after_trial=len(list(Path('/proc/self/task').iterdir())),
        max_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        limits=dict(RLIMIT_AS_bytes=resource.getrlimit(resource.RLIMIT_AS), RLIMIT_CPU_seconds=resource.getrlimit(resource.RLIMIT_CPU)),
        thread_request=dict(OPENBLAS_NUM_THREADS=os.environ.get('OPENBLAS_NUM_THREADS'), OMP_NUM_THREADS=os.environ.get('OMP_NUM_THREADS')),
        operating_system_filesystem_or_network_isolation=False, native_jobs_dispatched=0,
        files_sha256={path.name: digest(path) for path in output.iterdir()
            if path.is_file() and path.name in ('arrays.npz', 'result.json.gz')}, **FLAGS)
    receipt['receipt_id'] = identity(receipt); _write(output/'worker.json', receipt)
    return dict(completed=True, receipt_id=receipt['receipt_id'], execution=result['execution'], **FLAGS)


def run(folder, *, root=ROOT, max_trials=1):
    root = Path(root).resolve(); folder = Path(folder).resolve()
    if type(max_trials) is not int or not 0 <= max_trials <= 7:
        raise ValueError('An explicit invocation budget of zero to seven trials is required')
    folder.mkdir(parents=True, exist_ok=True)
    with (folder/'run.lock').open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state = _state(folder, root)
        configured = state['plan']; by_id = {t['trial_id']: t for t in configured['trials']}
        for trial_id in list(state['pending_trial_ids'])[:max_trials]:
            trial = by_id[trial_id]; output = folder/'trials'/trial_id
            if output.exists():
                raise ValueError('Unfinished private trial directory exists; inspect its real process and preserve evidence before retry')
            output.mkdir(parents=True)
            request = _request(configured, trial, state['baseline']); _write(output/'request.json', request)
            environment = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                OPENBLAS_CORETYPE='NEHALEM', PYTHONHASHSEED='0', PYTHONPATH=str(root))
            started = time.monotonic(); timeout = False
            with (output/'stdout.log').open('wb') as stdout, (output/'stderr.log').open('wb') as stderr:
                child = subprocess.Popen([sys.executable, '-m', 'engineering.design_search.civil_topology',
                    '_worker', str(output/'request.json'), str(output)], cwd=root, env=environment,
                    stdout=stdout, stderr=stderr, start_new_session=True)
                _write(output/'process.json', dict(pid=child.pid, request_id=request['request_id'], command='civil_topology _worker', started_at=time.time()))
                try:
                    returncode = child.wait(timeout=configured['specification']['resources']['maximum_trial_wall_seconds'])
                except subprocess.TimeoutExpired:
                    timeout = True; os.killpg(child.pid, signal.SIGKILL); returncode = child.wait()
            row = dict(trial_id=trial_id, request_id=request['request_id'], returncode=returncode,
                execution='wall-timeout' if timeout else 'worker-completed' if returncode == 0 else 'worker-failed',
                runtime_seconds=time.monotonic()-started,
                files_sha256={p.name: digest(p) for p in output.iterdir() if p.is_file()},
                physical_failure_inferred=False)
            if returncode == 0:
                receipt = json.loads((output/'worker.json').read_bytes()); _sealed(receipt, 'receipt_id')
                if receipt['request_id'] != request['request_id']:
                    raise ValueError('Worker returned another request')
                row['worker_receipt_id'] = receipt['receipt_id']
            row['attempt_id'] = identity(row)
            _write(output/'attempt.json', row)
            state['completed'].append(row); state['pending_trial_ids'].remove(trial_id)
            _write(folder/'state.json', state)
        return dict(campaign_id=configured['campaign_id'], completed=len(state['completed']),
            pending=len(state['pending_trial_ids']), failed=sum(r['returncode'] != 0 for r in state['completed']),
            selected_reference_changed=False, **{key: value for key, value in FLAGS.items() if key != 'selected_reference_changed'})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('plan', 'run', '_worker'))
    parser.add_argument('arguments', nargs='*')
    parser.add_argument('--state', type=Path, default=ROOT/'build/civil-topology')
    parser.add_argument('--max-trials', type=int, default=1)
    args = parser.parse_args(argv)
    if args.action == 'plan':
        result = plan()
    elif args.action == 'run':
        result = run(args.state, max_trials=args.max_trials)
    else:
        if len(args.arguments) != 2:
            raise ValueError('Internal worker requires exact request and private output paths')
        result = _worker(*args.arguments)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
