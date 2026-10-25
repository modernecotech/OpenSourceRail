"""Geometry, state identity and read-back guards; no train or field acceptance."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pytest

from engineering.halbach_scaling import candidates
from engineering.halbach_scaling import finite as f
from engineering.magnetic_confirmation import analysis


@pytest.fixture(scope='module')
def values():
    return candidates.candidates()


def test_pose_moves_every_train_item_without_changing_physical_definition(values):
    value = values[-1]; before = deepcopy(value)
    shifted = f.pose(value, .040)
    assert value == before and shifted['physical_id'] == value['physical_id']
    assert shifted['candidate_id'] == value['candidate_id']
    assert shifted['evaluation_state_id'] != f.pose(value, .012)['evaluation_state_id']
    for old, new in zip(value['regions'], shifted['regions']):
        if old['group'] == 'guideway':
            assert old == new
        else:
            assert np.subtract(new['bounds_yz_m'], old['bounds_yz_m']) == pytest.approx([0, 0, -.028, -.028])
    for old, new in zip(value['stock_parts'], shifted['stock_parts']):
        if old['group'] == 'guideway':
            assert old == new
        else:
            assert np.subtract(new['at_m'], old['at_m']) == pytest.approx([0, 0, -.028])
            assert np.subtract(new['cg_m'], old['cg_m']) == pytest.approx([0, 0, -.028])
            assert old['mass_kg'] == new['mass_kg']
            assert old['inertia_kg_m2'] == new['inertia_kg_m2']
    assert f.pose(value, .060)['evaluation_gap_m'] == .060


@pytest.mark.parametrize('gap', [True, 0, .0079, .0601, float('nan'), float('inf')])
def test_pose_refuses_out_of_domain_gaps(values, gap):
    with pytest.raises(ValueError, match='8 to 60'):
        f.pose(values[0], gap)


def test_formulation_specialises_grid_without_mutating_imported_kernel(values):
    value = values[0]; pm = [r for r in value['regions'] if r['material'] == value['grade_id']]
    mesh = dict(physical_pm=list(range(100, 100+len(pm))), pm_regions=pm)
    original = f.kernel.COUNTS
    text = f.formulation(value, mesh, f.contours(value), (256, 96, 48))
    assert '{256,96}' in text and 'Norm[$1]<1.e-6' in text
    assert f.kernel.COUNTS == original
    assert f.formulation(value, mesh, f.contours(value), original) == f.kernel.formulation(value, mesh, f.contours(value))
    with pytest.raises(ValueError):
        f.formulation(value, mesh, f.contours(value), (10000, 10000, 10000))


@pytest.fixture(scope='module')
def mesh_fixture(tmp_path_factory, values):
    pytest.importorskip('gmsh')
    value = next(v for v in values if v['parameters'].get('yoke_m'))
    value = f.pose(value, .024)
    directory = tmp_path_factory.mktemp('finite-scaled-mesh')
    settings = dict(margin_m=.07, near_mesh_size_m=.070, gap_mesh_size_m=.020)
    mesh = f.mesh_case(value, directory, settings)
    f.validate_mesh(directory/'coupon.msh', mesh, value, settings)
    return directory, value, mesh, settings


def test_actual_gmsh_mesh_includes_onboard_return_yoke(mesh_fixture):
    directory, value, mesh, settings = mesh_fixture
    steel = [s for s in mesh['magnetic_stock'] if s['material'] == 'steel']
    assert len(steel) == 2
    nodes, groups, xyz, boundary = f._tetrahedra(directory/'coupon.msh')
    volume = abs(np.linalg.det(xyz[:, 1:]-xyz[:, :1]))/6
    assert volume[groups == 200].sum() == pytest.approx(sum(np.prod(s['box_m'][3:]) for s in steel), rel=1e-8)
    assert len(boundary) > 0
    assert f.validate_mesh(directory/'coupon.msh', mesh, value, settings)['nodes'] == nodes


def test_mesh_source_and_outer_boundary_tamper_are_rejected(mesh_fixture, tmp_path):
    directory, value, mesh, settings = mesh_fixture
    changed = deepcopy(mesh); changed['magnetic_stock'][0]['box_m'][4] *= .5
    with pytest.raises(ValueError, match='source/settings'):
        f.validate_mesh(directory/'coupon.msh', changed, value, settings)
    lines = (directory/'coupon.msh').read_text().splitlines(); start = lines.index('$Elements')
    for index in range(start+2, start+2+int(lines[start+1])):
        row = lines[index].split()
        if row[1] == '2' and row[3] == '400':
            del lines[index]; lines[start+1] = str(int(lines[start+1])-1); break
    path = tmp_path/'missing-boundary.msh'; path.write_text('\n'.join(lines)+'\n')
    with pytest.raises(ValueError, match='boundary coverage'):
        f.validate_mesh(path, mesh, value, settings)


def test_deleted_air_tetrahedron_fails_even_with_rehashed_counts(mesh_fixture, tmp_path):
    directory, value, mesh, settings = mesh_fixture
    lines = (directory/'coupon.msh').read_text().splitlines(); start = lines.index('$Elements')
    for index in range(start+2, start+2+int(lines[start+1])):
        row = lines[index].split()
        if row[1] == '4' and row[3] == '300':
            del lines[index]; lines[start+1] = str(int(lines[start+1])-1); break
    path = tmp_path/'air-hole.msh'; path.write_text('\n'.join(lines)+'\n')
    changed = deepcopy(mesh); changed['tetrahedra'] -= 1
    with pytest.raises(ValueError, match='PDE domain/air volume'):
        f.validate_mesh(path, changed, value, settings)


def _faces(directory, boxes, counts, field=lambda p: np.tile([.2, .4, .7], (len(p), 1))):
    for index, (lo, hi) in enumerate(boxes):
        for axis in range(3):
            others = [k for k in range(3) if k != axis]
            for side in (0, 1):
                a, b = np.meshgrid(np.linspace(lo[others[0]], hi[others[0]], counts[others[0]]+1),
                                   np.linspace(lo[others[1]], hi[others[1]], counts[others[1]]+1), indexing='ij')
                points = np.zeros((a.size, 3)); points[:, axis] = hi[axis] if side else lo[axis]
                points[:, others[0]] = a.ravel(); points[:, others[1]] = b.ravel()
                np.savetxt(directory/f'face-{index}-{axis}-{side}.txt', np.column_stack([points, field(points)]))


@pytest.fixture()
def fields_fixture(tmp_path, mesh_fixture):
    directory, value, mesh, settings = mesh_fixture
    (tmp_path/'coupon.msh').write_bytes((directory/'coupon.msh').read_bytes())
    boxes = f.contours(value); counts = f.GRIDS[0]
    _faces(tmp_path, boxes, counts)
    centres = analysis.tetra_centroids(tmp_path/'coupon.msh', [*mesh['physical_pm'], 200])
    for name, groups, scalar in [('PM-H.txt', mesh['physical_pm'], -500000.), ('steel-B.txt', [200], 1.)]:
        points = np.vstack([centres[group] for group in groups])
        np.savetxt(tmp_path/name, np.column_stack([points, np.full(len(points), scalar)]))
    return tmp_path, value, mesh, settings, boxes, counts


def test_closed_contour_constant_field_and_full_scalar_coverage(fields_fixture):
    directory, value, mesh, _, boxes, counts = fields_fixture
    result = f.analyze(directory, value, mesh, boxes, counts)
    assert all(np.linalg.norm(row['force_N']) < 1e-8 for row in result['air_contour_results'])
    assert all(np.linalg.norm(row['moment_Nm']) < 1e-8 for row in result['air_contour_results'])
    assert result['PM_Hparallel_min_A_per_m'] == -500000.
    assert result['numerical_force_convergence_established'] is False
    assert len(result['scalar_checks']) == 2


@pytest.mark.parametrize('kind', ['missing', 'foreign', 'face', 'material-intersection'])
def test_incomplete_or_wrong_field_coordinates_cannot_receive_credit(fields_fixture, kind):
    directory, value, mesh, _, boxes, counts = fields_fixture
    if kind in ('missing', 'foreign'):
        path = directory/'PM-H.txt'; data = np.loadtxt(path)
        if kind == 'missing':
            data = data[:-1]
        else:
            data[0, 0] += .001
        np.savetxt(path, data)
    elif kind == 'face':
        path = directory/'face-0-0-0.txt'; data = np.loadtxt(path); data[0, 0] += .001; np.savetxt(path, data)
    else:
        boxes = deepcopy(boxes); boxes[0][1][2] = .002
    with pytest.raises(ValueError):
        f.analyze(directory, value, mesh, boxes, counts)


def test_manufactured_divergence_free_field_has_correct_force_and_moment(tmp_path):
    # curl(B)/mu0 × B = (a*b, -a²*y, 0)/mu0; integrate a unit cube.
    a, b = .2, .4; centre = np.array([.1, .2, .3]); boxes = [[centre-.5, centre+.5]]
    _faces(tmp_path, boxes, f.GRIDS[0], lambda p: np.column_stack([a*p[:, 1], np.full(len(p), b), np.zeros(len(p))]))
    row = f.legacy.maxwell(tmp_path, boxes)[0]; expected = np.array([a*b, -a*a*centre[1], 0])/f.legacy.MU0
    assert row['force_N'] == pytest.approx(expected, rel=1e-10, abs=1e-8)
    assert row['moment_Nm'] == pytest.approx(np.cross(centre, expected), rel=1e-10, abs=1e-8)


def _full_log():
    return ''.join(f'LOAD {i/10:.3f} INITIAL 1.000000000000000e+00\nCONTINUATION {i/10:.3f} 1 1.000000000000000e-12 1.000000000000000e-12\nSTAGE-END {i/10:.3f} 1 1.000000000000000e-12 1.000000000000000e-12\n' for i in range(1, 11))


def test_readback_rederives_field_values_and_refuses_partial_source(fields_fixture):
    directory, posed, mesh, settings, boxes, counts = fields_fixture
    # Reconstruct original stock; a gap is an evaluation pose, not a new design.
    source = deepcopy(posed)
    for region in source['regions']:
        if region['group'] == 'train':
            region['bounds_yz_m'][2] += .012; region['bounds_yz_m'][3] += .012
    for part in source['stock_parts']:
        if part['group'] == 'train':
            part['at_m'][2] += .012; part['cg_m'][2] += .012
    source.pop('evaluation_gap_m'); source.pop('evaluation_state_id')
    request = dict(candidates=[source], gaps_m=[.024], request_id='request-fixture', settings=settings,
                   contours_m=[boxes], face_counts=list(counts), source_sha256={}, getdp={'sha256':'fixture'})
    f.write(directory/'source-input.json', source); f.write(directory/'pose-input.json', posed)
    (directory/'coupon.pro').write_text(f.formulation(posed, mesh, boxes, counts))
    (directory/'getdp.stdout.log').write_text(_full_log())
    row = dict(case='case-00', request_id=request['request_id'], candidate_id=posed['candidate_id'],
               physical_id=posed['physical_id'], state_id=posed['evaluation_state_id'], gap_m=.024,
               evaluation_id=f.evaluation_id(request,0), settings=settings,
               mesh=mesh, solver_returncode=0, analysis={'fake_force_N': 1e12})
    derived = f._derive(directory, request, 0, record=row)
    assert derived['force_credit'] and derived['analysis']['air_contour_results'][0]['force_N'] == pytest.approx([0, 0, 0], abs=1e-8)
    assert 'fake_force_N' not in derived['analysis']
    (directory/'getdp.stdout.log').write_text(_full_log().split('LOAD 1.000')[0])
    derived = f._derive(directory, request, 0, record=row)
    assert not derived['force_credit'] and derived['execution_status'] == 'nonconverged' and 'analysis' not in derived


def test_worker_deadline_kills_process_group_and_sealed_interruption_cannot_gain_credit(tmp_path, values, monkeypatch):
    root = candidates.ROOT; solver = tmp_path/'solver'; solver.write_text('pinned tool fixture')
    tool = dict(path=str(solver), sha256=f.file_hash(solver), version='3.5.0')
    monkeypatch.setattr(f.previous, '_tool', lambda _: tool)
    monkeypatch.setattr(f, 'source_snapshot', lambda _: {'test-fixture.py': 'a'*64})
    original = subprocess.Popen; child_file = tmp_path/'child-pid.txt'
    def sleeping_worker(command, **kwargs):
        code = 'import subprocess,time,pathlib; p=subprocess.Popen(["sleep","60"]);pathlib.Path('+repr(str(child_file))+').write_text(str(p.pid));time.sleep(60)'
        return original([sys.executable, '-c', code], **kwargs)
    monkeypatch.setattr(f.subprocess, 'Popen', sleeping_worker)
    output = tmp_path/'run'
    result = f.run(output, root, solver, [values[0], values[0]], gap_m=[.012, .024], seconds_per_case=.2)
    assert [r['execution_status'] for r in result['rows']] == ['interrupted', 'interrupted']
    assert result['rows'][0]['state_id'] != result['rows'][1]['state_id']
    assert all(not r['force_credit'] for r in result['rows'])
    pid = child_file.read_text()
    stat = Path('/proc')/pid/'stat'
    assert not stat.exists() or stat.read_text().split()[2] == 'Z'
    result['rows'][0]['force_credit'] = True
    (output/'result.json').write_bytes(f.encoded(result))
    manifest = json.loads((output/'manifest.json').read_bytes()); manifest['files_sha256'] = f.inventory(output, ('manifest.json',))
    (output/'manifest.json').write_bytes(f.encoded(manifest))
    with pytest.raises(ValueError, match='cannot receive force credit'):
        f.verify(output, root)


def test_duplicate_state_budget_and_unsupported_material_are_rejected(tmp_path, values):
    value = values[0]
    for kwargs in ({'seconds_per_case':301}, {'seconds_per_case':True}, {'gap_m':.061}, {}):
        with pytest.raises(ValueError):
            f.run(tmp_path/'unused', candidates.ROOT, '/not/a/solver', [value, value], **kwargs)
    changed = deepcopy(value); changed['materials'][changed['grade_id']]['br_20c_t'] *= 2
    with pytest.raises(ValueError):
        f.run(tmp_path/'unused', candidates.ROOT, '/not/a/solver', [changed])
    assert not (tmp_path/'unused').exists()


def test_quadrature_dispatch_never_allows_a_solve_phase(tmp_path):
    directory = tmp_path/'grid-00'; directory.mkdir()
    f.write(directory/'execution.json', dict(command=['solver', 'coupon.pro', '-solve', 'Solve'], PDE_solves=1))
    with pytest.raises(ValueError, match='must not solve a PDE'):
        f._quadrature_row(tmp_path, {'getdp': {'path':'solver'}}, 0)


def test_embedded_parent_is_independently_admitted_even_after_outer_resealing():
    root = candidates.ROOT; source = f.legacy.source_input(root); sources = f.previous.source_snapshot(root)
    parent = dict(schema=f.previous.SCHEMA, source=source, source_sha256=sources,
                  cases=['coarse'], case_settings={'coarse':f.previous.PLAN['coarse']},
                  contours_m=analysis.contours(source['value']), temperature_C=80., currents_A={}, frame=f.FRAME,
                  budget=dict(seconds_per_case=300, numerical_workers=1, max_cases=3),
                  getdp={'version':'3.5.0'}, **f.previous.FLAGS)
    parent['request_id'] = f.identity(parent)
    manifest = dict(schema=f.previous.SCHEMA, request_id=parent['request_id'], source_sha256=sources, **f.previous.FLAGS)
    request = dict(parent_request=parent, parent_manifest=manifest, parent_source_sha256=sources, case='coarse')
    assert f._parent_contract(request, root)[1] == source['value']
    changed = deepcopy(request); changed['parent_request']['temperature_C'] = 50.
    with pytest.raises(ValueError, match='identity'):
        f._parent_contract(changed, root)
    mutations = [
        lambda p:p.__setitem__('temperature_C', 50.),
        lambda p:p.__setitem__('currents_A', {'unsupported':1.}),
        lambda p:p['frame'].__setitem__('moment_origin_m', [1.,0.,0.]),
        lambda p:p['case_settings']['coarse'].__setitem__('margin_m', .2),
        lambda p:p['budget'].__setitem__('seconds_per_case', 999),
        lambda p:p['source_sha256'].__setitem__('unlisted.py', 'f'*64),
        lambda p:p['source']['value']['stock_parts'][0].__setitem__('physical_release', True),
    ]
    for mutate in mutations:
        changed = deepcopy(request); mutate(changed['parent_request'])
        changed['parent_request']['request_id'] = f.identity({k:v for k,v in changed['parent_request'].items() if k != 'request_id'})
        changed['parent_manifest']['request_id'] = changed['parent_request']['request_id']
        with pytest.raises(ValueError):
            f._parent_contract(changed, root)
    changed = deepcopy(request); changed['parent_manifest']['physical_accepted'] = True
    with pytest.raises(ValueError, match='acceptance'):
        f._parent_contract(changed, root)
