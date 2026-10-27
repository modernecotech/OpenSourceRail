"""Exact-parent equipped-assembly proposals, never complete installed vehicles.

The three current research bodies retain their canonical railway bundles. A new
installed geometry/pose is a physical assembly revision, not a changed evidence
label on the parent bundle. Imports check bytes, scope and rigid-body arithmetic;
CAD validity, authentication, installation clearance and qualification remain open.
"""
from copy import deepcopy
from itertools import product
from math import isfinite
from pathlib import Path
import numpy as np
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity, digest
from . import design_grammar as grammar, system_body, railway_bundle, system_inventory

PRODUCER = 'engineering/design_search/equipped_candidates.py'
SCHEMA = 'osr-equipped-assembly-evidence/1'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             configuration_adopted=False, manufacturing_release=False,
             operating_release=False)
HARDWARE_KINDS = ('joint', 'bearing', 'slide', 'stop', 'fastener', 'retention',
                  'wire', 'protection', 'hose', 'duct', 'cooling')
REQUIRED_CLOSURE = ('net-body-cuts-and-joint-stock', 'all-equipment-and-mounts',
                    'wiring-protection-and-flexibility', 'cooling-ducts-and-flexibility',
                    'installation-removal-tool-and-lifting-access')


def _array(value, shape, name):
    raw = np.asarray(value, dtype=object)
    if any(type(v) not in (float, int) for v in raw.flat):
        raise ValueError('Numeric ' + name + ' required')
    a = np.asarray(value, dtype=float)
    if a.shape != shape or not np.isfinite(a).all():
        raise ValueError('Finite ' + name + ' required')
    return a


def _number(value, name, positive=False):
    if type(value) not in (float, int) or not isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError('Finite nonnegative ' + name + ' required')
    return float(value)


def _source(root, reference):
    if not isinstance(reference, dict) or set(reference) != {'path', 'sha256'}:
        raise ValueError('Explicit source path and SHA256 required')
    relative = Path(reference['path'])
    if relative.is_absolute() or not relative.parts or '..' in relative.parts:
        raise ValueError('Ordinary source path required')
    p = Path(root).resolve()
    for part in relative.parts:
        p = p / part
        if p.is_symlink(): raise ValueError('Linked assembly source refused')
    if not p.is_file() or digest(p) != reference['sha256']:
        raise ValueError('Assembly source bytes differ')
    return deepcopy(reference)


def transform(value):
    """Vehicle x longitudinal/y left/z up; SI coordinates, proper rotation."""
    if not isinstance(value, dict) or set(value) != {'frame_id', 'translation_m', 'rotation'} or value['frame_id'] != 'vehicle':
        raise ValueError('Explicit vehicle rigid transform required')
    t = _array(value['translation_m'], (3,), 'translation')
    R = _array(value['rotation'], (3, 3), 'rotation')
    if not np.allclose(R.T @ R, np.eye(3), atol=1e-9, rtol=0) or abs(np.linalg.det(R) - 1) > 1e-9:
        raise ValueError('Proper orthonormal rigid rotation required')
    return R, t


def _box(value):
    if not isinstance(value, dict) or set(value) != {'min_m', 'max_m'}:
        raise ValueError('Explicit finite envelope bounds required')
    lo = _array(value['min_m'], (3,), 'envelope minimum')
    hi = _array(value['max_m'], (3,), 'envelope maximum')
    if np.any(hi <= lo): raise ValueError('Positive envelope dimensions required')
    return lo, hi


def swept_envelope(bounds, path):
    """Conservative continuous sweep, including rotation between waypoints.

    Each segment translates linearly and rotates continuously about its declared
    local origin. The local bounding sphere contains every intermediate rotation;
    a segment capsule therefore cannot miss a corner between final positions.
    This broad envelope is not a collision-free installation certificate.
    """
    lo, hi = _box(bounds)
    if not isinstance(path, list) or not path: raise ValueError('Explicit finite installation/removal path required')
    poses = [transform(p) for p in path]
    vertices = np.array(list(product(*zip(lo, hi))))
    if len(poses) == 1:
        R, t = poses[0]; points = vertices @ R.T + t
        lower, upper = points.min(axis=0), points.max(axis=0)
    else:
        radius = float(np.linalg.norm(vertices, axis=1).max())
        translations = np.array([t for R, t in poses])
        lower, upper = translations.min(axis=0) - radius, translations.max(axis=0) + radius
    return dict(min_m=lower.tolist(), max_m=upper.tolist(),
                method='continuous-rotation-bounding-sphere/1' if len(poses) > 1 else 'exact-transformed-box/1',
                collision_checked=False, access_qualified=False)


def _inertia(value):
    J = _array(value, (3, 3), 'local CG inertia tensor')
    if not np.allclose(J, J.T, atol=1e-9, rtol=0): raise ValueError('Symmetric inertia tensor required')
    eigen = np.linalg.eigvalsh(J)
    if eigen[0] < -1e-9 or eigen[-1] > eigen[0] + eigen[1] + 1e-8:
        raise ValueError('Physically realizable inertia tensor required')
    return J


def _admit(record, base, bundle, root, allow_synthetic):
    r = deepcopy(record)
    if r.get('schema') != SCHEMA or r.get('record_id') != identity({k:v for k,v in r.items() if k != 'record_id'}):
        raise ValueError('Assembly record schema/identity differs')
    for key, expected in (('parent_bundle_id', bundle['bundle_id']), ('body_candidate_id', bundle['body_candidate_id'])):
        if r.get(key) != expected: raise ValueError('Assembly uses another parent bundle/body')
    if any(r.get(k, False) is not False for k in FLAGS):
        raise ValueError('Assembly imports cannot assert qualification or adoption')
    occurrence = r.get('component_occurrence_id')
    if occurrence not in base or r.get('parent_component_definition_id') != base[occurrence]['component_definition_id']:
        raise ValueError('Assembly uses another component definition')
    if base[occurrence]['scope'] == 'located-nominal-gross-body-stock':
        raise ValueError('Located body stock cannot also be imported as equipment')
    kind = r.get('evidence_kind')
    if kind == 'synthetic-method-test':
        if not allow_synthetic: raise ValueError('Synthetic records require explicit method-test opt-in')
    elif kind not in ('supplier-catalogue', 'dimensioned-design', 'measured-installed-assembly'):
        raise ValueError('Typed assembly evidence required')
    if not isinstance(r.get('source_locator'), str) or not r['source_locator']:
        raise ValueError('Traceable assembly source locator required')
    qualification = r.get('qualification_record_reference')
    if kind == 'measured-installed-assembly' and (not isinstance(r.get('serial_number'),str) or not r['serial_number'] or not isinstance(r.get('measurement_date'),str) or not r['measurement_date'] or qualification is None):
        raise ValueError('Measured assembly requires serial/date and qualification record reference')
    if r.get('assembly_mass_includes_hardware_and_services') is not True:
        raise ValueError('Explicit inclusive assembly mass basis required')
    references = [_source(root, v) for v in r.get('source_files', [])]
    if not references: raise ValueError('Actual source bytes required')
    if qualification is not None: references.append(_source(root,qualification))
    definition = r.get('physical_definition')
    if not isinstance(definition, dict) or set(definition) != {'local_frame','native_geometry', 'occupied_bounds_m', 'hardware', 'services'}:
        raise ValueError('Explicit installed assembly definition required')
    if definition['local_frame'] != dict(id='assembly',unit='m',axes='right-handed orthonormal',origin_m=[0.,0.,0.]):
        raise ValueError('Explicit assembly-local SI coordinate frame required')
    references.append(_source(root, definition['native_geometry']))
    lo, hi = _box(definition['occupied_bounds_m'])
    R, t = transform(r['installed_transform'])
    mass = _number(r['nominal_mass_kg'], 'nominal assembly mass', positive=True)
    interval = _array(r['mass_interval_kg'], (2,), 'mass interval')
    if not 0 < interval[0] <= mass <= interval[1]: raise ValueError('Bounded positive assembly mass required')
    cg = _array(r['local_CG_m'], (3,), 'local CG')
    if np.any(cg < lo) or np.any(cg > hi): raise ValueError('Local CG lies outside the occupied envelope')
    J = _inertia(r['local_CG_inertia_kg_m2'])
    # A positive semidefinite tensor can still be impossible for this envelope.
    # The coordinate variance is bounded by (upper-CG)*(CG-lower),
    # including the zero-variance condition when CG lies on an envelope face.
    covariance = np.trace(J) / 2 * np.eye(3) - J
    variance_bound = mass * (hi - cg) * (cg - lo)
    if np.any(np.diag(covariance) > variance_bound + 1e-8):
        raise ValueError('Assembly inertia exceeds its declared occupied envelope')
    if not isinstance(definition['hardware'],list) or not isinstance(definition['services'],list):
        raise ValueError('Explicit subordinate hardware and service occurrence lists required')
    hardware, ids = {}, set()
    for item in definition['hardware'] + definition['services']:
        if not isinstance(item, dict) or not isinstance(item.get('occurrence_id'), str) or not item['occurrence_id'] or item['occurrence_id'] in ids:
            raise ValueError('Unique subordinate physical occurrence IDs required')
        ids.add(item['occurrence_id'])
        if item.get('kind') not in HARDWARE_KINDS or type(item.get('quantity')) is not int or item['quantity'] <= 0:
            raise ValueError('Explicit hardware/service kind and count required')
        hardware[item['kind']] = hardware.get(item['kind'], 0) + item['quantity']
        _number(item.get('included_mass_kg'), 'included subordinate mass', positive=True)
        positions = _array(item.get('positions_local_m'), (item['quantity'],3), 'subordinate local positions')
        if np.any(positions < lo) or np.any(positions > hi):
            raise ValueError('Subordinate positions outside declared assembly envelope')
        if item['kind'] in ('wire','hose','duct','cooling'):
            if not isinstance(item.get('flexibility'), dict) or set(item['flexibility']) != {'minimum_bend_radius_m','provided_slack_m','duty_evidence'}:
                raise ValueError('Service motion/slack/bending evidence required')
            _number(item['flexibility']['minimum_bend_radius_m'], 'bend radius', positive=True)
            _number(item['flexibility']['provided_slack_m'], 'provided slack')
            references.append(_source(root,item['flexibility']['duty_evidence']))
    if sum(i['included_mass_kg'] for i in definition['hardware'] + definition['services']) > mass + 1e-9:
        raise ValueError('Included subordinate mass exceeds assembly total; do not double count')
    access = r['access']
    if set(access) != {'installation_path','removal_path','tool_envelopes','lifting','sequence'}:
        raise ValueError('Installation/removal, tool and lifting access required')
    for name in ('installation_path','removal_path'):
        if not isinstance(access[name], list) or not access[name] or access[name][0 if name == 'removal_path' else -1] != r['installed_transform']:
            raise ValueError('Access path must connect the installed pose')
    sweeps = {name:swept_envelope(definition['occupied_bounds_m'],access[name]) for name in ('installation_path','removal_path')}
    if not isinstance(access['tool_envelopes'],list):
        raise ValueError('Explicit tool envelope list required')
    for envelope in access['tool_envelopes']:
        if not isinstance(envelope,dict) or set(envelope) != {'frame_id','bounds_m'} or envelope['frame_id'] != 'vehicle':
            raise ValueError('Tool access must declare its vehicle coordinate frame')
        _box(envelope['bounds_m'])
    if not access['tool_envelopes'] or not isinstance(access['sequence'],list) or not access['sequence'] or any(not isinstance(s,str) or not s for s in access['sequence']):
        raise ValueError('Explicit tool envelope and assembly/repair sequence required')
    lifting = access['lifting']
    if not isinstance(lifting,dict) or set(lifting) != {'rated_capacity_kg','source','lifting_points_local_m'}:
        raise ValueError('Counted lifting capacity and source required')
    points = np.asarray(lifting['lifting_points_local_m'],dtype=object)
    if points.ndim != 2 or points.shape[0] < 1 or points.shape[1] != 3:
        raise ValueError('Explicit lifting point locations required')
    points = _array(lifting['lifting_points_local_m'],points.shape,'lifting points')
    if np.any(points < lo) or np.any(points > hi): raise ValueError('Lifting points outside assembly envelope')
    if _number(lifting['rated_capacity_kg'],'lifting capacity',positive=True) < interval[1]:
        raise ValueError('Lifting capacity does not cover declared upper mass')
    references.append(_source(root,lifting['source']))
    physical_id = identity(definition)
    return dict(component_occurrence_id=occurrence, parent_component_definition_id=r['parent_component_definition_id'],
        installed_component_definition_id=physical_id, physical_definition=definition, record_id=r['record_id'], evidence_kind=kind,
        nominal_mass_kg=mass, mass_interval_kg=interval.tolist(), vehicle_CG_m=(R @ cg + t).tolist(),
        vehicle_CG_inertia_kg_m2=(R @ J @ R.T).tolist(), installed_transform=r['installed_transform'],
        subordinate_occurrence_ids=sorted(ids), hardware_counts=hardware, access_sweeps=sweeps,
        access=deepcopy(access), input_record=deepcopy(r),
        source_files=references, qualification_record_reference=qualification,
        qualification_workflow='engineering/ferrite_maglev/qualification.py',
        qualification_routing_status='Current wheel/assembly subject adapter and authenticated limits/review required; no retained qualification inherited',
        lifting_point_count=len(points), lifting_capacity_necessary_bound='pass',
        lifting_load_sharing_and_retention_qualified=False,
        declaration_integrity_verified=True, source_authentication_verified=False,
        native_geometry_verified=False, access_qualified=False, synthetic=kind=='synthetic-method-test')


def _aggregate(rows):
    total=sum(r['mass_kg'] for r in rows)
    cg=sum(r['mass_kg']*np.asarray(r['CG_m']) for r in rows)/total
    tensor=np.zeros((3,3))
    for r in rows:
        d=np.asarray(r['CG_m'])-cg
        tensor+=np.asarray(r['CG_inertia_kg_m2'])+r['mass_kg']*((d@d)*np.eye(3)-np.outer(d,d))
    return dict(mass_kg=total,CG_m=cg.tolist(),CG_inertia_kg_m2=tensor.tolist())


def evaluate(bundle, body, *, assembly_records=(), source_root=ROOT, allow_synthetic=False):
    railway_bundle.validate(bundle);grammar.validate(body)
    if not allow_synthetic and (not (Path(source_root)/PRODUCER).is_file() or digest(Path(source_root)/PRODUCER) != digest(__file__)):
        raise ValueError('Executing equipped-assembly producer differs from source root')
    if bundle['body_candidate_id'] != body['candidate_id'] or bundle['body_definition_id'] != body['definition_id']:
        raise ValueError('Equipped projection uses another body definition')
    inventory=system_inventory.evaluate(body,bundle_id=bundle['bundle_id'],source_root=source_root,
        component_substitutions=bundle['component_substitutions'],extra_equipment_tasks=bundle['unweighed_architecture_equipment'])
    base={r['id']:r for r in inventory['engineering_BOM']}; imported=[];covered=set();subordinate=set()
    for record in assembly_records:
        row=_admit(record,base,bundle,source_root,allow_synthetic)
        if row['component_occurrence_id'] in covered or subordinate.intersection(row['subordinate_occurrence_ids']):
            raise ValueError('Physical assembly scope counted more than once')
        if set(row['subordinate_occurrence_ids']).intersection(base):
            raise ValueError('Subordinate stock overlaps an existing canonical occurrence')
        covered.add(row['component_occurrence_id']);subordinate.update(row['subordinate_occurrence_ids']);imported.append(row)
    geo=inventory['known_gross_stock_mass_properties']
    located=[dict(mass_kg=geo['known_gross_stock_mass_kg'],CG_m=geo['known_gross_stock_CG_m'],CG_inertia_kg_m2=geo['known_gross_stock_inertia_kg_m2'])]
    located += [dict(mass_kg=r['nominal_mass_kg'],CG_m=r['vehicle_CG_m'],CG_inertia_kg_m2=r['vehicle_CG_inertia_kg_m2']) for r in imported]
    unresolved=[r['id'] for r in inventory['engineering_BOM'] if r['scope']!='located-nominal-gross-body-stock' and r['id'] not in covered]
    evidence_sources={}
    for row in imported:
        for reference in row['source_files']:
            _source(source_root, reference)
            if reference['path'] in evidence_sources and evidence_sources[reference['path']] != reference['sha256']:
                raise ValueError('Mixed assembly source revisions')
            evidence_sources[reference['path']]=reference['sha256']
    proposal_bom=[deepcopy(r) for r in inventory['engineering_BOM'] if r['id'] not in covered]
    for row in imported:
        proposal_bom.append(dict(id=row['component_occurrence_id'],scope='installed-assembly-proposal',
            parent_component_definition_id=row['parent_component_definition_id'],component_definition_id=row['installed_component_definition_id'],
            nominal_mass_kg=row['nominal_mass_kg'],mass_interval_kg=row['mass_interval_kg'],
            vehicle_CG_m=row['vehicle_CG_m'],vehicle_CG_inertia_kg_m2=row['vehicle_CG_inertia_kg_m2'],
            physical_definition=row['physical_definition'],record_id=row['record_id'],physical_revision_required=True,geometry_verified=False))
    unlocated_mass=sum(r['accounted_mass_kg'] for r in inventory['engineering_BOM'] if r['id'] not in covered and r['scope']=='retained-unlocated-reference-account' and r['accounted_mass_kg'] is not None)
    located_projection=_aggregate(located)
    subtotal=located_projection['mass_kg']+unlocated_mass
    physical=dict(parent_bundle_id=bundle['bundle_id'],body_candidate_id=body['candidate_id'],
        installation_occurrences=[{k:r[k] for k in ('component_occurrence_id','installed_component_definition_id','installed_transform')} for r in imported])
    result=dict(schema='osr-equipped-candidate-projection/1',parent_bundle_id=bundle['bundle_id'],body_candidate_id=body['candidate_id'],
        body_definition_id=body['definition_id'],proposed_assembly_candidate_id=identity(physical),
        canonical_bundle_propagation_required=bool(imported),physical_revision_required=bool(imported),
        declared_accommodation=dict(cars=6,car_length_m=17.,fixed_seats_per_car=44,wheelchair_places_per_car=2,normal_people_per_car=46,crowd_control_people_per_car=160),
        parent_engineering_BOM=inventory['engineering_BOM'],engineering_BOM=proposal_bom,manufacturing_BOM=inventory['manufacturing_BOM'],
        manufacturing_BOM_scope='Parent body gross-stock groups only; imported assemblies and full installed routing remain ungenerated',
        complete_installed_manufacturing_BOM=None,assembly_dependencies=deepcopy(body['assembly']),
        imported_assembly_records=imported,located_nominal_projection=located_projection,
        known_accounted_design_mass_subtotal_kg_per_car=subtotal,
        loading_account_basis='75 kg/person arithmetic sensitivity inherited from the canonical railway bundle; no complete tare, baggage or installed uncertainty claim',
        loading_accounts={name:dict(people_per_car=n,known_accounted_mass_subtotal_kg_per_car=subtotal+n*75.,
            known_accounted_mass_subtotal_kg_six_cars=6*(subtotal+n*75.),complete_installed_mass_kg_per_car=None)
            for name,n in [('empty',0),('normal',46),('crowd-control',160)]},
        remaining_unlocated_account_mass_kg=unlocated_mass,
        unresolved_component_occurrence_ids=unresolved,required_scope_closure=list(REQUIRED_CLOSURE),
        hardware_counts={k:sum(r['hardware_counts'].get(k,0) for r in imported) for k in HARDWARE_KINDS},
        hardware_count_scope='Observed imported subordinate counts only; zero means no counted import of this kind, not absent installed hardware',
        declared_body_joint_count=len(body['joins']),declared_body_joint_ids=[j['id'] for j in body['joins']],
        located_body_stock_occurrence_count=len(body['parts']),
        total_installed_hardware_counts={k:None for k in HARDWARE_KINDS},
        coordinate_frames={'vehicle':dict(unit='m',origin_m=[0.,0.,0.],axes='x longitudinal/y left/z up')},
        structural_status=dict(family=body['parameters']['family'],model=body.get('full_body_evaluator','Declared intact linear metallic shell/frame research hypothesis'),
            qualified=False,required=['Directional hot/wet material laws where applicable','Joint local strength/slip/fatigue and buckling','Normal/crowd/accidental cases and actual bogie/brake load paths']),
        component_tasks=inventory['component_tasks'],source_sha256={**inventory['source_sha256'],**evidence_sources,PRODUCER:digest(__file__)},
        method_test_only=bool(allow_synthetic),
        complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,
        physical_journey_mass_admitted=False,source_authentication_verified=False,
        scope='Disjoint gross stock and declared installation proposals only; unknown joint cuts/hardware/equipment and approval prevent installed completeness',**FLAGS)
    result['evaluation_id']=identity(result);return result


def comparison(root=ROOT):
    parents=grammar.initial_candidates()
    bodies=[system_body.build(parents[0],topology='aluminium_frame',root=root),
            system_body.build(parents[2],topology='aluminium_stressed_skin',root=root),parents[1]]
    rows=[]
    for body in bodies:
        bundle=railway_bundle.materialize(body,family='P1',root=root)
        rows.append(dict(body=body,bundle=bundle,projection=evaluate(bundle,body,source_root=root)))
    if len({r['body']['candidate_id'] for r in rows}) != 3: raise ValueError('Three distinct physical body definitions required')
    result=dict(schema='osr-three-equipped-research-candidates/1',candidates=rows,
        complete_equipped_candidates=0,integrated_winner=None,selected_reference_changed=False,**FLAGS)
    result['evaluation_id']=identity(result);return result
