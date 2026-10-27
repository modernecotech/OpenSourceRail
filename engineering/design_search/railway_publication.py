"""Portable comparison of one coordinated railway experiment and its holds."""
from pathlib import Path
from hashlib import sha256
import gzip,json,shutil,tarfile,io
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import railway_campaign as engine,design_grammar,railway_bundle,grammar_shell,transient_lim,railway_delivery
from .generative_publication import archive

PRODUCER='engineering/design_search/railway_publication.py'
OUTPUT='docs/design-engine/coupled-railway'
FLAGS=engine.FLAGS


def compact_native_archive(folder):
    """Keep exact solver decks/logs; index duplicate large node/body metadata."""
    buf=io.BytesIO();kept={};omitted={}
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_symlink():raise ValueError('Ordinary native evidence files required')
            if not p.is_file() or '__pycache__' in p.parts:continue
            name=p.relative_to(folder).as_posix();h=digest(p)
            if p.suffix.lower() in ('.dat','.frd','.12d','.step','.fcstd','.fcstd1') or p.name in ('candidate.json','definition.json','worker-result.json') and p.stat().st_size>1_000_000:
                omitted[name]=h;continue
            raw=p.read_bytes();kept[name]=h;t=tarfile.TarInfo(name);t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
        raw=encoded(dict(retained_sha256=kept,omitted_sha256=omitted,storage='Exact FEM decks/results/logs retained; large fields and duplicate node/body metadata remain local or regenerate from exact source/body/request. Full raw-payload hashes preserved.'))
        t=tarfile.TarInfo('archive-index.json');t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
    return gzip.compress(buf.getvalue(),mtime=0)


def current(root=ROOT):
    root=Path(root);epoch=engine.source_epoch(root);spec=engine.specification(root);contract=identity(dict(specification=spec,source_sha256=epoch))
    folder=root/'build/coupled-railway'/contract;value=json.loads((folder/'result.json').read_bytes())
    if value['contract_id']!=contract or value['source_sha256']!=epoch or value['campaign_id']!=engine.semantic_id(value):raise ValueError('Source-matched coordinated execution required')
    if value['run_id']!=identity({k:v for k,v in value.items() if k!='run_id'}):raise ValueError('Invocation receipt differs')
    if len(value['rows'])!=len(value['bundles']):raise ValueError('Finish the pending bundle evaluation queue before publishing the complete comparison')
    return folder,value


def _body_response(native,body_id):
    cases=[r for r in native['body_results'] if r['body_candidate_id']==body_id]
    normal=next((r['raw'] for r in cases if r['case']=='normal'),{})
    fine=next((r['raw'] for r in cases if r['case']=='normal-fine'),{})
    refined=next((r['raw'] for r in cases if r['case']=='normal-refined'),{})
    a=normal.get('maximum_displacements',{}).get('vertical_m');b=fine.get('maximum_displacements',{}).get('vertical_m');extra=refined.get('maximum_displacements',{}).get('vertical_m')
    before,last=(b,extra) if extra is not None else (a,b)
    change=None if before is None or last is None else abs(before-last)/max(abs(last),1e-30)
    valid=all(r['raw'].get('numerical_validity')=='equilibrium_energy_confirmed_only' for r in cases) and len(cases)>=3
    hold=native['body_admission'].get(body_id,{}).get('computational_hold')
    return dict(native_cases=len(cases),normal_vertical_m=a,fine_vertical_m=b,extra_refined_vertical_m=extra,relative_vertical_refinement_change=change,
        mesh_levels=[dict(case=r['case'],mesh_m=r['mesh_m'],evaluation_id=r['evaluation_id'],maximum_displacements=r['raw'].get('maximum_displacements')) for r in cases],
        numerical_status='equilibrium/energy checked; maxima refinement reported' if valid else 'unconfirmed' if cases else 'computational resource hold' if hold else 'full-body model not admitted',
        engineering_screen='unknown',full_body_qualified=False)


def summary(value,magnetic=None):
    rows=[]
    for b in value['bodies']:
        cases=[r for r in value['rows'] if r['body_candidate_id']==b['candidate_id']]
        baseline=next((r for r in cases if r['family_id']=='P1'),None);response=_body_response(value['native'],b['candidate_id'])
        rows.append(dict(label=b['label'],body_candidate_id=b['candidate_id'],parent_ids=b['parent_candidate_ids'],
            known_structure_stock_kg=b['known_structure_stock_kg'],accounted_empty_mass_kg=None if baseline is None else baseline['accounted_mass']['accounted_tare_kg_per_car'],
            architecture_cases=len(cases),structural_status=response['numerical_status'],response=response,complete_installed_mass_kg=None))
    magnetic=[] if magnetic is None else magnetic
    result=dict(schema='osr-coupled-railway-summary/1',campaign_id=value['campaign_id'],contract_id=value['contract_id'],body_count=len(rows),
        initial_body_count=value['specification']['initial_structural_recipes'],body_rewrite_count=len(value['executed_body_revisions']),
        bundle_count=len(value['bundles']),evaluated_bundle_count=len(value['rows']),downstream_stage_count=sum(len(r['stages']) for r in value['rows']),
        body_rows=rows,method_fixture_count=len(value['native']['independent_fixtures']),native_body_case_count=len(value['native']['body_results']),
        CAD_case_count=len(value['native']['CAD_results']),magnetic_method_cases=len(magnetic),magnetic_completed=sum(r['result']['execution']=='completed' for r in magnetic),
        actual_force_driven_journeys=0,complete_installed_vehicle_masses=0,complete_lifecycle_costs=0,
        frontier_tasks=len(value['frontier']),dependency_graph=value['dependency_graph'],selection=value['partial_quantity_comparison'],
        integrated_selection=None,selected_reference_changed=False,city_performance_packages_written=0,**FLAGS)
    return result


def readme(s):
    lines=['# One coordinated railway experiment','',
        'Architecture, adaptive revision planning and physical body generation now share one coordinator, one explicit railway bundle and one dependency graph. A body edit creates new body/railway identities and automatically reevaluates inventory, interfaces, architecture, motor requirements, independent braking, civil loads, manufacture and economic coverage. The earlier campaigns remain reproducible component/historical tools. New coordinated work starts with `./osr design railway`.','',
        f"The executed comparison starts with **{s['initial_body_count']} structural recipes**, makes **{s['body_rewrite_count']} physical revisions**, and evaluates **{s['evaluated_bundle_count']} railway bundles through {s['downstream_stage_count']} downstream stage records**. Two primary-iron alternatives share unchanged onboard fin stock. Seven architecture families retain their own changed interfaces and unweighed equipment. **No complete installed mass, available operating LIM map, physical journey or whole-life-cost winner is demonstrated.**",'',
        '## Closed-loop physical and system changes','',
        'The existing adaptive planner diagnoses each declared pin-graph mechanism; the grammar produces a braced physical child instead of changing a pass threshold. A separate assembly-completion operator closes quantified frame/floor/roof gaps using counted metal stock and finite shared-face weld hypotheses. It generates an aluminium frame and an aluminium stressed-skin body, preserving passenger openings and required roof/PV/channel/drain functions. Missing composite laws are not replaced by isotropic GFRP.','',
        '| Body / physical revision | Known structure stock | Empty-mass account | 3D evidence | Architecture cases |',
        '|---|---:|---:|---|---:|']
    for r in s['body_rows']:
        mass='Unknown' if r['accounted_empty_mass_kg'] is None else f"{r['accounted_empty_mass_kg']/1000:.3f} t"
        lines.append(f"| {r['label']} | {r['known_structure_stock_kg']:.1f} kg | {mass} | {r['structural_status']} | {r['architecture_cases']} |")
    lines += ['',
        'These are exact generated nominal/net stock quantities plus retained source accounts. They are not complete vehicle tare or certified lower bounds: original gross-stock overlaps/cuts and missing installed hardware have different boundaries. The new welded children count net disjoint metal, retained covers, PV rails/spacers, trays/gutter/hangers and unknown weld/joint realization separately. Whole installed CG, inertia, clearances, hardware and repair access remain open.','',
        '## Three-dimensional structural method','',
        f"Four independent fixtures check bending/shear refinement, intact finite-face transfer and orthotropic axial/shear constitutive patches. The two new metal bodies have **{s['native_body_case_count']} native body cases** across normal, normal-fine and crowd loading. C3D8I solids resolve the declared actual metal geometry; no invisible gap ties or arbitrary rigid offsets create the load path. Intact autogenous weld/continuous-face transfer is an unqualified numerical hypothesis.",'',
        '| New solid body | Normal 1.7 m target | Finer 0.85 m | Extra 0.425 m | Last-step change |',
        '|---|---:|---:|---:|---:|']
    for r in s['body_rows']:
        a=r['response']
        if not a['native_cases']:continue
        val=lambda x:'Unknown' if x is None else f'{x*1000:.3f} mm'
        change='Unknown' if a['relative_vertical_refinement_change'] is None else f"{a['relative_vertical_refinement_change']*100:.2f}%"
        lines.append(f"| {r['label']} | {val(a['normal_vertical_m'])} | {val(a['fine_vertical_m'])} | {val(a['extra_refined_vertical_m'])} | {change} |")
    lines += ['',
        'The source-bound resource revision uses 1.7/0.85 m global subdivision targets; thin physical-feature cuts dominate the conformal grid. All actual mesh counts, resources, force/moment/work/energy residuals and failures are retained. A displacement trend is not strength or operating acceptance. C3D8I torsion limitations, quadratic confirmation, local/global buckling, material/HAZ/joint strength, fatigue, modes, thermal/fire/crash behaviour and physical calibration remain necessary work. Equipment loads are currently lumped over the floor with actual structural selfweight; real component positions and suspension compliance are not resolved.','',
        'The first baseline metal-frame job produced 152,004 cells and exceeded its 5 GiB allocation while factoring. It yielded no structural verdict. The generator then standardized and aligned floor/roof extrusion profiles, preserving openings, support pads and actual load paths. These are new physical children with different identities, fewer profile families and roughly 71% fewer conformal cells. The original failed execution, source epoch and CAD remain retained. A 60,000-cell dispatch budget is a computational control, not a railway acceptance rule or proof that the baseline body cannot work.','',
        'The frame\'s first refinement changed the three displacement maxima by about 10-12%. The coordinator therefore requested another unchanged-candidate numerical experiment at a 0.425 m target. Its 61,352-cell estimate justified an explicit computational budget revision to 65,000 cells under the same 5 GiB/150 s limits. Exact unchanged prior solves/CAD are reused across coordinator epochs, with new context records. A 5% refinement trigger requests work; it does not qualify a body. Whole-field, stress, torsion and physical convergence remain separate questions.','',
        'Original foam/honeycomb and GFRP bodies remain non-admitted to this whole-body solver until their own complete directional material laws, attachment stock and joint models are provided. Orthotropic method patches demonstrate implementation, not purchased composite properties.','',
        '## Available propulsion and forward motion','',
        'Every changed mass automatically reaches the 2 km required-force calculation, nine independent-brake loading/fault hypotheses and three crowd-loaded precast alternatives. Rotor equivalent mass enters acceleration and braking; it is excluded from static axle gravity. P6/P7 remove the old passive-secondary account and preserve unknown replacement mass. A candidate-bound available-map gate checks actual position/speed/current/temperature samples, electrical work, thermal/current/voltage domains and normal-force interfaces. No linear, generic DC or synthetic map is silently admitted as an operating motor.','',
        f"A new transient A-z/floating-current kernel executed {s['magnetic_method_cases']} bounded method controls ({s['magnetic_completed']} completed). It uses nonlinear reversible H(B), implicit timesteps, actual phase-current excitation, net-secondary-current closure and explicit stored-energy/Joule/mechanical/discrete-time work. Its finite conductor mask stays fixed at a declared frozen velocity. The generic curve, short secondary, incomplete circuit/copper/thermal model, independent steady/mesh/transit confirmation and actual 20 m/s operating domain prevent it supplying an available-force map. Residual closure is reported without relabelling this fixture as the full LIM.",'',
        'The forward-motion method has independent synthetic tests for constant-force energy, finite powered windows, zero entry force, thermal/bus limits and stopping. Actual railway journeys remain not-run because available propulsion and complete installed inputs are missing. The receiving drive receives no safety credit in independent-braking screens.','',
        '## Manufacturing, economics and evidence','',
        'Each shared bundle produces an EBOM of actual stock, retained accounts and unresolved joints; MBOM cuts/blanks and process groups; assembly/inspection dependencies; material, supplier, access, repair and QA tasks; and source-bound price/lead-time coverage. Missing equipment is neither a box invented for an animation nor a zero-mass part. Quotes require the exact bundle/component/quantity/unit/currency context.','',
        'The two executed new body CADs also compile candidate-bound delivery packages: the same stock IDs feed EBOM/MBOM, disabled research ERPNext Item/BOM drafts, assembly and procurement tasks, and reopened IFC body-stock geometry. Drafts are not posted to ERPNext and cannot release purchasing or manufacture. Unlocated equipment, unknown joint realization and missing commercial/process evidence remain explicit.','',
        'Partial Pareto comparisons retain unknown or differently scoped alternatives. Installed prices, energy purchase, tooling, labour, maintenance lives, renewals and downtime remain missing. The system cannot choose a cheapest qualified railway from gross stock. Civil results count axle envelopes, section/tendon quantities and preliminary foundation/erection hypotheses; site/geotechnical, torsional and construction qualification remain open.','',
        'Immutable stage requests include candidate and upstream evidence IDs. Native cache admission checks source/executable/payload plus exact body, load, mesh, method and resource request. New structural evidence invalidates dependent case evaluations even if geometry is unchanged. Stable experiment identity is separate from invocation cache counters; interrupted/pending work remains in the frontier. Native/CAD packets retain their original receipts.','',
        '```bash','./osr design railway plan','./osr design railway run --max-bundles 2 --native-jobs 1','./osr design railway run --native-jobs 12','./osr design railway publish','./osr design railway verify','```','',
        '[Summary](summary.json) · [Body definitions](bodies.json.gz) · [Canonical bundles](bundles.json.gz) · [Coupled evaluations](comparison.json.gz) · [Inventory/manufacturing records](inventories.json.gz) · [Delivery/IFC/ERP drafts](delivery-index.json) · [Native/CAD index](native-index.json) · [Transient method controls](magnetic-method.json.gz) · [Pending work](frontier.json.gz) · [Source epochs](source-epochs.json) · [Source/payload manifest](manifest.json)','',
        'Large fields and CAD solids stay local or regenerate with exact sources and indexed inputs; no remote artifact object or complete manufacturing/operating release is claimed. The selected reference and all 266 city performance packages remain unchanged.','']
    return '\n'.join(lines)


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    if (out/'manifest.json').is_file():
        m=json.loads((out/'manifest.json').read_bytes())
        if all(digest(root/n)==h for n,h in m['source_sha256'].items()):return verify(root,out)
    folder,value=current(root)
    if out.exists():
        retained=root/'build/coupled-railway/replaced-publications'/digest(out/'manifest.json');retained.parent.mkdir(parents=True,exist_ok=True)
        if retained.exists():raise ValueError('Previous coordinated publication already retained')
        shutil.move(out,retained)
    out.mkdir(parents=True);(out/'native').mkdir();native=[];epochs={}
    for i,r in enumerate(value['native']['packet_index']):
        p=folder/'native'/r['raw_path'];target='native/'+str(i)+'.tar.gz';(out/target).write_bytes(compact_native_archive(p))
        native.append(dict(kind=r['kind'],job_id=r['job_id'],archive=target,raw_manifest=json.loads((p/'manifest.json').read_bytes()),raw_result=json.loads((p/'result.json').read_bytes())))
    for r in value['native']['CAD_results']:
        p=folder/'native/CAD'/r['candidate_id'];target='native/CAD-'+r['candidate_id'][:12]+'.tar.gz';(out/target).write_bytes(archive(p))
        native.append(dict(kind='CAD',archive=target,raw_manifest=json.loads((p/'manifest.json').read_bytes()),raw_result=r))
    cad_ids={r['candidate_id'] for r in value['native']['CAD_results']}
    body_ids={b['candidate_id'] for b in value['bodies']}
    for p in sorted((root/'build/coupled-railway').glob('*/native/CAD/*/manifest.json')):
        r=json.loads((p.parent/'result.json').read_bytes())
        if r['candidate_id'] in cad_ids or r['candidate_id'] not in body_ids:continue
        target='native/historical-CAD-'+r['candidate_id'][:12]+'.tar.gz';(out/target).write_bytes(archive(p.parent));cad_ids.add(r['candidate_id'])
        native.append(dict(kind='historical-CAD',archive=target,raw_manifest=json.loads(p.read_bytes()),raw_result=r))
    magnetic_path=root/'build/coupled-railway/transient-method-r1/summary.json'
    magnetic=[] if not magnetic_path.is_file() else json.loads(magnetic_path.read_bytes())
    for i,r in enumerate(magnetic):
        p=root/r['path'];transient_lim.verify(p,root=root);target='native/magnetic-'+str(i)+'.tar.gz';(out/target).write_bytes(archive(p))
        native.append(dict(kind='transient-method',archive=target,raw_manifest=json.loads((p/'manifest.json').read_bytes()),raw_result=r['result']))
    seen={r['raw_result'].get('evaluation_id') for r in native}
    for p in sorted((root/'build/coupled-railway').glob('*/native/jobs/*/raw/result.json')):
        r=json.loads(p.read_bytes())
        if r.get('evaluation_id') in seen or r.get('execution')=='completed':continue
        target='native/historical-failed-'+r['evaluation_id'][:12]+'.tar.gz';(out/target).write_bytes(compact_native_archive(p.parent));seen.add(r['evaluation_id'])
        native.append(dict(kind='historical-resource-or-numerical-failure',archive=target,raw_manifest=json.loads((p.parent/'manifest.json').read_bytes()),raw_result=r))
    for r in native:
        result=r['raw_result'];manifest=r['raw_manifest']
        for name,h in result.get('source_sha256',manifest.get('source_sha256',{})).items():
            if digest(root/name)==h:continue
            original=root/'build/coupled-railway/source-epochs'/h
            if not original.is_file() or digest(original)!=h:raise ValueError('Historical native producer bytes are unavailable')
            (out/'historical-sources').mkdir(exist_ok=True);target='historical-sources/'+h;(out/target).write_bytes(original.read_bytes());epochs[h]=dict(repository_path=name,artifact=target)
    inventories=[];deliveries=[]
    for b in value['bodies']:
        row=next(r for r in value['rows'] if r['body_candidate_id']==b['candidate_id'] and r['family_id']=='P1')
        stage=next(r for r in row['stages'] if r['stage']=='installed_inventory');record=json.loads((folder/'stages'/identity(stage['request'])).read_bytes())
        if record['record_id']!=stage['record_id']:raise ValueError('Inventory stage changed')
        inventories.append(record['output'])
        CAD=next((r for r in value['native']['CAD_results'] if r['candidate_id']==b['candidate_id']),None)
        if CAD is not None:
            bundle=next(x for x in value['bundles'] if x['candidate_id']==row['candidate_id']);target=folder/'delivery'/bundle['candidate_id']
            if target.exists():
                manifest=json.loads((target/'manifest.json').read_bytes())
                if manifest['files_sha256']!={p.name:digest(p) for p in target.iterdir() if p.is_file() and p.name!='manifest.json'}:raise ValueError('Delivery cache changed')
            else:manifest=railway_delivery.write(target,bundle,b,record['output'],CAD=CAD)
            prefix='delivery/'+bundle['candidate_id'][:12];(out/prefix).mkdir(parents=True)
            for name in ('delivery.json.gz','ERPNext-draft.json.gz','bim.json','body-stock.ifc.gz'):
                if (target/name).is_file():shutil.copyfile(target/name,out/prefix/name)
            deliveries.append(dict(candidate_id=bundle['candidate_id'],body_candidate_id=b['candidate_id'],prefix=prefix,raw_manifest=manifest))
    s=summary(value,magnetic)
    files={'summary.json':encoded(s),'bodies.json.gz':gzip.compress(encoded(value['bodies']),mtime=0),'bundles.json.gz':gzip.compress(encoded(value['bundles']),mtime=0),
        'comparison.json.gz':gzip.compress(encoded(value['rows']),mtime=0),'inventories.json.gz':gzip.compress(encoded(inventories),mtime=0),
        'frontier.json.gz':gzip.compress(encoded(value['frontier']),mtime=0),'magnetic-method.json.gz':gzip.compress(encoded(magnetic),mtime=0),
        'native-index.json':encoded(native),'source-epochs.json':encoded(epochs),'delivery-index.json':encoded(deliveries),'execution.json':encoded(dict(campaign_id=value['campaign_id'],run_id=value['run_id'],contract_id=value['contract_id'],
            new_bundles=value['new_bundles'],reused_bundles=value['reused_bundles'],native=value['native'],executed_body_revisions=value['executed_body_revisions'])),
        'README.md':readme(s).encode()}
    for name,raw in files.items():(out/name).write_bytes(raw)
    m=dict(schema='osr-coupled-railway-publication/1',source_sha256={**value['source_sha256'],PRODUCER:digest(root/PRODUCER),
        railway_delivery.PRODUCER:digest(root/railway_delivery.PRODUCER),'engineering/design_search/wheel_twin.py':digest(root/'engineering/design_search/wheel_twin.py'),
        'engineering/design_search/generative_publication.py':digest(root/'engineering/design_search/generative_publication.py')},
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(out/'manifest.json').write_bytes(encoded(m));return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Coordinated publication receipt differs')
    if any(digest(root/p)!=h for p,h in m['source_sha256'].items()):raise ValueError('Coordinated source epoch changed')
    if m['files_sha256']!={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}:raise ValueError('Coordinated payload changed')
    s=json.loads((out/'summary.json').read_bytes());bodies=json.loads(gzip.decompress((out/'bodies.json.gz').read_bytes()));bundles=json.loads(gzip.decompress((out/'bundles.json.gz').read_bytes()));rows=json.loads(gzip.decompress((out/'comparison.json.gz').read_bytes()))
    for b in bodies:design_grammar.validate(b)
    for b in bundles:railway_bundle.validate(b)
    if len({b['candidate_id'] for b in bundles})!=len(bundles) or {r['candidate_id'] for r in rows}!={b['candidate_id'] for b in bundles}:raise ValueError('Mixed or incomplete bundle results')
    index={b['candidate_id']:b for b in bundles}
    for row in rows:
        if row['row_id']!=identity({k:v for k,v in row.items() if k!='row_id'}) or row['bundle_definition_id']!=index[row['candidate_id']]['definition_id']:raise ValueError('Coupled case identity differs')
        if row['body_candidate_id']!=index[row['candidate_id']]['body_candidate_id'] or row['accounted_mass']!=index[row['candidate_id']]['mass']:raise ValueError('Coupled body/mass mismatch')
        if row['motion']['forward_motion']['execution']!='not-run' or row['physical_journey_completed'] is not False:raise ValueError('Required motion cannot become an available physical journey')
    if any(s.get(k) is not False for k in FLAGS) or s['integrated_selection'] is not None:raise ValueError('Research comparison cannot release a railway')
    epochs=json.loads((out/'source-epochs.json').read_bytes())
    for h,r in epochs.items():
        if digest(out/r['artifact'])!=h:raise ValueError('Historical producer bytes differ')
    for item in json.loads((out/'native-index.json').read_bytes()):
        with tarfile.open(out/item['archive']) as tar:
            ai=json.loads(tar.extractfile('archive-index.json').read());manifest=json.loads(tar.extractfile('manifest.json').read());result=json.loads(tar.extractfile('result.json').read())
            if manifest!=item['raw_manifest'] or result!=item['raw_result']:raise ValueError('Native index differs from raw receipt')
            if manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Nested native manifest identity differs')
            if 'evaluation_id' in result and result['evaluation_id']!=identity({k:v for k,v in result.items() if k!='evaluation_id'}):raise ValueError('Nested native evaluation identity differs')
            if manifest['files_sha256']!={k:v for k,v in {**ai['retained_sha256'],**ai['omitted_sha256']}.items() if k!='manifest.json'}:raise ValueError('Native archive does not cover original payload')
            for name,h in ai['retained_sha256'].items():
                if sha256(tar.extractfile(name).read()).hexdigest()!=h:raise ValueError('Native payload changed')
            for name,h in result.get('source_sha256',manifest.get('source_sha256',{})).items():
                if digest(root/name)!=h and h not in epochs:raise ValueError('Native source changed')
    for r in json.loads((out/'delivery-index.json').read_bytes()):
        prefix=out/r['prefix'];manifest=r['raw_manifest'];value=json.loads(gzip.decompress((prefix/'delivery.json.gz').read_bytes()))
        if value['candidate_id']!=r['candidate_id'] or value['body_candidate_id']!=r['body_candidate_id'] or value['delivery_id']!=identity({k:v for k,v in value.items() if k!='delivery_id'}):raise ValueError('Mixed delivery identity')
        for p in prefix.iterdir():
            if digest(p)!=manifest['files_sha256'][p.name]:raise ValueError('Delivery bytes differ')
        if (prefix/'body-stock.ifc.gz').is_file() and sha256(gzip.decompress((prefix/'body-stock.ifc.gz').read_bytes())).hexdigest()!=manifest['files_sha256']['wheel-stock.ifc']:raise ValueError('Compressed IFC differs from native delivery')
    return dict(verified=True,manifest_id=m['manifest_id'],campaign_id=s['campaign_id'],body_count=len(bodies),evaluated_bundle_count=len(rows),
        native_body_case_count=s['native_body_case_count'],physical_journeys=0,complete_installed_masses=0,**FLAGS)
