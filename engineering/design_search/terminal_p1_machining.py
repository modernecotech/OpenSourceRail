"""Proposed P1 terminal RHS finishing; analytic material only, never admission.

The narrow domain is the three retained square-corner RHS stock families, with
disjoint, centred, finite cardinal bores at one nominal complete wall. No source
proxy tensor or previously subtracted mass enters the set difference. The saved
normalization owns machining; the finished local plan supplies ancestry only.
Numerical wall-boundary consistency is not a manufacturing tolerance: any tiny
accepted axial protrusion has an explicit geometric truncation-error bound.
This module performs no file I/O, body composition, native work or selection.
"""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from math import fsum, inf, isclose, isfinite, nextafter, pi

CASES = ('low', 'base', 'high')
FAMILIES = {
    'body/end-beam': (2.29, .14, .25, .008),
    'body/cantrail': (17., .10, .25, .0045),
    'body/side-post': (2.35, .06, .08, .003),
}
FLAGS = ('physical_accepted', 'engineering_accepted', 'manufacturing_release',
         'operating_release', 'selected_reference_changed', 'native_eligible',
         'installed_assembly_accepted', 'release_approved', 'movement_authority',
         'canonical_admitted', 'complete_installed_mass', 'complete_installed_cost',
         'installed_mass_complete')
PART_KEYS = ('component_definition_id', 'id', 'mass_each_kg', 'material_id',
             'quantity_per_train', 'source_part_id', 'stock')
PATTERN_KEYS = ('bogie_index', 'car_allocation', 'count', 'geometry', 'id',
                'part_id', 'positions_m', 'rotation')
HOLDS = (
    'Unmeasured stock, extrusion corner and bore tolerances remain unknown.',
    'Survey original stock/walls/old bores; declared source has no old voids.',
    'Shared drilling datum and source-position/fixture tolerance stack unresolved.',
    'Native CAD volume and full V/F/Q comparison for one of each three families pending.',
    'Tool approach, finite swept access, lifting/support and removal sequence pending.',
    'Internal deburring, swarf capture, coating and galvanic protection pending.',
    'Fastener stack/retention, bearing, tearout, fatigue and HAZ evidence pending.',
    'QA hours, setup/fixture split and complete installed costs remain unknown.',
    'No P6 header ancestry, body integration, installed assembly or qualification inherited.',
)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _number(x):
    return type(x) in (int, float) and isfinite(x)


def _close(a, b):
    return _number(a) and _number(b) and isclose(a, b, rel_tol=1e-10, abs_tol=1e-12)


def _vector(x):
    return isinstance(x, list) and len(x) == 3 and all(_number(v) for v in x)


def _hex(x):
    return isinstance(x, str) and len(x) == 64 and all(c in '0123456789abcdef' for c in x)


def _cases(x, *, positive=False):
    return (isinstance(x, dict) and set(x) == set(CASES) and
            all(_number(v) and (v > 0 if positive else v >= 0) for v in x.values()))


def _unqualified(record):
    for key in FLAGS:
        if key in record:
            _require(record[key] is False, 'Qualification/selection flag must remain false: ' + key)


def _load(raw, pin):
    _require(isinstance(raw, bytes), 'Exact source bytes required')
    _require(isinstance(pin, dict) and _hex(pin.get('raw_sha256')) and
             _hex(pin.get('evaluation_id')), 'Explicit raw/evaluation pins required')
    _require(sha256(raw).hexdigest() == pin['raw_sha256'], 'Raw source mismatch')
    def unique_object(pairs):
        out = {}
        for k, v in pairs:
            _require(k not in out, 'Duplicate JSON field')
            out[k] = v
        return out
    value = json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw,
                       object_pairs_hook=unique_object)
    _require(isinstance(value, dict), 'Source object required')
    eid = value.get('evaluation_id')
    _require(eid == pin['evaluation_id'] and eid == identity({k: v for k, v in value.items() if k != 'evaluation_id'}),
             'Sealed evaluation mismatch')
    _unqualified(value)
    return value


def _unique(rows, key):
    _require(isinstance(rows, list) and all(isinstance(x, dict) and key in x for x in rows), 'Typed source list required')
    result = {x[key]: x for x in rows}
    _require(len(result) == len(rows), 'Duplicate source ' + key)
    return result


def _rotation(R):
    _require(isinstance(R, list) and len(R) == 3 and all(_vector(r) for r in R), 'Finite source rotation required')
    # This is a cardinal stock kernel, not arbitrary orientable CSG.
    _require(all(v in (-1, 0, 1) for r in R for v in r) and
             all(sum(v*v for v in r) == 1 for r in R) and
             all(sum(R[i][j]**2 for i in range(3)) == 1 for j in range(3)), 'Cardinal orthogonal rotation required')
    det = (R[0][0]*(R[1][1]*R[2][2]-R[1][2]*R[2][1]) -
           R[0][1]*(R[1][0]*R[2][2]-R[1][2]*R[2][0]) +
           R[0][2]*(R[1][0]*R[2][1]-R[1][1]*R[2][0]))
    _require(det == 1, 'Proper source rotation required')


def _mv(R, v):
    return [fsum(R[i][j]*v[j] for j in range(3)) for i in range(3)]


def _box(size):
    V = size[0]*size[1]*size[2]
    return V, [0., 0., 0.], [[V*size[i]**2/12 if i == j else 0. for j in range(3)] for i in range(3)]


def _cylinder(h):
    V = pi*h['radius_m']**2*h['length_m']
    c, a = h['centre_m'], h['axis']
    Q = [[V*(c[i]*c[j] + (h['length_m']**2/12 if i == a else h['radius_m']**2/4) * (i == j))
          for j in range(3)] for i in range(3)]
    return V, [V*x for x in c], Q


def _subtract(outer, removed):
    V, F, Q = outer
    return (V-fsum(x[0] for x in removed),
            [F[i]-fsum(x[1][i] for x in removed) for i in range(3)],
            [[Q[i][j]-fsum(x[2][i][j] for x in removed) for j in range(3)] for i in range(3)])


def _world(material, R, T):
    V, F, Q = material
    RF = _mv(R, F)
    RQR = [[fsum(R[i][a]*Q[a][b]*R[j][b] for a in range(3) for b in range(3))
            for j in range(3)] for i in range(3)]
    return (V, [RF[i]+V*T[i] for i in range(3)],
            [[RQR[i][j]+RF[i]*T[j]+T[i]*RF[j]+V*T[i]*T[j] for j in range(3)] for i in range(3)])


def _properties(material):
    V, F, Q = material
    rho = 2710.
    J = [[rho*(fsum(Q[k][k] for k in range(3) if k != i) if i == j else -Q[i][j])
          for j in range(3)] for i in range(3)]
    return dict(volume_m3=V, first_volume_moment_m4=F, second_volume_moment_m5=Q,
                density_kg_m3=rho, mass_kg=V*rho, first_mass_moment_kg_m=[rho*x for x in F],
                origin_inertia_kg_m2=J, nominal_centroid_m=[x/V for x in F])


def _add(*xs):
    return [sum(x[0] for x in xs), sum(x[1] for x in xs)]


def _mul(a, b):
    xs = [x*y for x in a for y in b]
    return [min(xs), max(xs)]


def _outward(pair):
    """Convert exact rational endpoints once, toward the outside of the set."""
    result = []
    for value, direction in zip(pair, (-inf, inf)):
        try:
            rounded = float(value)
        except OverflowError as exc:
            raise ValueError('Finite interval endpoint required') from exc
        _require(isfinite(rounded), 'Finite interval endpoint required')
        represented = Fraction(rounded)
        if (direction == -inf and represented > value) or (direction == inf and represented < value):
            rounded = nextafter(rounded, direction)
        _require(isfinite(rounded), 'Finite outward interval endpoint required')
        result.append(rounded)
    return result


def _pose_bounds(local, R, T, uncertainty):
    """Exact interval arithmetic conditional on the supplied rounded nominal V/F/Q.

    Fractions denote the *binary inputs*, not exact CAD integration coefficients.
    Stock/bore tolerances and nominal integration roundoff are not enclosed here.
    """
    _require(isinstance(local, (list, tuple)) and len(local) == 3, 'Nominal V/F/Q required')
    V, F, Q = local
    _require(_number(V) and V > 0 and _vector(F) and isinstance(Q, list) and
             len(Q) == 3 and all(_vector(row) for row in Q), 'Finite nonboolean nominal V/F/Q required')
    _rotation(R)
    _require(_vector(T) and _vector(uncertainty) and all(u >= 0 for u in uncertainty),
             'Finite nonboolean translation and nonnegative uncertainty required')
    V = Fraction(V)
    F = [Fraction(x) for x in F]
    Q = [[Fraction(x) for x in row] for row in Q]
    R = [[Fraction(x) for x in row] for row in R]
    RF = [sum(R[i][j]*F[j] for j in range(3)) for i in range(3)]
    world_zero = [[sum(R[i][a]*Q[a][b]*R[j][b] for a in range(3) for b in range(3))
                   for j in range(3)] for i in range(3)]
    t = [[Fraction(x)-Fraction(u), Fraction(x)+Fraction(u)] for x, u in zip(T, uncertainty)]
    Fw = [_add([x, x], _mul([V, V], p)) for x, p in zip(RF, t)]
    Qw = []
    for i in range(3):
        row = []
        for j in range(3):
            tt = _mul(t[i], t[j])
            if i == j:
                tt = [Fraction(0) if t[i][0] <= 0 <= t[i][1] else min(x*x for x in t[i]), max(x*x for x in t[i])]
            row.append(_add([world_zero[i][j]]*2, _mul([RF[i]]*2, t[j]),
                            _mul([RF[j]]*2, t[i]), _mul([V]*2, tt)))
        Qw.append(row)
    J = [[_mul([Fraction(2710)]*2, _add(*(Qw[k][k] for k in range(3) if k != i))) if i == j
          else _mul([Fraction(-2710)]*2, Qw[i][j]) for j in range(3)] for i in range(3)]
    return dict(first_volume_moment_m4=[_outward(x) for x in Fw],
                second_volume_moment_m5=[[_outward(x) for x in row] for row in Qw],
                origin_inertia_kg_m2=[[_outward(x) for x in row] for row in J],
                coefficient_domain='Exact binary values of supplied rounded nominal V/F/Q/R/T/uncertainty; not exact CAD coefficients',
                basis='Translation-only outward-rounded marginal intervals conditional on rounded nominal coefficients; stock/bore tolerances, integration roundoff and wall truncation excluded and unknown/separate')


def _wall_truncation(h, size, wall, R, T):
    """Bound full-cylinder subtraction error without snapping saved bore geometry.

    The existing _close gate is a numerical-consistency gate only. If accepted
    cylinder ends extend outside the exact binary-input wall slab, that material
    is not in the RHS and cannot be exactly subtracted. Its volume is bounded by
    4*r^2*outside_length (pi < 4). Moment bounds use its containing cylinder box.
    These are geometric truncation bounds only, not integration-roundoff bounds.
    """
    a = h['axis']
    c = [Fraction(x) for x in h['centre_m']]
    r, length = Fraction(h['radius_m']), Fraction(h['length_m'])
    edge, wall = Fraction(size[a])/2, Fraction(wall)
    slab = [edge-wall, edge] if c[a] > 0 else [-edge, -edge+wall]
    cut = [c[a]-length/2, c[a]+length/2]
    inside = max(Fraction(0), min(cut[1], slab[1])-max(cut[0], slab[0]))
    outside = length-inside
    uncovered = wall-inside
    volume_bound = 4*r*r*outside
    local_max = [abs(c[k])+(length/2 if k == a else r) for k in range(3)]
    world_max = [abs(Fraction(T[i]))+sum(abs(Fraction(R[i][k]))*local_max[k] for k in range(3)) for i in range(3)]
    def bounds(maxima):
        F = [volume_bound*x for x in maxima]
        Q = [[volume_bound*x*y for y in maxima] for x in maxima]
        J = [[Fraction(2710)*(sum(Q[k][k] for k in range(3) if k != i) if i == j else Q[i][j])
              for j in range(3)] for i in range(3)]
        upper = lambda x: _outward([Fraction(0), x])[1]
        return dict(volume_m3=upper(volume_bound), mass_kg=upper(2710*volume_bound),
            first_volume_moment_m4=[upper(x) for x in F],
            second_volume_moment_m5=[[upper(x) for x in row] for row in Q],
            origin_inertia_kg_m2=[[upper(x) for x in row] for row in J])
    return dict(full_cylinder_subtraction_exact_in_binary_geometry=(outside == 0),
        nominal_binary_interval_covers_wall=(cut[0] <= slab[0] and cut[1] >= slab[1]),
        outside_wall_axial_length_m_upper=_outward([0, outside])[1],
        uncovered_wall_axial_length_m_upper=_outward([0, uncovered])[1],
        material_error_absolute_upper_local=bounds(local_max),
        material_error_absolute_upper_world_nominal_pose=bounds(world_max),
        basis='Exact binary wall/cylinder intervals; pi<4 cap bound. Full-cylinder nominal subtraction may over-remove only within these explicit residual bounds; stock/bore tolerances and integration roundoff are not bounded here.',
        through_wall_manufacturing_accepted=False)


def _stock(part, pattern):
    pid = part['id']
    _require(pid in FAMILIES and part.get('material_id') == 'body/al6005a', 'Unsupported P1 material/family')
    dims = FAMILIES[pid]
    stock = dict(kind='rhs', length_m=dims[0], width_m=dims[1], depth_m=dims[2], wall_m=dims[3])
    _require(part['stock'] == stock, 'Source stock section differs from studied family')
    expected = dict(kind='rhs', size_m=list(dims[:3]), source_stock=stock, exact_stock=True,
                    definition_basis='exact-gross-stock', finished_geometry_verified=False)
    _require(pattern['geometry'] == expected and pattern['geometry']['exact_stock'] is True and
             pattern['geometry']['finished_geometry_verified'] is False, 'Unsupported old voids or source geometry')
    _require(_cases(part['mass_each_kg'], positive=True), 'Positive source mass cases required')
    V = dims[0]*(dims[1]*dims[2]-(dims[1]-2*dims[3])*(dims[2]-2*dims[3]))
    _require(all(_close(m/V, 2710.) for m in part['mass_each_kg'].values()), 'Source density must remain 2710')
    return list(dims[:3]), dims[3]


def _holes(row, size, wall):
    remaining = row['remaining_geometry']
    _require(set(remaining) == {'kind', 'size_m', 'wall_m', 'holes'} and remaining['kind'] == 'rhs' and
             remaining['size_m'] == size and remaining['wall_m'] == wall, 'Full remaining RHS geometry required')
    holes, ops = remaining['holes'], row['operations']
    _require(isinstance(holes, list) and holes and isinstance(ops, list) and len(holes) == len(ops), 'Exact bore count required')
    _unique(ops, 'id')
    boxes = []
    for h, op in zip(holes, ops):
        _require(set(h) == {'axis', 'centre_m', 'radius_m', 'length_m'}, 'Centred cylinder schema required')
        a, c, r, length = h['axis'], h['centre_m'], h['radius_m'], h['length_m']
        _require(type(a) is int and a in (1, 2) and _vector(c) and _number(r) and r > 0 and
                 _number(length) and length > 0, 'Finite cardinal non-end wall bore required')
        _require(_close(length, wall) and _close(abs(c[a]), size[a]/2-wall/2), 'Bore must numerically match one nominal complete wall')
        # No rounded edge/overlap predicates may admit material outside the RHS.
        fc, fr, fl = [Fraction(x) for x in c], Fraction(r), Fraction(length)
        _require(all(Fraction(size[k])/2-abs(fc[k])-fr > 0 for k in range(3) if k != a), 'Bore exits stock edge')
        _require(all(op.get(k) == h[k] for k in h) and op.get('source_id') == row['source_id'] and
                 op.get('material') == 'body/al6005a' and op.get('source_stock_retained') is True and
                 op.get('edge_strength_qualified') is False, 'Operation/material/qualification differs')
        expected_world = [x+y for x, y in zip(_mv(row['rotation'], c), row['at_m'])]
        _require(_vector(op.get('centre_world_m')) and all(_close(x, y) for x, y in zip(op['centre_world_m'], expected_world)), 'Bore world pose differs')
        _require(_close(op.get('removed_volume_m3'), pi*r*r*length), 'Removed cylinder volume differs')
        ligand = min(size[k]/2-abs(c[k])-r for k in range(3) if k != a)
        _require(_close(op.get('nominal_minimum_edge_ligament_m'), ligand), 'Edge ligament differs')
        extent = [fl/2 if k == a else fr for k in range(3)]
        box = [[fc[k]-extent[k], fc[k]+extent[k]] for k in range(3)]
        for old, oldbox in zip(holes[:len(boxes)], boxes):
            if old['axis'] == a:
                radial_squared = sum((fc[k]-Fraction(old['centre_m'][k]))**2 for k in range(3) if k != a)
                overlap = (radial_squared < (fr+Fraction(old['radius_m']))**2 and
                           abs(fc[a]-Fraction(old['centre_m'][a])) < (fl+Fraction(old['length_m']))/2)
            else:
                # Conservative refusal rather than an unsupported skew cut-union calculation.
                overlap = all(min(box[k][1], oldbox[k][1]) > max(box[k][0], oldbox[k][0]) for k in range(3))
            _require(not overlap, 'Overlapping/crossing bores require a separate union domain')
        boxes.append(box)
    return holes


def propose(parent_raw, normalization_raw, finished_local_raw, *, request):
    """Return train-once replacements only; do not modify/combine a full body.

    Request pins all three exact raw/evaluation sources, the original parent CID,
    a nonempty exact source-key roster, and the exact total operation count.
    A deliberately explicit fixture request may exercise fewer occurrences.
    """
    _require(isinstance(request, dict) and request.get('schema') == 'osr-terminal-p1-machining-request/1' and
             _hex(request.get('request_id')), 'Explicit machining request required')
    pins = request['inputs']
    _require(set(pins) == {'parent', 'normalization', 'finished_local'}, 'Exact three-input ancestry required')
    parent = _load(parent_raw, pins['parent'])
    norm = _load(normalization_raw, pins['normalization'])
    local = _load(finished_local_raw, pins['finished_local'])
    cid = parent.get('candidate_id')
    _require(_hex(cid) and identity(parent['physical_definition']) == cid and pins['parent'].get('candidate_id') == cid,
             'Exact original physical P1 required')
    _require(norm['source_parent'] == pins['parent'], 'Mixed normalization P1 ancestry')
    local_physical = pins['finished_local'].get('physical_id')
    _require(_hex(local_physical) and identity(local['physical_definition']) == local_physical and
             local['local_component_geometry_id'] == local_physical, 'Exact finished-local physical context required')
    _require(local['ancestry']['terminal_evaluation_id'] == norm['evaluation_id'] and
             local['source_input_pin']['sources']['terminal']['raw_sha256'] == pins['normalization']['raw_sha256'],
             'Finished local context does not retain this normalization')
    _require(local['source_transactions_applied'] is False, 'Source cuts already applied')
    rows = norm['source_machining_train_once']
    by_key = _unique(rows, 'source_id')
    wanted = request['source_ids']
    _require(isinstance(wanted, list) and wanted and len(set(wanted)) == len(wanted) and set(wanted) == set(by_key), 'Exact unique machining roster required')
    _require(type(request['operation_count']) is int and request['operation_count'] > 0 and
             request['operation_count'] == sum(len(x['operations']) for x in rows), 'Exact nonboolean operation count required')
    parts = _unique(parent['parts'], 'id')
    patterns = _unique(parent['patterns'], 'id')
    physical_parts = _unique(parent['physical_definition']['parts'], 'id')
    physical_patterns = _unique(parent['physical_definition']['occurrence_patterns'], 'id')
    replacements = []
    for key in sorted(wanted):
        row = by_key[key]
        _unqualified(row)
        pid, pattern_id, index = row['source_part_id'], row['source_pattern_id'], row['source_position_index']
        _require(pid in FAMILIES and pid in parts and pattern_id in patterns, 'Unknown P1 source part/pattern')
        part, pattern = parts[pid], patterns[pattern_id]
        _require(pattern['part_id'] == pid and type(index) is int and 0 <= index < pattern['count'], 'Source occurrence index/owner mismatch')
        _require(key == 'source/'+identity([cid, pattern_id, index]), 'Exact source key mismatch')
        _require(row['source_part_sha256'] == identity(part) and row['source_pattern_sha256'] == identity(pattern), 'Source part/pattern hash mismatch')
        _require(physical_parts.get(pid) == {k: part[k] for k in PART_KEYS} and
                 physical_patterns.get(pattern_id) == {k: pattern[k] for k in PATTERN_KEYS}, 'Physical/source projections differ')
        owner_patterns = [p for p in patterns.values() if p['part_id'] == pid]
        for p in owner_patterns:
            _require(type(p['count']) is int and p['count'] == len(p['positions_m']) and all(_vector(v) for v in p['positions_m']), 'Source count/positions differ')
        _require(type(part['quantity_per_train']) is int and part['quantity_per_train'] == sum(p['count'] for p in owner_patterns), 'Source stock ownership count differs')
        _require(_vector(row['at_m']) and row['at_m'] == pattern['positions_m'][index] and row['rotation'] == pattern['rotation'] and
                 row['car_allocation'] == pattern['car_allocation'], 'Original occurrence pose/allocation differs')
        _rotation(row['rotation'])
        uncertainty = pattern['uncertainty_m']
        _require(_vector(uncertainty) and all(_close(x, .002) for x in uncertainty), 'Explicit source 2 mm pose bounds required')
        size, wall = _stock(part, pattern)
        holes = _holes(row, size, wall)
        truncation = [_wall_truncation(h, size, wall, row['rotation'], row['at_m']) for h in holes]
        _require(row['kind'] == 'machine_in_place' and row['gross_paid_source_retained'] is True and
                 _cases(row['paid_source_cost_usd']) and row['paid_source_cost_usd'] == part['direct_cost_each_usd'], 'Gross paid source owner must remain once')
        _require(_number(row['additional_process_h']) and _close(row['additional_process_h'], len(holes)*.05) and
                 _cases(row['additional_process_USD']) and row['additional_QA_h'] is None, 'Existing process/unknown QA scope required')
        outer = _box(size)
        cavity = _box([size[0], size[1]-2*wall, size[2]-2*wall])
        removed = [_cylinder(h) for h in holes]
        gross = _subtract(outer, [cavity])
        finished = _subtract(outer, [cavity, *removed])
        cut_V = fsum(x[0] for x in removed)
        _require(0 < finished[0] < gross[0] and _close(row['removed_material_m3'], cut_V), 'Positive complete set difference required')
        expected_removed_moment = [2710.*fsum(x[1][i] for x in [_world(h, row['rotation'], row['at_m']) for h in removed]) for i in range(3)]
        _require(_cases(row['removed_mass_kg']) and _cases(row['remaining_mass_kg'], positive=True) and
                 all(_close(row['removed_mass_kg'][c], cut_V*2710.) and _close(row['remaining_mass_kg'][c], finished[0]*2710.) for c in CASES), 'Source mass cases inconsistent with complete geometry')
        _require(all(_vector(row['removed_moment_kg_m'][c]) and all(_close(x, y) for x, y in zip(row['removed_moment_kg_m'][c], expected_removed_moment)) for c in CASES), 'Source removed first moment differs')
        world = _world(finished, row['rotation'], row['at_m'])
        _require(_vector(row['remaining_centroid_world_m']) and all(_close(x, y) for x, y in zip(row['remaining_centroid_world_m'], [x/world[0] for x in world[1]])), 'Source remaining centroid differs')
        geometry = dict(kind='analytic-rhs-minus-disjoint-wall-cylinders', size_m=size, wall_m=wall,
                        cavity_size_m=[size[0], size[1]-2*wall, size[2]-2*wall],
                        holes=deepcopy(holes), cut_convention='member-local centre, unsigned cardinal axis, symmetric +/-length/2')
        replacements.append(dict(source_id=key, source_part_id=pid, source_pattern_id=pattern_id,
            source_position_index=index, geometry=geometry, at_m=deepcopy(row['at_m']), rotation=deepcopy(row['rotation']),
            car_allocation=deepcopy(row['car_allocation']), material_id='body/al6005a',
            material_properties_local_nominal=_properties(finished), material_properties_world_nominal=_properties(world),
            pose_only_marginal_bounds=_pose_bounds(finished, row['rotation'], row['at_m'], uncertainty),
            wall_boundary_numerical_residuals=truncation,
            nominal_integration_contract='Rounded nominal outer-box minus cavity minus full cylinders. Any accepted axial wall-boundary protrusion is separately bounded per bore; these nominal coefficients are not exact clipped-set properties.',
            source_pose_uncertainty_m=deepcopy(uncertainty), stock_tolerance_m=None, bore_tolerance_m=None,
            complete_material_property_bounds=None, gross_stock_volume_m3=gross[0], removed_volume_m3=cut_V,
            gross_paid_source_retained_once=True, source_record=deepcopy(row),
            accounting=dict(status='nonadditive-existing-stock-and-machining-owners-retained-once',
                paid_source_cost_usd=deepcopy(row['paid_source_cost_usd']),
                additional_process_USD=deepcopy(row['additional_process_USD']), additional_process_h=row['additional_process_h'],
                additional_QA_h=None, new_invoice_generated=False, complete_installed_cost=False),
            holds=list(HOLDS), **dict.fromkeys(FLAGS, False)))
    physical = dict(schema='osr-terminal-p1-machining-physical-proposal/1', parent_candidate_id=cid,
        frame='original-P1-world', units='m-kg-SI', geometry_lift_to_apply_m=0.,
        replacements=[{k: r[k] for k in ('source_id', 'source_part_id', 'source_pattern_id', 'source_position_index',
            'geometry', 'at_m', 'rotation', 'car_allocation', 'material_id')} for r in replacements])
    result = dict(schema='osr-terminal-p1-machining-proposal/1', request_id=request['request_id'],
        physical_definition=physical, candidate_id=identity(physical), inputs=deepcopy(pins),
        source_context_role='Finished local plan is ancestry only; normalization owns the ten machining dispositions',
        proposed_finished_replacements=replacements, replacement_count=len(replacements), operation_count=request['operation_count'],
        full_body_generated=False, source_transactions_applied=False,
        native_crosscheck_complete=False, source_key_formula='source/sha256(canonical-LF([P1CID,pattern_id,index]))',
        holds=list(HOLDS), **dict.fromkeys(FLAGS, False))
    result['evaluation_id'] = identity(result)
    return result
