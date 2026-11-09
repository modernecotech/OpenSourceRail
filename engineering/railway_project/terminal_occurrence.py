"""Bounded terminal/P1 research occurrence ledger; no canonical/native admission.

Pure parsed-record API. The execution boundary must check the raw file pins;
this module checks parsed seals, physical projections and predecessor refs.
It imports no project producer, composer, preview or evaluator. Parent machining
is an explicit, UNAPPLIED proposal: the original material stays live. Unknown
properties and process-account overlap stay unknown rather than becoming zero.
"""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from math import fsum, isfinite, nextafter

CASES = ('low', 'base', 'high')
I = [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
FRONT = [[-1., 0., 0.], [0., -1., 0.], [0., 0., 1.]]
FLAGS = dict(canonical_admitted=False, installed_assembly_accepted=False,
             native_eligible=False, physical_accepted=False,
             engineering_accepted=False, manufacturing_release=False,
             operating_release=False, selected_reference_changed=False,
             release_approved=False, movement_authority=False)
# Grammar recognition only, never Boolean/volume/mesh validation. Unknown
# fields on a known source kind are retained IN FULL in the physical identity.
SOURCE_KINDS = frozenset(('box', 'rhs', 'annulus', 'cylinder', 'envelope',
    'poly-prism', 'profile-prism', 'triangle-prism', 'triangular-prism',
    'route', 'annular-sector', 'difference', 'union', 'union-material',
    'disjoint-material-union', 'cylinder-cut', 'finite-cylinder-void',
    'nested-revolved-frusta', 'revolved-frustum', 'thread-bounded-material',
    'double-thread-bounded-material', 'bounded-thread-void-fill',
    'thread-bounded-cut', '32chords-per-quarter',
    'two-opposite-90deg-bend-profile', 'one90deg-keeper',
    'ring-access-port-enlargement', 'hardpoint-thread-pocket',
    'box-minus-2revolvedcounterbores', 'box-minus-6revolvedcounterbores',
    'two-explicit-extruded-triangular-weld-profiles', 'open-round-ended-slot'))
# These are retained parent definitions, not newly admitted material/CSG models.
# Recognition is confined to authenticated parent-pattern geometry. Their full
# records stay in the physical definition; no solid, volume or mass is inferred.
RETAINED_PARENT_KINDS = {
    'cut-length': 'retained-source-stock-or-route-allowance',
    'proposed-equipment-zone': 'retained-source-equipment-allowance',
    'u_channel': 'retained-source-channel-stock',
}
DOMAINS = frozenset(('source-material-record', 'source-unresolved-finished-material',
    'finite-source-weld-polyhedron', 'revised-source-parent',
    'hardware-source-bounded-material', 'prospective-finished-source-material-set',
    'new-source-connector', 'bounded-complete-finished-source-material'))


def identity(value):
    return sha256((json.dumps(value, sort_keys=True, separators=(',', ':'),
                              allow_nan=False) + '\n').encode()).hexdigest()


def seal(value):
    if 'evaluation_id' in value:
        raise ValueError('Cannot reseal an existing evaluation')
    return dict(deepcopy(value), evaluation_id=identity(value))


def _closed(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('Closed ' + label + ' schema required')


def _hex(value, n=64):
    if not isinstance(value, str) or len(value) != n or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Explicit hexadecimal source identity required')


def _name(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 512:
        raise ValueError('Explicit bounded source identifier required')
    return value


def _number(x):
    if type(x) not in (int, float) or not isfinite(x):
        raise ValueError('Finite nonboolean SI scalar required')
    return x


def _vector(x):
    if not isinstance(x, list) or len(x) != 3:
        raise ValueError('Explicit SI vector required')
    return [_number(v) for v in x]


def _rotation(R):
    if not isinstance(R, list) or len(R) != 3:
        raise ValueError('Proper rotation required')
    for row in R:
        _vector(row)
    if any(abs(fsum(R[k][i]*R[k][j] for k in range(3))-(i == j)) > 1e-10
           for i in range(3) for j in range(3)):
        raise ValueError('Nonrigid rotation refused')
    det = fsum(R[0][j]*(R[1][(j+1)%3]*R[2][(j+2)%3]-R[1][(j+2)%3]*R[2][(j+1)%3]) for j in range(3))
    if abs(det-1.) > 1e-10:
        raise ValueError('Reflected rotation refused')
    return R


def _apply(R, p):
    return [fsum(R[i][j]*p[j] for j in range(3)) for i in range(3)]


def _pose(p, b):
    _vector(p['at_m']); _rotation(p['rotation'])
    at = _apply(b['rotation'], p['at_m'])
    return dict(at_m=[at[i]+b['at_m'][i] for i in range(3)],
        rotation=[[fsum(b['rotation'][i][k]*p['rotation'][k][j] for k in range(3))
                   for j in range(3)] for i in range(3)])


def _bound_entity_pose(e, physical, binding):
    """Only a physical-record pose can yield an installed entity pose.

    Legacy evaluation/packaging locations are not an authoritative substitute
    for vertex/CSG placement. The complete physical graph is always deployed
    by its outer binding, even when it has no singleton entity-pose model.
    """
    record = physical.get('physical_record')
    if physical.get('domain') == 'bounded-complete-finished-source-material':
        record = record.get('source_pose') if isinstance(record, dict) else None
    if isinstance(record, dict) and 'at_m' in record and 'rotation' in record:
        _vector(record['at_m']); _rotation(record['rotation'])
        if 'at_m' in e or 'rotation' in e:
            if e.get('at_m') != record['at_m'] or e.get('rotation') != record['rotation']:
                raise ValueError('Evaluated entity pose differs from physical source record')
            _vector(e['at_m']); _rotation(e['rotation'])
        return _pose(record, binding), 'bound-to-complete-physical-record-pose'
    return None, 'No authoritative singleton physical pose; evaluation/packaging proxy is not an installed pose'


def _cases(x):
    if x is None:
        return None
    if isinstance(x, list) and len(x) == 3:
        x = dict(zip(CASES, x))
    _closed(x, CASES, 'price/mass cases')
    values = [_number(x[c]) for c in CASES]
    if min(values) < 0 or values != sorted(values):
        raise ValueError('Ordered nonnegative cases required; unknown is None')
    return deepcopy(x)


def _index(rows, label, limit=3000):
    if not isinstance(rows, list) or not rows or len(rows) > limit:
        raise ValueError('Bounded nonempty ' + label + ' roster required')
    out = {_name(r['id']): r for r in rows}
    if len(out) != len(rows):
        raise ValueError('Duplicate ' + label)
    return out


def _authenticated(value, pin, schema, physical_key=None, identity_key=None):
    if value.get('schema') != schema:
        raise ValueError('Unsupported source schema')
    _hex(pin['evaluation_id']); _hex(pin['raw_sha256'])
    if value.get('evaluation_id') != pin['evaluation_id'] or value['evaluation_id'] != identity({k:v for k,v in value.items() if k != 'evaluation_id'}):
        raise ValueError('Parsed evaluation seal/source pin differs')
    if physical_key:
        _hex(pin[identity_key])
        if value[identity_key] != pin[identity_key] or identity(value[physical_key]) != pin[identity_key]:
            raise ValueError('Physical source identity differs')
    if any(k in value and (type(value[k]) is not bool or value[k] is not False) for k in FLAGS):
        raise ValueError('Only non-admitted research sources with actual boolean False flags accepted')


def _grammar(value, depth=0, *, retained_parent=False, retained_nodes=None, path=()):
    if depth > 48:
        raise ValueError('Finite source material grammar depth exceeded')
    if isinstance(value, dict):
        if 'kind' in value and value['kind'] not in SOURCE_KINDS:
            kind = value['kind']
            if not retained_parent or kind not in RETAINED_PARENT_KINDS:
                raise ValueError('Unknown source geometry kind: ' + str(kind))
            if retained_nodes is not None:
                retained_nodes.append(dict(kind=kind, node_path=list(path),
                    source_node_sha256=identity(value), domain=RETAINED_PARENT_KINDS[kind],
                    finished_geometry_supported=False, geometry_operations_performed=False,
                    mass_properties_derived=False, native_eligible=False,
                    reason='Authenticated parent source record retained in full; stock/routing/equipment or gross-channel definition is not verified finished material, a filled box or a new mass model'))
        for key, child in value.items():
            _grammar(child, depth+1, retained_parent=retained_parent,
                     retained_nodes=retained_nodes, path=path+(key,))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _grammar(child, depth+1, retained_parent=retained_parent,
                     retained_nodes=retained_nodes, path=path+(i,))


def _interval(x):
    if not isinstance(x, list) or len(x) != 2:
        raise ValueError('Explicit marginal interval required')
    a, b = map(_number, x)
    if a > b:
        raise ValueError('Inverted material interval')
    return [a, b]


def _plus(*xs):
    return [sum((Fraction(x[0]) for x in xs), Fraction(0)),
            sum((Fraction(x[1]) for x in xs), Fraction(0))]


def _times(a, x):
    vs = [Fraction(a)*Fraction(v) for v in x]
    return [min(vs), max(vs)]


def _outward(x):
    """Round exact binary-input rational bounds outwards to finite floats."""
    result = []
    for i, exact in enumerate(x):
        try:
            rounded = float(exact)
        except OverflowError as exc:
            raise ValueError('Origin moment exceeds finite output interval domain') from exc
        if not isfinite(rounded):
            raise ValueError('Origin moment exceeds finite output interval domain')
        represented = Fraction(rounded)
        if (i == 0 and represented > exact) or (i == 1 and represented < exact):
            rounded = nextafter(rounded, float('-inf') if i == 0 else float('inf'))
        if not isfinite(rounded):
            raise ValueError('Outward origin moment exceeds finite output interval domain')
        result.append(rounded)
    return result


def _affine_moments(mass, fm, J, b):
    """Conservative marginal intervals, exact coefficient arithmetic then outward rounding.

    Every supplied float denotes its exact binary value. All endpoint products,
    sums, rotation/translation coefficients and cancellation use rationals;
    only final bounds are rounded, outwards. Correlations remain unknown.
    """
    mass = _interval(mass)
    if mass[0] < 0:
        raise ValueError('Negative source mass bound')
    if fm is None or J is None:
        return None, None
    if not isinstance(fm, list) or len(fm) != 3 or not isinstance(J, list) or len(J) != 3 or any(not isinstance(r,list) or len(r)!=3 for r in J):
        raise ValueError('Explicit first moment/origin tensor bounds required')
    fm = [_interval(x) for x in fm]; J = [[_interval(x) for x in row] for row in J]
    _rotation(b['rotation']); _vector(b['at_m'])
    R = [[Fraction(x) for x in row] for row in b['rotation']]
    T = [Fraction(x) for x in b['at_m']]
    q = [_plus(*[_times(R[i][k], fm[k]) for k in range(3)]) for i in range(3)]
    world_fm = [_plus(q[i], _times(T[i], mass)) for i in range(3)]
    dot = _plus(*[_times(T[k], q[k]) for k in range(3)])
    world_J = []
    for i in range(3):
        row = []
        for j in range(3):
            rotated = _plus(*[_times(R[i][k]*R[j][l], J[k][l]) for k in range(3) for l in range(3)])
            shift = _times((sum(v*v for v in T) if i == j else 0)-T[i]*T[j], mass)
            row.append(_plus(rotated, shift, _times(2. if i == j else 0., dot),
                             _times(-T[i], q[j]), _times(-T[j], q[i])))
        world_J.append(row)
    return [_outward(x) for x in world_fm], [[_outward(x) for x in row] for row in world_J]


def _properties(e, b, finishing, completed=None):
    """Preserve supplied hypotheses; only explicit origin-moment intervals are transformed."""
    keys = ('mass_kg', 'mass_label_cases_kg', 'centroid_local_m', 'shape_I_per_kg',
        'centroid_terminal_cases_m', 'uncertainty_m', 'centroid_model_uncertainty_m',
        'mass_properties', 'mass_properties_part_frame', 'mass_properties_terminal_frame',
        'mass_basis', 'inertia_basis', 'mass_centroid_basis', 'properties_status',
        'cut_mass_model_evaluation', 'complete_material_rebuild', 'bounded_properties')
    source = {k:deepcopy(e[k]) for k in keys if k in e}
    result = dict(kind='unknown', mass_interval_kg=None,
        first_moment_about_body_origin_interval_kg_m=None,
        inertia_about_body_origin_interval_kg_m2=None,
        exact_point_CG_m=None, centroidal_inertia=None,
        source_property_record=source, finishing_supplement_required=finishing,
        physical_measurement=False, correlated_scenarios=False)
    if completed is not None:
        mass = completed['mass_interval_kg']
        reports = {}
        for mode in ('nominal_datum', 'with_source_position_uncertainty'):
            p = completed[mode]
            fm, J = _affine_moments(mass, p['first_moment_interval_kg_m'],
                p['inertia_about_terminal_origin_interval_kg_m2'], b)
            reports[mode] = dict(first_moment_about_body_origin_interval_kg_m=fm,
                inertia_about_body_origin_interval_kg_m2=J,
                exact_point_CG_m=None, centroidal_inertia=None)
        uncertain = reports['with_source_position_uncertainty']
        result.update(kind='bounded',mass_interval_kg=deepcopy(mass),
            first_moment_about_body_origin_interval_kg_m=uncertain['first_moment_about_body_origin_interval_kg_m'],
            inertia_about_body_origin_interval_kg_m2=uncertain['inertia_about_body_origin_interval_kg_m2'],
            body_frame_finishing_bounds=reports,
            source_position_uncertainty_terminal_axes_m=deepcopy(completed['source_position_uncertainty_m']),
            finishing_supplement_required=False)
        return result
    if finishing:
        return result
    mass = _cases(e.get('mass_label_cases_kg', e.get('mass_kg')))
    if mass is not None:
        if mass['low'] <= 0:
            raise ValueError('Positive source material mass required; unknown is None')
        result['mass_interval_kg'] = [mass['low'], mass['high']]
    p = e.get('mass_properties_terminal_frame')
    if p is not None:
        fm = p.get('mass_first_moment_interval_kg_m')
        J = p.get('inertia_about_frame_origin_interval_kg_m2')
        if mass is not None:
            fm, J = _affine_moments(result['mass_interval_kg'], fm, J, b)
            result.update(kind='bounded', first_moment_about_body_origin_interval_kg_m=fm,
                          inertia_about_body_origin_interval_kg_m2=J)
        return result
    if mass is not None:
        # A source point/centroidal proxy is evidence, not newly proved exact
        # material moments. Keep it tagged; no inferred tensor or point CG.
        result['kind'] = 'source-model-only'
    return result


def _finishing_properties(props):
    _closed(props, ('net_volume_interval_m3','mass_interval_kg','nominal_datum',
        'with_source_position_uncertainty','source_position_uncertainty_m','method',
        'uniform_density_research_kg_m3','physical_mass_CG_qualification'), 'finishing properties')
    V = _interval(props['net_volume_interval_m3']); m = _interval(props['mass_interval_kg'])
    rho = _number(props['uniform_density_research_kg_m3'])
    if V[0] <= 0 or m[0] <= 0 or rho <= 0 or props['physical_mass_CG_qualification'] is not None:
        raise ValueError('Positive unqualified finishing material bounds required')
    if Fraction(m[0]) > Fraction(rho)*Fraction(V[0]) or Fraction(m[1]) < Fraction(rho)*Fraction(V[1]):
        raise ValueError('Finished mass does not enclose volume/density context')
    if min(_vector(props['source_position_uncertainty_m'])) < 0:
        raise ValueError('Nonnegative finishing source uncertainty required')
    for mode in ('nominal_datum','with_source_position_uncertainty'):
        p = props[mode]
        _closed(p, ('first_moment_interval_kg_m','centroid_interval_m',
            'inertia_about_terminal_origin_interval_kg_m2','exact_point_CG_m','centroidal_tensor_kg_m2'), 'finishing moment report')
        if p['exact_point_CG_m'] is not None or p['centroidal_tensor_kg_m2'] is not None:
            raise ValueError('Finishing intervals cannot become exact point properties')
        for key in ('first_moment_interval_kg_m','centroid_interval_m'):
            if not isinstance(p[key],list) or len(p[key]) != 3:
                raise ValueError('Three finishing moment/centroid intervals required')
            for x in p[key]: _interval(x)
        J = p['inertia_about_terminal_origin_interval_kg_m2']
        if not isinstance(J,list) or len(J) != 3 or any(not isinstance(r,list) or len(r) != 3 for r in J):
            raise ValueError('Explicit finishing origin tensor intervals required')
        for i in range(3):
            for j in range(3):
                a, z = _interval(J[i][j]), _interval(J[j][i])
                if max(a[0],z[0]) > min(a[1],z[1]) or i == j and a[0] < 0:
                    raise ValueError('Compatible symmetric finishing origin bounds required')
    for key in ('first_moment_interval_kg_m','centroid_interval_m','inertia_about_terminal_origin_interval_kg_m2'):
        nominal=props['nominal_datum'][key]; uncertain=props['with_source_position_uncertainty'][key]
        pairs = ((nominal[i][j],uncertain[i][j]) for i in range(3) for j in range(3)) if key.startswith('inertia_') else zip(nominal,uncertain)
        if any(b[0] > a[0] or b[1] < a[1] for a,b in pairs):
            raise ValueError('Source uncertainty bounds must enclose nominal report')
    return deepcopy(props)


def _finishing_supplement(terminal, plan, es, gs, phys, owners, finishing, pin):
    """Bind the reviewed finisher and local application; never run a rebuild."""
    application = plan.get('finishing_application')
    updated = {k for k,p in phys.items() if p['domain'] == 'bounded-complete-finished-source-material'}
    if finishing is None and pin is None:
        if application is not None or updated:
            raise ValueError('Explicit finishing packet/pin required for revised material domain')
        return {}, None
    if finishing is None or pin is None or application is None:
        raise ValueError('Finishing packet/pin and revised local application are required together')
    _closed(pin, ('evaluation_id','raw_sha256','component_geometry_id','source_commit'), 'finishing pin')
    _hex(pin['source_commit'],40)
    _authenticated(finishing,pin,'osr-terminal-finishing-material-rebuild/1','physical_definition','component_geometry_id')
    if finishing['source_transactions_applied'] is not False or finishing['canonical_definition'] is not None:
        raise ValueError('Unapplied non-admitted finishing source required')
    _closed(application, ('schema','input_pin','parent_local_plan_evaluation_id',
        'parent_local_geometry_id','finishing_evaluation_id','finishing_component_geometry_id',
        'material_occurrences','paid_owners','cleared_calculation_holds','new_stock_purchases',
        'new_P1_retirements','new_deployments','source_transactions_applied'), 'finishing application')
    if application['schema'] != 'osr-terminal-local-finishing-application/1' or application['finishing_evaluation_id'] != finishing['evaluation_id'] or application['finishing_component_geometry_id'] != finishing['component_geometry_id']:
        raise ValueError('Mixed finishing application identity')
    for key in ('parent_local_plan_evaluation_id','parent_local_geometry_id'): _hex(application[key])
    ap = application['input_pin']
    _closed(ap, ('schema','sources'), 'local finishing application pin')
    _closed(ap['sources'], ('local_plan','finishing'), 'local finishing application sources')
    for p in ap['sources'].values():
        _closed(p, ('evaluation_id','raw_sha256'), 'application source pin')
        for v in p.values(): _hex(v)
    if ap['schema'] != 'osr-terminal-local-finishing-input-pin/1' or ap['sources']['finishing'] != {k:pin[k] for k in ('evaluation_id','raw_sha256')} or ap['sources']['local_plan']['evaluation_id'] != application['parent_local_plan_evaluation_id']:
        raise ValueError('Exact finisher/original-local application pin differs')
    for key in ('new_stock_purchases','new_P1_retirements','new_deployments'):
        if type(application[key]) is not int or application[key] != 0:
            raise ValueError('Finishing cannot buy blanks, retire P1 or deploy ends')
    if application['source_transactions_applied'] is not False or finishing['source_local_epoch'] != plan['source_local_epoch']:
        raise ValueError('Mixed/applied finishing local epoch')
    upstream = finishing['source_input_pin']
    _closed(upstream, ('schema','sources'), 'finisher source pin')
    _closed(upstream['sources'], ('terminal','weld','hardware'), 'finisher original source triple')
    if upstream['schema'] != 'osr-terminal-finishing-input-pin/1':
        raise ValueError('Unsupported original finisher source pin')
    for name in ('terminal','weld','hardware'):
        a = upstream['sources'][name]; b = plan['source_input_pin']['sources'][name]
        _closed(a, ('evaluation_id','raw_sha256') + (('source_commit',) if 'source_commit' in a else ()), 'finisher upstream pin')
        for key in ('evaluation_id','raw_sha256'):
            _hex(a[key]); _hex(b[key])
            if a[key] != b[key]: raise ValueError('Mixed original finishing source refs')
        for row in (a,b):
            if 'source_commit' in row: _hex(row['source_commit'],40)
        if 'source_commit' in a and 'source_commit' in b and a['source_commit'] != b['source_commit']:
            raise ValueError('Mixed original finishing source commits')
        if finishing['source_'+name+'_evaluation_id'] != plan['ancestry'][name+'_evaluation_id'] or a['evaluation_id'] != plan['ancestry'][name+'_evaluation_id']:
            raise ValueError('Mixed original finishing source ancestry')
    fp = finishing['physical_definition']
    _closed(fp, ('schema','units','frame','parents'), 'finished physical definition')
    if fp['schema'] != 'osr-terminal-complete-finishing-material-physical/1' or fp['units'] != 'm' or fp['frame'] != 'terminal-local-UVW':
        raise ValueError('Finished physical frame/schema differs')
    parents = _index(fp['parents'],'finished nominal parents')
    terminal_entities = _index(terminal['canonical_draft']['entities'],'original terminal material')
    terminal_groups = _index(terminal['canonical_draft']['stock_groups'],'original terminal paid owners')
    rows = {r['source_entity_id']:r for r in finishing['pending_draft_replacements']}
    required = {r['source_entity_id']:r for r in plan['source_finishing_records']}
    paid = {r['source_owner_id']:r for r in finishing['source_owner_conservation']}
    if len(rows) != len(finishing['pending_draft_replacements']) or len(required) != len(plan['source_finishing_records']) or len(paid) != len(finishing['source_owner_conservation']) or set(rows) != set(required) or set(rows) != set(parents) or updated != set(rows) or set(paid) != set(plan['finishing_paid_owner_ids']) or len(paid) != 2:
        raise ValueError('Complete finishing material/two-owner coverage differs')
    completed = {}
    for eid,r in rows.items():
        e = es[eid]; req = required[eid]; oid = owners[eid]; old = e['source_material_before_finishing']
        nominal = parents[eid]; g = gs[oid]['source_paid_group_before_finishing']
        if r['source_stock_owner_id'] != oid or oid not in paid or r['transaction_applied'] is not False or r['old_incremental_H_removal_is_not_debited'] is not True or r['frame'] != 'terminal-local-UVW':
            raise ValueError('Mixed finishing source material/owner disposition')
        if terminal_entities.get(eid) != old or terminal_groups.get(oid) != g or r['source_entity_ancestry'] != old or r['source_entity_sha256'] != identity(old) or r['source_owner_sha256'] != identity(g) or r['source_finishing_operation'] != req['source_record']:
            raise ValueError('Finishing original source record/hash differs')
        pose = dict(at_m=old['at_m'],rotation=old['rotation'])
        expected_nominal = dict(id=eid,material_id=old['material_id'],source_pose=pose,
            source_declared_finishing=req['physical_operation'],nominal_source_geometry=dict(
                material_id=old['material_id'],geometry=old['exact_CSG_entity']['geometry'],holes=old['exact_CSG_entity']['holes']))
        expected_physical = dict(id=eid,material_id=old['material_id'],domain='bounded-complete-finished-source-material',physical_record=nominal)
        if nominal != expected_nominal or phys[eid] != expected_physical or e['material_set_definition'] != phys[eid] or r['source_pose'] != pose or e['at_m'] != old['at_m'] or e['rotation'] != old['rotation'] or r['material_id'] != old['material_id']:
            raise ValueError('Finishing nominal material/pose physical projection differs')
        model = r['complete_material_rebuild']
        if model['kind'] not in ('hardpoint-stopped-thread','ring-through-ports') or model['complete_source_void_union'] != req['source_record']['source_complete_void_union'] or e['complete_material_rebuild'] != model or e['bounded_properties'] != model['bounded_properties']:
            raise ValueError('Complete finishing material graph/bounds differ')
        for key in ('minimum_material_graph','maximum_material_graph'): _grammar(model[key])
        props = _finishing_properties(model['bounded_properties'])
        rho = g['source_account']['density_cases_kg_m3']
        if not isinstance(rho,list) or len(rho) != 3 or any(_number(x) != props['uniform_density_research_kg_m3'] for x in rho) or props['source_position_uncertainty_m'] != old['uncertainty_m']:
            raise ValueError('Finishing density/source uncertainty differs')
        if e['finishing_source_evaluation_id'] != finishing['evaluation_id'] or req['complete_material_evaluation_id'] != finishing['evaluation_id'] or any(e[k] is not None for k in ('mass_kg','center_of_gravity_m','inertia_kg_m2')):
            raise ValueError('Finishing supplement cannot fabricate exact installed properties')
        completed[eid] = props
    for oid,r in paid.items():
        g = gs[oid]; old = g['source_paid_group_before_finishing']; ids = sorted(g['entity_ids'])
        if r['source_owner_ancestry'] != old or r['source_owner_sha256'] != identity(old) or sorted(r['source_occurrence_ids']) != ids or set(ids) != {eid for eid in rows if owners[eid] == oid} or g['complete_finished_owner_record'] != r:
            raise ValueError('Finishing complete paid-owner constituents differ')
        if type(r['paid_blank_group_count']) is not int or r['paid_blank_group_count'] != 1 or type(r['new_stock_purchase_count']) is not int or r['new_stock_purchase_count'] != 0 or any(r[k] is not False for k in ('new_material_charge','source_price_credit','transaction_applied')):
            raise ValueError('Finishing retains paid blanks once without purchase/credit')
        if r['paid_gross_mass_kg'] != old['gross_mass_kg'] or r['source_direct_price_retained_once'] != old['direct_cost_usd'] or g['direct_cost_usd'] != old['direct_cost_usd'] or g['gross_mass_kg'] != old['gross_mass_kg']:
            raise ValueError('Finishing original gross/price ownership differs')
        net = _interval(r['complete_rebuilt_net_mass_interval_kg']); scrap = _interval(r['rebuilt_scrap_mass_interval_kg'])
        if net[0] <= 0 or scrap[0] < 0 or g['net_mass_interval_kg'] != net or g['scrap_mass_interval_kg'] != scrap or g['net_mass_kg'] is not None or g['scrap_mass_kg'] is not None:
            raise ValueError('Finishing owner mass/scrap interval record differs')
        sums = [sum(Fraction(completed[eid]['mass_interval_kg'][i]) for eid in ids) for i in range(2)]
        gross = Fraction(_cases(old['gross_mass_kg'])['base'])
        if Fraction(net[0]) > sums[0] or Fraction(net[1]) < sums[1] or Fraction(scrap[0]) > gross-Fraction(net[1]) or Fraction(scrap[1]) < gross-Fraction(net[0]):
            raise ValueError('Finished owner bounds do not enclose constituent/gross conservation')
    counts = dict(finishing_operations=len(rows),material_occurrences=len(rows),
        hardpoints=sum(r['complete_material_rebuild']['kind']=='hardpoint-stopped-thread' for r in rows.values()),
        backing_rings=sum(r['complete_material_rebuild']['kind']=='ring-through-ports' for r in rows.values()),
        paid_owner_groups=2,new_stock_purchases=0)
    if finishing['counts'] != counts or any(type(x) is not int for x in finishing['counts'].values()) or plan['counts']['finishing_operations'] != len(rows) or application['material_occurrences'] != len(rows) or type(application['material_occurrences']) is not int or application['paid_owners'] != 2 or type(application['paid_owners']) is not int:
        raise ValueError('Finishing calculation count contract differs')
    opids = {r['operation_id'] for r in required.values()}
    allowed = {'finishing-material-properties-pending','density-context-unresolved'}
    cleared = application['cleared_calculation_holds']
    if len(cleared) != 2*len(opids) or {(h['kind'],h['subject']) for h in cleared} != {(kind,opid) for kind in allowed for opid in opids} or any(h['kind'] in allowed and h['subject'] in opids for h in plan['pending_contracts']):
        raise ValueError('Only exact covered finishing calculation holds may clear')
    if not any(h['kind']=='bounded-finishing-source-and-process-evidence' and h['resolved'] is False for h in plan['pending_contracts']):
        raise ValueError('Finishing source/process evidence must remain open')
    return completed, dict(schema='osr-terminal-occurrence-finishing-consumption/1',
        finishing_pin=deepcopy(pin),application=deepcopy(application),
        material_occurrences=len(rows),paid_owner_groups=2,
        calculation_supplement_resolved=True,physical_evidence_accepted=False,
        source_pending_contracts=deepcopy(finishing['pending_contracts']))


def _source_refs(parent, wanted, wanted_part_ids=None):
    """Validate every source occurrence, hashing predecessor keys where needed.

    None retains the unfiltered reference path. A supplied part set is an exact
    predecessor scope, not permission to skip unrelated pattern validation.
    Part hashes are reused only within this invocation of the filtered path.
    """
    parts = _index(parent['parts'], 'parent parts', 10000)
    patterns = _index(parent['patterns'], 'parent patterns', 50000)
    if wanted_part_ids is not None:
        if not isinstance(wanted_part_ids, (set, frozenset)):
            raise ValueError('Explicit predecessor source-part set required')
        wanted_part_ids = {_name(x) for x in wanted_part_ids}
        if not wanted_part_ids <= set(parts):
            raise ValueError('Unknown predecessor source part')
    physical = parent['physical_definition']
    pp = _index(physical['parts'], 'physical parts', 10000)
    pats = _index(physical['occurrence_patterns'], 'physical patterns', 50000)
    if set(parts) != set(pp) or set(patterns) != set(pats):
        raise ValueError('Physical/source catalogue coverage differs')
    out = {}; total = 0; part_counts = dict.fromkeys(parts, 0); source_domains = []
    part_hashes = {}
    for pid, pat in patterns.items():
        part = parts[pat['part_id']]
        for key, value in pp[part['id']].items():
            if key not in part or value != part[key]:
                raise ValueError('Source part differs from physical projection')
        for key, value in pats[pid].items():
            if key not in pat or value != pat[key]:
                raise ValueError('Source pattern differs from physical projection')
        q = pat['count']
        if type(q) is not int or q <= 0 or q != len(pat['positions_m']):
            raise ValueError('Source pattern count differs')
        _rotation(pat['rotation']); nodes = []
        _grammar(pat['geometry'], retained_parent=True, retained_nodes=nodes, path=('geometry',))
        _cases(pat['direct_cost_usd'])
        ph = identity(pat)
        if wanted_part_ids is None:
            sh = identity(part)
        else:
            if part['id'] not in part_hashes:
                part_hashes[part['id']] = identity(part)
            sh = part_hashes[part['id']]
        geometry_hash = identity(pat['geometry']) if nodes else None
        nodes.sort(key=lambda row: json.dumps(row['node_path'], separators=(',', ':')))
        source_domains.extend(dict(node, pattern_id=pid, part_id=part['id'],
            source_pattern_sha256=ph, source_part_sha256=sh,
            source_geometry_sha256=geometry_hash, original_pattern_count=q)
            for node in nodes)
        match_keys = wanted_part_ids is None or part['id'] in wanted_part_ids
        for j, position in enumerate(pat['positions_m']):
            _vector(position)
            if not match_keys:
                continue
            key = 'source/' + identity([parent['candidate_id'], pid, j])
            if key in wanted:
                ref = dict(parent_candidate_id=parent['candidate_id'], pattern_id=pid,
                    position_index=j, source_pattern_sha256=ph, source_part_sha256=sh)
                out[key] = dict(source_id=key, source_ref=ref, source_ref_sha256=identity(ref),
                    part_id=part['id'], pattern_id=pid, position_index=j,
                    original_geometry=deepcopy(pat['geometry']), at_m=deepcopy(position),
                    rotation=deepcopy(pat['rotation']))
        total += q
        part_counts[part['id']] += q
    if any(type(p['quantity_per_train']) is not int or part_counts[k] != p['quantity_per_train'] for k,p in parts.items()):
        raise ValueError('Parent catalogue/pattern quantity conservation differs')
    if set(out) != set(wanted):
        raise ValueError('Missing canonical predecessor source key')
    if wanted_part_ids is not None and {r['part_id'] for r in out.values()} != wanted_part_ids:
        raise ValueError('Requested predecessor parts differ from matched source keys')
    return out, patterns, total, source_domains


def compose(parent, terminal, local_plan, *, input_pin, request_id, finishing=None, finishing_pin=None):
    """Make a non-admitted TWO-END research ledger from three sealed records.

    Raw hashes are expected file-boundary pins, NOT checked from parsed objects.
    An original or subsequently revised same-schema local plan may be supplied;
    a revised finishing plan additionally requires its exact finishing packet
    and closed pin. No supplement is admitted by a status flag alone.
    """
    _hex(request_id)
    for value in (parent, terminal, local_plan, input_pin, finishing, finishing_pin):
        identity(value)  # JSON/finite check before any traversal.
    _closed(input_pin, ('schema', 'sources', 'expected_counts'), 'input pin')
    if input_pin['schema'] != 'osr-terminal-occurrence-input-pin/1':
        raise ValueError('Unsupported occurrence pin schema')
    pins = input_pin['sources']
    _closed(pins, ('parent', 'terminal', 'local_plan'), 'source roster')
    _closed(pins['parent'], ('candidate_id', 'evaluation_id', 'raw_sha256'), 'parent pin')
    _closed(pins['terminal'], ('evaluation_id', 'raw_sha256', 'source_commit'), 'terminal pin')
    _closed(pins['local_plan'], ('evaluation_id', 'raw_sha256', 'source_commit', 'local_component_geometry_id'), 'local plan pin')
    for name in ('terminal', 'local_plan'):
        _hex(pins[name]['source_commit'], 40)
    _authenticated(parent, pins['parent'], 'osr-vehicle-installation/1', 'physical_definition', 'candidate_id')
    _authenticated(terminal, pins['terminal'], 'osr-terminal-canonical-normalization-packet/1')
    _authenticated(local_plan, pins['local_plan'], 'osr-terminal-local-revision-plan/1', 'physical_definition', 'local_component_geometry_id')
    if terminal['source_parent'] != pins['parent'] or local_plan['source_local_epoch'] != terminal['source_pin'] or local_plan['ancestry']['terminal_evaluation_id'] != terminal['evaluation_id']:
        raise ValueError('Mixed parent/local terminal ancestry')
    if local_plan['source_input_pin']['sources']['terminal'] != pins['terminal']:
        raise ValueError('Local plan terminal input pin differs')
    if identity(terminal['source_physical_definition']) != terminal['source_pin']['candidate_id']:
        raise ValueError('Original terminal physical seal differs')
    if local_plan['source_transactions_applied'] is not False or local_plan['canonical_definition'] is not None or type(local_plan['deployment_quantity_multiplier_applied']) is not int or local_plan['deployment_quantity_multiplier_applied'] != 1:
        raise ValueError('Applied source transaction/deployment refused')
    layout = parent['physical_definition']['layout']
    fixed = dict(cars=6, car_length_m=17., car_width_m=2.65, intercar_gap_m=.65,
                 floor_top_m=1.15, roof_z_m=3.55)
    if any(layout.get(k) != v or parent['policy']['layout'].get(k) != v for k,v in fixed.items()) or parent['physical_definition']['config'].get('body_lift_m') != .15:
        raise ValueError('Exact already-lifted P1 layout required')
    bindings = local_plan['deployment_data_unapplied']
    if not isinstance(bindings, list):
        raise ValueError('Explicit two-end deployment roster required')
    for b in bindings:
        _closed(b, ('id','car','source_end','at_m','rotation'), 'end deployment')
        _vector(b['at_m']); _rotation(b['rotation'])
        if type(b['car']) is not int:
            raise ValueError('Nonboolean car allocation required')
    expected_bindings = [dict(id='terminal/front', car=0, source_end='body/terminal-end/end-0', at_m=[0.,0.,2.25], rotation=FRONT),
                         dict(id='terminal/rear', car=5, source_end='body/terminal-end/end-5', at_m=[105.25,0.,2.25], rotation=I)]
    if bindings != expected_bindings or terminal['source_bindings'] != bindings:
        raise ValueError('Two exact saved end deployments required; no second lift')
    draft = local_plan['canonical_local_draft']
    if draft['schema'] != 'osr-terminal-local-material-draft/1' or draft['material_projection'] != local_plan['physical_definition']:
        raise ValueError('Local material physical projection differs')
    projection = local_plan['physical_definition']
    _closed(projection, ('schema', 'units', 'frame', 'material_occurrences', 'material_owner_graph'), 'local physical projection')
    if projection['schema'] != 'osr-terminal-local-material-revision-physical/1' or projection['units'] != 'm' or projection['frame'] != 'terminal-local-UVW':
        raise ValueError('Unsupported local material frame/schema')
    es = _index(draft['entities'], 'local material'); gs = _index(draft['stock_groups'], 'local stock')
    phys = _index(projection['material_occurrences'], 'physical material')
    if set(es) != set(phys):
        raise ValueError('Local material physical coverage differs')
    owners = {}
    for gid, group in gs.items():
        if not group['entity_ids'] or len(set(group['entity_ids'])) != len(group['entity_ids']):
            raise ValueError('Unique nonempty owner material roster required')
        for eid in group['entity_ids']:
            if eid not in es or eid in owners:
                raise ValueError('Missing/reused paid material ownership')
            owners[eid] = gid
    if set(owners) != set(es) or sorted(projection['material_owner_graph'],key=lambda x:x['owner_id']) != [dict(owner_id=k,entity_ids=sorted(gs[k]['entity_ids'])) for k in sorted(gs)]:
        raise ValueError('Physical paid owner coverage differs')
    completed, finishing_consumption = _finishing_supplement(terminal,local_plan,es,gs,phys,owners,finishing,finishing_pin)
    for eid, p in phys.items():
        if p.get('domain') not in DOMAINS:
            raise ValueError('Unknown source material domain')
        _grammar(p)
        if es[eid]['frame'] != 'terminal-local-UVW' or es[eid]['scope'] not in ('installed','prospective-local-installed-material'):
            raise ValueError('Local material scope/frame differs')
    retirements = local_plan['P1_old_leaf_retirement_ledger_owned_once_by_terminal']
    if retirements != terminal['old_leaf_replacements_train_once']:
        raise ValueError('P1 source retirement ledger differs')
    retiring = []
    for row in retirements:
        if row['operation'] != 'replace-or-relocate-once' or type(row['old_count']) is not int or row['old_count'] != len(row['source_ids']) or type(row['retained_original_price_once']) is not bool:
            raise ValueError('Explicit once-only source retirement required')
        retiring.extend(row['source_ids'])
    if len(retiring) != len(set(retiring)):
        raise ValueError('Duplicate P1 retirement')
    for row in local_plan['inherited_P1_retirements']:
        if type(row['new_P1_retirement_count']) is not int or row['new_P1_retirement_count'] != 0 or row['inherited_price_metadata_added_as_new_hardware_charge'] is not False or not set(row['source_keys']) <= set(retiring):
            raise ValueError('Hardware ancestry cannot add another P1 retirement/price')
    machining = terminal['source_machining_train_once']
    mids = [x['source_id'] for x in machining]
    if len(mids) != len(set(mids)) or set(mids)&set(retiring):
        raise ValueError('Overlapping/reused source machining/retirement')
    wanted_parts = {_name(r['source_part_id']) for r in retirements + machining}
    refs, patterns, parent_count, parent_domains = _source_refs(parent, set(retiring)|set(mids), wanted_parts)
    retirement_ledger = []
    for row in retirements:
        _hex(row['source_part_sha256'])
        hashes = {x['id']:x['pattern_sha256'] for x in row['source_occurrence_hashes']}
        if len(hashes) != len(row['source_ids']) or set(hashes) != set(row['source_ids']):
            raise ValueError('Exact retirement source hash roster required')
        for sid in row['source_ids']:
            r = refs[sid]
            if r['part_id'] != row['source_part_id'] or r['source_ref']['source_part_sha256'] != row['source_part_sha256'] or r['source_ref']['source_pattern_sha256'] != hashes[sid]:
                raise ValueError('Retirement predecessor source hash differs')
            retirement_ledger.append(dict(deepcopy(r), disposition='retire-once-per-train',
                successor_installation_ids=[b['id'] for b in bindings], source_retirement=deepcopy(row)))
    machine_ledger = []
    for row in machining:
        r = refs[row['source_id']]
        for source_key, ref_key in (('source_part_sha256','source_part_sha256'),('source_pattern_sha256','source_pattern_sha256'),('source_pattern_id','pattern_id'),('source_position_index','position_index')):
            if row[source_key] != r['source_ref'][ref_key]:
                raise ValueError('Machining predecessor source hash/ref differs')
        if row['kind'] != 'machine_in_place' or row['gross_paid_source_retained'] is not True or row['at_m'] != r['at_m'] or row['rotation'] != r['rotation']:
            raise ValueError('Source machining cannot relocate or repurchase parent')
        pattern = patterns[r['pattern_id']]
        price = _cases(pattern['direct_cost_usd'])
        if row['source_part_id'] != r['part_id'] or _cases(row['paid_source_cost_usd']) != (None if price is None else {c:price[c]/pattern['count'] for c in CASES}):
            raise ValueError('Machining paid source owner price/part differs')
        _grammar(row['remaining_geometry'])
        machine_ledger.append(dict(deepcopy(r), proposed=deepcopy(row), geometry_applied=False,
            paid_blank_count=1, additional_stock_purchase_count=0,
            disposition='retain-original-material; proposed machining pending finished-material proof'))
    finishes = local_plan['source_finishing_records']
    fids = {f['source_entity_id'] for f in finishes}; paid = {f['paid_owner_id'] for f in finishes}
    if len(paid) != 2 or len({f['operation_id'] for f in finishes}) != len(finishes) or not fids <= set(es) or paid != set(local_plan['finishing_paid_owner_ids']) or any(owners[f['source_entity_id']] != f['paid_owner_id'] for f in finishes):
        raise ValueError('Exact finishing parent/two-paid-owner bindings required')
    expected = dict(local_material_occurrences=len(es), local_stock_groups=len(gs),
        deployment_bindings=len(bindings), p1_retirement_groups=len(retirements),
        p1_retired_occurrences=len(retiring), source_machining_dispositions=len(machining),
        finishing_source_occurrences=len(fids), finishing_paid_groups=len(paid))
    _closed(input_pin['expected_counts'], expected, 'count contract')
    if any(type(v) is not int or v < 0 for v in input_pin['expected_counts'].values()) or input_pin['expected_counts'] != expected:
        raise ValueError('Reviewed occurrence/count contract differs')
    for key in ('local_material_occurrences','local_stock_groups','finishing_source_occurrences','finishing_paid_groups'):
        if type(local_plan['counts'][key]) is not int or local_plan['counts'][key] != expected[key]:
            raise ValueError('Source declared local count differs')
    instances = []; evaluated = []; stock = []
    for b in bindings:
        for eid in sorted(es):
            e = es[eid]; oid = b['id']+'/'+eid
            # material_definition already contains source-local geometry/poses.
            # Apply this OUTER deployment once, not a second entity pose.
            instances.append(dict(id=oid, source_material_id=eid,
                material_definition=deepcopy(phys[eid]), deployment=deepcopy(b),
                car_allocation=[[b['car'],1.]], bogie_index=None,
                stock_owner_id=b['id']+'/'+owners[eid]))
            world_pose, pose_status = _bound_entity_pose(e, phys[eid], b)
            evaluated.append(dict(id=oid, source_entity_sha256=identity(e),
                world_entity_pose=world_pose, world_entity_pose_status=pose_status,
                properties=_properties(e,b,eid in fids,completed.get(eid))))
        stock.extend(dict(id=b['id']+'/'+g, source_owner_id=g,
            entity_ids=[b['id']+'/'+x for x in gs[g]['entity_ids']],
            source_group=deepcopy(gs[g]), procurement_multiplicity=1,
            part_accounts_are_nonpayable_subtotals=True) for g in sorted(gs))
    payable = []; allowances = []; unknown_prices = []
    local_price_rows = local_plan['pricing']['rows']
    if len({r['owner_id'] for r in local_price_rows}) != len(local_price_rows):
        raise ValueError('Duplicate local payable owner')
    group_prices = {r['owner_id']:r for r in local_price_rows if r['scope']=='one-local-terminal-group'}
    finish_prices = [r for r in local_price_rows if r['scope']=='one-local-machining-operation-no-new-blank']
    if set(group_prices) != set(gs) or len(group_prices)+len(finish_prices) != len(local_price_rows) or len(finish_prices) != len(finishes) or {r['source_operation_id'] for r in finish_prices} != {f['operation_id'] for f in finishes}:
        raise ValueError('Complete once-only price/source-operation coverage required')
    retired_by_pattern = {}
    for sid in retiring:
        r=refs[sid]; retired_by_pattern.setdefault(r['pattern_id'],set()).add(r['position_index'])
    retained = []
    for pid in sorted(patterns):
        p=patterns[pid]; exclusions=sorted(retired_by_pattern.get(pid,set())); n=p['count']-len(exclusions)
        retained.append(dict(pattern_id=pid, source_pattern_sha256=identity(p),
            original_count=p['count'], retained_count=n, retired_position_indices=exclusions,
            original_pattern_evaluation_record=deepcopy(p),
            properties_status='Retained original pattern hypotheses; retirement needs separate covariance/moment recomputation, not inferred point properties'))
        price=_cases(p['direct_cost_usd'])
        if n:
            payable.append(dict(owner_id='parent-pattern/'+pid, scope='retained-parent-pattern-once',
                amount_usd=None if price is None else {c:price[c]*n/p['count'] for c in CASES}))
    retained_counts = {p['pattern_id']:p['retained_count'] for p in retained}
    parent_domains = [dict(row, retained_pattern_count=retained_counts[row['pattern_id']],
        count_scope='One source-kind node in one pattern; node counts are not material, stock or purchase quantities')
        for row in parent_domains]
    for b in bindings:
        for gid in sorted(gs):
            r=group_prices[gid]; expected_price=gs[gid].get('direct_cost_usd',gs[gid].get('direct_cost_label_cases_USD'))
            price=_cases(r['direct_cost_label_cases_USD'])
            if price != _cases(expected_price):
                raise ValueError('Local owner price differs; constituent subtotals are not extra charges')
            payable.append(dict(owner_id=b['id']+'/'+gid,scope='installed-end-owner-once',amount_usd=price))
        for r in finish_prices:
            allowances.append(dict(owner_id=b['id']+'/'+r['owner_id'],amount_usd=_cases(r['direct_cost_label_cases_USD']),
                additivity='unresolved overlap with paid source-group process allowance; NOT added to subtotal',source=deepcopy(r)))
    for row in machine_ledger:
        allowances.append(dict(owner_id='train-once-machining/'+row['source_id'],
            amount_usd=_cases(row['proposed']['additional_process_USD']),
            additivity='separate train-once proposed process allowance; inclusion requires account reconciliation',
            stock_purchase_count=0))
    for r in payable:
        if r['amount_usd'] is None:unknown_prices.append(r['owner_id'])
    physical = dict(schema='osr-terminal-body-occurrence-physical/1', units='m',
        parent_physical_definition=deepcopy(parent['physical_definition']),
        parent_candidate_id=parent['candidate_id'],
        source_occurrence_suppression=sorted(retiring),
        terminal_local_physical_definition=deepcopy(projection),
        terminal_installations=deepcopy(bindings),
        interpretation='Parent minus exactly keyed suppressions, plus outer-transformed local material graph twice; parent machining proposals NOT applied',
        geometry_lift_to_apply_m=0.)
    finishing_contract = dict(required=True,resolved=False,source_local_plan_evaluation_id=local_plan['evaluation_id'],
        source_local_component_geometry_id=local_plan['local_component_geometry_id'],
        parent_entity_ids=sorted(fids),paid_owner_ids=sorted(paid),
        operation_bindings=[dict(operation_id=f['operation_id'],source_entity_id=f['source_entity_id'],paid_owner_id=f['paid_owner_id'],source_record_sha256=identity(f)) for f in finishes],
        accepted_supplement_schema=None,
        reason='Explicit source-specific finishing packet not supplied; do not infer final material properties from status flags')
    if finishing_consumption is not None:
        finishing_contract.update(resolved=True,accepted_supplement_schema='osr-terminal-finishing-material-rebuild/1',
            finishing_evaluation_id=finishing['evaluation_id'],
            reason='Exact source-specific finishing calculation supplement consumed; process/source/physical evidence remains open')
    return seal(dict(schema='osr-terminal-body-research-occurrence-ledger/1',request_id=request_id,
        candidate_id=identity(physical),physical_definition=physical,selection_id=None,
        source_inputs=deepcopy(pins),raw_hash_verification='Required at execution file boundary; this pure parsed API checks content seals only',
        source_terminal_evaluation_id=terminal['evaluation_id'],local_plan_evaluation_id=local_plan['evaluation_id'],
        counts=dict(expected,terminal_deployed_material_occurrences=len(instances),terminal_deployed_stock_owners=len(stock),
            parent_source_occurrences=parent_count,parent_retained_occurrences=parent_count-len(retiring)),
        terminal_material_occurrences=instances,terminal_evaluated_properties=evaluated,
        local_material_evaluation_records=deepcopy(draft['entities']),
        terminal_stock_owners=stock,retained_parent_patterns=retained,
        retained_parent_source_domains=parent_domains,
        p1_retirement_ledger=retirement_ledger,additional_hardware_P1_retirements=0,
        source_machining_train_once=machine_ledger,source_machining_geometry_applied=False,
        lifecycle_allocations=deepcopy(local_plan['lifecycle_allocations']),lifecycle_deployment_multiplier=1,
        finishing_supplement_contract=finishing_contract,
        finishing_consumption=finishing_consumption,
        pricing=dict(payable_owner_rows=payable,known_additive_subtotal_usd={c:fsum(r['amount_usd'][c] for r in payable if r['amount_usd'] is not None) for c in CASES},
            unknown_payable_owner_ids=unknown_prices,non_additive_process_allowances=allowances,
            source_residual_account=deepcopy(local_plan['pricing']['common_source_residual_account']),
            source_residual_applied=False,source_residual_additivity='Unresolved account coverage; source totals are NOT another payable charge',
            scope='Calculated direct owner subtotal, not complete installed/14-scope lifecycle cost; missing quotations are not outline failure'),
        accounting_coverage=dict(retired_parent_occurrences=len(retiring),new_local_groups_per_end=len(gs),end_count=2,
            source_prices_not_credited_twice=True,part_subtotals_added=False,finishing_additivity_pending=True,
            lifecycle_scopes_preserved_train_once=True,complete_installed_cost=False),
        unresolved_obligations=dict(finishing=finishing_contract,source_machining='Exact predecessor dispositions retained; finished geometry/moments/QA/access unproved',
            retained_parent_geometry_domains=[deepcopy(row) for row in parent_domains if row['retained_pattern_count']>0],
            inherited_local_contracts=deepcopy(local_plan['pending_contracts']),floor_wear_patch=deepcopy(terminal['floor_wear_patch_unapplied']),
            fourteen_scope_cost='Direct owner ledger only; integrate assembly, tooling, civil, construction, power, site/depot, fleet, electricity, operations, maintenance, renewals, recovery/reliability and disposal without double counting'),
        aggregate_mass_properties=None,complete_installed_mass=False,complete_installed_cost=False,
        physical_source_transactions_applied=False,canonical_definition=None,
        geometry_lift_to_apply_m=0.,deployment_count=2,**FLAGS))
