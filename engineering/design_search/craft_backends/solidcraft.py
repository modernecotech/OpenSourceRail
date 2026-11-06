"""SI scene primitives to SolidCraft 0.30.1's recorded command interface.

Each occurrence is a separately named body.  Provider measurements of curved
geometry use its tessellation and are diagnostics, not exact B-rep quantities.
The backend's default material/mass is never an OSR installed-mass account.
"""
from copy import deepcopy
from math import isfinite, sqrt

PROVIDER = 'solidcraft'
VERSION = '0.30.1'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)
SUPPORTED_SHAPES = frozenset(('box', 'cylinder', 'tube', 'sphere', 'profile'))


def _number(value, *, positive=False):
    if type(value) not in (int, float) or not isfinite(value) or (positive and value <= 0):
        raise ValueError('Finite positive SI dimension required' if positive else 'Finite SI coordinate required')
    return float(value)


def _vector(value):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError('Three explicit SI coordinates required')
    return [_number(x) for x in value]


def _mm(value):
    return _number(value) * 1000.


def _mm_vector(value):
    return [_mm(x) for x in _vector(value)]


def _axis(value):
    v = _vector(value)
    if abs(sqrt(sum(x*x for x in v))-1.) > 1e-9:
        raise ValueError('Source cylinder axis must be an explicit unit vector')
    return v


def _entity(value):
    """Accept the case contract and the original visual scene contract."""
    if not isinstance(value, dict):
        raise ValueError('Named physical occurrence required')
    e = deepcopy(value.get('source_entity', {}))
    e.update(deepcopy(value.get('geometry', {})))
    e.update({k: deepcopy(v) for k, v in value.items()
              if k not in ('geometry', 'source_entity', 'render_offset_m')})
    e.pop('render_offset_m', None)
    name = e.get('id')
    if not isinstance(name, str) or not name or len(name) > 512 or any(ord(c) < 32 for c in name):
        raise ValueError('Unique printable source occurrence ID required')
    if e.get('shape') not in SUPPORTED_SHAPES:
        raise ValueError('Unsupported CAD primitive; routing envelopes are not material solids')
    e['at_m'] = _vector(e.get('at_m'))
    return e


def _command(name, params):
    return dict(command=name, params=params)


def _cylinder(radius, length, base, axis, name=None, target=None):
    p = dict(radius=_mm(_number(radius, positive=True)),
             height=_mm(_number(length, positive=True)), base=_mm_vector(base), axis=_axis(axis),
             operation='cut' if target else 'new')
    if target:
        p['targets'] = [target]
    else:
        p['body_name'] = name
    return _command('solid.cylinder', p)


def _primitive(e):
    name, shape, at = e['id'], e['shape'], e['at_m']
    if shape == 'box':
        size = [_number(x, positive=True) for x in _vector(e.get('size_m'))]
        out = [_command('solid.box', dict(zip(('length', 'width', 'height'), map(_mm, size)),
                                          corner=_mm_vector(at), operation='new', body_name=name))]
        for hole in e.get('holes', []):
            axis = hole.get('axis', 'z')
            if axis not in ('x', 'y', 'z'):
                raise ValueError('Ordinary source through-hole axis required')
            index = 'xyz'.index(axis)
            radius = _number(hole['diameter_m'], positive=True)/2
            length = _number(hole.get('length_m', size[index]), positive=True)
            if length > size[index]:
                raise ValueError('Source hole length exceeds its material envelope')
            base = at[:]
            for j, key in enumerate(('x_m', 'y_m', 'z_m')):
                if j != index:
                    offset = _number(hole.get(key, 0.))
                    if offset-radius < 0 or offset+radius > size[j]:
                        raise ValueError('Source hole is not wholly inside its declared box')
                    base[j] += offset
            direction = [0., 0., 0.]
            direction[index] = 1.
            out.append(_cylinder(radius, length, base, direction, target=name))
        return out
    if shape in ('cylinder', 'tube'):
        radius = _number(e['radius_m'], positive=True)
        length = _number(e['length_m'], positive=True)
        axis = _axis(e['axis'])
        out = [_cylinder(radius, length, at, axis, name=name)]
        if shape == 'tube':
            inner = _number(e['inner_radius_m'], positive=True)
            if inner >= radius:
                raise ValueError('Tube requires positive material thickness')
            out.append(_cylinder(inner, length, at, axis, target=name))
        return out
    if shape == 'sphere':
        return [_command('solid.sphere', dict(radius=_mm(_number(e['radius_m'], positive=True)),
                                              center=_mm_vector(at), operation='new', body_name=name))]
    points = e.get('points_yz_m')
    if not isinstance(points, list) or len(points) < 3 or any(not isinstance(p, (list, tuple)) or len(p) != 2 for p in points):
        raise ValueError('Closed source section points required')
    coordinates = [[_number(x) for x in p] for p in points]
    area = abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in zip(coordinates, coordinates[1:]+coordinates[:1])))/2
    if area == 0:
        raise ValueError('Source profile has no material area')
    return [_command('sketch.create', dict(plane=dict(origin=_mm_vector(at), x_dir=[0, 1, 0], y_dir=[0, 0, 1]), name='OSR section '+name)),
            _command('sketch.line', dict(points=[[_mm(x) for x in p] for p in coordinates], closed=True, infer=False)),
            _command('sketch.finish', {}),
            _command('solid.extrude', dict(distance=_mm(_number(e['length_m'], positive=True)), operation='new', body_name=name))]


def script_for(case):
    """Create a new-design script, preserving installed SI occurrence placement.

    The caller starts a fresh CLI session; this script does not open, save or
    overwrite files.  Export paths and process isolation belong to the runner.
    """
    if not isinstance(case, dict) or not isinstance(case.get('entities'), list) or not 1 <= len(case['entities']) <= 3500:
        raise ValueError('Bounded named case required')
    if any(case.get(k, False) is not False for k in FLAGS):
        raise ValueError('Research CAD cannot grant acceptance or authority')
    for key in ('candidate_id', 'component_geometry_id'):
        value = case.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError('Exact candidate and component geometry identities required')
    entities = sorted((_entity(e) for e in case['entities']), key=lambda e: e['id'])
    if len({e['id'] for e in entities}) != len(entities):
        raise ValueError('Duplicate physical occurrence ID')
    binding = {k: deepcopy(case.get(k)) for k in ('case_id', 'candidate_id', 'component_geometry_id',
                                               'source_evaluation_id', 'source_selection_id', 'source_study_id')}
    binding.update(declared_input_units='m', native_geometry_units='mm', display_offsets_applied=False, **FLAGS)
    commands = [_command('document.units', {'units': 'mm'}),
                _command('document.metadata.set', {'values': {'org.opensourcerail.candidate': binding}})]
    materials = case.get('materials', {})
    assigned = {}
    for e in entities:
        commands.extend(_primitive(e))
        # Optional density assignment is an explicit hypothesis, never a strength
        # value or proof of an installed material.  Missing density stays missing.
        spec = materials.get(e.get('material')) if isinstance(materials, dict) else None
        if isinstance(spec, dict):
            density = spec.get('density_kg_m3', spec.get('density_hypothesis_kg_m3'))
            if density is not None:
                density = _number(density, positive=True)
                material = 'OSR '+str(e.get('material'))
                if e.get('material') not in assigned:
                    commands.append(_command('material.create', dict(name=material, density_g_cm3=density/1000.)))
                    assigned[e.get('material')] = density
                commands.append(_command('material.assign', dict(bodies=[e['id']], material=material)))
    commands.append(_command('inspect.measure', {}))
    return dict(commands=commands)


def parse_measurements(value):
    """Convert explicit provider measurements to SI without trusting CAD mass.

    Accept either inspect.measure or run --results. Curved volume and bounds
    are provider tessellation diagnostics; independent STEP checks remain needed.
    """
    if isinstance(value, list):
        options = [v for v in value if isinstance(v, dict) and isinstance(v.get('bodies'), list)
                   and all(isinstance(b, dict) for b in v['bodies']) and 'total' in v]
        if not options:
            raise ValueError('No native inspect.measure result')
        value = options[-1]
    if not isinstance(value, dict) or not isinstance(value.get('bodies'), list) or not value['bodies']:
        raise ValueError('Explicit nonempty native body measurements required')
    bodies = []
    for b in value['bodies']:
        if not isinstance(b, dict) or not isinstance(b.get('name'), str):
            raise ValueError('Named native body measurement required')
        def scale(key, factor):
            v = b.get(key)
            return None if v is None else _number(v)*factor
        center = b.get('center_of_mass')
        bbox = b.get('bbox')
        bodies.append(dict(id=b['name'], closed=b.get('closed'),
                           volume_m3=scale('volume_mm3', 1e-9), area_m2=scale('area_mm2', 1e-6),
                           center_of_mass_m=None if center is None else [x*.001 for x in _vector(center)],
                           bbox_m=None if bbox is None else {k: [x*.001 for x in _vector(bbox[k])] for k in ('min', 'max')},
                           mass_kg=None, backend_material=b.get('material'),
                           provider_mass_ignored=True, measurement_error=b.get('error')))
    if len({b['id'] for b in bodies}) != len(bodies) or value.get('body_count', len(bodies)) != len(bodies):
        raise ValueError('Native body identity/count differs')
    total = value.get('total', {})
    if not isinstance(total, dict):
        raise ValueError('Explicit native measurement totals required')
    volume = total.get('volume_mm3')
    all_closed = all(b['closed'] is True and b['volume_m3'] is not None for b in bodies)
    return dict(schema='osr-solidcraft-measurements/1', provider=PROVIDER,
                native_units=dict(length='mm', area='mm2', volume='mm3'),
                units=dict(length='m', area='m2', volume='m3'), bodies=bodies,
                total_volume_m3=None if volume is None or not all_closed else _number(volume)*1e-9,
                open_bodies_skipped=total.get('open_bodies_skipped'),
                measurement_fidelity='Provider tessellation diagnostics; not exact curved B-rep quantities',
                installed_mass_complete=False, **FLAGS)
