"""Reproducible v0.6 reference publication; cities remain geographically indexed holds."""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import fcntl,gzip,io,json,os,shutil,tarfile,tempfile
from . import ROOT,FLAGS
from .common import encoded,identity,digest
from . import evaluation,exports,cities,comparison,figures
from .evaluation import IDS
OUTPUT='docs/design-engine/current'
WORKBENCH='docs/workbench/current'

def write(path,raw):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp');tmp.write_bytes(raw);os.replace(tmp,path)
def archive(folder):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_file():
                data=p.read_bytes();item=tarfile.TarInfo(p.relative_to(folder).as_posix());item.size=len(data);item.mtime=0;item.mode=0o644;tar.addfile(item,io.BytesIO(data))
    return gzip.compress(raw.getvalue(),mtime=0)
def extract(path,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    with tarfile.open(path) as tar:
        members=tar.getmembers()
        if sum(m.size for m in members)>512*1024**2:raise ValueError('bounded native archive required')
        for member in members:
            name=Path(member.name)
            if name.is_absolute() or '..' in name.parts or not(member.isfile() or member.isdir()):raise ValueError('ordinary relative native files required')
            if member.isfile():write(folder/name,tar.extractfile(member).read())
    return folder

def verify_package(path,root=ROOT):
    path=Path(path);m=json.loads((path/'manifest.json').read_bytes())
    if m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('native package identity differs')
    for name,expected in m['source_sha256'].items():
        if digest(Path(root)/name)!=expected:raise ValueError('native source differs: '+name)
    actual={p.relative_to(path).as_posix():digest(p) for p in path.rglob('*') if p.is_file() and p.relative_to(path).as_posix()!='manifest.json'}
    if actual!=m['files_sha256']:raise ValueError('native payload differs')
    if any(m.get(k) is not v for k,v in FLAGS.items()):raise ValueError('native result cannot grant release')
    result=json.loads((path/'result.json').read_bytes())
    if any(result.get(k) is not v for k,v in FLAGS.items()):raise ValueError('native result disposition differs')
    if result.get('schema')=='osr-station-rail-native/1':
        from .vehicle import build
        v=build(root);cad=result['CAD']
        if (abs(cad['native_material_kg']-v['mass']['located_material_kg'])>1e-5
            or cad['part_count']!=len(v['geometry_parts']) or not cad['all_part_volumes_match']
            or not cad['reopened_volume_matches']):raise ValueError('Native CAD does not match selected material')
    if result.get('schema')=='osr-native-LIM-secondary-diffusion/1':
        if result['candidate_force_map'] is not False or result['actual_primary_current_map'] is not False:
            raise ValueError('A manufactured slab cannot qualify a complete motor')
        cases=result['cases']
        if [(c['nx'],c['ny']) for c in cases]!=[(40,4),(80,8),(160,16)]:raise ValueError('Native refinement case inventory differs')
        if result['convergence_screen']!='pass' or cases[-1]['relative_force_error']>=.02:raise ValueError('Native diffusion convergence does not pass')
    return result

def native_package(name,record,root=ROOT,output=None,provided=None):
    from . import native,controls
    root=Path(root);output=root/OUTPUT if output is None else Path(output)
    if name=='vehicle':check=lambda path:native.verify(path,root)
    elif name=='controls':check=lambda path:controls.verify(path,record,root)
    else:check=lambda path:verify_package(path,root)
    candidates=[]
    if provided:candidates.append(Path(provided))
    candidates += [root/'build/v06-development'/('native-vehicle-final' if name=='vehicle' else 'native-secondary-final' if name=='drive' else 'native-controls-'+record['evaluation_id'][:16]+'-'+identity(controls.sources(root))[:12])]
    for path in candidates:
        if (path/'manifest.json').is_file():
            try:check(path)
            except(ValueError,OSError,KeyError):
                if provided:raise
            else:return path
    retained=output/('native-'+name+'.tar.gz')
    if retained.is_file():
        target=root/'build/v06-development/cache'/('native-'+name+'-'+digest(retained)[:16])
        if not (target/'manifest.json').is_file():extract(retained,target)
        try:check(target)
        except (ValueError,OSError,KeyError):pass
        else:return target
    if name=='controls':
        target=candidates[-1]
        controls.run(target,record,root);check(target);return target
    raise ValueError('Required native '+name+' package unavailable; execute its source-bound worker into a fresh run directory')

def sources(root,record,index,delivery):
    root=Path(root);maps=[record['source_sha256'],index['source_sha256'],delivery['source_sha256']]
    names=['AGENTS.md','README.md','VERSION','Cargo.toml','Cargo.lock','package.json','package-lock.json','docs/ROADMAP.md','docs/ARCHITECTURE.md',
        'engineering/development-baseline.toml','engineering/maglev_research/readme_context.py','osr','install.sh',
        '.github/workflows/development-baseline.yml','tools/automation/default-design.py','tools/automation/default-design-workbench.py',
        'tools/automation/default-design-cycle.py','tools/automation/tests/verify-development-baseline.mjs','tools/automation/v06-native-benchmarks.py',
        'tools/automation/architecture-native-benchmarks.py','tools/automation/generative-native-benchmarks.py',
        'tools/automation/coupled-native-benchmarks.py']
    for directory in ('engineering/station_rail','engineering/development_baseline'):
        names += [p.relative_to(root).as_posix() for p in (root/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.toml','.js','.html','.css') and '__pycache__' not in p.parts]
    followup=root/'docs/design-engine/v06-physical-closure'
    if followup.is_dir():names += [p.relative_to(root).as_posix() for p in sorted(followup.iterdir()) if p.is_file()]
    for folder in ('v06-optimisation','v06-design-space','v06-architecture','v06-adaptive-design','generative-structure','coupled-railway'):
        campaign_folder=root/'docs/design-engine'/folder
        if campaign_folder.is_dir():names += [p.relative_to(root).as_posix() for p in sorted(campaign_folder.rglob('*')) if p.is_file()]
        if folder=='coupled-railway' and (campaign_folder/'manifest.json').is_file():maps.append(json.loads((campaign_folder/'manifest.json').read_bytes()).get('source_sha256',{}))
    return evaluation.merge(*maps,{n:digest(root/n) for n in sorted(set(names))})

def compact(record,index,natives,delivery):
    value=evaluation.summary(record);value.update(cities=dict(city_count=index['city_count'],summary=index['summary'],
        baghdad=None,default_city='baghdad',index_path=OUTPUT+'/cities.json',longest_gap=index['longest_gap']),
        native=dict(controls=natives['controls']['controls'],all_controls_pass=natives['controls']['all_controls_pass'],
            CAD=natives['vehicle']['CAD'],underframe_fixtures=natives['vehicle']['underframe_fixtures'],
            drive_convergence=natives['drive']['convergence_screen'],
            scope='Actual FreeCAD/STEP export and reopen, limited CalculiX underframe fixtures, GetDP manufactured conductive-slab convergence and Rust ATP/interface regressions. No complete physical train journey.',
            physical_train_simulated=False),known_gate_counts=dict(Counter(g['state'] for g in record['gates'])),
        current_outputs=dict(exports=OUTPUT+'/exports/manifest.json',reader='OpenSourceRail-Book.pdf',physical_followup='docs/design-engine/v06-physical-closure/README.md'),
        economics_acceptance='unknown',city_performance_packages_written=0)
    return value

def readme(record,summary):
    v=record['vehicle'];m=v['mass'];o=record['service'];p=o['selected_scenario']['profile'];z=o['selected_station'];r=record['civil']['selected_reference'];e=o['electrical'];b=e['battery']
    lines=['# v0.6 station-powered freewheeling rail','',
      'OpenSourceRail aims for simple, affordable urban transport, repeated precast civil components and local manufacture and repair. Six lightweight comfort cars run on passive steel-wheel bogies and conventional rails. Station LIMs act on passive onboard aluminium secondaries; no onboard traction motor, traction battery or levitation magnet is fitted. Independent service power, braking and the existing station-led GoA4 architecture remain.','',
      '**Selected for reference engineering and prototype investigation. No physical, manufacturing or operating release.** The [selector](../../../engineering/development-baseline.toml) binds the same vehicle, body, support and propulsion identities through this packet, delivery records, Workbench and reader. [v0.5 maglev evidence](../../archives/v0.5-maglev/README.md) remains independently pinned.','',
      '| Item | Recalculated basis |','|---|---|',
      '| Formation and comfort | Six 17 m cars; 104.5 m overall; 44 seats + two wheelchair places/car; zero planned standing |',
      '| Running gear | 12 unpowered bogies, 24 axles, 48 wheels; independent friction/WSP/parking brake requirements |',
      '| Body/platform | Retained lightweight aluminium/GFRP stock with revised bogie load paths; 1.0 m reference floor above rail |',
      f"| Accounted tare / normal load | {m['accounted_tare_kg_per_car']/1000:.3f} / {m['accounted_cap_loaded_kg_per_car']/1000:.3f} t/car at 75 kg/person |",
      f"| Located material / remaining reference accounts | {m['located_material_kg']/1000:.3f} / {m['unlocated_or_reference_account_kg']/1000:.3f} t/car |",
      '| Complete installed mass, CG and inertia | Unknown; inherited service allocations may overlap new equipment and must be disaggregated |',
      f"| Service-only battery | {b['gross_energy_kWh']:.1f} kWh, {b['mass_kg']:.0f} kg/car reference account; cooled installation and rail approval open |",
      '| Service targets | 72 km/h, 0.4 m/s² acceleration, 0.6 m/s² braking, 35 s dwell, 120 s headway; 8,280 pphpd arithmetic |','',
      '## Reference journey and power','',
      f"The 2 km, normal-load longitudinal requirement, including counted wheel/axle/disc rotational inertia, takes **{p['runtime_s']:.3f} s**, reaching 20 m/s and arriving at **{p['arrival_speed_before_braking_m_s']:.3f} m/s** before braking. Required peak launch force is **{p['peak_launch_force_N_per_car']/1000:.3f} kN/car**, mechanical power **{p['peak_launch_power_W_per_car']/1000:.1f} kW/car**. Actual available thrust, current, voltage and full motor efficiency remain unknown.",'',
      f"Full-train engagement requires **{z['required_shared_winding_m']:.1f} m** of shared launch/receiving winding; the library chooses **{z['length_m']:.0f} m**, **{z['sections_per_direction']} sections/direction** at 12.5 m and at least two independently controlled train branches. The **{z['nominal_resource_interval_s']:.2f} s** nominal berth interval is a necessary resource screen, not verified two-minute operation.",'',
      'Reference profiles cover empty, 46-person and 160-person structural-control loads at 1.5 and 2 km, with grade/wind, charge and independent wet/downhill stopping bounds. A 0.05 adhesion hypothesis on a 2% downgrade gives approximately 700 m stopping from 20 m/s including one second response. Supplier brakes, WSP, uncertainties and actual routes must establish the protection envelope. Receiving motor recovery receives no safety credit.','',
      'The 82.8 kWh service reference uses 75 industrial Type3-20 modules plus explicit enclosure/cooling/conversion accounts. The 200 kW charging target passes a catalogue voltage/current necessary bound; available charge power versus SOC/temperature remains unknown. A 50°C environment exceeds the module ambient catalogue range. Normal 35 kW/car hotel duty balances in the prototype calculation; 50 kW/car adverse duty needs more charging. Solar yield is not guaranteed or credited to make the balance pass.','',
      'The actual GetDP conductive-slab benchmark converges against its exact imposed-field solution. It has no real primary winding, steel/end geometry, current-to-force map or finite-height return currents. Its conditional thrust is not available station thrust. Active-plate-only and all-aluminium heat-capacity bounds expose the dependence on thermal connection; actual temperatures remain unknown.','',
      'The [native physical follow-up](../v06-physical-closure/README.md) adds 18 current-excited LIM cases, 24 reduced Chrono brake runs and native body-interface/fit-up experiments. The tested full primary fails force and steel-field screens. Its raw field calculations remain conditional; the default geometry and acceptance holds are unchanged.','',
      '[Prototype/fault test plan](prototype-test-plan.json) · [Full evaluation](evaluation.json.gz) · [Motor method evidence](native-drive.tar.gz) · [Speed requirement](service-profile.svg) · [Equal-service comparison](comparison.json)','',
      '## Vehicle and civil design','',
      'New bogie hardpoints, deep side sills and retained roof longitudinal members replace the magnetic carrier arrangement. The isolated side sills fail their declared stiffness screen; ideal whole-body chord coupling is an upper stiffness bound, with shear transfer, openings and joints unqualified. Native CAD is counted material geometry, not a complete installed or collision-free certified vehicle. Split battery cassettes, brakes, suspension, couplers, frame joints and maintenance paths still need detailed installation.','',
      'The roof proposal uses HP60 core and a counted white finish; long-term loaded hot strength, durable reflectance and HVAC performance remain open. Unchanged door, glass, floor and seat stock retains its source ancestry; the revised vehicle receives a new identity. Plastic glazing remains an unqualified alternative.','',
      f"Three conventional guideway families are compared across 15/20/25/30 m spans. The crowd-sized {r['span_m']:.0f} m box reference counts **{r['concrete_m3']:.3f} m³ concrete**, **{r['running_rail_kg']/1000:.3f} t running rail**, **{r['direct_fastener_sets']} fastener sets** and **{r['counted_steel_kg']/1000:.3f} t total preliminary steel including rail, fasteners, reinforcement, tendons and anchorages. Its **{r['total_counted_span_mass_kg']/1000:.2f} t** span account still excludes complete bearings, piers, foundations, access/containment and station equipment.",'',
      'New rails and fasteners are much lighter than the old magnetic interface stock, while concrete and remaining structural quantities have different boundaries. Lower installed cost is unproven. Each longitudinal section gets its own moving-load envelope; torsion, fatigue, unequal rail loads, prestress losses, erection and sites remain open. Twin and U sections retain their failures.','',
      '[Native vehicle material package](native-vehicle.tar.gz) · [Vehicle drawing](vehicle-overview.svg) · [Reference section](interface-section.svg) · [Civil alternatives](exports/civil.json) · [Partial native IFC](exports/selected-interface.ifc) · [IFC scope](exports/bim.json) · [BOM](exports/engineering-bom.json.gz) · [Processes](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly](exports/assembly.json) · [Controls](exports/controls.json)','',
      '## Automation, comparison and cities','',
      'Station-led GoA4, onboard ATP, OCC, TCMS, door control, interlocking and communications remain. New actual Rust wheel-interface fixtures check configuration/readiness and independent brake demands; existing ATP regressions remain software evidence. They use assumed readiness and have no physical brake plant or hardware outputs. Loss of propulsion leaves wheel support intact. Off-zone restart requires protected rescue/towing; mainline switches remain excluded, with depot exceptions only.','',
      'v0.6 is chosen for prototype investigation to remove the unproven levitation system and repeated magnetic-facing assemblies. It is heavier than the v0.5 accounted car and lighter than the optimistic stripped-v0.4 mass proxy. No same-service supplier-priced whole-life superiority is established. See the explicit comparison and open price coverage.','',
      f"All **{summary['cities']['city_count']} city geographies and maps are preserved**; **zero city performance packages are regenerated**. A metadata scan of 17,268 adjacent operating-stop gaps finds a longest retained gap of approximately 3 km in Faisalabad. Reference adverse cases test that distance; uphill unreachable cases and downhill speed-cap violations are retained. Historical city fleet, windings and finance figures are not v0.6 results.",'',
      '[Geographic catalogue and holds](cities.json) · [Workbench](../../workbench/current/index.html) · [Native controls](native-controls.tar.gz)','',
      '## Iterative alternatives','', 'The [failure-driven campaign](../v06-optimisation/README.md) generates body/motor/brake revisions, reruns native solvers, propagates the same mass into civil/service calculations and compiles matching research twins. The research winner is the next experiment; no qualified replacement is silently promoted. The comparison exposes normal/crowd deflection, additional mass and changed thrust requirements; conditional motor results remain outside their declared linear-steel domain. Participating-panel lateral displacement remains nonconverged under mesh refinement; its vertical values are diagnostic rather than validated full-body performance.','',
      'The [whole-railway architecture campaign](../v06-architecture/README.md) tests seven propulsion families, different speed/formation/powered-track arrangements and civil sections. It compares analytical demand and conditional quantities while keeping new equipment mass and actual motor capability unknown. Repaired finite-area joint/body and generic nonlinear magnetic method checks retain their independent numerical and engineering dispositions. No architecture is qualified, no city performance is regenerated and the selected v0.6 reference is preserved.','',
      'The [function-first adaptive generator](../v06-adaptive-design/README.md) separates mandatory obligations, advisory targets, revisable hypotheses and numerical model domains. Its extensible material/structure/joining/equipment/system variables drive coupled revision tasks. New thinner/deeper sill experiments redistribute counted material, with native normal/fine/crowd cases and matched mass, axle, demand and civil calculations. Provisional deflection alone neither rejects nor accepts a car; local stability, strength, joints, clearances and correlation remain open.','',
      'The [generative structural campaign](../generative-structure/README.md) composes different physical body arrangements, generates actual stock and interface graphs, diagnoses mechanisms and executes topology, layout and function-integration rewrites. Gross structure stock is not equipped vehicle tare. Native axial underfloor checks and CAD exports do not validate complete shell, laminate, joint or vehicle response; no integrated design is selected.','',
      'The [coordinated railway experiment](../coupled-railway/README.md) connects architecture, adaptive proposals, generated bodies, inventory, motor requirements, independent braking, civil loads, manufacturing and economic coverage through one versioned bundle and dependency graph. Changed body stock automatically triggers downstream evaluation. New three-dimensional metal-body research and conditional operating requirements retain their exact models and missing evidence; complete installed mass, available nonlinear LIM capability and a qualified journey remain open.','',
      '## Readiness and reproduction','', '| Gate | State | Evidence still needed |','|---|---|---|']
    lines += [f"| {g['gate']} | **{g['state']}** | {g['reason']} |" for g in record['gates']]
    lines += ['','```bash','./osr status','./osr build','./osr verify','./osr test','./osr book --check','./osr sim baghdad  # explicit city evaluation hold','./osr legacy verify','```','',
      '[Source/payload receipt](manifest.json) · [README context](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Project ethos](../../../README.md)','']
    for name in IDS:lines += [name.replace('_',' ').capitalize()+' `'+record[name]+'`','']
    return '\n'.join(lines)

def prototype_plan(record):
    cases=[]
    required=('position','speed','acceleration','motor_current','motor_thrust','electrical_power','secondary_temperature',
        'stator_temperature','wheel_and_axle_forces','brake_force_and_temperature','service_SOC','resource_occupancy','following_separation','failure_reason')
    for p in record['service']['profiles']:
        d=p['inputs']['distance_m'];load=p['inputs']['loading']
        fault=('receiving drive power lost' if load=='empty' else 'wet-rail braking' if load=='normal' else 'emergency stop')
        cases.append(dict(case_id=identity(dict(profile_id=p['profile_id'],fault=fault)),distance_m=d,loading=load,
            normal_analytical_profile_id=p['profile_id'],degraded_case=fault,
            reference_calculation_execution='completed',physical_run_execution='held',
            missing_inputs=['Validated station motor map','Qualified brake/WSP/adhesion map','Flexible body and wheel-rail dynamics'],
            physical_outputs={key:None for key in required}))
    return dict(schema='osr-v06-prototype-test-plan/1',**{k:record[k] for k in IDS},development_default=True,
        reference_cases=cases,longest_gap=record['service']['longest_retained_gap_context'],
        additional_faults=['Communications lost','Occupied or delayed receiving berth','Gradient overspeed','Train integrity/localisation lost',
            'One brake control channel lost','Missed charge','Station power lost during launch','Off-zone rescue and high-viaduct evacuation'],
        releases=dict(production_drawings=False,supplier_brakes=False,motor_map=False,structural_body=False,prototype_review=False),
        proof_rule='Method and reference calculations do not replace the same-candidate physical journey and independent qualification.',**FLAGS)

def seal(output,root=ROOT):
    root=Path(root);output=Path(output);record=evaluation.build(root);index=cities.read_catalogue(root);delivery=json.loads((output/'exports/manifest.json').read_bytes())
    m=dict(schema='osr-current-development-publication/2',**{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],development_default=True,
      source_sha256=sources(root,record,index,delivery),files_sha256={p.relative_to(output).as_posix():digest(p) for p in sorted(output.rglob('*')) if p.is_file() and p.relative_to(output).as_posix()!='manifest.json'},
      workbench_files_sha256={n:digest(root/WORKBENCH/n) for n in ('index.html','app.js','app.css')},**FLAGS)
    m['linked_artifacts_sha256']={n:digest(root/n) for n in ('OpenSourceRail-Book.pdf','OpenSourceRail-Book.receipt.json') if (root/n).is_file()}
    m['manifest_id']=identity(m);write(output/'manifest.json',encoded(m));return m

def publish(output=None,*,root=ROOT,native_dir=None,cities_dir=None):
    root=Path(root).resolve();output=root/OUTPUT if output is None else Path(output)
    record=evaluation.build(root);natives={};packages={}
    for name in ('vehicle','drive','controls'):
        packages[name]=native_package(name,record,root,output,native_dir if name=='vehicle' else None)
        natives[name]=verify_package(packages[name],root)
    if output.exists():
        previous=root/'build/v06-development/replaced-current'/digest(output/'manifest.json') if (output/'manifest.json').is_file() else root/'build/v06-development/replaced-current/incomplete'
        if previous.exists():shutil.rmtree(output)
        else:previous.parent.mkdir(parents=True,exist_ok=True);shutil.move(output,previous)
    output.mkdir(parents=True,exist_ok=True)
    index=cities.publish_all(root=root);delivery=exports.write(output/'exports',record,root,index,natives['vehicle'])
    compact_value=compact(record,index,natives,delivery)
    for name,raw in {'summary.json':encoded(compact_value),'evaluation.json.gz':gzip.compress(encoded(record),mtime=0),
       'comparison.json':encoded(comparison.evaluate(record,root)),'prototype-test-plan.json':encoded(prototype_plan(record)),'README.md':readme(record,compact_value).encode()}.items():write(output/name,raw)
    for name,path in packages.items():write(output/('native-'+name+'.tar.gz'),archive(path))
    figures.write(record,output)
    for name in ('index.html','app.js','app.css'):write(root/WORKBENCH/name,(root/'engineering/development_baseline/web'/name).read_bytes())
    seal(output,root)
    return dict(published=True,selection_id=record['selection_id'],evaluation_id=record['evaluation_id'],city_count=index['city_count'],city_performance_packages_written=0,**FLAGS)

def verify(output=None,*,root=ROOT,replay=True):
    root=Path(root).resolve();output=root/OUTPUT if output is None else Path(output)
    from engineering.development_baseline.entrypoint import read_packet
    value,m=read_packet(root,output.relative_to(root).as_posix())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('publication identity differs')
    record=evaluation.build(root)
    if json.loads(gzip.decompress((output/'evaluation.json.gz').read_bytes()))!=record:raise ValueError('evaluation differs')
    citycheck=cities.verify_all(root=root,replay=replay);index=cities.read_catalogue(root);delivery=exports.verify(output/'exports',record,root,index)
    natives={}
    for name in ('vehicle','drive','controls'):
        path=native_package(name,record,root,output);natives[name]=verify_package(path,root)
    exported=json.loads((output/'exports/manifest.json').read_bytes())
    if value!=compact(record,index,natives,exported):raise ValueError('current summary differs')
    if (output/'README.md').read_text()!=readme(record,value):raise ValueError('current introduction differs')
    if json.loads((output/'comparison.json').read_bytes())!=comparison.evaluate(record,root):raise ValueError('comparison differs')
    if json.loads((output/'prototype-test-plan.json').read_bytes())!=prototype_plan(record):raise ValueError('prototype test plan differs')
    if m['source_sha256']!=sources(root,record,index,exported):raise ValueError('publication source set differs')
    from engineering.maglev_research import readme_context
    audit=readme_context.audit(root)
    if not audit['current'] or json.loads((output/'readme-coverage.json').read_bytes())!=audit:raise ValueError('README context differs')
    for name,expected in m['workbench_files_sha256'].items():
        if digest(root/WORKBENCH/name)!=expected:raise ValueError('Workbench changed')
    for name,expected in m['linked_artifacts_sha256'].items():
        if digest(root/name)!=expected:raise ValueError('reader changed')
    return dict(verified=True,replayed=replay,selection_id=record['selection_id'],evaluation_id=record['evaluation_id'],
       city_count=citycheck['city_count'],city_performance_packages_written=0,native_controls=natives['controls']['controls'],exports=delivery,**FLAGS)

def build(root=ROOT,force=False,output=None):
    root=Path(root);output=root/OUTPUT if output is None else Path(output);lock=root/'build/v06-development/build.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if not force:
            try:
                value=verify(output,root=root,replay=False)
                from .reader import build as reader
                reader(root=root,check=True);return dict(value,cached=True)
            except(ValueError,OSError,KeyError):pass
        value=publish(output,root=root)
        from engineering.maglev_research import readme_context
        readme_context.write_owned(root);audit=readme_context.audit(root)
        if not audit['current']:raise ValueError('README context: '+'; '.join(audit['errors']))
        write(output/'readme-coverage.json',(json.dumps(audit,sort_keys=True,indent=2)+'\n').encode());write(output/'readme-coverage.md',readme_context.markdown(audit).encode());seal(output,root)
        from .reader import build as reader
        reader(root=root);seal(output,root)
        return dict(value,verification=verify(output,root=root),cached=False)
