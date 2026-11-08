"""Small decision-facing dossier backed by complete source-bound run packets."""
from pathlib import Path
from copy import deepcopy
import gzip,json,shutil
from engineering.station_rail.common import identity,encoded,digest
from engineering.design_search import requirement_policy
from . import ROOT,FLAGS,coordinator,fleet,cost,civil_reference
from . import fleet_bridge
from engineering.station_pair import native_bridge as journey_bridge

OUTPUT='docs/design-engine/reconciled-pilot'


def seal(v,key='evaluation_id'):
    v[key]=identity(v);return v


def summary(study):
    rows=[]
    for r in study['records']:
        journeys=[d['journey'] for d in r['result']['departures'] if d['journey']]
        method=r['cost']['full_scope']['methods'][0]
        rows.append(dict(experiment=r['experiment'],recovery_enabled=r['enabled'],
            service_id=r['service']['evaluation_id'],headway_s=r['service']['headway_s'],
            opposite_phase_s=r['service']['opposite_phase_s'],trainsets=r['service']['total_trainsets'],
            active_trainsets=r['service']['active_trainsets'],spare_trainsets=r['service']['spare_trainsets'],
            planning_capacity_pphpd=r['service']['planning_capacity_pphpd'],
            arrivals=r['result']['normal_arrivals'],requested=r['result']['requested_departures'],
            maximum_journey_s=max((j['elapsed_s'] for j in journeys),default=None),
            maximum_moving_jerk_m_s3=max((j['maximum_absolute_jerk_m_s3'] for j in journeys),default=None),
            maximum_thermal_proxy_C=r['result']['maximum_thermal_proxy_temperature_c'],
            grid_traction_kwh=r['result']['ledger']['grid_traction_energy_j']/3.6e6,
            capture_kwh=r['result']['ledger']['capture_work_j']/3.6e6,
            relaunch_kwh=r['result']['ledger']['delivered_launch_work_j']/3.6e6,
            initial_store_kwh=r['result']['ledger']['initial_store_j']/3.6e6,
            final_store_kwh=r['result']['ledger']['final_store_j']/3.6e6,
            model_screen=r['assessment']['nominal_model_screen'],screen_tests=r['assessment']['tests'],
            cost=dict(installed_capital_usd=method['installed_capital_usd'],
                capital_per_route_km_usd=method['capital_per_route_km_usd'],
                whole_life_NPV_usd=method['whole_life_NPV_usd'],
                known_lifecycle_subtotal_usd=method['known_whole_life_subtotal_usd']),
            fleet_evaluation_id=r['result']['evaluation_id'],cost_evaluation_id=r['cost']['full_scope']['evaluation_id']))
    return dict(schema='osr-railway-closure-summary/1',study_id=study['study_id'],bundle=study['bundle'],
                route_km=1.5,stations=2,rows=rows,body=study['body_summary'],
                installed_load_cases=study['installed']['load_cases'],
                civil=dict(candidate_id=study['civil']['civil_candidate_id'],screens=study['civil']['screens'],
                    cost=study['civil']['cost'],lifting=study['civil']['lifting'],quantities=study['civil']['quantities'],
                    native_reference=study['civil_native_reference']),
                battery_alternatives=study['battery_alternatives'],frontier=frontier(study),
                price_maturity='Calculated low/base/high scenarios; no supplier, site or financing verification',
                status=dict(execution='complete',outline='calculated under explicit assumptions',
                    engineering='evidence pending',prototype='not physically validated',release='not approved'),
                integrated_selection=None,priced_cities_replaced=False,**FLAGS)


def frontier(study):
    tasks=[
        ('powered-bogie','Detail real motor/gear housings, shaft offsets, revised bogie frame and mounts; resolve clashes before installed admission','geometry and supplier interface'),
        ('wheel-rail-profile','Verify actual wheel tread/flange profiles, contact, clearances, wear and derailment protection; nominal rail-head-centre alignment is a declared geometry hypothesis','running gear analysis and physical tests'),
        ('body-joints','Independently evaluate tapered underframe, welds, local buckling, fatigue, crash and load-transfer joints','native analysis and physical tests'),
        ('civil-bearing-detail','Verify real bearing contact, segment joints, cracking, prestress, fatigue and construction stages; an elastic method comparison does not establish these','native analysis and physical tests'),
        ('terminal-control','Resolve actual turnout geometry, single-sided platform access, interlocking, standstill jerk, brake/adhesion/WSP and degraded rescue','dynamics and physical tests'),
        ('storage-mechanism','Replace generic transfer ceilings with measured force-stroke/pressure-flow/contact, reset and hot repeated-duty characteristics','mechanism drawings and tests'),
        ('storage-dispatch','Explore explicit minimum-worthwhile release and early-disengagement policies; positive residual energy can occupy a bank and bypass a later capture','control/resource evaluation'),
        ('electrical','Verify converter/collector short-circuit protection, conductor ampacity, battery hot-current/cooling/fire behaviour and station peak duty','detailed design and tests'),
        ('manufacturing-release','Replace proposed stock/envelopes with controlled mating drawings, tolerances, qualified procedures, fixtures and inspection release','engineering review'),
        ('city-application','Carry an explicitly selected complete configuration into city-specific grades, surveys, demand, utilities and ground; do not multiply pilot costs into cities','site evidence and user-visible selection')]
    return dict(purpose='Required next engineering work, separate from completed outline calculations and any integrated selection',
                tasks=[dict(id=k,task=text,dependency=dependency,status='open') for k,text,dependency in tasks],
                source_candidate_id=study['bundle']['candidate_id'],physical_accepted=False)


def requirement_context(study):
    criteria={k:deepcopy(v) for k,v in requirement_policy.catalogue()['criteria'].items() if v['category']=='mandatory_obligation'}
    return dict(schema='osr-railway-closure-requirements/1',candidate_id=study['bundle']['candidate_id'],
        assessments=[requirement_policy.assess({},criteria,candidate_id=study['bundle']['candidate_id'])],
        interpretation='Missing authenticated physical evidence stays open. Declared nominal journey/jerk/body/civil screens are research targets, never automatic qualification.',**FLAGS)


def readme(study):
    s=summary(study);lines=[]
    native=study['civil_native_reference']
    archive=native.get('archive_file','civil-final-load01-proof.tar.gz')
    if native['applicable']:
        r=native['report'];u=r['results'][-1]['fieldcraft']['displacement_m'][2]*1000
        changes=' / '.join(f"{x*100:.4f}%" for x in native['refinement_changes'])
        civil_text=f'''The **exact current normal-base load and corrected wheel/rail interface** have a source-bound three-mesh elastic comparison. Rotation-free bearing lines give {abs(u):.4f}mm fine-mesh deflection, refinement changes {changes}, passing the unchanged5% target. FieldCraft and CalculiX agree closely. [Complete compact proof](civil-native/{archive}) includes raw inputs, meshes, solver outputs, resource logs and sources. Earlier mismatched-gauge and biased support-patch results remain historical; their evidence is not inherited. Rotation-free line supports, gross elastic concrete and one native load pose do not verify real bearing contact, segment joints, cracking, prestress, fatigue or high/crowd3D cases.'''
    else:
        civil_text='This variant has no exact matching native civil result; earlier or different-load FEM is not inherited. Current loads need their own mesh, contact and convergence evidence.'
    for r in s['rows']:
        if r['experiment'] not in ('nominal','recovery-disabled'):continue
        price=r['cost']['installed_capital_usd']['base']/1e6
        jerk='—' if r['maximum_moving_jerk_m_s3'] is None else f"{r['maximum_moving_jerk_m_s3']:.3f}"
        lines.append(f"| {r['headway_s']:g}s / phase{r['opposite_phase_s']:g}s | {'on' if r['recovery_enabled'] else 'off'} | {r['active_trainsets']}+{r['spare_trainsets']} | {r['arrivals']}/{r['requested']} | {jerk} | ${price:.2f}m | {'pass' if r['model_screen'] else 'held'} |")
    return f'''# Reconciled railway research pilot

[Open the decision view](index.html) · [Download complete calculated study](study.json.gz) · [Manufacturing BOM](vehicle/bom.csv) · [Installed assembly model](vehicle/assembly.glb)

**Calculated outline complete under explicit assumptions. Engineering evidence pending.**
One physical bundle connects a six-car research body, counted drive/interface additions, axle reactions, civil quantities, terminal layout, counted fleet, causal energy-store simulation and all fourteen lifecycle scopes. The passive v0.6 reference remains unchanged; this powered-wheel research comparison does not select installed propulsion.

The underframe batch retains both failures and alternatives. A constant-depth girder clashed with the bogies. Shallow-end revisions were recalculated; the aluminium option failed its declared crowd roll target, so this packet details the eligible steel family. Joint stiffness/material properties and functional allocations remain provisional. No roof stiffness is credited. Every removed passive-secondary component is explicit in this separate research body.

The wheel/rail interface now carries an explicit inner-face gauge, nominal rail-head width and common contact-centre datum through vehicle placements, civil rails, fasteners and numerical load patches. Wheel envelopes have their axle direction along the track's transverse axis. These definitions correct the earlier inconsistent rail spacing and wheel-envelope orientation; actual tread/flange profiles and contact behaviour still require engineering verification.

![Calculated civil assembly](civil-assembly.svg)

| Headway / opposite departure phase | Recovery | Active+reserve trains | Arrivals | Moving jerk m/s³ | Complete pilot base capital | Nominal model screen |
|---|---|---:|---:|---:|---:|---|
'''+ '\n'.join(lines)+f'''

The 1.5km pilot has two stations and two running tracks. Additional platform, pocket and crossover track, four turnouts, station access, grid feeds, backup chargers, depot, rescue, land/utilities and renewals are priced explicitly. No extra blanket bulk discount or uncommitted future-order credit is applied. Manufacturing versus purchasing compares declared setup scopes, not supplier quotations. Financing, taxes, customs and FX remain separate project-finance layers.

Energy stores start empty in nominal cases. Release substitutes for independently available grid traction with finite slew; it cannot add free force. Shared-bank collisions or unready stores bypass recovery. Actual train identities, reverse stopping offsets, route occupancy and full-grid thermal proxies carry through the timetable. Faults remain visible. Finite-run energy extrapolation, terminal maneuvers, voltage/loss/cooling assumptions and electronics allowances are disclosed in the full study; they do not establish qualified daily operation.

The study has a new whole-railway identity. {civil_text}

Full installed motor shapes, joints, fatigue, emergency braking, station mechanical force/flow maps, hot electrical characteristics and site conditions remain open.

All original part origins are retained or explicitly superseded, with materials, quantities, process/assembly plans, proposed locations and positive reserves. Stock blanks and equipment envelopes are distinguished from finished solids. These are research manufacturing drafts, not released production drawings or work orders.

No city is silently repriced from this pilot. [Remaining engineering tasks](frontier.json) identify the exact work needed before city-specific adoption or physical qualification. [Mandatory requirement context](requirements.json) keeps unsupported obligations open.

```bash
./osr design closure run --output /path/to/fresh/private/run
./osr design closure publish --run /path/to/private/run --output /path/to/fresh/dossier
./osr design closure verify
```

Study `{study['study_id']}`. Whole bundle `{study['bundle']['candidate_id']}`.
Physical acceptance, manufacturing and operating release are false.
'''


def artifacts(study,root=ROOT,*,include_study=True):
    values={'summary.json':encoded(summary(study)),
            'README.md':readme(study).encode(),'frontier.json':encoded(frontier(study)),
            'requirements.json':encoded(requirement_context(study))}
    if include_study:values['study.json.gz']=gzip.compress(encoded(study),mtime=0)
    for name in ('index.html','app.css','app.js'):values[name]=(Path(root)/'engineering/railway_closure/web'/name).read_bytes()
    return values


def study_value(raw):
    """Authenticate canonical JSON independently of the gzip implementation.

    The publication manifest still authenticates the exact compressed bytes.
    Gzip headers and deflate streams may differ across supported runtimes.
    """
    data=gzip.decompress(raw);value=json.loads(data)
    if data!=encoded(value):raise ValueError('Canonical study encoding differs')
    return value


def publish(run,*,root=ROOT,output=None,native_cad_evidence=None):
    root=Path(root);run=Path(run);out=root/OUTPUT if output is None else Path(output)
    if out.exists():raise ValueError('Fresh publication folder required')
    m=json.loads((run/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Run manifest differs')
    for n,want in m['files_sha256'].items():
        if digest(run/n)!=want:raise ValueError('Run artifact changed: '+n)
    study=json.loads(gzip.decompress((run/'study.json.gz').read_bytes()))
    if study['source_sha256']!=coordinator.sources(root):raise ValueError('Source changed; run cannot be published as current')
    out.mkdir(parents=True)
    for name,raw in artifacts(study,root).items():(out/name).write_bytes(raw)
    shutil.copytree(run/'vehicle',out/'vehicle')
    if study['civil_native_reference']['applicable']:
        target=out/'civil-native';target.mkdir()
        name=study['civil_native_reference'].get('manifest_file',civil_reference.MANIFEST)
        proof=civil_reference.verify(root=root,manifest_name=name)
        for filename in (name,proof['manifest']['archive_file']):
            shutil.copyfile(root/civil_reference.FOLDER/filename,target/filename)
    for group,build_name,runs_name in (('serial','cycle-build.json','native-runs'),('fleet','fleet-build.json','fleet-runs')):
        target=out/'native'/group;target.mkdir(parents=True)
        for name in (build_name,'native-build.json','native-build.log'):
            shutil.copyfile(run/group/name,target/name)
        for folder in (run/group/runs_name).iterdir():
            if not folder.is_dir():continue
            destination=target/runs_name/folder.name;destination.mkdir(parents=True)
            for name in ('receipt.json','input.json.gz','output.json.gz','execution.json','stderr.log'):
                path=folder/name
                if path.is_file():shutil.copyfile(path,destination/name)
    (out/'run-manifest.json').write_bytes((run/'manifest.json').read_bytes())
    if native_cad_evidence is not None:
        source=Path(native_cad_evidence)
        body=json.loads(gzip.decompress((out/'vehicle/installation.json.gz').read_bytes()))
        verify_cad(source,body,root)
        target=out/'native-cad';target.mkdir()
        names=['verification.json','case.json','commands.json',
               'solidcraft/assembly.sc','solidcraft/assembly.step','solidcraft/results.json',
               'solidcraft/execution.json','solidcraft/invocation.json','solidcraft/usage.json',
               'independent-freecad/result.json','independent-freecad/measurement.json',
               'independent-freecad/command.json','independent-freecad/resource.json','independent-freecad/worker.py']
        for name in names:
            p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,p)
    for n in ('civil.json','civil-assembly.json','civil-assembly.svg','bundle.json','axle-loads.json','usage.json'):
        shutil.copyfile(run/n,out/n)
    files={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}
    manifest=dict(schema='osr-railway-closure-publication/1',study_id=study['study_id'],
                  source_sha256=study['source_sha256'],files_sha256=files,run_manifest_id=m['manifest_id'],**FLAGS)
    manifest['manifest_id']=identity(manifest);(out/'manifest.json').write_bytes(encoded(manifest))
    return verify(root=root,output=out)


def verify_cad(folder,body,root):
    from engineering.vehicle_installation import model,underframe,export
    from engineering.design_search.craft_backends import solidcraft
    folder=Path(folder);r=json.loads((folder/'verification.json').read_bytes())
    if (r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'})
        or r['candidate_id']!=body['candidate_id'] or r['installation_evaluation_id']!=body['evaluation_id']
        or r['source_sha256']!=model.sources(root)):
        raise ValueError('Native CAD belongs to a different body/source evaluation')
    if digest(folder/'solidcraft/assembly.step')!=r['step_sha256'] or digest(folder/'solidcraft/assembly.sc')!=r['native_sha256']:
        raise ValueError('Native CAD geometry bytes differ')
    expected=underframe.cad_case(body)
    recorded=json.loads((folder/'case.json').read_bytes())
    if recorded!=expected or r['component_geometry_id']!=expected['component_geometry_id']:
        raise ValueError('Native CAD physical definition differs')
    measured=solidcraft.parse_measurements(json.loads((folder/'solidcraft/results.json').read_bytes()))
    reference=json.loads((folder/'independent-freecad/result.json').read_bytes())
    if export._compare(expected,measured)!=r['diagnostic'] or export._compare(expected,reference,associate=True)!=r['independent_exact']:
        raise ValueError('Native CAD/independent B-rep comparison differs')
    return True


def verify_native(study,out,root):
    """Resolve every cited result to actual immutable request/output receipts."""
    inventories={}
    for group,build_name,runs_name in (('serial','cycle-build.json','native-runs'),('fleet','fleet-build.json','fleet-runs')):
        folder=out/'native'/group;build=json.loads((folder/build_name).read_bytes())
        if build['receipt_id']!=identity({k:v for k,v in build.items() if k!='receipt_id'}):raise ValueError('Native build seal differs')
        if build['source_sha256']!=journey_bridge.sources(root):raise ValueError('Native source epoch differs')
        cases={}
        for path in (folder/runs_name).iterdir():
            receipt=json.loads((path/'receipt.json').read_bytes())
            if receipt['receipt_id']!=identity({k:v for k,v in receipt.items() if k!='receipt_id'}):raise ValueError('Native execution seal differs')
            execution=json.loads((path/'execution.json').read_bytes())
            if receipt['exit_code']!=0 or receipt['failure'] is not None or any(execution.get(k)!=receipt.get(k) for k in execution):
                raise ValueError('Native execution was unsuccessful or its outcome differs')
            if receipt['build_receipt_id']!=build['receipt_id']:raise ValueError('Native result belongs to another build')
            input_key='input_sha256' if group=='fleet' else 'input_gzip_sha256'
            if digest(path/'input.json.gz')!=receipt[input_key] or digest(path/'output.json.gz')!=receipt['output_sha256']:
                raise ValueError('Native request/output bytes changed')
            q=json.loads(gzip.decompress((path/'input.json.gz').read_bytes()))
            r=json.loads(gzip.decompress((path/'output.json.gz').read_bytes()))
            if len(q['cases'])!=len(r['cases']):raise ValueError('Native case inventory differs')
            for request,result in zip(q['cases'],r['cases']):
                if result['id']!=request['id'] or result['candidate_id']!=request['candidate_id']:raise ValueError('Native case identity differs')
                key=(receipt['receipt_id'],identity(request));result_id=identity(result)
                if key in cases and cases[key]!=result_id:raise ValueError('Conflicting duplicate native result')
                cases[key]=result_id
        inventories[group]=cases
    pairs=[('serial',q,r) for q,r in zip(study['serial_requests'],study['serial_results'])]
    pairs += [('fleet',record['request'],record['result']) for record in study['records']]
    if len(study['serial_requests'])!=len(study['serial_results']):raise ValueError('Serial result inventory differs')
    for group,q,r in pairs:
        if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Annotated native result seal differs')
        key=(r['native_receipt_id'],identity(q))
        raw={k:v for k,v in r.items() if k not in ('native_receipt_id','native_input_id','evaluation_id')}
        if r['native_input_id']!=identity(q) or inventories[group].get(key)!=identity(raw):
            raise ValueError('Claimed native result does not resolve to preserved execution output')
    return True


def verify(*,root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    if any(p.is_symlink() for p in (out,*out.parents)) or any(p.is_symlink() for p in out.rglob('*')):
        raise ValueError('Ordinary bounded publication required')
    m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Publication manifest differs')
    files={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}
    if files!=m['files_sha256'] or m['source_sha256']!=coordinator.sources(root):raise ValueError('Publication source/artifact changed')
    study=study_value((out/'study.json.gz').read_bytes())
    if study['study_id']!=identity({k:v for k,v in study.items() if k!='study_id'}) or study['study_id']!=m['study_id']:
        raise ValueError('Study seal differs')
    run=json.loads((out/'run-manifest.json').read_bytes())
    if (run['manifest_id']!=identity({k:v for k,v in run.items() if k!='manifest_id'})
        or run['manifest_id']!=m['run_manifest_id'] or run['study_id']!=study['study_id']):
        raise ValueError('Native run/publication provenance differs')
    if any(study.get(k) is not v for k,v in FLAGS.items()) or study['integrated_selection'] is not None:
        raise ValueError('Research publication cannot grant release or integrated selection')
    verify_native(study,out,root)
    if study['civil_native_reference']['applicable']:
        proof=civil_reference.verify(out/'civil-native',root=root,
            manifest_name=study['civil_native_reference'].get('manifest_file',civil_reference.MANIFEST))
        axles=json.loads((out/'axle-loads.json').read_bytes())
        if (proof['report']!=study['civil_native_reference']['report']
            or proof['manifest']['civil_evaluation_id']!=study['civil']['evaluation_id']
            or proof['manifest']['input_load_evaluation_id']!=axles['evaluation_id']):
            raise ValueError('Current civil proof belongs to a different candidate/load evaluation')
    for name,raw in artifacts(study,root,include_study=False).items():
        if (out/name).read_bytes()!=raw:raise ValueError('Generated decision view differs: '+name)
    body=json.loads(gzip.decompress((out/'vehicle/installation.json.gz').read_bytes()))
    if (out/'native-cad').exists():verify_cad(out/'native-cad',body,root)
    for record in study['records']:
        q,r,s=record['request'],record['result'],record['service']
        if r['native_input_id']!=identity(q) or r['candidate_id']!=study['bundle']['candidate_id']:
            raise ValueError('Mixed native evidence')
        if record['assessment']!=fleet.screen(r,s):raise ValueError('Fleet screen differs')
        if record['terminal_calendar']!=fleet.terminal_check(r,s):raise ValueError('Detailed terminal calendar differs')
        expected=None
        expected_hold=None
        if record['experiment'] in ('nominal','recovery-disabled') and record['assessment']['nominal_model_screen']:
            try:expected=fleet.energy(r,q,s,root=root)
            except fleet.EnergyDomainHold as exc:expected_hold=str(exc)
        if record['energy']!=expected or record['energy_hold']!=expected_hold:raise ValueError('Timetable/energy binding differs')
        actual=cost.evaluate(body,study['installed'],study['civil'],s,energy=expected,root=root)
        if actual!=record['cost']:raise ValueError('Disjoint cost ledger differs')
    return dict(verified=True,study_id=study['study_id'],candidate_id=study['bundle']['candidate_id'],
                fleet_cases=len(study['records']),**FLAGS)
