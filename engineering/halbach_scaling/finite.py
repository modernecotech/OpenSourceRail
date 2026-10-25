"""Bounded finite Halbach coupons and retained-solution quadrature diagnostics.

All steel contrasts, including an onboard return yoke, enter the mesh. The
unchanged corrected continuation kernel is specialised to declared face grids;
neither historical source nor historical result files are edited. This is a
static 80 C, zero-current research calculation, never a suspension acceptance.
"""
from copy import deepcopy
from hashlib import sha256
import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from types import FunctionType

import numpy as np

from engineering.design_search.storage import atomic_immutable
from engineering.magnetic_confirmation import analysis, constitutive
from engineering.magnetic_confirmation import formulation as kernel
from engineering.magnetic_confirmation import runner as previous
from engineering.trip_dynamics.fixtures.magnetics import finite_coupon as legacy

SCHEMA = 'osr-scaled-halbach-finite/1'
QUADRATURE_SCHEMA = 'osr-retained-halbach-quadrature/1'
FLAGS = dict(force_map_generated=False, hover_executed=False,
             material_proxy_validated=False, configuration_adopted=False,
             engineering_accepted=False, physical_accepted=False)
SETTINGS = dict(margin_m=.15, near_mesh_size_m=.028, gap_mesh_size_m=.008)
GRIDS = ((64, 24, 12), (128, 48, 24), (256, 96, 48))
FRAME = dict(x='travel', y='left', z='up', handedness='right',
             moment_origin_m=[0., 0., 0.])


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    atomic_immutable(Path(path), encoded(value))


def _validate(value, root):
    from . import candidates
    candidates.validate(value, root)
    if value['length_x_m'] != 1. or value['reference_gap_m'] != .012:
        raise ValueError('this bounded study requires 1 m stock and 12 mm gaps')
    return value


def source_snapshot(root):
    from . import candidates
    paths = set(candidates.source_paths())
    paths.update(Path(module.__file__).resolve() for module in
                 (analysis, constitutive, kernel, previous, legacy))
    paths.add(Path(__file__).resolve())
    tests = Path(__file__).parent/'tests/test_finite.py'
    if tests.is_file():
        paths.add(tests)
    initialiser = Path(__file__).parent/'__init__.py'
    if initialiser.is_file():
        paths.add(initialiser)
    records = {}
    for path in sorted(paths):
        if path.is_symlink():
            raise ValueError('ordinary numerical implementation sources required')
        parts = path.parts
        name = '/'.join(parts[parts.index('engineering'):])
        records[name] = file_hash(path)
    return records


def inventory(directory, exclude=()):
    directory = Path(directory)
    values = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError('symlink in retained numerical output')
        if path.is_file() and path.relative_to(directory).as_posix() not in exclude:
            values[path.relative_to(directory).as_posix()] = file_hash(path)
    return values


def _fresh(output):
    output = Path(output).absolute()
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):
        raise ValueError('ordinary fresh numerical directory required')
    output.mkdir(parents=True, exist_ok=False)
    return output


def _counts(counts):
    if not isinstance(counts, (list, tuple)) or any(type(v) is not int for v in counts) or tuple(counts) not in GRIDS:
        raise ValueError('declared bounded face grid required')
    return tuple(counts)


def _unaccepted(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {*FLAGS, 'physical_release', 'physical_validation', 'manufacturing_release', 'design_complete', 'adopted'} and item is not False:
                raise ValueError('research cannot assert acceptance: '+key)
            _unaccepted(item)
    elif isinstance(value, list):
        for item in value:
            _unaccepted(item)


def formulation(value, mesh, boxes, counts=GRIDS[1]):
    """Bind numerical grid constants without mutating imported kernel globals."""
    counts = _counts(counts)
    generator = FunctionType(kernel.formulation.__code__,
                             dict(kernel.formulation.__globals__, COUNTS=counts))
    return generator(value, mesh, boxes)


def contours(value):
    train = [p for p in value['stock_parts'] if p['group'] == 'train']
    lo = [min(p['at_m'][k] for p in train) for k in range(3)]
    hi = [max(p['at_m'][k]+p['size_m'][k] for p in train) for k in range(3)]
    facing_bottom = min(r['bounds_yz_m'][2] for r in value['regions'] if r['group'] == 'guideway')
    clearance = facing_bottom-hi[2]
    if clearance <= 0:
        raise ValueError('positive air clearance above complete train stock required')
    offsets = (min(.0042, .35*clearance), min(.0066, .55*clearance))
    return [[[x-distance for x in lo], [x+distance for x in hi]] for distance in offsets]


def pose(value, gap_m):
    """Translate train stock as an evaluation state, preserving physical IDs."""
    if type(gap_m) not in (int, float) or not math.isfinite(gap_m) or not .008 <= gap_m <= .060:
        raise ValueError('finite evaluation gap must be within 8 to 60 mm')
    out = deepcopy(value); delta = -(gap_m-value['reference_gap_m'])
    for region in out['regions']:
        if region['group'] == 'train':
            region['bounds_yz_m'][2] += delta; region['bounds_yz_m'][3] += delta
    for part in out['stock_parts']:
        if part['group'] == 'train':
            part['at_m'][2] += delta
            if part.get('cg_m') is not None:
                part['cg_m'][2] += delta
    out['evaluation_gap_m'] = gap_m
    out['evaluation_state_id'] = identity(dict(candidate_id=value['candidate_id'], gap_m=gap_m,
                                               temperature_C=80., currents_A={}, frame=FRAME))
    return out


def magnetic_stock(value):
    selected = [r for r in value['regions']
                if r['material'] == value['grade_id'] or r['material'] == 'steel']
    result = []
    for region in selected:
        a, b, c, d = region['bounds_yz_m']
        result.append(dict(id=region['id'], material=region['material'],
                           box_m=[-value['length_x_m']/2, a, c,
                                  value['length_x_m'], b-a, d-c]))
    return result


def mesh_case(value, directory, settings=SETTINGS):
    """Generate PM and ALL passive/onboard steel contrasts from exact regions."""
    import gmsh
    directory = Path(directory)
    pm = [r for r in value['regions'] if r['material'] == value['grade_id']]
    steel = [r for r in value['regions'] if r['material'] == 'steel']
    if not pm or not steel:
        raise ValueError('permanent magnets and passive steel required')
    ordered = pm+steel
    stock = {r['id']: r for r in magnetic_stock(value)}
    margin = settings['margin_m']
    ymin = min(r['bounds_yz_m'][0] for r in value['regions'])-margin
    ymax = max(r['bounds_yz_m'][1] for r in value['regions'])+margin
    zmin = min(r['bounds_yz_m'][2] for r in value['regions'])-margin
    zmax = max(r['bounds_yz_m'][3] for r in value['regions'])+margin
    length = value['length_x_m']
    box = [-length/2-margin, ymin, zmin, length+2*margin, ymax-ymin, zmax-zmin]
    gmsh.initialize()
    gmsh.option.setNumber('General.Terminal', 0)
    gmsh.logger.start()
    try:
        gmsh.model.add('scaled-halbach-coupon')
        tools = [(3, gmsh.model.occ.addBox(*stock[r['id']]['box_m'])) for r in ordered]
        air = gmsh.model.occ.addBox(*box)
        result, mapping = gmsh.model.occ.fragment([(3, air)], tools)
        gmsh.model.occ.synchronize()
        assigned, steel_volumes = set(), set()
        for i, entities in enumerate(mapping[1:]):
            volumes = {tag for dim, tag in entities if dim == 3}
            if not volumes or assigned.intersection(volumes):
                raise ValueError('overlapping or missing magnetic stock after fragmentation')
            assigned.update(volumes)
            if i < len(pm):
                gmsh.model.addPhysicalGroup(3, sorted(volumes), 100+i)
            else:
                steel_volumes.update(volumes)
        gmsh.model.addPhysicalGroup(3, sorted(steel_volumes), 200)
        gmsh.model.addPhysicalGroup(3, [tag for dim, tag in result if dim == 3 and tag not in assigned], 300)
        external = []
        for _, tag in gmsh.model.getEntities(2):
            bounds = gmsh.model.getBoundingBox(2, tag)
            if any((abs(bounds[k]-box[k]) < 1e-6 and abs(bounds[k+3]-box[k]) < 1e-6)
                   or (abs(bounds[k]-box[k]-box[k+3]) < 1e-6 and abs(bounds[k+3]-box[k]-box[k+3]) < 1e-6)
                   for k in range(3)):
                external.append(tag)
        gmsh.model.addPhysicalGroup(2, external, 400)
        gmsh.option.setNumber('Mesh.MeshSizeMin', settings['gap_mesh_size_m'])
        gmsh.option.setNumber('Mesh.MeshSizeMax', .09)
        near = gmsh.model.mesh.field.add('Box')
        near_bounds = dict(XMin=-length/2-.02, XMax=length/2+.02,
                           YMin=ymin+margin-.02, YMax=ymax-margin+.02,
                           ZMin=zmin+margin-.02, ZMax=zmax-margin+.02)
        for key, number in dict(VIn=settings['near_mesh_size_m'], VOut=.09, **near_bounds).items():
            gmsh.model.mesh.field.setNumber(near, key, number)
        gap = gmsh.model.mesh.field.add('Box')
        gap_bounds = dict(near_bounds, ZMin=-value.get('evaluation_gap_m', value['reference_gap_m'])-.008, ZMax=.008)
        for key, number in dict(VIn=settings['gap_mesh_size_m'], VOut=.09, **gap_bounds).items():
            gmsh.model.mesh.field.setNumber(gap, key, number)
        minimum = gmsh.model.mesh.field.add('Min')
        gmsh.model.mesh.field.setNumbers(minimum, 'FieldsList', [near, gap])
        gmsh.model.mesh.field.setAsBackgroundMesh(minimum)
        gmsh.model.mesh.generate(3)
        gmsh.option.setNumber('Mesh.MshFileVersion', 2.2)
        gmsh.write(str(directory/'coupon.msh'))
        gmsh.write(str(directory/'coupon.brep'))
        nodes = len(gmsh.model.mesh.getNodes()[0])
        kinds, tags, _ = gmsh.model.mesh.getElements(3)
        tetra = sum(len(t) for k, t in zip(kinds, tags) if k == 4)
        (directory/'gmsh.log').write_text('\n'.join(gmsh.logger.get())+'\n')
        return dict(nodes=nodes, tetrahedra=tetra, physical_pm=list(range(100, 100+len(pm))),
                    pm_regions=pm, magnetic_stock=[stock[r['id']] for r in ordered],
                    outer_box_m=box, settings=dict(settings), gmsh_version=gmsh.__version__)
    finally:
        gmsh.logger.stop()
        gmsh.finalize()


def _tetrahedra(path):
    path = Path(path)
    if path.is_symlink() or path.stat().st_size > 128*1024**2:
        raise ValueError('bounded ordinary ASCII mesh required')
    lines = path.read_text().splitlines()
    if lines[lines.index('$MeshFormat')+1] != '2.2 0 8':
        raise ValueError('ASCII MSH 2.2 required')
    start = lines.index('$Nodes'); count = int(lines[start+1]); nodes = {}
    for line in lines[start+2:start+2+count]:
        key, *numbers = line.split(); xyz = list(map(float, numbers))
        if int(key) in nodes or len(xyz) != 3 or not all(math.isfinite(x) for x in xyz):
            raise ValueError('mesh node identity/coordinates differ')
        nodes[int(key)] = xyz
    if lines[start+2+count] != '$EndNodes':
        raise ValueError('mesh node terminator differs')
    start = lines.index('$Elements'); count = int(lines[start+1]); groups, xyz, boundary, ids = [], [], [], set()
    for line in lines[start+2:start+2+count]:
        row = list(map(int, line.split())); element, kind, tags = row[:3]
        if element in ids:
            raise ValueError('duplicate mesh element')
        ids.add(element)
        if kind == 4:
            if tags < 1 or len(row) != 7+tags:
                raise ValueError('invalid tetrahedral record')
            groups.append(row[3]); xyz.append([nodes[k] for k in row[3+tags:]])
        elif kind == 2 and tags >= 1 and row[3] == 400:
            if len(row) != 6+tags:
                raise ValueError('invalid outer boundary triangle')
            boundary.append([nodes[k] for k in row[3+tags:]])
    if lines[start+2+count] != '$EndElements' or not xyz or len(xyz) > 1000000:
        raise ValueError('bounded complete tetrahedral inventory required')
    return len(nodes), np.asarray(groups), np.asarray(xyz), np.asarray(boundary)


def validate_mesh(path, mesh, value, settings=SETTINGS):
    pm = [r for r in value['regions'] if r['material'] == value['grade_id']]
    steel = [r for r in value['regions'] if r['material'] == 'steel']
    by_id = {r['id']: r for r in magnetic_stock(value)}
    stock = [by_id[r['id']] for r in pm+steel]
    if mesh['physical_pm'] != list(range(100, 100+len(pm))) or mesh['pm_regions'] != pm or mesh['magnetic_stock'] != stock or mesh['settings'] != settings:
        raise ValueError('mesh material/physical source/settings differ')
    margin = settings['margin_m']; length = value['length_x_m']
    y0 = min(r['bounds_yz_m'][0] for r in value['regions'])-margin
    y1 = max(r['bounds_yz_m'][1] for r in value['regions'])+margin
    z0 = min(r['bounds_yz_m'][2] for r in value['regions'])-margin
    z1 = max(r['bounds_yz_m'][3] for r in value['regions'])+margin
    box = [-length/2-margin, y0, z0, length+2*margin, y1-y0, z1-z0]
    if not np.allclose(mesh['outer_box_m'], box, rtol=0, atol=1e-12):
        raise ValueError('outer mesh domain differs')
    nodes, groups, xyz, boundary = _tetrahedra(path)
    if nodes != mesh['nodes'] or len(groups) != mesh['tetrahedra'] or set(groups) != set([*mesh['physical_pm'], 200, 300]):
        raise ValueError('mesh node/tetrahedral inventory differs')
    lo, hi = np.asarray(box[:3]), np.asarray(box[:3])+np.asarray(box[3:])
    if np.any(xyz < lo-1e-8) or np.any(xyz > hi+1e-8):
        raise ValueError('mesh node outside source air domain')
    air = xyz[groups == 300]
    if not np.allclose([air.min(axis=(0, 1)), air.max(axis=(0, 1))], [lo, hi], rtol=0, atol=1e-8):
        raise ValueError('actual air mesh boundary differs from source domain')
    if boundary.ndim != 3 or boundary.shape[1:] != (3, 3):
        raise ValueError('outer Dirichlet boundary triangles required')
    covered = np.zeros(len(boundary), dtype=bool)
    areas = np.linalg.norm(np.cross(boundary[:, 1]-boundary[:, 0], boundary[:, 2]-boundary[:, 0]), axis=1)/2
    for axis in range(3):
        others = [k for k in range(3) if k != axis]
        target = (hi[others[0]]-lo[others[0]])*(hi[others[1]]-lo[others[1]])
        for coordinate in (lo[axis], hi[axis]):
            mask = np.all(abs(boundary[:, :, axis]-coordinate) <= 1e-8, axis=1)
            covered |= mask
            if not math.isclose(float(areas[mask].sum()), target, rel_tol=1e-7, abs_tol=1e-10):
                raise ValueError('outer Dirichlet boundary coverage differs')
    if not covered.all():
        raise ValueError('Dirichlet constraint applied away from outer boundary')
    volumes = abs(np.linalg.det(xyz[:, 1:]-xyz[:, :1]))/6
    if not np.isfinite(volumes).all() or np.any(volumes <= 1e-18):
        raise ValueError('degenerate tetrahedron')
    domain_volume = float(np.prod(np.asarray(box[3:])))
    magnetic_volume = math.fsum(float(np.prod(s['box_m'][3:])) for s in stock)
    if (not math.isclose(float(volumes.sum()), domain_volume, rel_tol=1e-7, abs_tol=1e-12)
            or not math.isclose(float(volumes[groups == 300].sum()), domain_volume-magnetic_volume,
                                rel_tol=1e-7, abs_tol=1e-12)):
        raise ValueError('PDE domain/air volume does not close')
    for group, boxes in [(100+i, [stock[i]['box_m']]) for i in range(len(pm))]+[(200, [s['box_m'] for s in stock[len(pm):]])]:
        points = xyz[groups == group]; volume = volumes[groups == group]
        membership = []
        for bounds in boxes:
            a = np.asarray(bounds[:3]); b = a+np.asarray(bounds[3:])
            inside = np.all((points >= a-1e-8) & (points <= b+1e-8), axis=(1, 2))
            membership.append(inside)
            if not inside.any() or not math.isclose(float(volume[inside].sum()), float(np.prod(bounds[3:])), rel_tol=1e-7, abs_tol=1e-12):
                raise ValueError('magnetic material volume/coverage differs')
        if not np.any(np.asarray(membership), axis=0).all():
            raise ValueError('magnetic tetrahedron outside actual source stock')
    air_centres = xyz[groups == 300].mean(axis=1)
    for item in stock:
        bounds = item['box_m']; a = np.asarray(bounds[:3]); b = a+np.asarray(bounds[3:])
        if np.any(np.all((air_centres > a+1e-9) & (air_centres < b-1e-9), axis=1)):
            raise ValueError('air tetrahedron inside magnetic material')
    return dict(nodes=nodes, tetrahedra=len(groups), mesh_sha256=file_hash(path),
                physical_tetrahedra={str(k): int(sum(groups == k)) for k in sorted(set(groups))})


def analyze(directory, value, mesh, boxes, counts):
    counts = _counts(counts)
    guard = FunctionType(analysis.validate_contours.__code__,
                         dict(analysis.validate_contours.__globals__, COUNTS=counts))
    faces = guard(directory, boxes, mesh, value)
    scalar = analysis.validate_scalar_coverage(directory, mesh)
    forces = legacy.maxwell(Path(directory), boxes)
    pm = analysis.checked_table(Path(directory)/'PM-H.txt', 4)
    steel = analysis.checked_table(Path(directory)/'steel-B.txt', 4)
    grade = value['materials'][value['grade_id']]
    limit = grade['demag_hcj_fraction_limit']*grade['hcj_20c_a_m']*(1+60*grade['hcj_temperature_coefficient_per_k'])
    minimum = float(pm[:, -1].min())
    return dict(air_contour_results=forces, face_checks=faces, scalar_checks=scalar,
                PM_Hparallel_min_A_per_m=minimum, steel_B_peak_T=float(steel[:, -1].max()),
                demag_proxy_limit_A_per_m=limit, demag_proxy_margin_A_per_m=limit+minimum,
                demag_proxy_screen_pass=limit+minimum >= 0,
                contour_force_change=analysis.change(forces[0]['force_N'], forces[1]['force_N']),
                contour_moment_change=analysis.change(forces[0]['moment_Nm'], forces[1]['moment_Nm']),
                numerical_force_convergence_established=False,
                scope='Centroid Hparallel and air-contour diagnostics; no measured knee, full map, hover or physical acceptance')


def _derive(directory, request, index, record=None):
    directory = Path(directory); source = request['candidates'][index]
    value = pose(source, request['gaps_m'][index])
    row = json.loads((directory/'calculation.json').read_bytes()) if record is None else record
    if (row['case'] != f'case-{index:02d}' or row['request_id'] != request['request_id']
            or row['candidate_id'] != value['candidate_id'] or row['physical_id'] != value['physical_id']
            or row['state_id'] != value['evaluation_state_id']
            or row['gap_m'] != request['gaps_m'][index]
            or row['evaluation_id'] != evaluation_id(request, index)
            or row['settings'] != request['settings']
            or json.loads((directory/'source-input.json').read_bytes()) != source
            or json.loads((directory/'pose-input.json').read_bytes()) != value):
        raise ValueError('case physical/evaluation input linkage differs')
    expected = dict(row)
    try:
        if 'mesh' in row:
            expected['mesh_verification'] = validate_mesh(directory/'coupon.msh', row['mesh'], value, request['settings'])
            if (directory/'coupon.pro').read_text() != formulation(value, row['mesh'], request['contours_m'][index], request['face_counts']):
                raise ValueError('executed GetDP formulation differs')
        parsed = analysis.parse_stages((directory/'getdp.stdout.log').read_text(errors='replace'))
        expected['continuation'] = parsed
        expected['full_source_converged'] = parsed['full_source_converged']
        expected['force_credit'] = row.get('solver_returncode') == 0 and parsed['full_source_converged']
        expected['execution_status'] = ('completed' if expected['force_credit'] else
                                        'nonconverged' if row.get('solver_returncode') == 0 else 'failed')
        if expected['force_credit']:
            expected['analysis'] = analyze(directory, value, row['mesh'], request['contours_m'][index], request['face_counts'])
        else:
            expected.pop('analysis', None)
    except (ValueError, OSError, KeyError, IndexError) as error:
        expected.update(execution_status='failed', force_credit=False, full_source_converged=False,
                        error_type=type(error).__name__, error=str(error))
        expected.pop('analysis', None)
    return json.loads(encoded(expected))


def _kill(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=5)


def evaluation_id(request, index):
    value = pose(request['candidates'][index], request['gaps_m'][index])
    return identity(dict(candidate_id=value['candidate_id'], state_id=value['evaluation_state_id'],
                         source_sha256=request['source_sha256'], getdp_sha256=request['getdp']['sha256'],
                         settings=request['settings'], face_counts=request['face_counts']))


def _execute(request_path, index, output):
    request = json.loads(Path(request_path).read_bytes()); root = Path(request['root']); output = Path(output)
    _request_contract(request, root)
    if not 0 <= index < len(request['candidates']):
        raise ValueError('worker index outside declared candidate collection')
    source = _validate(request['candidates'][index], root)
    value = pose(source, request['gaps_m'][index])
    if file_hash(request['getdp']['path']) != request['getdp']['sha256']:
        raise ValueError('worker solver binary differs')
    write(output/'source-input.json', source); write(output/'pose-input.json', value)
    row = dict(case=f'case-{index:02d}', candidate_id=value['candidate_id'], physical_id=value['physical_id'],
               state_id=value['evaluation_state_id'], gap_m=request['gaps_m'][index], evaluation_id=evaluation_id(request, index),
               request_id=request['request_id'], settings=request['settings'], execution_status='failed',
               force_credit=False, full_source_converged=False)
    try:
        row['mesh'] = mesh_case(value, output, request['settings'])
        row['mesh_verification'] = validate_mesh(output/'coupon.msh', row['mesh'], value, request['settings'])
        (output/'coupon.pro').write_text(formulation(value, row['mesh'], request['contours_m'][index], request['face_counts']))
        command = [request['getdp']['path'], 'coupon.pro', '-msh', 'coupon.msh', '-solve', 'Solve', '-pos', 'Results']
        row['solver_command'] = command
        with (output/'getdp.stdout.log').open('wb') as stdout, (output/'getdp.stderr.log').open('wb') as stderr:
            p = subprocess.run(command, cwd=output, stdout=stdout, stderr=stderr)
        row['solver_returncode'] = p.returncode
        row = _derive(output, request, index, record=row)
    except Exception as error:
        row.update(execution_status='failed', force_credit=False, full_source_converged=False,
                   error_type=type(error).__name__, error=str(error))
        row.pop('analysis', None)
    if request['source_sha256'] != source_snapshot(root) or file_hash(request['getdp']['path']) != request['getdp']['sha256']:
        raise ValueError('worker source/tool changed during execution')
    write(output/'calculation.json', row)


def run(output, root, getdp, candidate_bundles, *, gap_m=.012, face_counts=GRIDS[1], seconds_per_case=300):
    root = Path(root).resolve(); values = [deepcopy(v) for v in candidate_bundles]
    if not 1 <= len(values) <= 3:
        raise ValueError('one to three candidate/state cases required')
    if type(seconds_per_case) not in (int, float) or not 0 < seconds_per_case <= 300:
        raise ValueError('complete worker budget must be positive and at most 300 seconds')
    for value in values:
        _validate(value, root)
    gaps = list(gap_m) if isinstance(gap_m, (list, tuple)) else [gap_m]*len(values)
    if len(gaps) != len(values):
        raise ValueError('one evaluation gap per finite candidate required')
    poses = [pose(value, gap) for value, gap in zip(values, gaps)]
    if len({value['evaluation_state_id'] for value in poses}) != len(poses):
        raise ValueError('duplicate physical candidate and evaluation gap')
    before = source_snapshot(root); tool = previous._tool(getdp)
    request = dict(schema=SCHEMA, root=str(root), candidates=values, settings=dict(SETTINGS),
                   face_counts=list(_counts(face_counts)), gaps_m=gaps, contours_m=[contours(v) for v in poses],
                   source_sha256=before, getdp=tool, temperature_C=80., currents_A={}, frame=FRAME,
                   budget=dict(seconds_per_case=seconds_per_case, numerical_workers=1, max_cases=3), **FLAGS)
    request['request_id'] = identity(request); output = _fresh(output); write(output/'request.json', request)
    fixtures = [constitutive.fixture(v['materials']['steel']) for v in values]
    write(output/'jacobian-fixtures.json', fixtures)
    if not all(v['passed'] for v in fixtures):
        raise ValueError('constitutive derivative fixture failed')
    rows = []; code_root = Path(__file__).resolve().parents[2]
    for index, value in enumerate(values):
        directory = output/f'case-{index:02d}'; directory.mkdir(); started = time.monotonic()
        command = [sys.executable, '-m', 'engineering.halbach_scaling.finite', 'worker',
                   '--request', str(output/'request.json'), '--index', str(index), '--output', str(directory)]
        env = dict(os.environ, PYTHONPATH=str(code_root)+os.pathsep+str(root), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        with (directory/'worker.stdout.log').open('wb') as stdout, (directory/'worker.stderr.log').open('wb') as stderr:
            p = subprocess.Popen(command, cwd=code_root, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                code = p.wait(timeout=seconds_per_case); timed_out = False
            except subprocess.TimeoutExpired:
                _kill(p); code = p.returncode; timed_out = True
            except BaseException:
                _kill(p)
                raise
        execution = dict(command=command, returncode=code, timed_out=timed_out, elapsed_s=time.monotonic()-started)
        write(directory/'execution.json', execution)
        if not timed_out and code == 0 and (directory/'calculation.json').is_file():
            row = _derive(directory, request, index)
        else:
            row = dict(case=f'case-{index:02d}', candidate_id=value['candidate_id'], physical_id=value['physical_id'],
                       state_id=poses[index]['evaluation_state_id'],
                       gap_m=gaps[index], evaluation_id=evaluation_id(request, index),
                       execution_status='interrupted' if timed_out else 'failed', force_credit=False,
                       full_source_converged=False, error='Complete worker deadline' if timed_out else 'Worker did not complete')
        row.update(execution=execution, files_sha256=inventory(directory)); rows.append(row)
    if source_snapshot(root) != before or file_hash(tool['path']) != tool['sha256']:
        raise ValueError('source/tool changed during finite campaign')
    result = dict(schema=SCHEMA, request_id=request['request_id'], rows=rows, execution_status='completed',
                  source_sha256=before, candidate_ids=[v['candidate_id'] for v in values],
                  scope='Finite 1 m stock, 80 C, zero current, nonlinear steel proxy; no complete operating map or accepted vehicle', **FLAGS)
    write(output/'result.json', result)
    write(output/'manifest.json', dict(schema=SCHEMA, request_id=request['request_id'], source_sha256=before,
                                      files_sha256=inventory(output, ('manifest.json',)), **FLAGS))
    verify(output, root=root)
    return result


def verify(output, root=None):
    output = Path(output); request = json.loads((output/'request.json').read_bytes())
    if request.get('schema') == QUADRATURE_SCHEMA:
        return verify_quadrature(output, root=root)
    root = Path(root or request['root']); manifest = json.loads((output/'manifest.json').read_bytes())
    result = json.loads((output/'result.json').read_bytes())
    values, poses = _request_contract(request, root)
    if manifest.get('schema') != SCHEMA or result.get('schema') != SCHEMA:
        raise ValueError('finite result schema differs')
    if request['source_sha256'] != source_snapshot(root) or manifest['source_sha256'] != request['source_sha256'] or result['source_sha256'] != request['source_sha256']:
        raise ValueError('finite implementation source binding differs')
    values = request['candidates']
    if not 1 <= len(values) <= 3:
        raise ValueError('bounded finite candidate/state cases required')
    for value in values:
        _validate(value, root)
    _counts(request['face_counts'])
    if len(request['gaps_m']) != len(values):
        raise ValueError('finite gap-state membership differs')
    poses = [pose(v, gap) for v, gap in zip(values, request['gaps_m'])]
    if len({v['evaluation_state_id'] for v in poses}) != len(poses):
        raise ValueError('duplicate candidate and gap state')
    if (request['settings'] != SETTINGS or request['contours_m'] != [contours(v) for v in poses]
            or request['temperature_C'] != 80. or request['currents_A'] != {} or request['frame'] != FRAME
            or request['budget']['max_cases'] != 3 or request['budget']['numerical_workers'] != 1
            or type(request['budget']['seconds_per_case']) not in (int, float)
            or not 0 < request['budget']['seconds_per_case'] <= 300):
        raise ValueError('finite scenario/domain/budget differs')
    if manifest['files_sha256'] != inventory(output, ('manifest.json',)) or file_hash(request['getdp']['path']) != request['getdp']['sha256']:
        raise ValueError('finite payload/tool integrity differs')
    for record in (request, manifest, result):
        if record.get('request_id') != request['request_id'] or any(record.get(k) is not False for k in FLAGS):
            raise ValueError('finite request linkage/acceptance differs')
    fixture = [constitutive.fixture(v['materials']['steel']) for v in values]
    if json.loads((output/'jacobian-fixtures.json').read_bytes()) != fixture or not all(v['passed'] for v in fixture):
        raise ValueError('constitutive fixture differs')
    if result['execution_status'] != 'completed' or result['candidate_ids'] != [v['candidate_id'] for v in values] or len(result['rows']) != len(values):
        raise ValueError('finite collection membership differs')
    for index, row in enumerate(result['rows']):
        directory = output/f'case-{index:02d}'; execution = json.loads((directory/'execution.json').read_bytes())
        if row['case'] != directory.name or row['candidate_id'] != values[index]['candidate_id'] or row['physical_id'] != values[index]['physical_id'] or row['state_id'] != poses[index]['evaluation_state_id'] or row['gap_m'] != request['gaps_m'][index] or row['evaluation_id'] != evaluation_id(request, index):
            raise ValueError('finite case candidate membership differs')
        if row['execution'] != execution or row['files_sha256'] != inventory(directory):
            raise ValueError('finite case execution/inventory differs')
        if not execution['timed_out'] and execution['returncode'] == 0 and (directory/'calculation.json').is_file():
            expected = _derive(directory, request, index)
            expected.update(execution=execution, files_sha256=inventory(directory))
            if row != expected:
                raise ValueError('recomputed finite field/mesh/stage result differs')
        elif row.get('force_credit') or row.get('full_source_converged') or 'analysis' in row:
            raise ValueError('failed/interrupted case cannot receive force credit')
    return dict(current=True, case_count=len(values), full_source_cases=sum(bool(v.get('force_credit')) for v in result['rows']),
                source_sha256=request['source_sha256'], **FLAGS)


def _request_contract(request, root):
    if request.get('schema') != SCHEMA or request.get('request_id') != identity({k: v for k, v in request.items() if k != 'request_id'}):
        raise ValueError('finite request schema/identity differs')
    _unaccepted(request)
    if request['source_sha256'] != source_snapshot(root):
        raise ValueError('finite executing source binding differs')
    values = request['candidates']
    if not isinstance(values, list) or not 1 <= len(values) <= 3 or len(request['gaps_m']) != len(values):
        raise ValueError('bounded finite candidate/state membership differs')
    for value in values:
        _validate(value, root)
    poses = [pose(v, g) for v, g in zip(values, request['gaps_m'])]
    if len({v['evaluation_state_id'] for v in poses}) != len(poses):
        raise ValueError('duplicate candidate and gap state')
    _counts(request['face_counts'])
    budget = request['budget']; seconds = budget.get('seconds_per_case')
    if (type(seconds) not in (int, float) or not 0 < seconds <= 300
            or budget != dict(seconds_per_case=seconds, numerical_workers=1, max_cases=3)
            or type(budget['numerical_workers']) is not int or type(budget['max_cases']) is not int
            or request['settings'] != SETTINGS or request['contours_m'] != [contours(v) for v in poses]
            or request['temperature_C'] != 80. or request['currents_A'] != {} or request['frame'] != FRAME
            or request['getdp']['version'] != '3.5.0'):
        raise ValueError('finite scenario/domain/budget differs')
    return values, poses


def _parent_contract(request, root):
    parent = request['parent_request']; manifest = request['parent_manifest']
    _unaccepted(parent); _unaccepted(manifest)
    if (parent.get('schema') != previous.SCHEMA
            or parent.get('request_id') != identity({k: v for k, v in parent.items() if k != 'request_id'})
            or manifest.get('schema') != previous.SCHEMA
            or manifest.get('request_id') != parent['request_id']):
        raise ValueError('retained parent request/manifest identity differs')
    sources = previous.source_snapshot(root)
    if (parent['source_sha256'] != sources or manifest['source_sha256'] != sources
            or request['parent_source_sha256'] != sources or parent['source'] != legacy.source_input(root)):
        raise ValueError('retained parent source binding differs')
    value = analysis.validate_source(parent['source'])
    cases = parent['cases']
    if (not 1 <= len(cases) <= 3 or len(set(cases)) != len(cases) or any(c not in previous.PLAN for c in cases)
            or request['case'] not in cases or parent['case_settings'] != {c:previous.PLAN[c] for c in cases}
            or parent['budget'] != dict(seconds_per_case=300, numerical_workers=1, max_cases=3)
            or parent['temperature_C'] != 80. or parent['currents_A'] != {} or parent['frame'] != FRAME
            or parent['contours_m'] != analysis.contours(value)
            or parent['getdp']['version'] != '3.5.0'):
        raise ValueError('retained parent scenario/domain/budget differs')
    for item in (parent, manifest):
        if any(item.get(k) is not False for k in previous.FLAGS):
            raise ValueError('retained parent acceptance flags differ')
    return parent, value


def _quadrature_sources(root):
    result = source_snapshot(root)
    for name, digest in previous.source_snapshot(root).items():
        if name in result and result[name] != digest:
            raise ValueError('quadrature executing/retained sources disagree')
        result[name] = digest
    return dict(sorted(result.items()))


def quadrature(output, root, getdp, retained_run, *, case='fine', face_grids=GRIDS):
    """Resample one verified retained solution; never call a PDE resolution.

    GetDP's documented standalone ``-pos`` phase reads the captured .pre/.res.
    Air-contour B and centroid H/steel B depend on that saved solution; no new
    magnetisation state or additional mesh-convergence credit is inferred.
    https://www.getdp.info/doc/texinfo/getdp.html#PostOperation-examples
    """
    root = Path(root).resolve(); retained_run = Path(retained_run)
    if case not in ('coarse', 'fine', 'expanded') or not 1 <= len(face_grids) <= 3:
        raise ValueError('one retained case and at most three face grids required')
    grids = [list(_counts(g)) for g in face_grids]
    if len({tuple(g) for g in grids}) != len(grids):
        raise ValueError('distinct quadrature grids required')
    previous.verify(retained_run, root=root)
    parent_request = json.loads((retained_run/'request.json').read_bytes())
    parent_manifest = json.loads((retained_run/'manifest.json').read_bytes())
    record = previous._derived(retained_run/case, parent_request, case)
    if not record.get('force_credit'):
        raise ValueError('retained full-source converged solution required')
    tool = previous._tool(getdp)
    if tool['sha256'] != parent_request['getdp']['sha256']:
        raise ValueError('postprocessing solver differs from retained solver')
    request = dict(schema=QUADRATURE_SCHEMA, root=str(root), case=case, face_grids=grids,
                   source_sha256=_quadrature_sources(root), parent_source_sha256=previous.source_snapshot(root),
                   parent_request=parent_request, parent_manifest=parent_manifest, getdp=tool,
                   budget=dict(max_grids=3, seconds_per_grid=45, numerical_workers=1, PDE_solves=0), **FLAGS)
    request['request_id'] = identity(request); output = _fresh(output); write(output/'request.json', request)
    seed = output/'seed'; seed.mkdir()
    names = ('coupon.msh', 'coupon.pre', 'coupon.res', 'calculation.json', 'source-input.json', 'getdp.stdout.log')
    for name in names:
        raw = (retained_run/case/name).read_bytes()
        if sha256(raw).hexdigest() != parent_manifest['files_sha256'][case+'/'+name]:
            raise ValueError('retained solution source bytes differ')
        atomic_immutable(seed/name, raw)
    value = parent_request['source']['value']; rows = []
    for index, counts in enumerate(grids):
        directory = output/f'grid-{index:02d}'; directory.mkdir()
        for name in ('coupon.msh', 'coupon.pre', 'coupon.res'):
            shutil.copyfile(seed/name, directory/name)
        (directory/'coupon.pro').write_text(formulation(value, record['mesh'], parent_request['contours_m'], counts))
        command = [tool['path'], 'coupon.pro', '-msh', 'coupon.msh', '-pos', 'Results']
        started = time.monotonic()
        with (directory/'post.stdout.log').open('wb') as stdout, (directory/'post.stderr.log').open('wb') as stderr:
            p = subprocess.Popen(command, cwd=directory, stdout=stdout, stderr=stderr,
                                 env=dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1'), start_new_session=True)
            try:
                code = p.wait(timeout=45); timed_out = False
            except subprocess.TimeoutExpired:
                _kill(p); code = p.returncode; timed_out = True
            except BaseException:
                _kill(p)
                raise
        write(directory/'execution.json', dict(command=command, returncode=code, timed_out=timed_out,
                                               elapsed_s=time.monotonic()-started, PDE_solves=0))
        rows.append(_quadrature_row(output, request, index))
    result = dict(schema=QUADRATURE_SCHEMA, request_id=request['request_id'], rows=rows,
                  execution_status='completed', PDE_solves=0, source_sha256=request['source_sha256'],
                  scope='Quadrature sensitivity on one unchanged retained finite solution; no new field, mesh or physical acceptance', **FLAGS)
    write(output/'result.json', result)
    write(output/'manifest.json', dict(schema=QUADRATURE_SCHEMA, request_id=request['request_id'],
                                      source_sha256=request['source_sha256'],
                                      files_sha256=inventory(output, ('manifest.json',)), **FLAGS))
    verify_quadrature(output, root=root)
    return result


def _quadrature_row(output, request, index):
    output = Path(output); directory = output/f'grid-{index:02d}'; seed = output/'seed'
    execution = json.loads((directory/'execution.json').read_bytes())
    command = [request['getdp']['path'], 'coupon.pro', '-msh', 'coupon.msh', '-pos', 'Results']
    if execution['command'] != command or execution.get('PDE_solves') != 0:
        raise ValueError('quadrature phase must not solve a PDE')
    parent_request = request['parent_request']; value = parent_request['source']['value']
    record = json.loads((seed/'calculation.json').read_bytes()); counts = request['face_grids'][index]
    for name in ('coupon.msh', 'coupon.pre', 'coupon.res'):
        if file_hash(directory/name) != file_hash(seed/name):
            raise ValueError('postprocessing changed retained mesh/DOF/solution')
    if (directory/'coupon.pro').read_text() != formulation(value, record['mesh'], parent_request['contours_m'], counts):
        raise ValueError('quadrature formulation differs')
    row = dict(grid_index=index, face_counts=counts, execution=execution,
               execution_status='interrupted' if execution['timed_out'] else 'failed', force_credit=False)
    if not execution['timed_out'] and execution['returncode'] == 0:
        row['analysis'] = analyze(directory, value, record['mesh'], parent_request['contours_m'], counts)
        row.update(execution_status='completed', force_credit=True)
    row['files_sha256'] = inventory(directory)
    return row


def verify_quadrature(output, root=None):
    output = Path(output); request = json.loads((output/'request.json').read_bytes())
    root = Path(root or request['root']); manifest = json.loads((output/'manifest.json').read_bytes())
    result = json.loads((output/'result.json').read_bytes())
    if request.get('schema') != QUADRATURE_SCHEMA or request.get('request_id') != identity({k: v for k, v in request.items() if k != 'request_id'}):
        raise ValueError('quadrature request identity differs')
    _unaccepted(request); _unaccepted(result); _unaccepted(manifest)
    if request['source_sha256'] != _quadrature_sources(root) or request['parent_source_sha256'] != previous.source_snapshot(root):
        raise ValueError('quadrature or retained-solution source binding differs')
    if request['parent_manifest']['source_sha256'] != request['parent_source_sha256']:
        raise ValueError('retained parent manifest source binding differs')
    if request['budget'] != dict(max_grids=3, seconds_per_grid=45, numerical_workers=1, PDE_solves=0):
        raise ValueError('quadrature budget differs')
    if not 1 <= len(request['face_grids']) <= 3 or len({tuple(g) for g in request['face_grids']}) != len(request['face_grids']):
        raise ValueError('quadrature grid inventory differs')
    for grid in request['face_grids']:
        _counts(grid)
    seed = output/'seed'; parent, value = _parent_contract(request, root)
    record = json.loads((seed/'calculation.json').read_bytes())
    if (request['case'] not in ('coarse', 'fine', 'expanded') or record['case'] != request['case']
            or record['request_id'] != parent['request_id']
            or record['candidate_id'] != parent['source']['vehicle_candidate_id']
            or record['magnet_component_id'] != value['physical_id']
            or record['settings'] != previous.PLAN[request['case']]):
        raise ValueError('retained case identity differs')
    for name in ('coupon.msh', 'coupon.pre', 'coupon.res', 'calculation.json', 'source-input.json', 'getdp.stdout.log'):
        if file_hash(seed/name) != request['parent_manifest']['files_sha256'][request['case']+'/'+name]:
            raise ValueError('retained solution bytes differ')
    if json.loads((seed/'source-input.json').read_bytes()) != parent['source'] or not analysis.parse_stages((seed/'getdp.stdout.log').read_text())['full_source_converged'] or record['solver_returncode'] != 0:
        raise ValueError('full-source retained solve admission differs')
    analysis.validate_mesh(seed/'coupon.msh', record['mesh'], value, record['settings']['margin_m'])
    if request['getdp']['sha256'] != parent['getdp']['sha256'] or file_hash(request['getdp']['path']) != request['getdp']['sha256']:
        raise ValueError('retained/postprocessing solver differs')
    if manifest['files_sha256'] != inventory(output, ('manifest.json',)):
        raise ValueError('quadrature payload integrity differs')
    for item in (request, result, manifest):
        if item.get('schema') != QUADRATURE_SCHEMA or item.get('request_id') != request['request_id'] or item.get('source_sha256') != request['source_sha256'] or any(item.get(k) is not False for k in FLAGS):
            raise ValueError('quadrature record linkage/acceptance differs')
    if result['execution_status'] != 'completed' or result['PDE_solves'] != 0 or len(result['rows']) != len(request['face_grids']):
        raise ValueError('quadrature collection disposition differs')
    for index, row in enumerate(result['rows']):
        if row != _quadrature_row(output, request, index):
            raise ValueError('recomputed quadrature force/field result differs')
    return dict(current=True, grid_count=len(result['rows']), PDE_solves=0, **FLAGS)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('worker',)); p.add_argument('--request', type=Path, required=True)
    p.add_argument('--index', type=int, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); _execute(a.request, a.index, a.output)


if __name__ == '__main__':
    main()
