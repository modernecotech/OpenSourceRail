"""Publish one selected development configuration; keep physical holds explicit."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import fcntl
import gzip
import io
import json
import os
import shutil
import tarfile
import tempfile

from . import ROOT, OUTPUT, WORKBENCH, FLAGS
from . import selection, evaluate, exports, cities
from engineering.comfort_design import native_vehicle, interfaces, report_service

NATIVE_ARCHIVE = 'native-controls.tar.gz'
BODY_ARCHIVE = 'docs/design-engine/ferrite-maglev/comfort-design/vehicle-artifacts.tar.gz'
IDS = ('selection_id','candidate_id','body_candidate_id','magnet_component_id')


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write(path, raw):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_bytes(raw)
    os.replace(temporary, path)


def archive(folder):
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_file():
                raw = p.read_bytes(); info = tarfile.TarInfo(p.relative_to(folder).as_posix())
                info.size = len(raw); info.mode = 0o644; info.mtime = 0
                tar.addfile(info, io.BytesIO(raw))
    return gzip.compress(out.getvalue(), mtime=0)


def extract(path, folder, strip=None):
    """Only bounded ordinary relative files, no links or device members."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path) as tar:
        members = tar.getmembers()
        if sum(m.size for m in members) > 512*1024*1024:
            raise ValueError('native archive exceeds extraction budget')
        for m in members:
            name = Path(m.name)
            if name.is_absolute() or '..' in name.parts or not (m.isfile() or m.isdir()):
                raise ValueError('ordinary native archive files required')
            if strip:
                if not name.parts or name.parts[0] != strip:
                    raise ValueError('native archive root differs')
                name = Path(*name.parts[1:])
            if m.isfile():
                write(folder/name, tar.extractfile(m).read())
    return folder


def body_package(root=ROOT):
    root = Path(root); source = root/BODY_ARCHIVE
    selected = selection.load(root)
    receipt = json.loads((root/selected['selection']['source_manifest']).read_bytes())
    if digest(source) != receipt['files_sha256']['vehicle-artifacts.tar.gz']:
        raise ValueError('selected body archive differs from its source receipt')
    target = root/'build/development-baseline-cache'/('vehicle-'+digest(source)[:16])
    if not (target/'manifest.json').is_file():
        extract(source, target, 'vehicle')
    return target


def native_package(record, root=ROOT, output=None):
    root = Path(root); output = root/OUTPUT if output is None else Path(output)
    target = root/'build/development-baseline-cache'/('controls-'+record['evaluation_id'][:16])
    if (target/'manifest.json').is_file():
        evaluate.verify_native(target, record, root); return target
    if (output/NATIVE_ARCHIVE).is_file():
        # An incompatible retained package cannot be silently reused.
        with tempfile.TemporaryDirectory(prefix='osr-current-controls-') as tmp:
            extract(output/NATIVE_ARCHIVE, Path(tmp))
            try:
                evaluate.verify_native(tmp, record, root)
            except (ValueError, OSError, KeyError):
                pass
            else:
                shutil.copytree(tmp, target, dirs_exist_ok=True); return target
    preferred = root/'build/default-baseline-migration/native-72'
    if (preferred/'manifest.json').is_file():
        try:
            evaluate.verify_native(preferred, record, root)
        except (ValueError,OSError,KeyError):
            pass  # Preserve the older run; use a fresh evaluation-specific directory.
        else:
            shutil.copytree(preferred, target, dirs_exist_ok=True); return target
    if target.exists():
        raise ValueError('incomplete native execution retained at '+str(target)+'; preserve and use a fresh run directory')
    evaluate.run_native(target, root)
    return target


def sources(root, record, city_index, exported):
    paths = ['AGENTS.md','README.md','docs/ROADMAP.md','docs/ARCHITECTURE.md','osr','install.sh','package.json',
             'engineering/maglev_research/readme_context.py',
             '.github/workflows/development-baseline.yml']
    paths += [p.relative_to(root).as_posix() for p in sorted((root/'engineering/development_baseline').rglob('*'))
              if p.is_file() and (p.suffix in ('.py','.js','.html','.css')) and '__pycache__' not in p.parts]
    paths += ['tools/automation/default-design.py','tools/automation/default-design-workbench.py','tools/automation/default-design-cycle.py',
              'tools/automation/tests/verify-development-baseline.mjs']
    return evaluate._merge(record['source_sha256'], city_index['source_sha256'],
                           exported['source_sha256'], {name:digest(root/name) for name in paths})


def summary(record, index, native, exported):
    car, service = record['vehicle'], record['service']
    result = evaluate.summary(record)
    baghdad = next(r for r in index['cities'] if r['slug']=='baghdad')
    result.update(schema='osr-current-development-summary/1',
        selection_revision=record['selection']['revision'],
        service=dict(headway_s=120.,launch_speed_cap_m_s=20.,dwell_s=35.,cars=6,
            passengers_per_car=46,capacity_pphpd=8280.,shared_winding_m=800.,
            prototype_station_spacing_m=2000.,prototype_runtime_s=service['selected_scenario']['profile']['runtime_s'],
            retained_stops=True,physical_headway_qualified=False),
        mass=car['mass'], cities=dict(city_count=index['city_count'],index_path=OUTPUT+'/cities.json',
            default_city='baghdad',baghdad=baghdad['totals'],summary=index['summary']),
        native=dict(controls=native['controls'],all_controls_pass=native['all_controls_pass'],
            evaluation_id=native['evaluation_id'],physical_train_simulated=False,
            native_CAD_reused_exact_candidate=True,bim_execution=exported['bim_execution'],
            scope='Actual Rust protection-protocol fixtures with synthetic gap/brake inputs; exact native material CAD reference and selected civil IFC, no physical journey.'),
        current_outputs=dict(exports=OUTPUT+'/exports/manifest.json',reader='OpenSourceRail-Book.pdf'),
        known_gate_counts=dict(Counter(g['state'] for g in record['gates'])))
    return result


def readme(record, compact):
    m=record['vehicle']['mass']; s=record['service']; gates=record['gates']
    lines=['# Current comfort-first development design','',
      'OpenSourceRail develops simple, affordable, locally maintainable urban transport. All permanent magnets and fast suspension controls stay on the train. Ordinary guideway is a concrete beam with passive steel facings; station winding groups launch and receive trains. Repeated lightweight vehicles and civil components aim to reduce total cost while providing frequent comfortable service.','',
      '**This is the repository development default, not a physical or operating release.** The selector is [engineering/development-baseline.toml](../../../engineering/development-baseline.toml). Every current city, control setting and delivery export carries the same selection, vehicle, body and magnet identities. Historical packets retain their original scope and source revision.','',
      '| Item | Selected basis |','|---|---|',
      '| Formation | Six 17 m cars, 104.5 m train including gaps |',
      '| Comfort and payload | 44 fixed seats + two wheelchair places/car, zero planned standing; 276/train |',
      '| Layout | Four abreast where structural posts permit, wall seating at the doors; two passenger doors on one side |',
      '| Structure | Aluminium extrusion frame, retained GFRP sides, aluminium-skin sandwich floor and revised roof |',
      '| Windows | Retained laminated glass; plastic alternatives are not qualified |',
      '| PM assembly | Selected onboard NdFeB Halbach component; active multiaxis stabilization remains open |',
      f"| Accounted tare / capped loaded mass | {m['accounted_tare_kg_per_car']/1000:.3f} / {m['accounted_cap_loaded_kg_per_car']/1000:.3f} t/car |",
      '| Complete installed mass / CG / inertia | Unknown; retained allocations and supplier references are not located material |',
      '| Service target | 120 s, 30 trains/hour, 8,280 normal passengers/hour/direction |',
      '| Retained-stop proposal | 72 km/h launch cap, 35 s dwell; actual coast/brake legs and bounded station library |','',
      'The lower passenger count is a comfort and normal-load choice. The former 14,400 pphpd comparison is not achieved by this seating capacity. Enforceable admission, crowd loading, accessible boarding, one-sided platform compatibility and evacuation remain design requirements.','',
      '## Recalculated service and cities','',
      f"All **{compact['cities']['city_count']} city packages** use this default and retain their existing route geography and stops. Baghdad requires **906 trainsets (791 active, 101 spare, 14 cold reserve), 5,436 cars and 390,500 m of directional station winding** under the declared flat-route and drag hypotheses. No additional passenger stops are imposed. Its four motor-interval overlaps and 36.743% mainline powered coverage require physical resource/handoff design; they are not qualified infrastructure.",'',
      'The 2 km prototype has an analytical runtime of **151.930 s**, with 20 m/s launch and approximately 14.266 m/s arrival before braking. A station shares **800 m** of winding across launch and receipt, divided into 64 addresses/direction at 12.5 m, with at least two simultaneous train phase/current branches per direction. The nominal resource interval is **79.504 s**, not a safe headway determination. The earlier 54 km/h, 450 m prototype is a named comparison.','',
      'Mass, propulsion energy requirements, service cycles, fleet and station quantities are recalculated; unavailable actual thrust, control, HVAC power, unit prices, site quantities, crew duty and finance totals remain unknown. Historical fleet and CAPEX/OPEX figures do not apply automatically.','',
      '[All-city index](cities.json) · [Baghdad current package](../../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/current/README.md) · [Coasting profile](service-profile.svg) · [Workbench](../../workbench/current/index.html)','',
      '## Native evidence and consistent delivery records','',
      f"The selected-profile native package contains **{compact['native']['controls']} actual Rust control executions**. They test nominal, journal and fault protection protocols using virtual healthy gaps and assumed braking. They do not establish a physical operating gap, stable hover or a physical two-minute headway. The exact unchanged native car material geometry is independently reverified; complete installed geometry and structure remain open.",'',
      '[Native controls archive](native-controls.tar.gz) · [Engineering BOM](exports/engineering-bom.json.gz) · [Manufacturing](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly/construction](exports/assembly.json) · [Civil interface](exports/civil.json) · [Controls](exports/controls.json) · [CAD reference receipt](exports/cad.json) · [Selected civil IFC](exports/selected-interface.ifc). The IFC contains the declared civil shell, facings and equipment contexts; it is not a complete vehicle or civil model.','',
      '[Native car](../ferrite-maglev/comfort-design/vehicle.FCStd) · [STEP](../ferrite-maglev/comfort-design/vehicle.step.gz) · [Material overview](vehicle-overview.svg) · [Guideway section](interface-section.svg) · [Complete current evaluation](evaluation.json.gz)','',
      '## Physical gates','',
      '| Gate | Screen | Remaining evidence |','|---|---|---|']
    lines += [f"| {g['gate']} | **{g['state']}** | {g['reason']} |" for g in gates]
    lines += ['',
      'The 12 mm section pose is a magnetic coupon reference, not an accepted operating gap. The lighter car has excess upward force at that sample; equilibrium, current authority, lateral/rotational response, damping, temperature and boarding datum must be resolved together. EPM load trimming and new Halbach families remain research alternatives rather than replacements for fast control.','',
      'The counted civil interface is conservative and heavy: approximately 865 t steel/directional km before remaining reinforcement, prestress, bearings, piers and foundations. It is an optimization input, not a low-cost viaduct claim. Unknown stock and prices never become zero.','',
      '## Reproduce and verify','', '```bash','./osr build','./osr verify','./osr test','./osr book --check','./osr legacy verify','```','',
      '[Summary](summary.json) · [Source/payload receipt](manifest.json) · [README coverage](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Historical archive](../../archives/pre-comfort-default/README.md) · [Project ethos](../../../README.md)','',
      f"Selection `{record['selection_id']}`",'',f"Vehicle `{record['candidate_id']}`",'',
      f"Body `{record['body_candidate_id']}`",'',f"Magnet `{record['magnet_component_id']}`",'']
    return '\n'.join(lines)


def seal(output=ROOT/OUTPUT, root=ROOT):
    root,output=Path(root).resolve(),Path(output).resolve()
    record=evaluate.build(root);index=cities.read_catalogue(root)
    exported=json.loads((output/'exports/manifest.json').read_bytes())
    ui={name:digest(root/WORKBENCH/name) for name in ('index.html','app.js','app.css')}
    files={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*'))
           if p.is_file() and p.name!='manifest.json'}
    # Nested export receipts themselves are required payloads too.
    files['exports/manifest.json']=digest(output/'exports/manifest.json')
    m=dict(schema='osr-current-development-publication/1',**{k:record[k] for k in IDS},
        evaluation_id=record['evaluation_id'],development_default=True,
        source_sha256=sources(root,record,index,exported),files_sha256=files,
        workbench_files_sha256=ui,**FLAGS)
    linked={}
    for name in ('OpenSourceRail-Book.pdf','OpenSourceRail-Book.receipt.json'):
        if (root/name).is_file():linked[name]=digest(root/name)
    m['linked_artifacts_sha256']=linked
    m['manifest_id']=selection.identity(m)
    write(output/'manifest.json',selection.encoded(m));return m


def publish(output=ROOT/OUTPUT, *, root=ROOT, native_dir=None, cities_dir=None):
    root,output=Path(root).resolve(),Path(output).resolve();record=evaluate.build(root)
    if cities_dir is not None:
        origin=Path(cities_dir)
        cities.verify_all(origin,root=root,replay=False)
        receipt=json.loads((origin/cities.INDEX_MANIFEST).read_bytes())
        for name in (*receipt['files_sha256'],cities.INDEX_MANIFEST):write(root/name,(origin/name).read_bytes())
    try:cities.verify_all(root,root=root,replay=False)
    except (ValueError,OSError,KeyError):cities.publish_all(root,root=root,update_readmes=True)
    index=cities.read_catalogue(root)
    native_dir=native_package(record,root,output) if native_dir is None else Path(native_dir)
    evaluate.verify_native(native_dir,record,root)
    native=json.loads((native_dir/'result.json').read_bytes())
    body=body_package(root);native_vehicle.verify_export(body,record['vehicle'],root=root)
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='osr-current-exports-') as temporary:
        exportdir=Path(temporary)/'exports'
        exported=exports.write(exportdir,record,root=root,city_index=index,native_vehicle_folder=body)
        destination=output/'exports'
        if destination.exists():
            previous=root/'build/development-baseline-cache/replaced-exports'/digest(destination/'manifest.json')
            previous.parent.mkdir(parents=True,exist_ok=True)
            if previous.exists():shutil.rmtree(destination)
            else:shutil.move(destination,previous)
        shutil.copytree(exportdir,destination)
    compact=summary(record,index,native,exported)
    payloads={'summary.json':selection.encoded(compact),'evaluation.json.gz':gzip.compress(selection.encoded(record),mtime=0),
              'README.md':readme(record,compact).encode(),'service-profile.svg':report_service.render_profile_svg(record['service']).encode(),
              'interface-section.svg':interfaces.render_section_svg(record['interfaces']).encode(),
              'vehicle-overview.svg':(body/'assembly.svg').read_bytes(),NATIVE_ARCHIVE:archive(native_dir)}
    for name,raw in payloads.items():write(output/name,raw)
    for name in ('index.html','app.js','app.css'):write(root/WORKBENCH/name,(root/'engineering/development_baseline/web'/name).read_bytes())
    seal(output,root)
    return dict(published=True,selection_id=record['selection_id'],evaluation_id=record['evaluation_id'],city_count=index['city_count'],**FLAGS)


def verify(output=ROOT/OUTPUT, *, root=ROOT, replay=True):
    root,output=Path(root).resolve(),Path(output).resolve()
    from .entrypoint import read_packet
    compact,m=read_packet(root,output.relative_to(root).as_posix())
    if m['manifest_id']!=selection.identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('publication identity differs')
    record=evaluate.build(root)
    if json.loads(gzip.decompress((output/'evaluation.json.gz').read_bytes()))!=record:raise ValueError('published evaluation differs from current inputs')
    citycheck=cities.verify_all(root,root=root,replay=replay)
    index=cities.read_catalogue(root)
    if any(index.get(k) is not v for k,v in FLAGS.items()) or index.get('development_default') is not True:
        raise ValueError('city catalogue cannot grant physical acceptance')
    exported=exports.verify(output/'exports',record,root=root,city_index=index)
    with tempfile.TemporaryDirectory(prefix='osr-current-verify-') as tmp:
        extract(output/NATIVE_ARCHIVE,tmp);nativecheck=evaluate.verify_native(tmp,record,root)
        native=json.loads((Path(tmp)/'result.json').read_bytes())
    exported_manifest=json.loads((output/'exports/manifest.json').read_bytes())
    if m['source_sha256']!=sources(root,record,index,exported_manifest):raise ValueError('current publication source set differs')
    expected=summary(record,index,native,exported_manifest)
    if compact!=expected:raise ValueError('current summary differs from selected calculations')
    if (output/'README.md').read_text()!=readme(record,expected):raise ValueError('current introduction differs from selected calculations')
    from engineering.maglev_research import readme_context
    coverage=readme_context.audit(root)
    if not coverage['current'] or json.loads((output/'readme-coverage.json').read_bytes())!=coverage:
        raise ValueError('current README context or coverage differs')
    for name,expected in m['workbench_files_sha256'].items():
        if digest(root/WORKBENCH/name)!=expected:raise ValueError('Workbench differs: '+name)
    for name,expected in m.get('linked_artifacts_sha256',{}).items():
        if digest(root/name)!=expected:raise ValueError('linked artifact differs: '+name)
    return dict(verified=True,replayed=replay,selection_id=record['selection_id'],evaluation_id=record['evaluation_id'],
        city_count=citycheck['city_count'],native_controls=nativecheck['controls'],exports=exported,**FLAGS)


def build(root=ROOT, force=False, output=None):
    root=Path(root).resolve();output=root/OUTPUT if output is None else Path(output)
    lock=root/'build/development-baseline-cache/build.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if not force:
            try:
                result=verify(output,root=root,replay=False)
                from . import book
                book.build(root=root,check=True)
                return dict(result,cached=True)
            except (ValueError,OSError,KeyError):pass
        result=publish(output,root=root)
        from engineering.maglev_research import readme_context
        readme_context.write_owned(root)
        audit=readme_context.audit(root)
        if not audit['current']:raise ValueError('README coverage: '+'; '.join(audit['errors']))
        write(output/'readme-coverage.json',(json.dumps(audit,sort_keys=True,indent=2)+'\n').encode())
        write(output/'readme-coverage.md',readme_context.markdown(audit).encode())
        seal(output,root)
        from . import book
        book.build(root=root)
        seal(output,root)
        return dict(result,verification=verify(output,root=root),cached=False)
