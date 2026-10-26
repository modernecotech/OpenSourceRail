"""Compile one matched comfort-vehicle, station and two-minute service dossier."""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tempfile

from . import ROOT, PARENT_REVISION, FLAGS
from . import vehicle, service, interfaces, native_vehicle, report_service
from .common import encoded, identity, require_candidate, sources, inventory, package, unpack

OUTPUT='docs/design-engine/ferrite-maglev/comfort-design'
WORKBENCH='docs/workbench/trip/readiness/comfort-design'


def _read(path):return json.loads(Path(path).read_bytes())


def _native(paths,car,operations,root):
    if not paths:return dict(execution='not-run',reason='Explicit native CAD and Rust method packages required',physical_train_simulated=False)
    checks=dict(vehicle=native_vehicle.verify_export(paths['vehicle'],car,root=root),
                service=service.verify_native(car,operations,paths['service'],root=root))
    if checks['vehicle'].get('native_reopen_established') is not True:
        raise ValueError('completed native CAD export/reopen required; retain failed job separately')
    records={}
    for label,directory in paths.items():
        m=_read(Path(directory)/'manifest.json')
        records[label]=dict(manifest=m,files_sha256=inventory(directory),verification=checks[label])
    return dict(execution='completed',packages=records,physical_train_simulated=False,
                scope='Native geometry/reopen and protection-protocol method evidence; no accepted multiaxis hover or physical journey')


def assemble(root=ROOT,native_paths=None):
    root=Path(root).resolve();car=vehicle.build(root=root)
    vehicle.validate(car,root=root)
    operations=service.evaluate(car,root=root);require_candidate(operations,car)
    domain=interfaces.evaluate(car,operations,root=root);require_candidate(domain,car)
    native=_native(native_paths,car,operations,root)
    evidence=[car,operations,domain]
    if native_paths:
        evidence.extend(p['manifest'] for p in native['packages'].values())
    system=dict(vehicle_candidate_id=car['candidate_id'],station_id=operations['selection']['selected_station_id'],
        civil_interface_id=domain['civil']['civil_interface_id'],target_headway_s=120.,
        prototype_station_spacing_m=operations['selected_scenario']['inputs']['distance_m'],
        brief_sha256=sha256((root/'engineering/comfort_design/brief.json').read_bytes()).hexdigest())
    v=dict(schema='osr-matched-comfort-design/1',parent_revision=PARENT_REVISION,
        brief=_read(root/'engineering/comfort_design/brief.json'),
        candidate_id=car['candidate_id'],body_candidate_id=car['body_candidate_id'],
        magnet_component_id=car['magnet_component_id'],vehicle=car,service=operations,
        system_physical_definition=system,system_candidate_id=identity(system),
        interfaces=domain,native_evidence=native,source_sha256=sources(root,evidence),
        design_basis_selected=True,design_basis_scope='User-authorised 44-seat plus two-wheelchair six-car proposal with a 120-second target; existing city plans remain historical comparison inputs',
        physical_journey_execution='not-run; matched support/control/braking/structure acceptance prerequisites remain open',
        complete_engineering_design=False,**FLAGS)
    v['study_id']=identity(v)
    return v


def summary(v):
    return dict(study_id=v['study_id'],candidate_id=v['candidate_id'],system_candidate_id=v['system_candidate_id'],body_candidate_id=v['body_candidate_id'],
        magnet_component_id=v['magnet_component_id'],mass=deepcopy(v['vehicle']['mass']),
        service=service.summary(v['service']),interfaces=interfaces.summary(v['interfaces']),
        native=dict(execution=v['native_evidence']['execution'],physical_train_simulated=False),
        gates=deepcopy(v['interfaces']['gates']),geometry=deepcopy(v['vehicle']['interfaces']),
        inventory_coverage=deepcopy(v['vehicle']['coverage']),
        target_headway_s=120,cars=6,fixed_seats_per_car=44,wheelchair_places_per_car=2,
        planned_standing_per_car=0,capacity_pphpd=8280,regular_service_average_wait_s=60,
        previous_comparison_pphpd=14400,complete_engineering_design=False,**FLAGS)


def readme(v):
    m=v['vehicle']['mass']
    lines=['# Matched comfort train and two-minute service design','',
        'OpenSourceRail develops simple, locally maintainable trains on concrete beams with passive steel facings. All permanent magnets and suspension controls remain onboard; finite station windings launch and receive the trains. This dossier composes one seating/body/equipment proposal with its station, civil, power and service interfaces.','',
        '[System ethos and current evidence](../../../../README.md) · [Earlier component investigation](../comfort-options/README.md) · [Interactive design](../../../workbench/trip/readiness/comfort-design/)','',
        '**Selected design basis:** six 17 m cars; each has 44 fixed seats, two wheelchair places and no planned standing. Two doors are on one side. The service target is 120 seconds: 276 people/train, 30 trains/hour and **8,280 passengers/hour/direction**, with a 60-second mean wait under regular unsaturated service. The former 14,400 benchmark remains a comparison, rather than being relabelled as achieved.','',
        f"The matched proposal accounts for **{m['accounted_tare_kg_per_car']/1000:.3f}t tare/car** and **{m['accounted_cap_loaded_kg_per_car']/1000:.3f}t at the 46-person cap**. Complete installed mass, full equipped CG/inertia and physical acceptance remain open. Counted material, supplier references and retained allocations are distinguished; an unlocated allocation is not turned into a uniform solid.",'',
        '## Vehicle design and assembly','',
        'The body uses an aluminium extrusion frame with retained GFRP side/end structure, the selected aluminium-skin floor, a revised sandwich roof on the retained ribs, explicitly fitted paired/single seats, deeper door panels and retained laminated-glass references. The original added-crossrail roof is preserved as a rejected interference control. Polycarbonate remains an alternative until stiffness, retention, optics and emergency release are established.','',
        'The component definitions, material quantities, occurrences, transforms, assembly dependencies, retained interfaces, missing equipment and installation clashes are in [the complete dossier](design.json.gz). Native CAD and portable geometry represent their declared material/reference scope; equipment envelopes are labelled and do not invent the mass distribution of unweighed assemblies.','',
        '[Engineering BOM and unresolved inventory](engineering-bom.json.gz) · [Assembly/construction plan](assembly-plan.json) · [Matched station and civil definitions](station-civil.json). These are candidate-bound research/manufacturing-planning inputs; fabrication release remains held.','',
        'The section drawing retains a 12 mm magnetic-coupon reference, not an accepted operating gap. That PM state produces strong excess upward force for this lighter vehicle. Samples at 28/35.338 mm require a different relative car/facing pose; an eventual operating gap also determines the boarding-height datum. The required equilibrium, current authority and installed multiaxis map must be solved before any drawing pose becomes an operating configuration.','',
        '## Two-minute service, station resources and fleet','',
        report_service.markdown(v['service']),'',
        '## Coupled electrical, support and civil design','',
        interfaces.markdown(v['interfaces']),'',
        '## Qualification and remaining work','',
        'A complete design dossier is not an accepted complete engineering design. The native geometry and protection-protocol executions below have their declared method scope. Static PM-force samples do not establish stable hover; virtual healthy-gap inputs do not establish the new magnetic controller; assumed braking floors do not establish emergency stopping hardware. A physical-force 2 km journey remains gated rather than animated with invented support.','',
        '1. Finish the joined-body, seat/door/roof interfaces and exact equipped mass/CG/inertia; correlate material/joint loads and modes.',
        '2. Converge the installed 3D PM/steel/current maps, guidance/damping and fault-control envelope for this body and new guideway facings.',
        '3. Qualify hot-weather HVAC, support cooling, essential battery, bus, charging and receiving/dump duty.',
        '4. Establish measured independent braking, capture, train integrity and receiving-power-loss behaviour at every coasting location.',
        '5. Confirm native station-group switching, worst-case dwell and protected 120-second operation, then feed supplier/site evidence into the selected guideway and cost model.','',
        'The lower passenger cap is a design/boarding-control requirement. The 160-person crowd/control and asymmetric load cases remain visible until revised structural loads and cap enforcement are qualified. Low-cost trainsets remain a cost objective; the dossier compares fleet and price sensitivity without assigning an unknown unit price zero.','',
        '## Reproduction','',
        '```bash',
        'python -m engineering.comfort_design verify',
        'python -m pytest --import-mode=importlib -q engineering/comfort_design/tests',
        '```','',
        '[Compact results](summary.json) · [Source/payload receipt](manifest.json) · [Native FreeCAD model](vehicle.FCStd) · [Compressed STEP](vehicle.step.gz) · [Vehicle overview](vehicle-overview.svg) · [Coasting profile](service-profile.svg) · [Matched train/guideway section](interface-section.svg) · [Native CAD evidence](vehicle-artifacts.tar.gz) · [Rust method evidence](service-artifacts.tar.gz)','',
        f"Candidate: `{v['candidate_id']}`. Study: `{v['study_id']}`. Parent: `{v['parent_revision']}`. Engineering, manufacturing, operating and physical release flags remain false.",'']
    text='\n'.join(lines)
    if v['native_evidence']['execution']=='completed':
        methods=v['native_evidence']['packages']
        cad=methods['vehicle']['verification'];control=methods['service']['verification']
        paragraph='\n'.join(['## Executed native evidence','',
            f"Actual FreeCAD and STEP export/reopen checks passed for **{cad['primitive_count']:,} material primitives**, representing **{cad['defined_material_mass_kg']:,.3f} kg of defined material**. This is a subset of the accounted tare, with its own material-only CG/inertia; complete installed mass and CG remain unknown. The revised roof has zero native intersection volume with the checked primary longitudinal members; a full-body interference or structural release is not claimed.",'',
            f"The current candidate-bound Rust package independently verifies **{control['controls']} executed controls**: nominal/journal 120-second departures and retained-authority receiving/brake/gap/integrity fault responses. Its healthy support and brake inputs remain explicit protocol fixtures. The native receipts, requests and logs are retained in the linked archives.",''])
        text=text.replace('## Qualification and remaining work',paragraph+'\n## Qualification and remaining work')
    return text


def _payloads(v,native_paths):
    files={'design.json.gz':gzip.compress(encoded(v),mtime=0),'summary.json':encoded(summary(v)),
           'README.md':readme(v).encode(),'interface-section.svg':interfaces.render_section_svg(v['interfaces']).encode(),
           'service-profile.svg':report_service.render_profile_svg(v['service']).encode()}
    subject={k:v[k] for k in ('candidate_id','body_candidate_id','magnet_component_id','system_candidate_id')}
    bom=dict(schema='osr-comfort-engineering-bom/1',**subject,
        mass=v['vehicle']['mass'],occurrences=v['vehicle']['inventory'],
        missing_inventory=v['vehicle']['missing_inventory'],coverage=v['vehicle']['coverage'],
        source_evaluation_id=v['vehicle']['evaluation_id'],**FLAGS)
    files['engineering-bom.json.gz']=gzip.compress(encoded(bom),mtime=0)
    files['assembly-plan.json']=encoded(dict(schema='osr-comfort-assembly-plan/1',**subject,
        vehicle_operations=v['vehicle']['assembly_plan'],
        system_operations=v['interfaces']['assembly_and_construction_plan'],
        material_supplier_and_release_requirements=v['interfaces']['procurement_and_economics'],**FLAGS))
    files['station-civil.json']=encoded(dict(schema='osr-comfort-station-civil/1',**subject,
        station_id=v['service']['selection']['selected_station_id'],
        station=v['service']['selected_station'],civil=v['interfaces']['civil'],
        power_and_electrical_requirements=v['interfaces']['station'],**FLAGS))
    for label,directory in native_paths.items():
        files[label+'-artifacts.tar.gz']=package(directory,label)
    # Direct access to actual export artifacts without requiring an archive reader.
    directory=Path(native_paths['vehicle'])
    for p in sorted(directory.rglob('*')):
        if p.is_file() and p.suffix=='.FCStd':files['vehicle.FCStd']=p.read_bytes()
        if p.is_file() and p.name.endswith(('.step.gz','.stp.gz')):files['vehicle.step.gz']=p.read_bytes()
        if p.is_file() and p.name in ('overview.svg','assembly.svg'):files['vehicle-overview.svg']=p.read_bytes()
    if not {'vehicle.FCStd','vehicle.step.gz','vehicle-overview.svg'}<=files.keys():
        raise ValueError('native model, STEP and overview required for a reviewable design')
    receipt=dict(schema='osr-matched-comfort-design-publication/1',study_id=v['study_id'],candidate_id=v['candidate_id'],
        source_sha256=v['source_sha256'],files_sha256={n:sha256(raw).hexdigest() for n,raw in files.items()},**FLAGS)
    receipt['manifest_id']=identity(receipt);files['manifest.json']=encoded(receipt)
    return files


def _ui(root,files):
    digest=sha256(files['summary.json']).hexdigest().encode()
    return {name:(Path(root)/'engineering/comfort_design/web'/name).read_bytes().replace(b'__SUMMARY_SHA256__',digest)
            for name in ('index.html','app.js','app.css')}


def publish(output=OUTPUT,*,root=ROOT,vehicle_native,service_native):
    root=Path(root).resolve();output=Path(output).resolve()
    if output.exists():raise ValueError('fresh publication output required; preserve previous runs')
    paths=dict(vehicle=Path(vehicle_native),service=Path(service_native));v=assemble(root,paths);files=_payloads(v,paths)
    output.mkdir(parents=True)
    for n,raw in files.items():(output/n).write_bytes(raw)
    if output==root/OUTPUT:
        web=root/WORKBENCH;web.mkdir(parents=True,exist_ok=True)
        for n,raw in _ui(root,files).items():(web/n).write_bytes(raw)
    return dict(study_id=v['study_id'],candidate_id=v['candidate_id'],native_execution=v['native_evidence']['execution'],physical_accepted=False)


def verify(output=OUTPUT,*,root=ROOT):
    root=Path(root).resolve();output=Path(output).resolve();m=_read(output/'manifest.json')
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('publication receipt identity differs')
    for name,digest in m['files_sha256'].items():
        if (output/name).is_symlink() or sha256((output/name).read_bytes()).hexdigest()!=digest:raise ValueError('payload differs: '+name)
    value=json.loads(gzip.decompress((output/'design.json.gz').read_bytes()))
    if value['study_id']!=identity({k:v for k,v in value.items() if k!='study_id'}):raise ValueError('design identity differs')
    with tempfile.TemporaryDirectory(prefix='osr-comfort-design-') as temp:
        paths={label:unpack((output/(label+'-artifacts.tar.gz')).read_bytes(),Path(temp)/label,label) for label in ('vehicle','service')}
        expected=assemble(root,paths)
        if value!=expected:raise ValueError('design differs from matched deterministic replay')
        files=_payloads(expected,paths)
        for n,raw in files.items():
            if (output/n).read_bytes()!=raw:raise ValueError('derived publication differs: '+n)
    if output==root/OUTPUT:
        for n,raw in _ui(root,files).items():
            if (root/WORKBENCH/n).read_bytes()!=raw:raise ValueError('Workbench differs: '+n)
    return dict(verified=True,study_id=value['study_id'],candidate_id=value['candidate_id'],physical_accepted=False)
