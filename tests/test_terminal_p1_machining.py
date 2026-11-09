"""Invented tiny source graphs only; no retained source, CAD, FEM or body run."""
from copy import deepcopy
from hashlib import sha256
import gzip
import math
import pytest
from engineering.design_search import terminal_p1_machining as t


I = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
ROTATIONS = (I, [[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]],
             [[0., 1., 0.], [0., 0., 1.], [1., 0., 0.]])


def seal(x):
    x = deepcopy(x)
    x.pop('evaluation_id', None)
    x['evaluation_id'] = t.identity(x)
    return x


def raw_pin(x):
    x = seal(x)
    raw = gzip.compress(t.encoded(x), mtime=0)
    return x, raw, dict(evaluation_id=x['evaluation_id'], raw_sha256=sha256(raw).hexdigest())


def mv(R, v):
    return [sum(R[i][j]*v[j] for j in range(3)) for i in range(3)]


def fixture(radius=.002):
    """Three source families, one occurrence each and two opposite-wall bores."""
    parts, patterns = [], []
    for n, (pid, (length, width, depth, wall)) in enumerate(t.FAMILIES.items()):
        stock = dict(kind='rhs', length_m=length, width_m=width, depth_m=depth, wall_m=wall)
        volume = length*(width*depth-(width-2*wall)*(depth-2*wall))
        part = dict(component_definition_id=t.identity(['invented', pid]), id=pid,
            mass_each_kg=dict.fromkeys(t.CASES, volume*2710.), material_id='body/al6005a',
            quantity_per_train=1, source_part_id=pid, stock=stock,
            direct_cost_each_usd=dict(low=1., base=2., high=3.), fixture='invented')
        pattern = dict(bogie_index=None, car_allocation=[[0, 1.]], count=1,
            geometry=dict(kind='rhs', size_m=[length, width, depth], source_stock=deepcopy(stock),
                exact_stock=True, definition_basis='exact-gross-stock', finished_geometry_verified=False),
            id=pid+'@invented', part_id=pid, positions_m=[[.1+n*40., -.2, .3]],
            rotation=ROTATIONS[n], uncertainty_m=[.002]*3,
            # Deliberately huge group proxy; it must never enter material moments.
            shape_I_per_kg=[[1e9, 0., 0.], [0., 1e9, 0.], [0., 0., 1e9]])
        parts.append(part)
        patterns.append(pattern)
    parent = dict(parts=parts, patterns=patterns, physical_definition=dict(schema='invented-P1',
        parts=[{k: p[k] for k in t.PART_KEYS} for p in parts],
        occurrence_patterns=[{k: p[k] for k in t.PATTERN_KEYS} for p in patterns]),
        **dict.fromkeys(t.FLAGS, False))
    parent['candidate_id'] = t.identity(parent['physical_definition'])
    rows = []
    for part, pattern in zip(parts, patterns):
        L, W, D, wall = t.FAMILIES[part['id']]
        key = 'source/'+t.identity([parent['candidate_id'], pattern['id'], 0])
        R, T = pattern['rotation'], pattern['positions_m'][0]
        holes = [dict(axis=1, centre_m=[.03, s*(W-wall)/2, .01], radius_m=radius, length_m=wall) for s in (-1, 1)]
        operations = []
        for j, h in enumerate(holes):
            world = [x+y for x, y in zip(mv(R, h['centre_m']), T)]
            operations.append(dict(h, id=key+'/bore/'+str(j), source_id=key, centre_world_m=world,
                removed_volume_m3=math.pi*h['radius_m']**2*wall, material='body/al6005a',
                source_stock_retained=True, edge_strength_qualified=False,
                nominal_minimum_edge_ligament_m=min(L/2-.03-radius, D/2-.01-radius)))
        V = L*(W*D-(W-2*wall)*(D-2*wall))
        loss = sum(h['removed_volume_m3'] for h in operations)
        moment = [sum(h['removed_volume_m3']*2710.*h['centre_world_m'][k] for h in operations) for k in range(3)]
        centroid = [(V*T[k]-moment[k]/2710.)/(V-loss) for k in range(3)]
        rows.append(dict(source_id=key, source_part_id=part['id'], source_pattern_id=pattern['id'],
            source_position_index=0, source_part_sha256=t.identity(part), source_pattern_sha256=t.identity(pattern),
            terminal_id='invented/front', kind='machine_in_place', operations=operations,
            remaining_geometry=dict(kind='rhs', size_m=[L, W, D], wall_m=wall, holes=holes),
            gross_paid_source_retained=True, removed_material_m3=loss,
            removed_mass_kg=dict.fromkeys(t.CASES, loss*2710.),
            removed_moment_kg_m={c: deepcopy(moment) for c in t.CASES},
            remaining_mass_kg=dict.fromkeys(t.CASES, (V-loss)*2710.),
            remaining_centroid_world_m=centroid, at_m=deepcopy(T), rotation=deepcopy(R),
            car_allocation=[[0, 1.]], paid_source_cost_usd=deepcopy(part['direct_cost_each_usd']),
            additional_process_USD=dict(low=.6, base=1., high=1.6), additional_process_h=.1,
            additional_QA_h=None, person_hours_scope='invented TRAIN-ONCE', QA_hours_scope='unknown'))
    norm = dict(source_machining_train_once=rows, source_parent=None, **dict.fromkeys(t.FLAGS, False))
    local = dict(ancestry={}, source_input_pin=dict(sources=dict(terminal={})), source_transactions_applied=False,
                 physical_definition=dict(schema='invented-finished-local', material=[]), **dict.fromkeys(t.FLAGS, False))
    return parent, norm, local


def prepare(data):
    parent, norm, local = deepcopy(data)
    parent['candidate_id'] = t.identity(parent['physical_definition'])
    parent, pr, pp = raw_pin(parent)
    pp['candidate_id'] = parent['candidate_id']
    norm['source_parent'] = deepcopy(pp)
    norm, nr, np = raw_pin(norm)
    local['ancestry']['terminal_evaluation_id'] = norm['evaluation_id']
    local['source_input_pin']['sources']['terminal']['raw_sha256'] = np['raw_sha256']
    local['local_component_geometry_id'] = t.identity(local['physical_definition'])
    local, lr, lp = raw_pin(local)
    lp['physical_id'] = local['local_component_geometry_id']
    request = dict(schema='osr-terminal-p1-machining-request/1', request_id='a'*64,
        inputs=dict(parent=pp, normalization=np, finished_local=lp),
        source_ids=[r['source_id'] for r in norm['source_machining_train_once']],
        operation_count=sum(len(r['operations']) for r in norm['source_machining_train_once']))
    return (pr, nr, lr), request


def run(data=None):
    raws, request = prepare(fixture() if data is None else data)
    return t.propose(*raws, request=request)


def rebind(data):
    """Reseal invented changed graphs, preserving deliberately changed row metadata."""
    parent, norm, _ = data
    parent['physical_definition']['parts'] = [{k: p[k] for k in t.PART_KEYS} for p in parent['parts']]
    parent['physical_definition']['occurrence_patterns'] = [{k: p[k] for k in t.PATTERN_KEYS} for p in parent['patterns']]
    parent['candidate_id'] = t.identity(parent['physical_definition'])
    parts = {p['id']: p for p in parent['parts']}
    patterns = {p['id']: p for p in parent['patterns']}
    for r in norm['source_machining_train_once']:
        r['source_part_sha256'] = t.identity(parts[r['source_part_id']])
        r['source_pattern_sha256'] = t.identity(patterns[r['source_pattern_id']])
        oldkey = r['source_id']
        r['source_id'] = 'source/'+t.identity([parent['candidate_id'], r['source_pattern_id'], r['source_position_index']])
        for op in r['operations']:
            op['source_id'] = r['source_id']
            op['id'] = op['id'].replace(oldkey, r['source_id'])
    return data


def test_complete_rhs_set_difference_conserves_independent_volume_and_moments():
    data = fixture()
    before = deepcopy(data)
    out = run(data)
    assert data == before
    assert out['operation_count'] == 6 and out['replacement_count'] == 3
    by_id = {r['source_part_id']: r for r in out['proposed_finished_replacements']}
    for pid, (L, W, D, wall) in t.FAMILIES.items():
        row = by_id[pid]
        p = row['material_properties_local_nominal']
        gross = L*(W*D-(W-2*wall)*(D-2*wall))
        hole_V = math.pi*.002**2*wall
        assert p['volume_m3'] == pytest.approx(gross-2*hole_V, rel=1e-12)
        assert p['first_volume_moment_m4'] == pytest.approx([-2*hole_V*.03, 0., -2*hole_V*.01])
        expected_xx = (W*D-(W-2*wall)*(D-2*wall))*L**3/12 - 2*hole_V*(.03**2+.002**2/4)
        assert p['second_volume_moment_m5'][0][0] == pytest.approx(expected_xx, rel=1e-12)
        assert p['origin_inertia_kg_m2'][0][1] == pytest.approx(0.)
        assert p['mass_kg'] == pytest.approx(p['volume_m3']*2710.)
        assert p['nominal_centroid_m'][0] < 0
        assert p['nominal_centroid_m'][2] < 0
        assert row['source_record'] in before[1]['source_machining_train_once']


def test_original_three_rigid_frames_once_and_origin_tensor_not_group_proxy():
    out = run()
    for row in out['proposed_finished_replacements']:
        a = row['material_properties_local_nominal']
        b = row['material_properties_world_nominal']
        R, T = row['rotation'], row['at_m']
        assert b['nominal_centroid_m'] == pytest.approx([x+y for x, y in zip(mv(R, a['nominal_centroid_m']), T)])
        for i in range(3):
            for j in range(3):
                expected = sum(R[i][u]*a['second_volume_moment_m5'][u][v]*R[j][v] for u in range(3) for v in range(3))
                RF = mv(R, a['first_volume_moment_m4'])
                expected += RF[i]*T[j]+T[i]*RF[j]+a['volume_m3']*T[i]*T[j]
                assert b['second_volume_moment_m5'][i][j] == pytest.approx(expected, rel=1e-12, abs=1e-15)
        assert max(a['origin_inertia_kg_m2'][i][i] for i in range(3)) < 1e6
    assert out['physical_definition']['geometry_lift_to_apply_m'] == 0.


def test_pose_only_intervals_enclose_all_translation_corners_but_tolerances_unknown():
    import itertools
    for row in run()['proposed_finished_replacements']:
        p = row['material_properties_local_nominal']
        local = (p['volume_m3'], p['first_volume_moment_m4'], p['second_volume_moment_m5'])
        bounds = row['pose_only_marginal_bounds']
        for delta in itertools.product((-.002, .002), repeat=3):
            props = t._properties(t._world(local, row['rotation'], [x+d for x, d in zip(row['at_m'], delta)]))
            for name in ('second_volume_moment_m5', 'origin_inertia_kg_m2'):
                for i in range(3):
                    for j in range(3):
                        lo, hi = bounds[name][i][j]
                        assert lo-1e-8 <= props[name][i][j] <= hi+1e-8
        assert row['stock_tolerance_m'] is None and row['bore_tolerance_m'] is None
        assert row['complete_material_property_bounds'] is None


def test_existing_prices_process_hours_unknown_QA_and_false_acceptance_preserved():
    data = fixture()
    out = run(data)
    rows = {r['source_id']: r for r in data[1]['source_machining_train_once']}
    for r in out['proposed_finished_replacements']:
        original, account = rows[r['source_id']], r['accounting']
        for k in ('paid_source_cost_usd', 'additional_process_USD', 'additional_process_h', 'additional_QA_h'):
            assert account[k] == original[k]
        assert account['new_invoice_generated'] is False
        assert account['complete_installed_cost'] is False
        assert 'nonadditive' in account['status']
        assert all(r[k] is False for k in t.FLAGS)
        assert len(r['holds']) >= 8
    assert all(out[k] is False for k in t.FLAGS)
    assert out['source_transactions_applied'] is False and out['full_body_generated'] is False


def test_price_only_change_changes_evaluation_but_not_physical_geometry():
    a = run()
    data = fixture()
    data[0]['parts'][0]['direct_cost_each_usd']['base'] = 99.
    data[1]['source_machining_train_once'][0]['paid_source_cost_usd']['base'] = 99.
    b = run(rebind(data))
    assert a['candidate_id'] == b['candidate_id']
    assert a['physical_definition'] == b['physical_definition']
    assert a['evaluation_id'] != b['evaluation_id']


def test_bore_change_changes_material_and_physical_identity_not_original_source():
    a, b = run(fixture(.002)), run(fixture(.0025))
    assert a['candidate_id'] != b['candidate_id']
    assert a['inputs']['parent'] == b['inputs']['parent']
    for x, y in zip(a['proposed_finished_replacements'], b['proposed_finished_replacements']):
        assert x['material_properties_local_nominal']['mass_kg'] > y['material_properties_local_nominal']['mass_kg']
        assert x['source_record']['paid_source_cost_usd'] == y['source_record']['paid_source_cost_usd']


@pytest.mark.parametrize('change', [
    lambda d: d[1]['source_machining_train_once'].append(deepcopy(d[1]['source_machining_train_once'][0])),
    lambda d: d[1]['source_machining_train_once'][0].update(source_id='source/'+'0'*64),
    lambda d: d[1]['source_machining_train_once'][0].update(source_part_sha256='0'*64),
    lambda d: d[1]['source_machining_train_once'][0].update(source_position_index=True),
    lambda d: d[1]['source_machining_train_once'][0].update(at_m=[.1, -.2, .45]),
    lambda d: d[1]['source_machining_train_once'][0].update(rotation=[[-1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]),
    lambda d: d[1]['source_machining_train_once'][0].update(gross_paid_source_retained=False),
    lambda d: d[1]['source_machining_train_once'][0]['paid_source_cost_usd'].update(base=0.),
    lambda d: d[1]['source_machining_train_once'][0].update(additional_QA_h=0.),
    lambda d: d[1]['source_machining_train_once'][0].update(additional_process_h=.05),
    lambda d: d[1]['source_machining_train_once'][0]['removed_mass_kg'].update(base=0.),
    lambda d: d[1]['source_machining_train_once'][0]['remaining_mass_kg'].update(base=0.),
    lambda d: d[1]['source_machining_train_once'][0]['removed_moment_kg_m']['base'].__setitem__(0, 0.),
    lambda d: d[1]['source_machining_train_once'][0]['remaining_centroid_world_m'].__setitem__(0, 0.),
    lambda d: d[2].update(source_transactions_applied=True),
    lambda d: d[0].update(physical_accepted=True),
    lambda d: d[1].update(native_eligible=True),
    lambda d: d[2].update(installed_assembly_accepted=True),
    lambda d: d[2].update(canonical_admitted=True),
    lambda d: d[0].update(installed_mass_complete=True),
    lambda d: d[1].update(physical_accepted=0),
])
def test_duplicate_mixed_pose_accounting_and_qualification_refusals(change):
    data = fixture()
    change(data)
    with pytest.raises(ValueError):
        run(data)


@pytest.mark.parametrize('change', [
    lambda d: d[0]['patterns'][0]['geometry'].update(holes=[dict(axis=1, centre_m=[0, 0, 0], radius_m=.001, length_m=.01)]),
    lambda d: d[0]['patterns'][0]['geometry'].update(kind='box'),
    lambda d: d[0]['patterns'][0]['geometry'].update(finished_geometry_verified=True),
    lambda d: d[0]['patterns'][0]['geometry'].update(exact_stock=1),
    lambda d: d[0]['patterns'][0].update(uncertainty_m=[0., 0., 0.]),
    lambda d: d[0]['parts'][0]['mass_each_kg'].update(base=100.),
    lambda d: d[0]['parts'][0].update(material_id='P6/header'),
    lambda d: d[0]['parts'][0].update(quantity_per_train=2),
    lambda d: d[0]['patterns'][0].update(count=2),
    lambda d: d[0]['parts'][0]['stock'].update(wall_m=.007),
])
def test_resealed_but_unsupported_source_domain_still_refuses(change):
    data = fixture()
    change(data)
    with pytest.raises(ValueError):
        run(rebind(data))


@pytest.mark.parametrize('change', [
    lambda r: r['remaining_geometry']['holes'][0].update(axis=True),
    lambda r: r['remaining_geometry']['holes'][0].update(axis=0),
    lambda r: r['remaining_geometry']['holes'][0].update(length_m=.05),
    lambda r: r['remaining_geometry']['holes'][0]['centre_m'].__setitem__(1, 0.),
    lambda r: r['remaining_geometry']['holes'][0]['centre_m'].__setitem__(0, 1.145),
    lambda r: r['remaining_geometry']['holes'][0].update(radius_m=-.002),
    lambda r: r['remaining_geometry']['holes'][0].update(kind='base-cylinder'),
    lambda r: r['remaining_geometry']['holes'].append(deepcopy(r['remaining_geometry']['holes'][0])),
    lambda r: r['operations'][0]['centre_world_m'].__setitem__(0, 999.),
    lambda r: r['operations'][0].update(source_stock_retained=1),
    lambda r: r['operations'][0].update(edge_strength_qualified=True),
])
def test_cut_schema_wall_edge_count_pose_and_acceptance_refusals(change):
    data = fixture()
    change(data[1]['source_machining_train_once'][0])
    with pytest.raises(ValueError):
        run(data)


def test_overlapping_equal_wall_bores_refuse_before_any_summed_subtraction():
    data = fixture()
    row = data[1]['source_machining_train_once'][0]
    row['remaining_geometry']['holes'][1] = deepcopy(row['remaining_geometry']['holes'][0])
    old_id = row['operations'][1]['id']
    row['operations'][1] = dict(row['operations'][0], id=old_id)
    with pytest.raises(ValueError, match='Overlapping'):
        run(data)


def test_perpendicular_corner_bores_refuse_unsupported_cut_union():
    data = fixture()
    row = data[1]['source_machining_train_once'][0]
    wall = row['remaining_geometry']['wall_m']
    L, W, D = row['remaining_geometry']['size_m']
    for j, axis in enumerate((1, 2)):
        h = dict(axis=axis, centre_m=[.03, (W-wall)/2, (D-wall)/2], radius_m=.002, length_m=wall)
        row['remaining_geometry']['holes'][j] = h
        row['operations'][j].update(h)
        row['operations'][j]['centre_world_m'] = [x+y for x, y in zip(mv(row['rotation'], h['centre_m']), row['at_m'])]
        row['operations'][j]['nominal_minimum_edge_ligament_m'] = min(
            (L, W, D)[k]/2-abs(h['centre_m'][k])-.002 for k in range(3) if k != axis)
    with pytest.raises(ValueError, match='Overlapping/crossing'):
        run(data)


@pytest.mark.parametrize('which', range(3))
def test_exact_raw_pin_required(which):
    raw, request = prepare(fixture())
    raw = list(raw)
    raw[which] += b'corruption'
    with pytest.raises(ValueError, match='Raw source mismatch'):
        t.propose(*raw, request=request)


def test_exact_source_roster_counts_and_three_input_ancestry():
    raw, req = prepare(fixture())
    for change in (lambda r: r['source_ids'].pop(), lambda r: r['source_ids'].append(r['source_ids'][0]),
                   lambda r: r.update(operation_count=True), lambda r: r.update(operation_count=5),
                   lambda r: r['inputs'].pop('normalization')):
        bad = deepcopy(req)
        change(bad)
        with pytest.raises(ValueError):
            t.propose(*raw, request=bad)


def test_tampered_seal_and_finished_local_ancestry_refuse():
    data = fixture()
    raw, req = prepare(data)
    bad = deepcopy(data[2])
    bad['evaluation_id'] = '0'*64
    encoded = t.encoded(bad)
    req['inputs']['finished_local'] = dict(raw_sha256=sha256(encoded).hexdigest(), evaluation_id='0'*64)
    with pytest.raises(ValueError, match='Sealed'):
        t.propose(raw[0], raw[1], encoded, request=req)
    parent, norm, local = fixture()
    raws, req = prepare((parent, norm, local))
    import json
    local = json.loads(gzip.decompress(raws[2]))
    local['ancestry']['terminal_evaluation_id'] = '0'*64
    local, lr, lp = raw_pin(local)
    lp['physical_id'] = local['local_component_geometry_id']
    req['inputs']['finished_local'] = lp
    with pytest.raises(ValueError, match='context'):
        t.propose(raws[0], raws[1], lr, request=req)


def test_finished_local_physical_pin_and_duplicate_json_fields_refuse():
    raw, req = prepare(fixture())
    req['inputs']['finished_local']['physical_id'] = '0'*64
    with pytest.raises(ValueError, match='physical context'):
        t.propose(*raw, request=req)
    bad = b'{"evaluation_id":"x","evaluation_id":"y"}\n'
    pin = dict(raw_sha256=sha256(bad).hexdigest(), evaluation_id='0'*64)
    with pytest.raises(ValueError, match='Duplicate JSON'):
        t._load(bad, pin)


def exact_point_properties(local, rotation, position):
    """Independent homogeneous-moment congruence at a point, never interval code."""
    from fractions import Fraction as F
    volume, first, second = local
    moment4 = [[F(second[i][j]) for j in range(3)]+[F(first[i])] for i in range(3)]
    moment4.append([F(v) for v in first]+[F(volume)])
    transform4 = [[F(v) for v in rotation[i]]+[position[i]] for i in range(3)]
    transform4.append([F(0), F(0), F(0), F(1)])
    moved = [[sum(transform4[i][a]*moment4[a][b]*transform4[j][b] for a in range(4) for b in range(4))
              for j in range(4)] for i in range(4)]
    # Direct Cartesian integral identities, independent of source interval transforms.
    inertia = [[F(2710)*(moved[1][1]+moved[2][2]), -F(2710)*moved[0][1], -F(2710)*moved[0][2]],
               [-F(2710)*moved[1][0], F(2710)*(moved[0][0]+moved[2][2]), -F(2710)*moved[1][2]],
               [-F(2710)*moved[2][0], -F(2710)*moved[2][1], F(2710)*(moved[0][0]+moved[1][1])]]
    return [moved[i][3] for i in range(3)], [row[:3] for row in moved[:3]], inertia


@pytest.mark.parametrize('coordinate', [2.25, 17., 105.25, -105.25, 1e12, -1e12, 1e20])
@pytest.mark.parametrize('rotation', ROTATIONS)
def test_fraction_corner_oracle_encloses_without_endpoint_epsilon(coordinate, rotation):
    from fractions import Fraction as F
    import itertools
    local = (.7, [.01, -.02, .03], [[.5, .02, -.01], [.02, .4, .03], [-.01, .03, .3]])
    position, uncertainty = [coordinate, -.1, 2.25], [.002, .003, .004]
    bounds = t._pose_bounds(local, rotation, position, uncertainty)
    for signs in itertools.product((-1, 1), repeat=3):
        exact_position = [F(x)+s*F(u) for x, s, u in zip(position, signs, uncertainty)]
        first, second, inertia = exact_point_properties(local, rotation, exact_position)
        for i in range(3):
            lo, hi = bounds['first_volume_moment_m4'][i]
            assert F(lo) <= first[i] <= F(hi)
            for name, expected in [('second_volume_moment_m5', second), ('origin_inertia_kg_m2', inertia)]:
                for j in range(3):
                    lo, hi = bounds[name][i][j]
                    assert F(lo) <= expected[i][j] <= F(hi)
    assert 'rounded nominal' in bounds['coefficient_domain']


def test_exact_binary_unit_witness_and_correlated_square_interior():
    from fractions import Fraction as F
    local = (1., [0., 0., 0.], [[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])
    for coordinate in (2.25, 17., 105.25):
        bounds = t._pose_bounds(local, I, [coordinate, 0., 0.], [.002, .002, .002])
        lo, hi = bounds['first_volume_moment_m4'][0]
        assert F(lo) <= F(coordinate)-F(.002)
        assert F(hi) >= F(coordinate)+F(.002)
    centered = t._pose_bounds(local, I, [0., 0., 0.], [1., 2., 3.])
    for i, upper in enumerate((1., 4., 9.)):
        assert centered['second_volume_moment_m5'][i][i] == [0., upper]
    # Off-diagonal may be negative, while a correlated same-coordinate square cannot.
    assert centered['second_volume_moment_m5'][0][1] == [-2., 2.]


@pytest.mark.parametrize('argument,index,value', [
    ('local', 0, True), ('local_first', 0, False), ('local_second', 0, True),
    ('position', 0, True), ('uncertainty', 0, False), ('uncertainty', 0, -.002),
    ('rotation', 0, True), ('position', 0, math.inf), ('uncertainty', 0, math.nan),
])
def test_pose_bounds_refuse_boolean_nonfinite_and_negative_inputs(argument, index, value):
    local = [1., [0., 0., 0.], [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]]
    rotation, position, uncertainty = deepcopy(I), [105.25, 0., 0.], [.002]*3
    if argument == 'local_first':
        local[1][index] = value
    elif argument == 'local_second':
        local[2][index][index] = value
    elif argument == 'rotation':
        rotation[index][index] = value
    else:
        {'local': local, 'position': position, 'uncertainty': uncertainty}[argument][index] = value
    with pytest.raises(ValueError):
        t._pose_bounds(local, rotation, position, uncertainty)


def boundary_row(hole, size, wall):
    row = deepcopy(fixture()[1]['source_machining_train_once'][0])
    row['at_m'], row['rotation'] = [105.25, 0., 2.25], I
    row['remaining_geometry'] = dict(kind='rhs', size_m=size, wall_m=wall, holes=[deepcopy(hole)])
    world = [x+y for x, y in zip(hole['centre_m'], row['at_m'])]
    row['operations'] = [dict(hole, id='invented/boundary-bore', source_id=row['source_id'],
        centre_world_m=world, material='body/al6005a', source_stock_retained=True,
        edge_strength_qualified=False, removed_volume_m3=math.pi*hole['radius_m']**2*hole['length_m'],
        nominal_minimum_edge_ligament_m=min(size[k]/2-abs(hole['centre_m'][k])-hole['radius_m'] for k in range(3) if k != hole['axis']))]
    return row


@pytest.mark.parametrize('sign', (-1, 1))
def test_numerical_boundary_protrusion_retains_source_and_bounds_actual_cap(sign):
    from fractions import Fraction as F
    size, wall = [2., .125, .25], .03125
    shifted = math.nextafter(sign*.046875, sign*math.inf)
    h = dict(axis=1, centre_m=[.01, shifted, .02], radius_m=.001953125, length_m=wall)
    before = deepcopy(h)
    row = boundary_row(h, size, wall)
    assert t._holes(row, size, wall) == [h]
    bound = t._wall_truncation(h, size, wall, I, row['at_m'])
    assert h == before
    displacement = abs(F(shifted)-F(sign*.046875))
    # Independent high-precision decimal pi reference for the tiny excluded cap.
    pi_reference = F('3.141592653589793238462643383279502884197169399375105820974944592307816406286')
    actual_volume = pi_reference*F(h['radius_m'])**2*displacement
    upper = bound['material_error_absolute_upper_local']
    assert 0 < actual_volume <= F(upper['volume_m3'])
    assert displacement <= F(bound['outside_wall_axial_length_m_upper'])
    assert displacement <= F(bound['uncovered_wall_axial_length_m_upper'])
    assert not bound['full_cylinder_subtraction_exact_in_binary_geometry']
    assert not bound['nominal_binary_interval_covers_wall']
    assert bound['through_wall_manufacturing_accepted'] is False
    # Every cap lies within the full cylinder box, independently checked at corners.
    for i in range(3):
        extent_i = F(h['length_m'])/2 if i == h['axis'] else F(h['radius_m'])
        max_i = abs(F(h['centre_m'][i]))+extent_i
        assert actual_volume*max_i <= F(upper['first_volume_moment_m4'][i])
        for j in range(3):
            extent_j = F(h['length_m'])/2 if j == h['axis'] else F(h['radius_m'])
            max_j = abs(F(h['centre_m'][j]))+extent_j
            assert actual_volume*max_i*max_j <= F(upper['second_volume_moment_m5'][i][j])


def test_short_bore_does_not_claim_complete_wall_and_large_protrusion_refuses():
    size, wall = [2., .125, .25], .03125
    short = dict(axis=1, centre_m=[.01, .046875, .02], radius_m=.001953125,
                 length_m=math.nextafter(wall, 0.))
    row = boundary_row(short, size, wall)
    assert t._holes(row, size, wall) == [short]
    bound = t._wall_truncation(short, size, wall, I, row['at_m'])
    assert bound['full_cylinder_subtraction_exact_in_binary_geometry']
    assert not bound['nominal_binary_interval_covers_wall']
    assert bound['uncovered_wall_axial_length_m_upper'] > 0
    assert bound['material_error_absolute_upper_local']['volume_m3'] == 0.
    protruding = dict(short, length_m=wall+.000001)
    with pytest.raises(ValueError, match='nominal complete wall'):
        t._holes(boundary_row(protruding, size, wall), size, wall)


def test_proposal_exposes_residual_contract_separately_from_conditional_pose_bounds():
    for row in run()['proposed_finished_replacements']:
        assert len(row['wall_boundary_numerical_residuals']) == len(row['geometry']['holes'])
        assert 'not exact clipped-set properties' in row['nominal_integration_contract']
        assert row['complete_material_property_bounds'] is None
        assert row['stock_tolerance_m'] is None and row['bore_tolerance_m'] is None
        assert all(b['through_wall_manufacturing_accepted'] is False for b in row['wall_boundary_numerical_residuals'])
