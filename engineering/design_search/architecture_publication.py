"""Publish replayable architecture research and bounded component evidence.

No native method fixture, analytical journey or prototype plan confers physical
acceptance. Large regenerable fields stay local with explicit retained/omitted
hash indexes; historical producer bytes travel with the published evidence.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from hashlib import sha256
import gzip,io,json,shutil,subprocess,tarfile,tempfile
from engineering.station_rail import ROOT,vehicle,civil
from engineering.station_rail.common import encoded,identity,digest
from . import railway_architecture as engine,capabilities

PRODUCER='engineering/design_search/architecture_publication.py'
OUTPUT='docs/design-engine/v06-architecture'
FLAGS=engine.FLAGS


def civil_program(spec,reference):
    rows=[]
    for cars in spec['space']['cars']:
        context=dict(mass=deepcopy(reference['mass']),physical_definition=dict(vehicle=deepcopy(reference['physical_definition']['vehicle']),support=deepcopy(reference['physical_definition']['support'])))
        context['physical_definition']['vehicle']['cars']=cars
        for family in spec['civil']['families']:
            for span in spec['civil']['span_m']:
                result=civil.alternative(context,span,family,'crowd_control')
                quantity=round(spec['scenario']['directional_ring_length_m']/span)
                rows.append(dict(cars=cars,load_context_id=identity(context),reference_vehicle_id=reference['candidate_id'],
                    model=result,ring_spans=quantity,counted_route_concrete_m3=quantity*result['concrete_m3'],
                    counted_route_steel_kg=quantity*result['counted_steel_kg'],
                    support_locations_for_closed_ring=quantity,
                    complete_pier_bearing_foundation_quantities=None,actual_installed_cost_USD=None,
                    scope='Crowd-sized reference vehicle/accounted mass only. New traction, articulation and equipment require updated loads before civil selection.',**FLAGS))
    process=[dict(operation=i,stage=stage,prerequisite=i-1 if i else None,duration_s=None,crew_hours=None,material_available_date=None,
        release='Authenticated inspection, surveyed geometry or measured material/assembly evidence required',**FLAGS)
        for i,stage in enumerate(('survey and geotechnical investigation','foundation installation and inspection','pier/headstock fabrication and erection',
            'bearings and temporary stability','precast curing and measured-strength release','transport and lifting with actual radius/capacity',
            'rails, gauge control, containment and access','station motor/supply and platform interfaces','alignment, inspection and protected testing'))]
    support_options=[]
    for cars in spec['space']['cars']:
        normal_mass=reference['mass']['accounted_cap_loaded_kg_per_car']*cars
        conventional=2*cars;shared=cars+1
        support_options.append(dict(cars=cars,conventional_bogies=conventional,shared_bogie_hypothesis=shared,
            reference_gross_bogie_account_difference_kg=(conventional-shared)*6730/2,
            uniform_comparison_axle_load_kg_conventional=normal_mass/(2*conventional),
            uniform_comparison_axle_load_kg_shared=normal_mass/(2*shared),
            bogie_account_basis='6730kg/car for two reference bogies; gross comparison account, not supplier-priced installed savings',
            net_installed_mass_delta_kg=None,new_articulation_and_body_reinforcement_mass_kg=None,
            native_support_geometry_and_load_paths_available=False,complete_maintenance_cost_USD=None,**FLAGS))
    return dict(schema='osr-architecture-civil-and-construction/1',alternatives=rows,construction_sequence=process,
        ground_scenarios=spec['civil']['ground_allowable_kPa_hypotheses'],foundation_families=spec['civil']['foundation_families'],
        support_options=support_options,foundation_geometry=None,settlement_lateral_seismic_fatigue='unknown',
        full_route_cost_USD=None,lowest_concrete_is_not_installed_cost=True,**FLAGS)


def prototype_program(registry,reference_id):
    plans={}
    extra={
      'M1':dict(test_articles=['Source-bound motor section and passive secondary','Six-axis joint specimens and representative door/window panel','Actual brake/actuator/thermal and adhesion test article'],
        measurements=['thrust/normal forces and moments','gap, current, voltage, speed and temperatures','all-axis compliance, strain, modal response and joint slip','brake force, fade, response and stopping'],
        conditions=['empty and declared ballast equivalents','cold/normal/hot measured conditions','repeated duty, manufacturing variation and degraded cases']),
      'M2':dict(test_articles=['One inventoried passive carriage and independent brakes','Finite launch section and protected receiving/overrun','Separately identified rescue/tow equipment'],
        measurements=['equipped mass/CG/inertia','repeated launch, coast and stop trajectories','battery/thermal duty and safe-stop response','off-zone holding, coupling and recovery'],
        conditions=['Initially unoccupied and ballast loaded','Staged speed envelope, initially1/3/5m/s as proposed tests','Reviewed fault injection after validated lower-energy tests']),
      'M3':dict(test_articles=['Full-sized equipped vehicle and representative guideway/stations','Protected1.5/2/3km route configurations','Formation/coupler and degraded-service extensions'],
        measurements=['same-candidate journey/force/current/heat records','protected headway and accessible boarding','receiving/station/communications/brake failure responses','evacuation and recovery operation'],
        conditions=['Empty and normal ballast equivalents; crowd cases only under reviewed test conditions','No occupied service inferred from simulation','Actual surveyed grades, weather and supply resources']),
    }
    for name,definition in registry['measurement_plans'].items():
        p=dict(schema='osr-prototype-test-plan/1',milestone=name,reference_candidate_id=reference_id,scope=definition['scope'],required=definition['required'],
            **extra[name],specimen_geometry_and_lot_ids=[],instrument_calibration_records=[],raw_measurement_files=[],
            uncertainty_model=None,approved_correlation_limits=None,independent_review=None,
            manufacturing_release=False,operating_release=False,physical_accepted=False,
            completion='unknown',scope_warning='A plan and numerical fixture are not physical measurements or qualification')
        p['plan_id']=identity(p);plans[name]=p
    return dict(schema='osr-staged-prototype-program/1',plans=plans,physical_milestones_completed=0,**FLAGS)


def assembly_program(reference_id):
    systems={
      'body':['ply/section schedule and core orientation','mould/extrusion segments and actual joints','bogie hardpoints, inserts, trim and repairs'],
      'glazing':['pane grade and thickness','seal/retention/frame geometry','thermal movement, replacement and impact/fire evidence'],
      'doors':['frame and moving leaves','actuators, guides, locks and emergency release','one-sided platform/egress compatibility'],
      'benches':['seat shells and occupied loads','structural mounts/fasteners','cleaning and replacement access'],
      'HVAC':['actual50C capacity and electrical duty','duct/filter/drainage/insulation routes','access, replacement and redundancy'],
      'solar':['flush mounts and sealing','wiring/connector/protection routes','thermal cycling and panel replacement'],
      'electrical':['distribution and isolation','conduits, connectors, protection and cooled batteries','inspection and emergency endurance'],
      'runninggear':['spring/bearing/brake/stop stock','actual load paths and tolerances','wheelset, brake and new-drive maintenance'],
      'propulsion':['finite primary/secondary and cooling','inverter/supply/section switching','clearance, inspection and removal'],
    }
    return dict(schema='osr-architecture-installed-assembly-contract/1',reference_candidate_id=reference_id,
        component_requirements=[dict(system=s,required=r,structural_participation='explicit-per-part required',
            assembly_prerequisites=None,tools=None,tolerances=None,inspection=None,removal_path=None,
            complete_installed_mass_kg=None,unit_price_USD=None,qualified=False) for s,r in systems.items()],
        retention_policy='Primary load-bearing joints need validated load paths; removable service-panel clips require separate positive retention and are not structural substitution',
        EBOM_MBOM_IFC_ERP_status='Research component/occurrence contracts only. No complete new-architecture installed twin or ERP manufacturing release.',**FLAGS)


def _source_bytes(root,name,wanted):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts:raise ValueError('Ordinary source path required')
    current=Path(root)/path
    if current.is_file() and digest(current)==wanted:return current.read_bytes(),True
    epochs=Path(root)/'build/v06-architecture/nonlinear-source-epochs'
    for p in epochs.rglob(path.name):
        if p.is_file() and digest(p)==wanted:return p.read_bytes(),False
    commits=subprocess.check_output(['git','log','--all','--format=%H','-n','40','--',name],cwd=root,text=True).splitlines()
    for commit in commits:
        r=subprocess.run(['git','show',commit+':'+name],cwd=root,capture_output=True)
        if r.returncode==0 and sha256(r.stdout).hexdigest()==wanted:return r.stdout,False
    raise ValueError('Historical source bytes unavailable: '+name+' '+wanted)


def _archive(folder):
    """Retain inputs, logs and raw textual responses; index bulky fields."""
    folder=Path(folder);buf=io.BytesIO();kept={};omitted={}
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for p in sorted(folder.rglob('*')):
            if p.is_symlink():raise ValueError('Ordinary native files required')
            if not p.is_file():continue
            name=p.relative_to(folder).as_posix();h=digest(p)
            if p.suffix in ('.msh','.pre','.res','.pos','.frd','.12d','.eig'):omitted[name]=h;continue
            raw=p.read_bytes();kept[name]=h;t=tarfile.TarInfo(name);t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
        raw=encoded(dict(retained_sha256=kept,omitted_sha256=omitted,raw_directory=str(folder),remote_storage=None,
            scope='Omitted raw bytes require local access or source/tool-matched regeneration',**FLAGS))
        t=tarfile.TarInfo('archive-index.json');t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
    value=gzip.compress(buf.getvalue(),mtime=0)
    if len(value)>32*1024**2:raise ValueError('Bounded32MiB component evidence package required')
    return value


def native_packages(out,root):
    roots=['joint-benchmarks-r1','joint-finite-pilot-r1','joint-refinement-r2','joint-control-r2','nonlinear-pilot/v1','nonlinear-pilot/v2','nonlinear-native-r1','nonlinear-portable-r2',
           'finite-body-coarse-r1','finite-body-refinement-r2','finite-body-fine-r3','finite-body-resource-r4']
    rows=[];bindings={};snapshots={};dest=out/'native';dest.mkdir()
    for raw_name in roots:
        folder=Path(root)/'build/v06-architecture'/raw_name
        name=raw_name.replace('/','-')
        if not (folder/'manifest.json').is_file():continue
        package_sources={}
        for mf in sorted(folder.rglob('manifest.json')):
            m=json.loads(mf.read_bytes())
            if m['manifest_id']!=identity({n:v for n,v in m.items() if n!='manifest_id'}):raise ValueError('Native manifest identity differs: '+str(mf))
            actual={p.relative_to(mf.parent).as_posix():digest(p) for p in mf.parent.rglob('*') if p.is_file() and p!=mf}
            if actual!=m['files_sha256']:raise ValueError('Native files differ: '+str(mf))
            if m.get('physical_accepted') is not False or any(m.get(n) is True for n in ('engineering_accepted','manufacturing_release','operating_release')):raise ValueError('Component research cannot grant railway release')
            for path,h in m.get('source_sha256',{}).items():
                raw,current=_source_bytes(root,path,h);package_sources.setdefault(path,[])
                if h not in package_sources[path]:package_sources[path].append(h)
                if current:bindings[path]=h
                else:
                    target=out/'historical-sources'/h;target.parent.mkdir(exist_ok=True)
                    if not target.exists():target.write_bytes(raw)
                    snapshots[h]=dict(repository_path=path,artifact=target.relative_to(out).as_posix())
        result_file=folder/('summary.json' if (folder/'summary.json').is_file() else 'result.json');r=json.loads(result_file.read_bytes())
        if r.get('physical_accepted') is not False:raise ValueError('Native result disposition differs')
        if 'evaluation_id' in r and r['evaluation_id']!=identity({n:v for n,v in r.items() if n!='evaluation_id'}):raise ValueError('Native result identity differs')
        (dest/(name+'.tar.gz')).write_bytes(_archive(folder))
        rows.append(dict(name=name,archive='native/'+name+'.tar.gz',raw_result=r,source_sha256_by_path=package_sources,
            evidence_context_id=identity(dict(result_id=r.get('evaluation_id'),manifest_sha256=digest(folder/'manifest.json'),source=package_sources)),
            scope='Numerical method/control or ideal body-model research only; consult exact case and validity',**FLAGS))
    smoke=Path(root)/'build/v06-architecture/joint-smoke-r1'
    if (smoke/'smoke-result.json').is_file():
        record=json.loads((smoke/'smoke-result.json').read_bytes());name='engineering/design_search/joint_models.py';h=record['source_sha256']
        raw,current=_source_bytes(root,name,h);target=out/'historical-sources'/h;target.parent.mkdir(exist_ok=True);target.write_bytes(raw)
        snapshots[h]=dict(repository_path=name,artifact=target.relative_to(out).as_posix())
        (dest/'joint-smoke-r1.tar.gz').write_bytes(_archive(smoke))
        rows.append(dict(name='joint-smoke-r1',archive='native/joint-smoke-r1.tar.gz',raw_result=record,
            original_manifest_absent=True,source_sha256_by_path={name:[h]},evidence_context_id=identity(record),
            scope='Unsealed first smoke/parser failure. Wrapper retains exact raw bytes and historical producer; no original producer manifest or acceptance is invented.',**FLAGS))
    return rows,bindings,snapshots


def summary(value,native):
    by={c['case_id']:c for c in value['cases']};families=[]
    for family in value['specification']['families']:
        rr=[r for r in value['results'] if by[r['case_id']]['family_id']==family]
        families.append(dict(family_id=family,label=value['capability_registry']['families'][family]['label'],cases=len(rr),
            target_reached_at_comparison_mass=sum(r['screens']['analytical_reach']=='pass' for r in rr),
            stalled=sum(r['screens']['analytical_reach']=='fail' for r in rr),numerical_resource_holds=sum(r['screens']['analytical_reach']=='unknown' for r in rr),
            serial_berth_exceedances=sum(r['screens']['serial_berth_target']=='fail' for r in rr),
            physical_journeys=0,complete_cost_USD=None,integrated_qualified=False))
    return dict(schema='osr-railway-architecture-summary/1',campaign_id=value['campaign_id'],contract_id=value['contract_id'],
        evaluation_cases=len(value['cases']),physical_definitions=value['distinct_physical_candidates'],requirement_contexts=value['distinct_requirement_contexts'],
        generations=value['generations'],families=families,native_evidence_packages=len(native),physical_journeys=0,
        integrated_selection=value['integrated_selection'],development_default_changed=False,city_performance_packages_written=0,**FLAGS)


def readme(s,native):
    lines=['# Whole-railway architecture research','',
      'OpenSourceRail seeks simple, locally repairable transport at low whole-life cost. This umbrella campaign keeps v0.6 as the selected research reference and challenges its propulsion, speed, formation, powered-track and guideway hypotheses under separately identified configurations. Safety, passenger protection and accessibility remain mandatory holds until supported.','',
      f"The campaign executes **{s['evaluation_cases']} analytical cases**, **{s['physical_definitions']} distinct physical definitions** and **{s['generations']} generations**. It generates definitions first, checks necessary demand/geometry/recovery bounds, retains explicit failed cases and prepares specialist/native tasks. **No complete architecture is qualified; zero physical station-to-station journeys are claimed.**",'',
      '| Family | Research arrangement | Cases | Demand target reached* | Off-zone stall* | Numerical/horizon hold |',
      '|---|---|---:|---:|---:|---:|']
    for r in s['families']:lines.append(f"| {r['family_id']} | {r['label']} | {r['cases']} | {r['target_reached_at_comparison_mass']} | {r['stalled']} | {r['numerical_resource_holds']} |")
    lines += ['',
      '*These are analytical required-force trajectories at inherited v0.6 comparison mass, not journeys driven by an available motor/brake map. Extra recovery/traction equipment remains unweighed. Invalid calculations and interrupted horizons do not generate physical rankings or geometry revisions.','',
      '## What changes and what stays mandatory','',
      'The bounded space varies 4/6/8 cars; 1.5/2/3 km station spacing; 43.2/57.6/72 km/h caps; finite station launch/receiving geometry; explicit booster/distributed sections; recovery-driven axles; battery/conductor wheel-traction supply; and box/twin/U guideway sections. The former station-only/no-onboard-traction hypothesis can change inside a research configuration. The selected v0.6 default, seating policy and city geography are preserved.','',
      'A synthetic 6 km directional ring keeps route extent explicit. Changing station density changes access service and requires a separate city/demand comparison. Formation/headway is recalculated for 8,280 offered passengers/hour/direction; protected headway remains unknown. Fleet and energy quantities are conditional on required trajectories, not validated operational performance.','',
      'Physical, requirement, evaluation, source/tool and selection identities remain separate. The same hardware can appear under different speed requirements. Stator quantity uses the geometric union of installed intervals expanded for the full train/fin envelope, including periodic overlap. Geometric overlap is never multiplied by centred thrust to invent an entry/exit force.','',
      '## Foundation checks before full-body and motor ranking','',
      'The joint work retains the two-point mechanism and unconverged point-transfer controls. Corrected finite-area fixtures check all six work-conjugate force/moment directions, energy, reciprocity and modes under genuine three-dimensional refinement. Independent review found and corrected a misplaced force reference and duplicate near-identical mesh cuts; previous source-bound failures remain available. Actual joint preload, slip, bearing, fatigue, temperature and measured correlation stay open.','',
      'The resulting whole-body alternative counts 40 backing inserts, 240 finite-area bond regions and 160 complete bolt stacks, with floor-lap notches and no positive-volume overlap against retained stock. Its known-stock increase is 113.008 kg/car. The 0.3 m to 0.2 m mesh check changes vertical displacement by 1.43%, lateral by 0.98% and longitudinal by 0.41%. Normal vertical deflection is **28.018 mm**, failing the **25.6 mm** screen despite the confirmed mesh trend. The coarser crowd case is 41.115 mm and is not independently mesh-confirmed. Ideal rigid-section transfer and perfect bonds remain upper-bound hypotheses; local bearing, slip, fatigue, strength, modes and physical joint correlation remain open.','',
      'The first finer body solve exhausted its 3 GiB address-space budget. A separately recorded 5 GiB resource revision completed the same physical case without changing geometry, loads or pass limits. Both executions are retained. Numerical confirmation does not make this body structurally acceptable.','',
      'The nonlinear magnetic fixture uses a pinned generic reversible 49-point numerical reference, not selected rail steel. A nonzero airgap force is checked independently against a scalar circuit and fixed-current coenergy derivative. Real finite-primary entry/centred/exit linear controls show why overlap needs spatial evaluation. Selected-grade nonlinear moving LIM, finite-height current paths, core losses, inverter control and repeated thermal duty remain separate holds. The old linear-material screen is not relaxed.','',
      'See [native evidence index](native-index.json) and [historical producer bytes](historical-source-index.json). Inputs, logs and textual responses are retained; bulky fields are indexed for regeneration. A numerical method pass does not pass M1 physical correlation or qualify the train.','',
      '## Cost, construction and assembly','',
      '[Civil/construction comparison](civil-construction.json.gz) evaluates 27 crowd-load section/span/formation contexts and preserves moving-load, prestress, deflection and erection quantities. Piers, actual foundations, bearings, lateral/seismic loads, containment, survey, crane radius and priced construction remain incomplete. No beam is selected by concrete quantity alone. Shared-bogie counts expose higher axle-load and new body/articulation requirements without pretending gross bogie-account removal is an installed saving.','',
      'Each architecture exposes powered motor/conductor metres, stations, conditional fleet/car/drive counts, platform length and a symbolic installed-cost expression. Unknown equipment, labour, energy tariffs, renewals and recovery disruption remain unknown; no zero-cost winner or complete CAPEX/OPEX comparison is produced.','',
      '[Installed assembly contract](assembly-contract.json) requires doors, glazing, benches, HVAC ducts/drains, solar sealing, wiring, bogies and every joint to have geometry, mass, interfaces, installation/removal and QA records. Primary structural joints and removable service-panel clips remain separate roles. New architectures cannot inherit the reference CAD/ERP records as complete assembled products.','',
      '## Staged working-system milestones','',
      '[Prototype programme](prototype-program.json) defines M1 measured component/joint/brake correlation, M2 repeated passive-carriage launch/coast/stop/fault tests, and M3 full-sized station-to-station pilot/recovery. It requires instrument calibration, raw measurements, uncertainty, specimen identity and independent review. Proposed tests and simulation do not count as completed measurements. No physical milestone is marked complete.','',
      '[Campaign cases/results](campaign.json.gz) · [Summary](summary.json) · [Capability registry](capabilities.json) · [Next bounded tasks](next-tasks.json.gz) · [Execution journal](journal.json) · [Interrupted-run receipt](interruption.json) · [Publication receipt](manifest.json)','',
      '```bash','./osr design architecture run --max-cases 1  # new-job budget; exit3 if interrupted','./osr design architecture run              # exact-source resume','./osr design architecture publish','./osr design architecture verify','```','',
      'Cached jobs bind exact candidate, requirements, numerical settings and source epoch. A source change creates a new contract. Native evaluation requires the capability registry to admit a matching, independently benchmarked model in its declared domain. Unsupported material/topology combinations create implementation or measurement tasks instead of inheriting unrelated results.','']
    return '\n'.join(lines)


def comparison_table(value):
    """Same six-car/2km quantities with explicit service and mass caveats."""
    by={c['case_id']:c for c in value['cases']};chosen=[]
    for family in value['specification']['families']:
        options=[r for r in value['results'] if by[r['case_id']]['family_id']==family and by[r['case_id']]['generation']==0
            and by[r['case_id']]['physical_definition']['formation']['cars']==6 and by[r['case_id']]['physical_definition']['route']['station_spacing_m']==2000.]
        if not options:continue
        def key(r):
            c=by[r['case_id']];return(c['requirements']['speed_cap_m_s'],c['knobs'].get('launch_m',0.),c['knobs'].get('booster_m',0.),c['knobs'].get('powered_axles_per_car',0.))
        r=max(options,key=key);c=by[r['case_id']];q=r['quantity_coefficients']
        chosen.append(dict(family_id=family,case_id=c['case_id'],candidate_id=c['candidate_id'],requirement_revision=c['requirement_revision'],
            supply=c['physical_definition']['onboard']['supply'],driven_axles=c['physical_definition']['onboard']['driven_axle_count'],
            commanded_power_windows_m=c['commanded_power_windows_m'],
            commanded_speed_cap_m_s=c['requirements']['speed_cap_m_s'],demand_peak_speed_m_s=r['trajectory']['peak_speed_m_s'],
            demand_runtime_s=r['trajectory']['runtime_s'] if r['trajectory']['reachable'] else None,
            required_traction_force_N_per_car=r['trajectory']['peak_required_force_N_per_car'],
            required_mechanical_energy_kWh_train=r['trajectory']['traction_mechanical_energy_J_train']/3.6e6,
            linear_motor_track_m_per6km_ring=q['linear_motor_track_m'],conductor_track_m_per6km_ring=q['conductor_track_m'],
            conditional_purchased_cars=q['purchased_cars'],self_recovery_necessary_screen=r['screens']['self_recovery'],
            actual_available_force_N=None,complete_CAPEX_USD=None,physical_journey_completed=False,**FLAGS))
    return chosen


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);value=engine.evaluate_campaign(root)
    if value.get('state')=='interrupted':raise ValueError('Complete bounded campaign before publication')
    if out.exists():
        receipt=out/'manifest.json'
        previous=root/'build/v06-architecture/replaced-publications'/(digest(receipt) if receipt.is_file() else identity({p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}));previous.parent.mkdir(parents=True,exist_ok=True)
        if previous.exists():raise ValueError('Previous publication already retained; inspect before replacing')
        shutil.move(out,previous)
    out.mkdir(parents=True);native,native_sources,snapshots=native_packages(out,root)
    ref=vehicle.build(root);cp=civil_program(value['specification'],ref);program=prototype_program(value['capability_registry'],ref['candidate_id'])
    s=summary(value,native);folder=root/'build/v06-architecture/campaigns'/value['contract_id']
    files={'campaign.json.gz':gzip.compress(encoded(value),mtime=0),'summary.json':encoded(s),'capabilities.json':encoded(value['capability_registry']),
        'next-tasks.json.gz':gzip.compress(encoded(value['next_tasks']),mtime=0),'civil-construction.json.gz':gzip.compress(encoded(cp),mtime=0),
        'prototype-program.json':encoded(program),'assembly-contract.json':encoded(assembly_program(ref['candidate_id'])),
        'native-index.json':encoded(native),'historical-source-index.json':encoded(snapshots),'README.md':readme(s,native).encode(),
        'journal.json':(folder/'journal.json').read_bytes(),'equal_context_comparison.json':encoded(comparison_table(value))}
    interruption=root/'build/v06-architecture/umbrella-interruption-final.json'
    if not interruption.is_file():interruption=root/'build/v06-architecture/umbrella-interruption.json'
    first=json.loads(interruption.read_bytes())
    if first['contract_id']!=value['contract_id'] or first['state']!='interrupted':raise ValueError('Matching-source interruption demonstration required')
    files['interruption.json']=encoded(first)
    for name,raw in files.items():(out/name).write_bytes(raw)
    lines=['','## Example architecture trade-offs','',
        'Six cars over a 2 km leg within the same 6 km comparison ring, at inherited normal comparison mass. These are representative parameter choices, not optimised or physically validated winners. P2 uses a lower speed requirement; new equipment mass and actual available traction remain unknown.','',
        '| Family | Supply / driven axles | Required trip time | Required peak force/car | Linear motor metres/ring | Conductor metres/ring | Conditional purchased cars |',
        '|---|---|---:|---:|---:|---:|---:|']
    for row in comparison_table(value):
        trip='Held' if row['demand_runtime_s'] is None else f"{row['demand_runtime_s']:.1f} s"
        lines.append(f"| {row['family_id']} | {row['supply']} / {row['driven_axles']} | {trip} | {row['required_traction_force_N_per_car']/1000:.2f} kN | {row['linear_motor_track_m_per6km_ring']:.1f} | {row['conductor_track_m_per6km_ring']:.0f} | {row['conditional_purchased_cars']} |")
    lines += ['', '[Exact cases and requirements](equal_context_comparison.json). Removing linear motor track does not remove battery, conductor, converter, charging, braking, maintenance or recovery costs. The installed price and mass coverage are incomplete for every family.','']
    with (out/'README.md').open('a') as f:f.write('\n'.join(lines))
    sources={**value['source_sha256'],**native_sources,PRODUCER:digest(root/PRODUCER)}
    m=dict(schema='osr-architecture-publication/1',campaign_id=value['campaign_id'],source_sha256=sources,
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(out/'manifest.json').write_bytes(encoded(m));return verify(root,out,replay=False)


def verify(root=ROOT,output=None,*,replay=True):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({n:v for n,v in m.items() if n!='manifest_id'}):raise ValueError('Architecture publication identity differs')
    if any(digest(root/n)!=h for n,h in m['source_sha256'].items()):raise ValueError('Architecture publication source differs')
    if {p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}!=m['files_sha256']:raise ValueError('Architecture publication payload differs')
    value=json.loads(gzip.decompress((out/'campaign.json.gz').read_bytes()));native=json.loads((out/'native-index.json').read_bytes());s=json.loads((out/'summary.json').read_bytes())
    if value['campaign_id']!=identity({n:v for n,v in value.items() if n!='campaign_id'}) or summary(value,native)!=s:raise ValueError('Architecture campaign/summary differs')
    for record in (m,value,s):
        if any(record.get(n) is not v for n,v in FLAGS.items()):raise ValueError('Architecture research cannot grant release')
    for h,record in json.loads((out/'historical-source-index.json').read_bytes()).items():
        if digest(out/record['artifact'])!=h:raise ValueError('Historical producer snapshot differs')
    for row in native:
        with tarfile.open(out/row['archive']) as tar:
            index=json.loads(tar.extractfile('archive-index.json').read())
            if {n:sha256(tar.extractfile(n).read()).hexdigest() for n in index['retained_sha256']}!=index['retained_sha256']:raise ValueError('Native retained input/log bytes differ')
    if replay and engine.evaluate_campaign(root)!=value:raise ValueError('Architecture replay differs')
    return dict(verified=True,replayed=replay,manifest_id=m['manifest_id'],**s)
