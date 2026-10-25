"""Strict SI reduced-modal exchange and a separate analytical laminate coupon.

No coupon in this module is an equipped rail body. A vehicle modal import needs
the full equipped load-case mass distribution, equilibrium and attachment map.
Only three translational physical DOFs per node are accepted; mixed rotation /
translation matrix units are deliberately not inferred from an external solver.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path
import re

import numpy as np

from .vehicle import _checked, identity

UNITS = dict(position='m', physical_mass='kg', physical_stiffness='N/m',
             shape='kg^-0.5', modal_mass='1', modal_stiffness='s^-2',
             modal_damping='s^-1', modal_coordinate='m*kg^0.5', force='N')


def _array(value, shape, label):
    # bool, strings and ragged arrays must not acquire plausible SI values.
    array = np.asarray(value)
    if array.shape != shape or array.dtype.kind not in 'fi' or not np.isfinite(array).all():
        raise ValueError('finite numeric ' + label + ' with shape ' + str(shape) + ' required')
    return array.astype(float)


def _same(actual, expected, label, rtol=1e-7, atol=1e-9):
    if not np.allclose(actual, expected, rtol=rtol, atol=atol):
        raise ValueError(label + ' mismatch')


def _equipped(vehicle, load):
    properties = vehicle.get('equipped_properties', {}).get(load)
    if not properties or vehicle.get('complete_equipped_vehicle') is not True or vehicle.get('unknown_installed_inventory'):
        raise ValueError('complete equipped load-case mass/CG/inertia is unknown')
    mass = properties.get('mass_kg_per_car')
    if type(mass) not in (float, int) or not math.isfinite(mass) or mass <= 0:
        raise ValueError('positive equipped mass required')
    cg = _array(properties.get('cg_m'), (3,), 'equipped CG')
    inertia = _array(properties.get('inertia_kg_m2'), (3, 3), 'equipped inertia')
    _same(inertia, inertia.T, 'equipped inertia symmetry')
    eig = np.linalg.eigvalsh(inertia)
    if eig[0] <= 0 or eig[2] > eig[0] + eig[1] + 1e-8:
        raise ValueError('physical positive equipped inertia required')
    return float(mass), cg, inertia


def validate_modal_model(data: dict, vehicle: dict, scenario: dict) -> dict:
    """Validate a small exported modal model; return a defensive data copy.

    Source files are checked by ``load_modal``. Calling this lower-level function
    validates numerical/identity content only. Numerical agreement does not
    establish measured material properties or installed structural acceptance.
    """
    value = deepcopy(data)
    if value.get('schema') != 'osr-reduced-flexible-body/1' or value.get('units') != UNITS:
        raise ValueError('explicit reduced-model schema and exact SI units required')
    for key in ('candidate_id', 'geometry_id', 'material_id'):
        if not re.fullmatch('[0-9a-f]{64}', str(value.get(key, ''))) or value[key] != vehicle.get(key):
            raise ValueError(key + ' does not identify the selected vehicle')
    if scenario.get('scenario_id') != value['candidate_id']:
        raise ValueError('scenario physical candidate mismatch')
    if value.get('model_id') != identity({k: v for k, v in value.items() if k != 'model_id'}):
        raise ValueError('model content identity changed')
    if any(value.get(k) is not False for k in ('configuration_adopted', 'physical_accepted', 'engineering_accepted')):
        raise ValueError('modal exchange cannot assert physical/design acceptance')
    benchmark = value.get('scope') == 'benchmark-coupon'
    if benchmark != (vehicle.get('scope') == 'benchmark-coupon') or benchmark and scenario.get('mode') != 'benchmark':
        raise ValueError('benchmark coupon cannot become evidence for an actual body')
    applicability = value['applicability']
    for key in ('cars', 'car_length_m', 'load_case'):
        if applicability.get(key) != scenario.get(key):
            raise ValueError('modal applicability mismatch: ' + key)
    temp = scenario.get('temperature_C')
    temp_range = _array(applicability.get('temperature_range_C'), (2,), 'temperature range')
    if temp_range[0] > temp_range[1] or type(temp) not in (int, float) or not math.isfinite(temp) or not temp_range[0] <= temp <= temp_range[1]:
        raise ValueError('modal temperature applicability mismatch')
    context = vehicle.get('structural_context', {}).get(scenario.get('load_case'))
    if not context:
        raise ValueError('vehicle equilibrium/boundary/load context unknown')
    equilibrium = value['equilibrium']
    for key in ('boundary_case_id', 'equilibrium_id', 'external_load_id'):
        if not equilibrium.get(key) or equilibrium[key] != context.get(key):
            raise ValueError('equilibrium applicability mismatch: ' + key)
    if equilibrium.get('prestress_included') is not True:
        raise ValueError('equilibrium prestress applicability is not established')
    residual = equilibrium.get('residual_force_N')
    # A producer cannot set an arbitrary tolerance to accept its own residual.
    if type(residual) not in (int, float) or not math.isfinite(residual) or residual < 0 or residual > 1e-6:
        raise ValueError('unresolved equilibrium force residual')
    mass, cg, inertia = _equipped(vehicle, scenario['load_case'])
    nodes = value['nodes']
    if not 3 <= len(nodes) <= 100:
        raise ValueError('bounded 3..100 translational nodes required')
    ids = [x['id'] for x in nodes]
    if any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError('unique node IDs required')
    coordinates = _array([x['xyz_m'] for x in nodes], (len(nodes), 3), 'node coordinates')
    dofs = 3 * len(nodes)
    modes = value.get('mode_count')
    if type(modes) is not int or not 1 <= modes <= min(dofs, 30):
        raise ValueError('bounded mode count required')
    M = _array(value['physical_mass_matrix_kg'], (dofs, dofs), 'physical mass')
    K = _array(value['physical_stiffness_matrix_N_m'], (dofs, dofs), 'physical stiffness')
    phi = _array(value['shapes_dof_by_mode'], (dofs, modes), 'mode shapes')
    Km = _array(value['modal_stiffness_s2'], (modes, modes), 'modal stiffness')
    C = _array(value['modal_damping_s1'], (modes, modes), 'modal damping')
    for matrix, label, positive in [(M, 'mass', True), (K, 'stiffness', False),
                                    (Km, 'modal stiffness', True), (C, 'damping', False)]:
        _same(matrix, matrix.T, label + ' symmetry')
        eigen = np.linalg.eigvalsh(matrix)
        bad = eigen[0] <= 0 if positive else eigen[0] < -1e-8 * max(1., abs(eigen[-1]))
        if bad:
            raise ValueError('nonphysical ' + label + ' eigenvalue')
    _same(phi.T @ M @ phi, np.eye(modes), 'mass normalisation')
    _same(phi.T @ K @ phi, Km, 'projected modal stiffness')
    # This exchange consists of normal modes, not arbitrary Ritz vectors.
    _same(Km, np.diag(np.diag(Km)), 'normal mode diagonal stiffness')
    _same(K @ phi, M @ phi @ Km, 'full eigen residual', rtol=2e-6, atol=1e-7)
    frequency = _array(value['frequencies_hz'], (modes,), 'frequencies')
    _same((2 * np.pi * frequency) ** 2, np.diag(Km), 'frequency/stiffness')
    if (frequency <= 0).any():
        raise ValueError('positive elastic frequencies required')
    # Congruence with rigid velocities independently checks equipped mass,
    # CG and all products of inertia, not only a modal checksum.
    rigid = np.zeros((dofs, 6))
    for i, position in enumerate(coordinates - cg):
        rigid[3*i:3*i+3, :3] = np.eye(3)
        x, y, z = position
        rigid[3*i:3*i+3, 3:] = [[0, z, -y], [-z, 0, x], [y, -x, 0]]
    target = np.zeros((6, 6))
    target[:3, :3], target[3:, 3:] = mass * np.eye(3), inertia
    _same(rigid.T @ M @ rigid, target, 'equipped rigid mass/CG/inertia', rtol=1e-6)
    attachments = value['attachments']
    if not attachments or len({x['id'] for x in attachments}) != len(attachments):
        raise ValueError('unique explicit attachments required')
    required = context.get('attachments')
    if not required or {x['id'] for x in attachments} != set(required):
        raise ValueError('attachment set differs from equipped boundary/load contract')
    for attachment in attachments:
        weights = attachment['node_weights']
        names = [x['node_id'] for x in weights]
        if not weights or len(set(names)) != len(names) or any(n not in ids for n in names):
            raise ValueError('unknown/duplicate attachment node')
        w = _array([x['weight'] for x in weights], (len(weights),), 'attachment weights')
        if (w < 0).any() or not math.isclose(float(w.sum()), 1., abs_tol=1e-10):
            raise ValueError('convex partition-of-unity attachment interpolation required')
        position = _array(attachment['position_m'], (3,), 'attachment position')
        _same(position, sum((a * coordinates[ids.index(n)] for a, n in zip(w, names)), np.zeros(3)), 'interpolated attachment position')
        _same(position, _array(required[attachment['id']], (3,), 'equipped attachment'), 'equipped attachment position')
    value['_numerically_validated'] = True
    return value


def load_modal(path: Path, vehicle: dict, scenario: dict) -> dict:
    """Import bounded JSON, checking all declared neighboring source files."""
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError('bounded ordinary modal JSON required')
    value = json.loads(path.read_text())
    if not value.get('source_sha256'):
        raise ValueError('modal mesh/material/equilibrium source bindings required')
    for name, digest in value['source_sha256'].items():
        _checked(path.parent, name, digest)
    return validate_modal_model(value, vehicle, scenario)


def attachment_operator(model: dict, attachment_id: str) -> np.ndarray:
    """3 x modes: displacement=Hq; conjugate generalised force=H.T F."""
    if model.get('_numerically_validated') is not True:
        raise ValueError('load/validate modal model before attachment interpolation')
    ids = [x['id'] for x in model['nodes']]
    matches = [x for x in model['attachments'] if x['id'] == attachment_id]
    if len(matches) != 1:
        raise ValueError('unknown attachment')
    phi = np.asarray(model['shapes_dof_by_mode'], dtype=float)
    H = np.zeros((3, model['mode_count']))
    for item in matches[0]['node_weights']:
        i = ids.index(item['node_id'])
        H += item['weight'] * phi[3*i:3*i+3]
    return H


def laminate_benchmark(elements: int = 24) -> dict:
    """Execute a CLT + Euler--Bernoulli *coupon*, never a vehicle solve.

    [0/90/90/0], 1 mm plies, 1 m x .1 m cantilever. Cylindrical bending
    (transverse curvature restrained) uses EI=b*D11. Lamina properties are
    declared synthetic inputs; no supplier, hot/wet or rail qualification.
    Consistent-mass beam FE static/modal results are checked against independent
    cantilever formulas. This does not exercise Code_Aster shell elements.
    """
    if type(elements) is not int or not 4 <= elements <= 100:
        raise ValueError('4..100 bounded beam elements required')
    from scipy.linalg import eigh
    E1, E2, G12, nu12, rho = 25e9, 8e9, 4e9, .25, 1900.
    nu21 = nu12 * E2 / E1
    Q11, Q22 = E1 / (1 - nu12*nu21), E2 / (1 - nu12*nu21)
    Q12 = nu12*E2 / (1 - nu12*nu21)
    Q0 = np.array([[Q11, Q12, 0], [Q12, Q22, 0], [0, 0, G12]])
    Q90 = np.array([[Q22, Q12, 0], [Q12, Q11, 0], [0, 0, G12]])
    A, B, D = np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))
    edges = np.linspace(-.002, .002, 5)
    for q, lo, hi in zip([Q0, Q90, Q90, Q0], edges[:-1], edges[1:]):
        A += q * (hi-lo)
        B += q * (hi*hi-lo*lo) / 2
        D += q * (hi**3-lo**3) / 3
    length, width, thickness, force = 1., .1, .004, .1
    EI, mu = width*D[0, 0], rho*width*thickness
    step = length/elements
    k = EI/step**3*np.array([[12, 6*step, -12, 6*step], [6*step, 4*step**2, -6*step, 2*step**2],
                             [-12, -6*step, 12, -6*step], [6*step, 2*step**2, -6*step, 4*step**2]])
    m = mu*step/420*np.array([[156, 22*step, 54, -13*step], [22*step, 4*step**2, 13*step, -3*step**2],
                              [54, 13*step, 156, -22*step], [-13*step, -3*step**2, -22*step, 4*step**2]])
    K, M = np.zeros((2*(elements+1),)*2), np.zeros((2*(elements+1),)*2)
    for e in range(elements):
        sl = slice(2*e, 2*e+4)
        K[sl, sl] += k
        M[sl, sl] += m
    K, M = K[2:, 2:], M[2:, 2:]
    f = np.zeros(2*elements)
    f[-2] = force
    static = np.linalg.solve(K, f)
    frequencies = np.sqrt(eigh(K, M, subset_by_index=[0, 2])[0])/(2*np.pi)
    analytical_deflection = force*length**3/(3*EI)
    analytical_f = 1.875104068711961**2/(2*np.pi*length**2)*math.sqrt(EI/mu)
    return dict(schema='osr-analytical-laminate-coupon/1', scope='benchmark-coupon',
        executed=True, solver='Classical laminate theory + consistent-mass Euler-Bernoulli beam FE (NumPy/SciPy)',
        code_aster_executed=False, elements=elements, laminate_deg=[0, 90, 90, 0],
        ply_thickness_m=.001, length_m=length, width_m=width, thickness_m=thickness,
        lamina=dict(E1_Pa=E1, E2_Pa=E2, G12_Pa=G12, nu12=nu12, density_kg_m3=rho,
                    basis='Declared synthetic orthotropic benchmark constants, not measured material'),
        A_N_m=A.tolist(), B_N=B.tolist(), D_N_m=D.tolist(), EI_N_m2=float(EI),
        material_mass_kg=rho*length*width*thickness,
        tip_force_N=force, tip_deflection_FE_m=float(static[-2]),
        tip_deflection_analytical_m=float(analytical_deflection),
        frequencies_FE_hz=frequencies.tolist(), first_frequency_analytical_hz=analytical_f,
        limitations=['Cylindrical bending and small-displacement thin beam only',
                     'No transverse shear, delamination, joint, body torsion, prestress or actual equipped inertia',
                     'Not a Code_Aster execution and not evidence of a qualified composite vehicle'],
        configuration_adopted=False, physical_accepted=False, engineering_accepted=False)
