"""Source-bound SI geometry fixtures for the optional CAD/CAE backend pilot.

These are selected *subsets*, plus a separately identified research shuttle.
They do not supply complete installed geometry or establish railway acceptance.
"""
from copy import deepcopy
from hashlib import sha256
from math import fsum, isfinite, pi, sqrt
from pathlib import Path
import gzip
import io
import json


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = 'osr-craft-cad-case/1'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False,
             installed_mass_complete=False)
CURRENT = 'docs/design-engine/current'
GALLERY = 'docs/engineering-models'
PRODUCER = 'engineering/design_search/craft_backends/cases.py'
_LOADED = sha256(Path(__file__).read_bytes()).hexdigest()


def identity(value):
    return sha256((json.dumps(value, sort_keys=True, separators=(',', ':'),
                              allow_nan=False) + '\n').encode()).hexdigest()


def _ordinary(root, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or not p.parts:
        raise ValueError('Ordinary source path required')
    target = root / p
    for part in (target, *target.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Linked source is not admitted')
    if not target.is_file() or target.stat().st_size > 64 * 1024**2:
        raise ValueError('Bounded ordinary source required: ' + relative)
    return target


def _digest(root, name):
    return sha256(_ordinary(root, name).read_bytes()).hexdigest()


def _json(root, name):
    raw = _ordinary(root, name).read_bytes()
    if name.endswith('.gz'):
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(32 * 1024**2 + 1)
    if len(raw) > 32 * 1024**2:
        raise ValueError('Source definition exceeds decompression budget')
    return json.loads(raw)


def _unreleased(value):
    for name in FLAGS:
        if name in value and value[name] is not False:
            raise ValueError('Research fixture cannot promote ' + name)


def _vector(value, positive=False):
    if (not isinstance(value, (list, tuple)) or len(value) != 3
            or any(type(x) not in (int, float) or not isfinite(x)
                   or (positive and x <= 0) for x in value)):
        raise ValueError('Finite three-coordinate SI geometry required')
    return list(value)


def normalize_entity(source, material=None):
    """Keep installed coordinates; presentation displacement is never applied."""
    s = source['shape']
    if s not in ('box', 'cylinder', 'tube', 'sphere'):
        raise ValueError('Unsupported or unquantified material geometry: ' + s)
    geometry = dict(at_m=_vector(source['at_m']))
    if s == 'box':
        if source.get('holes'):
            raise ValueError('Perforated boxes need their own exact geometry adapter')
        geometry['size_m'] = _vector(source['size_m'], positive=True)
    else:
        r = source['radius_m']
        if type(r) not in (int, float) or not isfinite(r) or r <= 0:
            raise ValueError('Positive finite radius required')
        geometry['radius_m'] = r
        if s in ('cylinder', 'tube'):
            length = source['length_m']
            axis = _vector(source['axis'])
            if (type(length) not in (int, float) or not isfinite(length) or length <= 0
                    or abs(fsum(x*x for x in axis) - 1.) > 1e-10):
                raise ValueError('Positive length and explicit unit axis required')
            geometry.update(length_m=length, axis=axis)
        if s == 'tube':
            inner = source['inner_radius_m']
            if type(inner) not in (int, float) or not isfinite(inner) or not 0 < inner < r:
                raise ValueError('Positive tube wall required')
            geometry['inner_radius_m'] = inner
    _unreleased(source)
    return dict(id=source['id'], shape=s, geometry=geometry,
                material=material or source['material'],
                source_material=source.get('source_material', source['material']),
                basis=source['basis'], source=source['source'],
                source_entity=deepcopy(source),
                presentation_offset_applied=False)


def measures(entity):
    """Analytical occurrence measures, never a fused/intersection or installed claim."""
    g = entity['geometry']; p = _vector(g['at_m']); s = entity['shape']
    if s == 'box':
        a, b, c = _vector(g['size_m'], positive=True)
        v = a*b*c; centre = [p[0]+a/2, p[1]+b/2, p[2]+c/2]
        bounds = [p, [p[0]+a, p[1]+b, p[2]+c]]
    elif s in ('cylinder', 'tube'):
        r, length, axis = g['radius_m'], g['length_m'], g['axis']
        if (any(type(x) not in (int,float) or not isfinite(x) or x <= 0 for x in (r,length))
                or abs(fsum(x*x for x in _vector(axis))-1.) > 1e-10
                or not 0 <= g.get('inner_radius_m',0.) < r):
            raise ValueError('Valid SI cylindrical material geometry required')
        v = pi*(r*r-g.get('inner_radius_m', 0.)**2)*length
        centre = [a+b*length/2 for a, b in zip(p, axis)]
        end = [a+b*length for a, b in zip(p, axis)]
        width = [r*sqrt(max(0., 1.-a*a)) for a in axis]
        bounds = [[min(a,b)-c for a,b,c in zip(p,end,width)],
                  [max(a,b)+c for a,b,c in zip(p,end,width)]]
    elif s == 'sphere':
        r = g['radius_m']
        if type(r) not in (int,float) or not isfinite(r) or r <= 0:
            raise ValueError('Positive SI radius required')
        v = 4*pi*r**3/3; centre = p
        bounds = [[a-r for a in p], [a+r for a in p]]
    else:
        raise ValueError('Unknown material volume remains unknown')
    if not isfinite(v) or v <= 0:
        raise ValueError('Positive finite material volume required')
    return dict(volume_m3=v, centroid_m=centre, bounds_m=bounds)


def geometry_identity(entities):
    return identity(dict(schema='osr-physical-geometry-subset/1', units='m',
                         entities=[{k:e[k] for k in ('id','shape','geometry','material')}
                                   for e in entities]))


def _case(case_id, entities, materials, sources, *, candidate_id=None,
          source_evaluation_id=None, source_selection_id=None,
          source_study_id=None, scope, assumptions, source_candidate_id=None):
    parts = {e['id']:measures(e) for e in entities}
    total = fsum(p['volume_m3'] for p in parts.values())
    centroid = [fsum(p['volume_m3']*p['centroid_m'][i] for p in parts.values())/total
                for i in range(3)]
    bounds = [[min(p['bounds_m'][0][i] for p in parts.values()) for i in range(3)],
              [max(p['bounds_m'][1][i] for p in parts.values()) for i in range(3)]]
    masses = {e['id']:(None if materials[e['material']]['density_kg_m3'] is None
                       else parts[e['id']]['volume_m3']*materials[e['material']]['density_kg_m3'])
              for e in entities}
    gid = geometry_identity(entities)
    value = dict(schema=SCHEMA, case_id=case_id, candidate_id=candidate_id or gid,
                 component_geometry_id=gid, source_candidate_id=source_candidate_id,
                 source_evaluation_id=source_evaluation_id,
                 source_selection_id=source_selection_id, source_study_id=source_study_id,
                 units=dict(length='m', volume='m3', mass='kg', density='kg/m3'),
                 coordinate_frame='x-forward, y-left, z-up; source rail surface z=0',
                 entities=entities, materials=materials, source_sha256=dict(sorted(sources.items())),
                 expected=dict(part_count=len(entities), part_measures=parts,
                               total_volume_m3=total, centroid_m=centroid, bounds_m=bounds,
                               part_material_masses_kg=masses,
                               known_material_mass_subtotal_kg=fsum(m for m in masses.values() if m is not None),
                               total_material_mass_kg=(None if any(m is None for m in masses.values()) else fsum(masses.values())),
                               volume_scope='sum of individual occurrences; not a Boolean union',
                               centroid_scope='material-volume weighted centroid, not installed equipment CG'),
                 scope=scope, assumptions=assumptions,
                 presentation_offsets_are_installed_positions=False, **FLAGS)
    value['case_definition_id'] = identity(value)
    return value


def validate_case(value):
    if value.get('schema') != SCHEMA or value.get('units') != dict(length='m',volume='m3',mass='kg',density='kg/m3'):
        raise ValueError('Explicit SI case required')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('Provisional case cannot grant acceptance')
    if value.get('case_definition_id') != identity({k:v for k,v in value.items() if k!='case_definition_id'}):
        raise ValueError('Case definition changed')
    if value.get('component_geometry_id') != geometry_identity(value['entities']):
        raise ValueError('Physical subset geometry differs')
    if value['source_candidate_id'] is None:
        if value['candidate_id'] != value['component_geometry_id'] or value['source_selection_id'] is not None:
            raise ValueError('Standalone research component cannot inherit a selection')
    elif value['candidate_id'] != value['source_candidate_id']:
        raise ValueError('Mixed selected candidate identity')
    if len({e['id'] for e in value['entities']}) != len(value['entities']):
        raise ValueError('Unique occurrence identities required')
    ids={e['id'] for e in value['entities']}
    if (set(value['expected']['part_measures']) != ids
            or set(value['expected']['part_material_masses_kg']) != ids
            or value['expected']['part_count'] != len(ids)):
        raise ValueError('Exact occurrence coverage required')
    for e in value['entities']:
        if e.get('presentation_offset_applied') is not False:
            raise ValueError('Exploded offsets are not physical placement')
        if value['expected']['part_measures'][e['id']] != measures(e):
            raise ValueError('Physical quantity differs')
        if e['material'] not in value['materials']:
            raise ValueError('Explicit material or material hypothesis required')
    parts=value['expected']['part_measures'];total=fsum(p['volume_m3'] for p in parts.values())
    if value['expected']['total_volume_m3'] != total:
        raise ValueError('Aggregate volume differs')
    if value['expected']['centroid_m'] != [fsum(p['volume_m3']*p['centroid_m'][i] for p in parts.values())/total for i in range(3)]:
        raise ValueError('Aggregate centroid differs')
    if value['expected']['bounds_m'] != [[min(p['bounds_m'][0][i] for p in parts.values()) for i in range(3)],
                                        [max(p['bounds_m'][1][i] for p in parts.values()) for i in range(3)]]:
        raise ValueError('Aggregate placement bounds differ')
    for e in value['entities']:
        density=value['materials'][e['material']]['density_kg_m3']
        if density is not None and (type(density) not in (int,float) or not isfinite(density) or density <= 0):
            raise ValueError('Density must be positive or explicitly unknown')
        expected_mass=None if density is None else parts[e['id']]['volume_m3']*density
        if value['expected']['part_material_masses_kg'][e['id']] != expected_mass:
            raise ValueError('Material quantity differs')
    masses=value['expected']['part_material_masses_kg']
    if value['expected']['known_material_mass_subtotal_kg'] != fsum(m for m in masses.values() if m is not None):
        raise ValueError('Known material subtotal differs')
    if value['expected']['total_material_mass_kg'] != (None if any(m is None for m in masses.values()) else fsum(masses.values())):
        raise ValueError('Unknown material mass cannot become a complete quantity')
    return value


def cases(root=ROOT):
    root = Path(root).resolve()
    if sha256(Path(__file__).read_bytes()).hexdigest() != _LOADED:
        raise ValueError('Fixture producer changed during execution')
    current_manifest = _json(root, CURRENT+'/manifest.json')
    _unreleased(current_manifest)
    if current_manifest.get('manifest_id') != identity({k:v for k,v in current_manifest.items() if k!='manifest_id'}):
        raise ValueError('Current publication identity differs')
    current_name = CURRENT+'/evaluation.json.gz'
    if _digest(root, current_name) != current_manifest['files_sha256']['evaluation.json.gz']:
        raise ValueError('Current geometry payload differs')
    record = _json(root, current_name)
    for name in ('candidate_id','evaluation_id','selection_id'):
        if record[name] != current_manifest[name]:
            raise ValueError('Mixed current '+name)
    gallery = _json(root, GALLERY+'/manifest.json')
    _unreleased(gallery)
    if gallery.get('publication_id') != identity({k:v for k,v in gallery.items() if k!='publication_id'}):
        raise ValueError('Gallery publication identity differs')
    sources = {PRODUCER:_LOADED,CURRENT+'/manifest.json':_digest(root,CURRENT+'/manifest.json'),
               current_name:_digest(root,current_name),
               GALLERY+'/manifest.json':_digest(root,GALLERY+'/manifest.json')}
    for name, expected in gallery['source_sha256'].items():
        actual = _digest(root,name)
        if actual != expected:
            raise ValueError('Gallery input source changed: '+name)
        sources[name] = actual
    definitions = {}
    for key in ('vehicle-fabrication','launcher-booster'):
        relative = 'definitions/'+key+'.json.gz'; name = GALLERY+'/'+relative
        if _digest(root,name) != gallery['files_sha256'][relative]:
            raise ValueError('Published component definition differs: '+key)
        definitions[key] = _json(root,name); sources[name] = _digest(root,name)
        _unreleased(definitions[key])
        if definitions[key].get('units') != 'metres':
            raise ValueError('Source geometry must explicitly use metres')
    # The concrete solids reproduce _beam() rather than a similarly named
    # portfolio section which omits the source end diaphragms.
    s = record['civil']['selected_reference']; d = s['section']['dimensions']; dia = s['diaphragm_definition']
    L,B,H,w,f,top = s['span_m'],d['outer_width_m'],d['depth_m'],d['wall_m'],d['flange_m'],-.192
    pieces = [('bottom',[0.,-B/2,top-H],[L,B,f]),('top',[0.,-B/2,top-f],[L,B,f]),
              ('near-web',[0.,-B/2,top-H+f],[L,w,H-2*f]),('far-web',[0.,B/2-w,top-H+f],[L,w,H-2*f])]
    if dia['quantity'] != 2:
        raise ValueError('This pilot requires the actual two-end-diaphragm beam')
    for i,x in enumerate((0.,L-dia['thickness_m'])):
        pieces.append((f'diaphragm-{i}',[x,-dia['clear_width_m']/2,top-H+f],
                       [dia['thickness_m'],dia['clear_width_m'],dia['height_m']]))
    beam = [normalize_entity(dict(id='selected-beam/'+n,shape='box',at_m=at,size_m=size,
                                  material='concrete',basis='source-geometry',
                                  source=current_name+'#/civil/selected_reference')) for n,at,size in pieces]
    if abs(fsum(measures(e)['volume_m3'] for e in beam)-s['concrete_m3']) > 1e-8:
        raise ValueError('Selected six-piece beam volume does not reconcile')
    concrete_density = s['concrete_mass_kg']/s['concrete_m3']
    selected = dict(candidate_id=record['candidate_id'],source_candidate_id=record['candidate_id'],
                    source_evaluation_id=record['evaluation_id'],source_selection_id=record['selection_id'])
    result = [_case('selected-beam20m',beam,dict(concrete=dict(density_kg_m3=concrete_density,
                    basis='Source concrete mass/volume; source engineering material hypothesis, not a material certificate')),
                    sources,scope='Six concrete stock solids only; source reinforcement, prestress, anchors, rails and bearings are excluded, not zero',
                    assumptions=['Linear material/strength assumptions belong to separate evaluations; this is geometry, not a bridge acceptance.'],**selected)]
    vehicle = definitions['vehicle-fabrication']; prefix='source/wheel-underframe/sill/1/'
    subset = [e for e in vehicle['entities'] if e['id'].startswith(prefix)]
    if {e['id'] for e in subset} != {prefix+str(i) for i in range(4)}:
        raise ValueError('Exact four source sill walls required')
    if vehicle['reference_context']['reference_candidate_id'] != record['candidate_id']:
        raise ValueError('Vehicle visual subset belongs to another candidate')
    stock = {p['id']:p for p in record['vehicle']['geometry_parts']}
    for e in subset:
        p=stock[e['source_part_id']]
        if e['at_m'] != p['at_m'] or e['size_m'] != p['size_m']:
            raise ValueError('Installed source sill placement differs')
    sill = [normalize_entity(e,'6082-T6-proposed') for e in sorted(subset,key=lambda e:e['id'])]
    densities = {stock[e['source_part_id']]['density_kg_m3'] for e in subset}
    if len(densities) != 1:
        raise ValueError('Explicit per-part density adapter needed')
    result.append(_case('selected-side-sill',sill,{'6082-T6-proposed':dict(density_kg_m3=densities.pop(),
                    basis='Source proposed aluminium specification; no certified allowables inferred')},sources,
                    source_study_id=vehicle['visual_study_id'],scope='One installed 17m side sill: four source walls, not a whole carbody',
                    assumptions=['Source exploded rendering offsets are excluded; joints, interfaces and complete installed body remain outside this subset.'],**selected))
    shuttle = definitions['launcher-booster']; subset=[e for e in shuttle['entities'] if e['id'].startswith('launch-shuttle/')]
    if len(subset) != 14:
        raise ValueError('Exact fourteen-part launch shuttle layout required')
    material_map = {'teal':'steel-proposed','orange':'steel-proposed','dark_steel':'steel-proposed',
                    'steel':'steel-proposed','rubber':'rubber-unresolved','white':'target-material-unresolved'}
    entities=[normalize_entity(e,material_map[e['material']]) for e in subset]
    materials={'steel-proposed':dict(density_kg_m3=7850.,basis='Explicit carbon-steel candidate assignment to rendered structural envelopes; strength, fatigue and actual material unknown'),
               'rubber-unresolved':dict(density_kg_m3=None,basis='Elastomer compound unspecified; volume is known, material mass remains unknown'),
               'target-material-unresolved':dict(density_kg_m3=None,basis='Rendered white target has no physical material assignment')}
    result.append(_case('research-launch-shuttle',entities,materials,sources,
                    source_evaluation_id=shuttle['reference_context']['source_physics_evaluation_id'],
                    source_study_id=shuttle['visual_study_id'],
                    scope='Independent proposed launch shuttle component; not an installed or selected propulsion system',
                    assumptions=['Source scenario '+shuttle['reference_context']['source_scenario_id'],
                                 'Source motion is an illustrative160000kg point mass, not the selected train mass.',
                                 'Colour names are source rendering appearances, not material certificates; candidate material assignments are explicit.',
                                 'Occurrence sums may overlap at joints; no fused volume, clearance, pressure, fatigue or impact qualification is asserted.'] ))
    control = normalize_entity(dict(id='control/asymmetric-box',shape='box',at_m=[-2.3,1.7,.6],
                                   size_m=[.321,.047,.013],material='aluminium-control',
                                   basis='declared-analytic-control',source='Explicit metre/mm and placement control'))
    result.append(_case('asymmetric-si-control',[control],{'aluminium-control':dict(density_kg_m3=2700.,
                    basis='Declared unit-control density only')},{PRODUCER:_LOADED},scope='Analytical unit and translation control, not railway hardware',
                    assumptions=['Native CAD millimetre conversion must be explicit; API values and expected outputs remain SI.']))
    for case in result:
        validate_case(case)
    return result


def verify_case(value, root=ROOT):
    validate_case(value)
    expected = next((c for c in cases(root) if c['case_id']==value['case_id']),None)
    if expected != value:
        raise ValueError('Case differs from current source-bound definition')
    return value
