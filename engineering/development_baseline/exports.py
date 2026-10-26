"""Compile the selected development design into consistent delivery records.

These are research and request-for-quotation records. Unknown installed stock,
prices, production times and acceptance limits remain explicit unknowns.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import math
import tarfile
import tempfile
import uuid

from engineering.comfort_design import native_vehicle
from . import ROOT, FLAGS
from . import evaluate

SCHEMA = 'osr-current-development-exports/1'


def _bound(record):
    return {k: record[k] for k in ('selection_id', 'candidate_id', 'body_candidate_id', 'magnet_component_id')}


def compile(record, *, root=ROOT, city_index=None):
    """Return one candidate-bound package; no legacy component is a fallback."""
    evaluate.validate(record, root)
    producer = 'engineering/development_baseline/exports.py'
    producer_bytes = Path(__file__).read_bytes()
    if (Path(root) / producer).is_symlink() or (Path(root) / producer).read_bytes() != producer_bytes:
        raise ValueError('executed export producer differs from source root')
    car, service, interfaces = record['vehicle'], record['service'], record['interfaces']
    station, civil = service['selected_station'], interfaces['civil']
    common = dict(schema=SCHEMA, **_bound(record), evaluation_id=record['evaluation_id'],
        service_evaluation_id=service['evaluation_id'], station_id=station['station_id'],
        civil_interface_id=civil['civil_interface_id'], development_default=True, **FLAGS)
    city_scope = dict(city_count=None, city_index_id=None,
        scope='Core vehicle and explicitly selected Baghdad network; all-city quantities require the current city index',
        whole_repository_city_delivery_complete=False)
    if city_index is not None:
        for key in ('selection_id', 'candidate_id', 'body_candidate_id', 'magnet_component_id'):
            if city_index.get(key) != record[key]:
                raise ValueError('city index belongs to another selected candidate: ' + key)
        city_scope.update(city_count=city_index.get('city_count'),
            city_index_id=city_index.get('index_id', city_index.get('evaluation_id')),
            scope='Current candidate-bound city index; city-specific holds remain in each package')
    bom = dict(**common, inventory_per_car=deepcopy(car['inventory']),
        missing_inventory=deepcopy(car['missing_inventory']), mass=deepcopy(car['mass']),
        located_material_properties=deepcopy(car['located_material_properties']),
        cars_per_trainset=6, inventory_is_complete=False, installed_cost_USD=None,
        unit_cost_coverage_fraction=None, unknown_mass_is_zero=False,
        note='Accounted allocations and material subtotals retain their original roles; no complete installed mass, CG or inertia is claimed.')
    manufacturing = dict(**common, assembly_sequence=deepcopy(interfaces['assembly_and_construction_plan']),
        material_geometry_part_count=len(car['geometry_parts']),
        component_definitions=deepcopy(car['components']),
        supplier_evidence_required=deepcopy(interfaces['procurement_and_economics']['supplier_evidence_required']),
        production_labour_hours_per_car=None, production_tooling_cost_USD=None,
        actual_supplier_process_routes=None, factory_capacity_cars_per_year=None,
        physical_serials_or_lots=[], quality_state='design-proposal-awaiting-prototype-and-independent-inspection')
    procurement = dict(**common, stock_inventory_per_car=deepcopy(car['inventory']),
        civil_stock_per_declared_span=deepcopy(civil['stock']),
        station_requirements=deepcopy(interfaces['station']),
        required_supplier_evidence=deepcopy(interfaces['procurement_and_economics']['supplier_evidence_required']),
        baghdad_network_proposal_id=service['fleet']['network_proposal_id'],
        baghdad_trainsets_analytical=service['fleet']['proposed_total_trainsets'],
        baghdad_directional_winding_m=service['fleet']['total_direction_winding_m'],
        city_scope=city_scope, quotes=[], purchase_orders=[], origin_evidence_complete=False,
        complete_material_availability_dates=None, procurement_lead_days=None,
        first_consumption_release='hold-until-selected-material-is-available-and-inspected',
        total_price_USD=None, unpriced_stock_is_zero=False)
    assembly = dict(**common, sequence=deepcopy(interfaces['assembly_and_construction_plan']),
        design_interfaces=deepcopy(interfaces['design_interfaces']),
        actual_insertion_paths_and_tool_access_qualified=False,
        scheduled_start_dates=None, construction_crew_and_lift_schedule=None,
        material_consumption_dependencies_qualified=False,
        resource_and_material_release='Hold: assign actual stock, procurement availability, crews, lifting plans and inspection releases before scheduling physical work')
    controls = dict(**common, cars=6, normal_passengers_per_car=46,
        fixed_seats_per_car=44, wheelchair_places_per_car=2, standing_passengers_per_car=0,
        target_headway_s=120., normal_capacity_pphpd=8280., launch_speed_cap_m_s=20.,
        dwell_s=35., station_spacing_prototype_m=2000., shared_station_winding_m=station['length_m'],
        electrical_section_m=station['electrical_section_m'],
        addressed_sections_per_direction=station['sections_per_direction'],
        addressed_sections_both_directions=station['sections_per_direction'] * station['directions'],
        minimum_concurrent_train_phase_current_branches_per_direction=station['minimum_concurrent_train_phase_current_branches_per_direction'],
        minimum_concurrent_train_phase_current_branches_both_directions=
            station['directions'] * station['minimum_concurrent_train_phase_current_branches_per_direction'],
        station_resource_architecture=station['power_resource_architecture'],
        physical_switchgear_count=None, physical_converter_rating=None,
        magnetic_modules_per_car=len(car['interfaces']['magnetic_mounts']),
        magnetic_operating_gap_m=None, permitted_physical_gap_range_m=None,
        coupon_drawing_reference_gap_m=civil['module_nominal_drawing_gap_m'],
        coupon_gap_is_selected_operating_gap=False,
        native_protocol_fixture_gap_um=[6000, 8000], fixture_gap_is_physical_evidence=False,
        force_maps_for_selected_installed_geometry=None, stable_hover_verified=False,
        actual_safe_headway_s=None, configuration_delivery_state='research-configuration-hold',
        gates=deepcopy(record['gates']))
    return dict(schema=SCHEMA, **_bound(record), evaluation_id=record['evaluation_id'],
        bom=bom, manufacturing=manufacturing, procurement=procurement, assembly=assembly,
        civil=dict(**common, proposal=deepcopy(civil),
            station_winding_library_m=deepcopy(service['assumptions']['station_winding_library_m']),
            selected_station_requirements=deepcopy(interfaces['station']),
            baghdad_network=deepcopy(record['network_proposal']),
            current_city_scope=deepcopy(city_scope),
            fully_installed_route_quantities=None, installed_price_per_direction_km_USD=None),
        controls=controls,
        source_sha256=evaluate._merge(record['source_sha256'], {
            producer: sha256(producer_bytes).hexdigest()}),
        **FLAGS)


def _verify_cad_archive(record, root):
    """Verify the retained portable packet without depending on a build folder."""
    root = Path(root).resolve()
    manifest_path = record['selection']['source_manifest']
    manifest_bytes = (root / manifest_path).read_bytes()
    if sha256(manifest_bytes).hexdigest() != record['selection']['source_manifest_sha256']:
        raise ValueError('selected source CAD publication manifest differs')
    manifest = json.loads(manifest_bytes)
    relative = (Path(manifest_path).parent / 'vehicle-artifacts.tar.gz').as_posix()
    archive = root / relative
    digest = sha256(archive.read_bytes()).hexdigest()
    if digest != manifest['files_sha256']['vehicle-artifacts.tar.gz']:
        raise ValueError('selected source CAD archive differs')
    with tempfile.TemporaryDirectory(prefix='osr-current-cad-') as tmp:
        directory = Path(tmp)
        size = 0
        names = set()
        with tarfile.open(archive, 'r:gz') as package:
            for member in package:
                name = Path(member.name)
                if (not member.isfile() or len(name.parts) != 2 or name.parts[0] != 'vehicle'
                    or name.name in names or name.name in ('.', '..') or name.is_absolute()):
                    raise ValueError('ordinary unique vehicle CAD archive members required')
                names.add(name.name)
                size += member.size
                if size > native_vehicle.MAX_BYTES:
                    raise ValueError('retained native CAD package exceeds its byte budget')
                stream = package.extractfile(member)
                (directory / name.name).write_bytes(stream.read())
        checked = native_vehicle.verify_export(directory, record['vehicle'], root=root)
        request = json.loads((directory / 'request.json').read_bytes())
        for key in ('candidate_id', 'body_candidate_id', 'magnet_component_id'):
            if request.get(key) != record[key]:
                raise ValueError('portable native CAD identity differs: ' + key)
        files = {name: sha256((directory / name).read_bytes()).hexdigest()
            for name in ('request.json', 'manifest.json', 'geometry.json.gz', 'native-result.json', 'model.FCStd', 'model.step.gz')}
    return dict(source_archive=relative, source_archive_sha256=digest,
        geometry_sha256=request['geometry_sha256'], files_sha256=files, verification=checked)


def _native_cad(record, output, root, folder):
    """Reuse physical geometry only after the existing native verifier matches it."""
    if folder is None:
        return dict(**_bound(record), execution='not-run', native_reopen_established=False,
            reason='No exact candidate-bound native CAD package supplied', **FLAGS)
    folder = Path(folder)
    checked = native_vehicle.verify_export(folder, record['vehicle'], root=root)
    request = json.loads((folder / 'request.json').read_bytes())
    for key in ('candidate_id', 'body_candidate_id', 'magnet_component_id'):
        if request.get(key) != record[key]:
            raise ValueError('native CAD identity differs: ' + key)
    # Match the private input to the immutable public packet. The current
    # receipt points to that portable packet, never to the private build path.
    files = {name: sha256((folder / name).read_bytes()).hexdigest()
        for name in ('request.json', 'manifest.json', 'geometry.json.gz', 'native-result.json', 'model.FCStd', 'model.step.gz')}
    portable = _verify_cad_archive(record, root)
    if files != portable['files_sha256'] or request['geometry_sha256'] != portable['geometry_sha256']:
        raise ValueError('private CAD package differs from its selected published archive')
    return dict(**_bound(record), execution='completed' if checked['native_reopen_established'] else checked['execution_status'],
        native_reopen_established=checked['native_reopen_established'],
        **portable,
        scope='Exact unchanged physical-car material geometry and native reopen receipt; new service selection is bound by this reference, not retroactively written into the historical package', **FLAGS)


def _bim_parts(record):
    """Explicit selected civil primitives and labelled equipment contexts only."""
    civil = record['interfaces']['civil']
    span, w, h = civil['span_m'], civil['reference_concrete_outer_width_m'], civil['reference_concrete_depth_m']
    parts = [dict(id='selected-civil/concrete-prismatic-shell', material='concrete',
        at_m=[-span / 2, -w / 2, civil['reference_concrete_top_z_m'] - h],
        size_m=[span, w, h], void_m=[span, w - .2, h - .3],
        expected_volume_m3=civil['reference_prismatic_concrete_volume_m3'],
        role='Counted prismatic shell only; rebar, prestress, end blocks, bearings and anchors are unresolved')]
    for index, y in enumerate(civil['rail_centres_y_m']):
        parts.append(dict(id='selected-civil/working-facing/' + str(index), material='steel',
            at_m=[-span / 2, y - civil['facing_width_m'] / 2, civil['rail_bottom_z_m']],
            size_m=[span, civil['facing_width_m'], civil['facing_thickness_m']],
            expected_volume_m3=span * civil['facing_width_m'] * civil['facing_thickness_m'],
            role='Selected35mm downward-facing passive steel; support stock is counted separately, not exported here'))
    for index, box in enumerate(record['vehicle']['interfaces']['HVAC_packages']):
        size = box['size_m']
        parts.append(dict(id='selected-car/HVAC-envelope/' + str(index), material='equipment-context',
            at_m=[x - s / 2 for x, s in zip(box['centre_m'], size)], size_m=size,
            expected_volume_m3=math.prod(size), role='Supplier installation envelope; not material, mass or a complete native car'))
    return parts


def _write_bim(output, record):
    try:
        import ifcopenshell
        import ifcopenshell.api
        import ifcopenshell.geom
        import ifcopenshell.util.element
        import ifcopenshell.util.shape
    except ImportError as error:
        return dict(**_bound(record), execution='not-run', reason=str(error), **FLAGS)
    parts = _bim_parts(record)
    f = ifcopenshell.api.run('project.create_file', version='IFC4X3')
    project = ifcopenshell.api.run('root.create_entity', f, ifc_class='IfcProject', name='Selected OpenSourceRail development interface')
    ifcopenshell.api.run('unit.assign_unit', f, length={'is_metric': True, 'raw': 'METERS'})
    context = ifcopenshell.api.run('context.add_context', f, context_type='Model')
    body = ifcopenshell.api.run('context.add_context', f, context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=context)
    site = ifcopenshell.api.run('root.create_entity', f, ifc_class='IfcSite', name='Unsited development prototype; not a surveyed route')
    ifcopenshell.api.run('aggregate.assign_object', f, products=[site], relating_object=project)
    def point(v): return f.createIfcCartesianPoint(tuple(float(x) for x in v))
    def axis(v): return f.createIfcAxis2Placement3D(point(v), None, None)
    def box(size, at):
        profile = f.createIfcRectangleProfileDef('AREA', None, None, float(size[0]), float(size[1]))
        return f.createIfcExtrudedAreaSolid(profile, axis([at[0] + size[0] / 2, at[1] + size[1] / 2, at[2]]),
            f.createIfcDirection((0., 0., 1.)), float(size[2]))
    rows = []
    for part in parts:
        obj = ifcopenshell.api.run('root.create_entity', f, ifc_class='IfcBuildingElementProxy', name=part['id'])
        obj.GlobalId = ifcopenshell.guid.compress(uuid.UUID(evaluate.identity([record['selection_id'], part['id']])[:32]).hex)
        solid = box(part['size_m'], part['at_m'])
        if 'void_m' in part:
            at = [x + (outer - inner) / 2 for x, outer, inner in zip(part['at_m'], part['size_m'], part['void_m'])]
            solid = f.createIfcBooleanResult('DIFFERENCE', solid, box(part['void_m'], at))
        representation = f.createIfcShapeRepresentation(body, 'Body', 'CSG' if 'void_m' in part else 'SweptSolid', [solid])
        ifcopenshell.api.run('geometry.assign_representation', f, product=obj, representation=representation)
        ifcopenshell.api.run('geometry.edit_object_placement', f, product=obj)
        ifcopenshell.api.run('spatial.assign_container', f, products=[obj], relating_structure=site)
        pset = ifcopenshell.api.run('pset.add_pset', f, product=obj, name='OSR_SelectedDevelopment')
        props = dict(_bound(record), civil_interface_id=record['interfaces']['civil']['civil_interface_id'],
            part_id=part['id'], role=part['role'], physical_accepted=False)
        ifcopenshell.api.run('pset.edit_pset', f, pset=pset, properties=props)
        rows.append(dict(part_id=part['id'], ifc_guid=obj.GlobalId, expected_volume_m3=part['expected_volume_m3'], role=part['role']))
    target = Path(output) / 'selected-interface.ifc'
    f.write(str(target))
    reopened = ifcopenshell.open(str(target))
    settings = ifcopenshell.geom.settings()
    for row in rows:
        obj = reopened.by_guid(row['ifc_guid'])
        props = ifcopenshell.util.element.get_psets(obj)['OSR_SelectedDevelopment']
        if any(props.get(k) != v for k, v in _bound(record).items()):
            raise ValueError('reopened IFC belongs to another selected candidate')
        shape = ifcopenshell.geom.create_shape(settings, obj)
        volume = abs(ifcopenshell.util.shape.get_volume(shape.geometry))
        if not math.isclose(volume, row['expected_volume_m3'], rel_tol=1e-6, abs_tol=1e-8):
            raise ValueError('selected IFC primitive volume differs: ' + row['part_id'])
        row['reopened_volume_m3'] = volume
    return dict(**_bound(record), execution='completed', ifc_schema=reopened.schema_identifier,
        native_reopened=True, identity_and_volume_checks_pass=True, parts=rows,
        complete_vehicle_IFC=False, complete_civil_BIM=False, complete_installed_mass_established=False,
        scope='Selected civil shell/two steel facings and five labelled vehicle HVAC contexts; exact full material-car CAD remains in the separately verified native package. No old default beam is imported.', **FLAGS)


def write(output, record, *, root=ROOT, city_index=None, native_vehicle_folder=None):
    output = Path(output).resolve()
    package = compile(record, root=root, city_index=city_index)
    output.mkdir(parents=True, exist_ok=False)
    for name in ('manufacturing', 'procurement', 'assembly', 'civil', 'controls'):
        (output / (name + '.json')).write_bytes(evaluate.encoded(package[name]))
    (output / 'engineering-bom.json.gz').write_bytes(gzip.compress(evaluate.encoded(package['bom']), mtime=0))
    cad = _native_cad(record, output, root, native_vehicle_folder)
    (output / 'cad.json').write_bytes(evaluate.encoded(cad))
    bim = _write_bim(output, record)
    (output / 'bim.json').write_bytes(evaluate.encoded(bim))
    files = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}
    result = dict(schema=SCHEMA, **_bound(record), current_evaluation_id=record['evaluation_id'],
        source_sha256=package['source_sha256'], files_sha256=files,
        cad_execution=cad['execution'], bim_execution=bim['execution'], **FLAGS)
    result['export_id'] = evaluate.identity(result)
    (output / 'manifest.json').write_bytes(evaluate.encoded(result))
    verify(output, record, root=root, city_index=city_index)
    return result


def verify(output, record, *, root=ROOT, city_index=None):
    output = Path(output)
    package = compile(record, root=root, city_index=city_index)
    m = json.loads((output / 'manifest.json').read_bytes())
    if m['export_id'] != evaluate.identity({k: v for k, v in m.items() if k != 'export_id'}):
        raise ValueError('current export manifest identity differs')
    if any(m.get(k) != v for k, v in _bound(record).items()) or m['current_evaluation_id'] != record['evaluation_id']:
        raise ValueError('current export belongs to another candidate or selection')
    if m['source_sha256'] != package['source_sha256']:
        raise ValueError('current export producer sources differ')
    actual = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file() and p.name != 'manifest.json'}
    if actual != m['files_sha256']:
        raise ValueError('current export payload differs')
    for name in ('manufacturing', 'procurement', 'assembly', 'civil', 'controls'):
        if json.loads((output / (name + '.json')).read_bytes()) != package[name]:
            raise ValueError('current export content differs: ' + name)
    if json.loads(gzip.decompress((output / 'engineering-bom.json.gz').read_bytes())) != package['bom']:
        raise ValueError('current export BOM differs')
    for name in ('cad', 'bim'):
        data = json.loads((output / (name + '.json')).read_bytes())
        if any(data.get(k) != v for k, v in _bound(record).items()) or any(data.get(k) is not v for k, v in FLAGS.items()):
            raise ValueError('current native export identity or acceptance differs')
    cad = json.loads((output / 'cad.json').read_bytes())
    if cad['execution'] == 'completed':
        portable = _verify_cad_archive(record, root)
        if any(cad.get(k) != v for k, v in portable.items()):
            raise ValueError('current CAD reference differs from its selected portable archive')
    return dict(current=True, export_id=m['export_id'], selection_id=record['selection_id'],
        cad_execution=m['cad_execution'], bim_execution=m['bim_execution'], **FLAGS)
