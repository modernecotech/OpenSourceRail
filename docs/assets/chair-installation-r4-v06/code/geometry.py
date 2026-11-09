"""Pure local-chair CAD definition and analytical oracle; executes no CAD.

The input is a sealed chair coupon, never a vehicle or a new chair generator.
All dimensions stay in its original component-local metres. SolidCraft commands
use millimetres. In particular, a max-face blind bore starts at max minus depth;
the generic corner-box compiler's minimum-face convention is not used here.
"""
from copy import deepcopy
from hashlib import sha256
import json
from math import fsum, isfinite, pi, prod
from pathlib import Path

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, native_evaluator_admitted=False,
             installed_mass_complete=False, movement_authority=False)
TOOL = dict(version='v0.30.1', commit='8e2b0cd60d14b4152b12b8f1fdb2bcfdcd8c52f4',
            binary_sha256='e8a778658ddc43214f253a33255c23d0b0c520ba6e3b283bd913123cda86b243')


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def identity(value):
    return sha256(encoded(value)).hexdigest()


def _number(x, *, positive=False):
    if type(x) not in (int, float) or not isfinite(x) or (positive and x <= 0):
        raise ValueError('Explicit finite SI number required')
    return float(x)


def _vector(x):
    if not isinstance(x, (list, tuple)) or len(x) != 3:
        raise ValueError('Three explicit component-local SI coordinates required')
    return [_number(v) for v in x]


def _name(x):
    if not isinstance(x, str) or not x.strip() or len(x) > 512 or any(ord(c) < 32 for c in x):
        raise ValueError('Nonempty printable identity required')
    return x


def _digest(x, length=64):
    if not isinstance(x, str) or len(x) != length or any(c not in '0123456789abcdef' for c in x):
        raise ValueError('Exact hexadecimal source identity required')
    return x


def _axis(x):
    if type(x) is not int or x not in (0, 1, 2):
        raise ValueError('Explicit integer round-stock axis 0/1/2 required')
    return x


def source_physical_projection(coupon):
    """Reproduce the published source identity contract, not its numerical code."""
    c = coupon['consumables']
    return dict(entities=deepcopy(coupon['entities']),
        bounded_welds=[{k: deepcopy(w[k]) for k in ('fillet_m', 'net_length_m', 'centroid_m')}
                       for w in c['welds']],
        bounded_consumables={n: {k: deepcopy(c[n][k]) for k in ('net_mass_kg', 'centroid_hypothesis_m')}
            for n in ('powder_coating', 'cover_seams', 'anchor_sealant', 'r3_added_foot_finish') if n in c})


def _cut_bounds(c):
    a = c['axis']; r = c['radius_m']; L = c['length_m']; b = c['base_m']
    return ([b[k] if k == a else b[k]-r for k in range(3)],
            [b[k]+L if k == a else b[k]+r for k in range(3)])


def _disjoint(cuts):
    for i, a in enumerate(cuts):
        for b in cuts[i+1:]:
            al, ah = _cut_bounds(a); bl, bh = _cut_bounds(b)
            if any(min(ah[k], bh[k]) <= max(al[k], bl[k]) for k in range(3)):
                continue
            if a['axis'] == b['axis']:
                transverse = [k for k in range(3) if k != a['axis']]
                d2 = fsum((a['base_m'][k]-b['base_m'][k])**2 for k in transverse)
                if d2 >= (a['radius_m']+b['radius_m'])**2:
                    continue
            # Orthogonal overlapping bounds are conservatively out of domain:
            # no invented cylinder-intersection/Boolean-union subtraction.
            raise ValueError('Intersecting or unresolved bore union; disjoint cuts required')


def solid_oracle(entity):
    """Independently derive a nominal solid, volume, centroid and tight bounds.

    Box holes use absolute transverse centres; their axial source coordinate is
    a centreline reference, not the material entry. All removed cylinders must
    be contained and disjoint. This arithmetic does not call chair source code.
    """
    e = deepcopy(entity)
    if not isinstance(e, dict):
        raise ValueError('Named material primitive required')
    name, mat = _name(e.get('id')), _name(e.get('material'))
    if e.get('shape') == 'box':
        if set(e) != {'id', 'material', 'shape', 'center_m', 'size_m', 'bores'}:
            raise ValueError('Unresolved or extra box geometry fields')
        center, size = _vector(e['center_m']), [_number(x, positive=True) for x in _vector(e['size_m'])]
        lo = [c-s/2 for c, s in zip(center, size)]; hi = [c+s/2 for c, s in zip(center, size)]
        if not isinstance(e['bores'], list) or len(e['bores']) > 64:
            raise ValueError('Bounded explicit bore list required')
        cuts = []
        for hole in e['bores']:
            if not isinstance(hole, dict) or set(hole) not in (
                    {'axis', 'center_m', 'diameter_m'},
                    {'axis', 'center_m', 'diameter_m', 'depth_m', 'entry_face'}):
                raise ValueError('Exact through or explicitly faced blind bore required')
            a, c = _axis(hole['axis']), _vector(hole['center_m'])
            radius = _number(hole['diameter_m'], positive=True)/2
            depth = _number(hole.get('depth_m', size[a]), positive=True)
            if depth > size[a]+1e-12:
                raise ValueError('Bore exceeds material depth')
            if any(c[k]-radius < lo[k]-1e-12 or c[k]+radius > hi[k]+1e-12 for k in range(3) if k != a):
                raise ValueError('Bore is not contained in its own box')
            face = hole.get('entry_face', -1)
            if type(face) is not int or face not in (-1, 1):
                raise ValueError('Explicit blind entry face -1/+1 required')
            base = c[:]; base[a] = lo[a] if face == -1 else hi[a]-depth
            cuts.append(dict(axis=a, base_m=base, length_m=depth, radius_m=radius))
        _disjoint(cuts)
        initial = prod(size)
        removals = [pi*c['radius_m']**2*c['length_m'] for c in cuts]
        volume = initial-fsum(removals)
        if volume <= 0:
            raise ValueError('Nonpositive net material')
        removed_centers = [[c['base_m'][k]+(c['length_m']/2 if k == c['axis'] else 0.) for k in range(3)] for c in cuts]
        centroid = [(initial*center[k]-fsum(v*c[k] for v, c in zip(removals, removed_centers)))/volume for k in range(3)]
        solid = dict(id=name, material=mat, shape='box', corner_m=lo, size_m=size, cuts=cuts)
    elif e.get('shape') == 'cylinder':
        if set(e) != {'id', 'material', 'shape', 'axis', 'start_m', 'length_m', 'radius_m', 'inner_radius_m'}:
            raise ValueError('Unresolved or extra round geometry fields')
        a, start = _axis(e['axis']), _vector(e['start_m'])
        length, radius = _number(e['length_m'], positive=True), _number(e['radius_m'], positive=True)
        inner = _number(e['inner_radius_m'])
        if not 0 <= inner < radius:
            raise ValueError('Positive annular material thickness required')
        volume = pi*(radius*radius-inner*inner)*length
        centroid = [start[k]+(length/2 if k == a else 0.) for k in range(3)]
        lo = [start[k] if k == a else start[k]-radius for k in range(3)]
        hi = [start[k]+length if k == a else start[k]+radius for k in range(3)]
        solid = dict(id=name, material=mat, shape='cylinder', axis=a, start_m=start,
                     length_m=length, radius_m=radius, inner_radius_m=inner)
    else:
        raise ValueError('Unknown/unresolved solid; cannot omit material')
    return solid, dict(volume_m3=volume, center_of_mass_m=centroid,
        bbox_m=dict(min=lo, max=hi), source_material=mat,
        method='Analytical contained disjoint primitive subtraction; no native/source evaluator',
        complete_installed=False)


def _tool(pin):
    if not isinstance(pin, dict) or any(pin.get(k) != v for k, v in TOOL.items()):
        raise ValueError('Recorded SolidCraft v0.30.1 API/tool pin required')
    return deepcopy(pin)


def script_for(case):
    """Recorded commands only; no save/open/process/tool invocation."""
    if (case.get('schema') != 'osr-local-chair-native-geometry/1'
            or case.get('units') != 'm' or case.get('frame') != 'coupon-local'):
        raise ValueError('Unchanged local metre datum required')
    if not isinstance(case.get('entities'), list) or not 1 <= len(case['entities']) <= 3500:
        raise ValueError('Bounded explicit normalized material entities required')
    names = [_name(e.get('id')) for e in case['entities']]
    if len(set(names)) != len(names):
        raise ValueError('Duplicate normalized material identity')
    if any(case.get(k) is not False for k in FLAGS):
        raise ValueError('CAD definition cannot grant acceptance')
    projection = {k: deepcopy(case[k]) for k in ('schema', 'units', 'frame', 'entities')}
    if identity(projection) != case['component_geometry_id']:
        raise ValueError('Component geometry identity differs')
    _digest(case['source_physical_definition_id']); _digest(case['source_execution_id'])
    def command(name, params): return dict(command=name, params=params)
    def cyl(r, L, base, a, *, name=None, target=None):
        axis = [float(k == a) for k in range(3)]
        q = dict(radius=r*1000., height=L*1000., base=[x*1000. for x in base], axis=axis,
                 operation='cut' if target else 'new')
        q.update(targets=[target]) if target else q.update(body_name=name)
        return command('solid.cylinder', q)
    binding = {k: deepcopy(case[k]) for k in ('component_geometry_id', 'source_physical_definition_id', 'source_execution_id')}
    binding.update(identity_scope='local chair coupon, not installed vehicle', display_offsets_applied=False, **FLAGS)
    commands = [command('document.units', dict(units='mm')),
                command('document.metadata.set', dict(values={'org.opensourcerail.local-chair': binding}))]
    assigned = set()
    for e in case['entities']:
        name = e['id']
        mat = _name(e.get('material'))
        spec = case.get('materials', {}).get(mat)
        if not isinstance(spec, dict) or 'density_kg_m3' not in spec:
            raise ValueError('Explicit normalized material/density hypothesis required')
        density = spec['density_kg_m3']
        if density is not None: density = _number(density, positive=True)
        if e['shape'] == 'box':
            if set(e) != {'id', 'material', 'shape', 'corner_m', 'size_m', 'cuts'}:
                raise ValueError('Unresolved normalized box geometry')
            lo = _vector(e['corner_m']); size = [_number(v, positive=True) for v in _vector(e['size_m'])]
            hi = [a+b for a, b in zip(lo, size)]
            if not isinstance(e['cuts'], list) or len(e['cuts']) > 64:
                raise ValueError('Bounded normalized cut list required')
            for c in e['cuts']:
                if set(c) != {'axis', 'base_m', 'length_m', 'radius_m'}:
                    raise ValueError('Unresolved normalized cut geometry')
                a, base = _axis(c['axis']), _vector(c['base_m'])
                r, L = _number(c['radius_m'], positive=True), _number(c['length_m'], positive=True)
                if (L > size[a]+1e-12 or
                    min(abs(base[a]-lo[a]), abs(base[a]+L-hi[a])) > 1e-12 or
                    any(base[k]-r < lo[k]-1e-12 or base[k]+r > hi[k]+1e-12 for k in range(3) if k != a)):
                    raise ValueError('Normalized cut must enter a real material face and stay contained')
            _disjoint(e['cuts'])
            commands.append(command('solid.box', dict(length=e['size_m'][0]*1000., width=e['size_m'][1]*1000.,
                height=e['size_m'][2]*1000., corner=[x*1000. for x in e['corner_m']], operation='new', body_name=name)))
            for c in e['cuts']:
                commands.append(cyl(c['radius_m'], c['length_m'], c['base_m'], c['axis'], target=name))
        elif e['shape'] == 'cylinder':
            solid_oracle(e)
            commands.append(cyl(e['radius_m'], e['length_m'], e['start_m'], e['axis'], name=name))
            if e['inner_radius_m']:
                commands.append(cyl(e['inner_radius_m'], e['length_m'], e['start_m'], e['axis'], target=name))
        else:
            raise ValueError('Unknown normalized material solid')
        if density is not None:
            material = 'OSR chair '+e['material']
            if material not in assigned:
                commands.append(command('material.create', dict(name=material, density_g_cm3=density/1000.)))
                assigned.add(material)
            commands.append(command('material.assign', dict(bodies=[name], material=material)))
    commands.append(command('inspect.measure', {}))
    return dict(commands=commands)


def export_definition(coupon_bytes, recipe_bytes, *, binding, tool_pin, units='m'):
    """Authenticate immutable bytes, return a pure case/oracle/command packet.

    Calling this on the retained actual coupon is a separately authorised
    definition experiment. Source tests call it only with invented small leaves.
    """
    if units != 'm' or not isinstance(coupon_bytes, bytes) or not isinstance(recipe_bytes, bytes):
        raise ValueError('Exact byte inputs with explicit metre units required')
    if len(coupon_bytes) > 8*1024**2 or len(recipe_bytes) > 1024**2:
        raise ValueError('Local coupon input budget exceeded')
    required = {'source_commit', 'source_module_sha256', 'source_packet_manifest_sha256',
                'coupon_sha256', 'recipe_sha256', 'source_physical_definition_id', 'source_execution_id'}
    if not isinstance(binding, dict) or set(binding) != required:
        raise ValueError('Complete exact source binding required')
    for k, v in binding.items(): _digest(v, 40 if k == 'source_commit' else 64)
    if sha256(coupon_bytes).hexdigest() != binding['coupon_sha256'] or sha256(recipe_bytes).hexdigest() != binding['recipe_sha256']:
        raise ValueError('Frozen coupon/recipe bytes changed')
    tool = _tool(tool_pin); coupon = json.loads(coupon_bytes); recipe = json.loads(recipe_bytes)
    if coupon.get('schema') != 'osr.chair-installation-proposal/1' or recipe.get('units') not in ('m', 'm, kg, N, Pa, person-hour, USD'):
        raise ValueError('Explicit source coupon/schema/units required')
    if identity(source_physical_projection(coupon)) != binding['source_physical_definition_id']:
        raise ValueError('Source local physical identity differs')
    if coupon.get('recipe_id') != identity(recipe) or any(v is not False for v in coupon.get('status', {}).values()) or not coupon.get('status'):
        raise ValueError('Source recipe/status binding differs')
    entities = coupon.get('entities')
    if not isinstance(entities, list) or not 1 <= len(entities) <= 3500:
        raise ValueError('Bounded nonempty local material entities required')
    solids, expected = [], {}
    for e in entities:
        s, oracle = solid_oracle(e)
        if s['id'] in expected: raise ValueError('Duplicate material identity')
        solids.append(s); expected[s['id']] = oracle
    solids.sort(key=lambda x: x['id'])
    materials = {}
    for mat in sorted({e['material'] for e in solids}):
        spec = recipe.get('materials', {}).get(mat)
        if not isinstance(spec, dict): raise ValueError('Unknown material must not become an omitted/default solid')
        density = spec.get('density_kg_m3')
        if density is not None: density = _number(density, positive=True)
        materials[mat] = dict(density_kg_m3=density, measured=False, grade_verified=False)
        for key, oracle in expected.items():
            if oracle['source_material'] == mat:
                oracle['nominal_material_mass_kg'] = None if density is None else oracle['volume_m3']*density
    stock = coupon.get('stock'); seen = set(); owned = set(); ownership = []
    if not isinstance(stock, list) or not stock: raise ValueError('Positive once-only stock ownership required')
    for row in stock:
        name = _name(row.get('id')); ids = row.get('entity_ids')
        if name in seen or not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or any(i not in expected or i in owned for i in ids):
            raise ValueError('Missing/duplicate/unknown stock owner')
        seen.add(name); owned.update(ids)
        if any(expected[i]['source_material'] != row.get('material') for i in ids):
            raise ValueError('Mixed stock material identity')
        net = fsum(expected[i]['volume_m3'] for i in ids)
        stated = _number(row.get('net_volume_m3'), positive=True)
        gross = _number(row.get('gross_volume_m3'), positive=True); scrap = _number(row.get('scrap_volume_m3'))
        if abs(net-stated) > 1e-12+net*1e-9 or gross < net-1e-12 or scrap < -1e-12 or abs(gross-stated-scrap) > 1e-12:
            raise ValueError('Stock analytic net/gross/scrap differs')
        ownership.append(dict(id=name, entity_ids=deepcopy(ids), material=row['material'],
                              net_volume_m3=net, gross_volume_m3=gross, scrap_volume_m3=scrap))
    if owned != set(expected): raise ValueError('Unowned positive material solid')
    case = dict(schema='osr-local-chair-native-geometry/1', units='m', frame='coupon-local', entities=solids)
    case['component_geometry_id'] = identity(case)
    case.update(source_physical_definition_id=binding['source_physical_definition_id'],
                source_execution_id=binding['source_execution_id'], materials=materials, **FLAGS)
    commands = script_for(case)
    result = dict(schema='osr-chair-native-definition-export/1', case=case, expected=expected,
        stock_ownership=ownership, source_binding=deepcopy(binding), tool_pin=tool,
        commands=commands, source_metadata_not_geometry=dict(stock=deepcopy(stock), materials=deepcopy(recipe['materials'])),
        bounded_nonprimitive_allowances=dict(source=deepcopy(coupon['consumables']),
            geometry_complete=False, included_in_native_material_solids=False,
            volume_m3=None, scope='Counted source weld/adhesive/finish groups remain separate; no invented solid or measured deposit'),
        numerical_domain=dict(disjoint_bores=True, orthogonal_overlapping_bore_bounds='refused',
            source_axial_bore_coordinate='centreline only; actual entry derived from material faces',
            stock_translation_m=[0., 0., 0.], installed_vehicle_or_P6_inference=False),
        native_comparison_plan=dict(SC='Tessellation diagnostic only', STEP='Independent FreeCAD/OpenCASCADE B-rep required',
            strict_native_names='separate verdict; renamed solids do not conceal a failed identity gate',
            geometric_correspondence='per-solid closed/valid volume+centroid+bounds; ambiguous matching is a hold'),
        implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), actual_native_calls=0, **FLAGS)
    result['evaluation_id'] = identity(result)
    return result
