"""Bounded, source-bound material and architecture research around a failed train.

Definition/necessary-bound proposals are deliberately separate from native
full-body evaluations. New topologies never inherit the old solver's results.
"""
from copy import deepcopy
from pathlib import Path
import gzip,json,shutil,tomllib
from . import ROOT
from .common import encoded,identity,digest

PRODUCER='engineering/station_rail/design_space.py'
SPEC='campaigns/v06-expanded-design-space.toml'
OUTPUT='docs/design-engine/v06-design-space'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)


def parent(root=ROOT):
    from engineering.design_search import contracts as k,wheel_families
    root=Path(root);folder=root/'docs/design-engine/v06-optimisation'
    comparison=json.loads(gzip.decompress((folder/'comparison.json.gz').read_bytes()))
    selected=json.loads((folder/'summary.json').read_bytes())['next_experiment']['selected_candidate_id']
    candidate=next(c for c in comparison['candidates'] if c['candidate_id']==selected);k.validate_candidate(candidate)
    results=[r for r in comparison['results'] if r['candidate_id']==selected]
    for result in results:k.validate_result(result)
    return candidate,wheel_families.materialize(candidate),results


def assemble(root=ROOT):
    from engineering.design_search import structural_families as bodies,propulsion_families as motors,joining_catalogue as joins
    root=Path(root);spec=tomllib.loads((root/SPEC).read_text())
    if spec['schema']!='osr-expanded-design-space/1' or spec['purpose']!='next-experiment':raise ValueError('Research-only versioned specification required')
    if (spec['maximum_structural_proposals'],spec['maximum_propulsion_proposals'],spec['maximum_native_motor_cases'],spec['maximum_native_coupon_cases'])!=(12,12,4,4):raise ValueError('Explicit first expansion budgets required')
    from . import braking
    candidate,car,results=parent(root);context=dict(accounted_mass_kg_per_car=car['mass']['accounted_cap_loaded_kg_per_car'],
        rotating_equivalent_mass_kg_per_car=braking.rotating_stock(car)['equivalent_inertial_mass_kg_per_car'])
    motor=motors.expanded_plan(candidate,results,context=context,native_case_budget=4,confirmation_case_budget=0)
    parameters=bodies.initial_parameters();rows=[]
    def add(p,generation,reason,parent_id=None):
        bundle=bodies.generate(car,p);bounds=bodies.necessary_bounds(bundle,maximum_core_temperature_C=spec['maximum_temperature_C'])
        existing=next((r for r in rows if r['bundle']['candidate_id']==bundle['candidate_id']),None)
        if existing is not None:
            existing.setdefault('additional_lineage',[]).append(dict(generation=generation,parent_proposal_id=parent_id,reason=reason))
            return
        rows.append(dict(generation=generation,parent_proposal_id=parent_id,reason=reason,bundle=bundle,bounds=bounds))
    for p in parameters:add(p,0,'Compare discrete load-path and material families; full-body evaluator remains held')
    # Match architecture, face layup, thickness and attachments while comparing
    # cores. This avoids confusing every material change with a different body.
    for core in bodies.material_catalogue()['cores']:
        p=bodies.default_parameters();p.update(core_id=core,core_thickness_m=.025)
        add(p,1,'Matched participating-panel material comparison; no full-body performance inherited')
    for initial in rows[4:8]:
        p=deepcopy(initial['bundle']['parameters']);p['crossmember_pitch_m']=.75
        p['cell_L_axis']='transverse' if p['core_id'].startswith(('al_','aramid_')) else 'x'
        p['joint']='bonded_edge_splice'
        if initial['bounds']['necessary_screens']['supplier_continuous_temperature']=='fail':p['core_id']='pet_t92_80'
        add(p,2,'Respond to temperature bounds; test shorter panel spans, joint architecture and directional core sensitivity',initial['bundle']['candidate_id'])
    if not 8<=len(rows)<=12 or len({r['bundle']['candidate_id'] for r in rows})!=len(rows):raise ValueError('Distinct bounded structural proposals required')
    supports=[[0.,0.,0.],[1.,0.,0.],[0.,.5,0.],[1.,.5,0.]]
    attachments=[joins.attachment_plan(strategy,supports) for strategy in ('bonded-flange','bond-plus-bolts','potted-insert','clip-plus-positive-retention','welded-node')]
    glazing=[joins.glazing_plan(1.3,.7,.006,product=product) for product in ('polycarbonate-flat-window','fire-retardant-flat-window')]
    return dict(schema='osr-expanded-design-space-results/1',parent_candidate_id=candidate['candidate_id'],
        parent_requirement_revision=candidate['requirement_revision'],vehicle_context=context,specification=spec,structural_plan=bodies.campaign_plan(),
        structural_proposals=rows,propulsion_plan=motor,material_catalogue=bodies.material_catalogue(),joining_catalogue=joins.catalogue(),
        concept_leads=bodies.concept_leads(),
        attachment_examples=attachments,glazing_examples=glazing,
        example_scope='Four-support1x0.5m attachment coupon and1.3x0.7x6mm glazing comparisons; not complete car joints/windows or installed substitutions',
        whole_system_winner=None,complete_installed_mass_kg=None,complete_installed_cost_USD=None,
        full_body_native_dispatch=False,default_changed=False,**FLAGS)


def readme(value,native,diagnosis=None,native_results=()):
    rows=value['structural_proposals'];prop=value['propulsion_plan'];lines=[
      '# Broader v0.6 design space','',
      'OpenSourceRail seeks simple, affordable transport that can be manufactured and repaired locally. This bounded search uses material and architecture choices to respond to the failed wheel-rail campaign, while preserving its exact evidence and the comfort-first service brief.','',
      '**Research definitions and necessary bounds.** None of these new structural families inherits a validated full-body model, installed mass or physical acceptance. The [executed native campaign](../v06-optimisation/README.md) remains a separate source-bound result.','',
      '## What can change','',
      '| Domain | Design variables | Required consequence |','|---|---|---|',
      '| Main body | Aluminium spaceframe; participating sandwich; hybrid integral panels; GFRP semi-monocoque | Regenerate load paths, aperture frames, bogie hardpoints and counted stock |',
      '| Panels | PET/PVC foam; aluminium/aramid honeycomb; face material and plies; thickness; cell orientation; support pitch | Include core shear, directional properties, temperature, bondlines, edges and local reinforcement |',
      '| Connections | Bonded flanges; bond plus bolts; potted inserts; welded nodes; clips with positive retention for removable panels | Count installation hardware and qualify peel, bearing, pullout, fatigue, cure and repair |',
      '| Station motor | Return/tooth/slot dimensions; pitch; fin count/length; single/double LIM; passive reluctance; conductor, circuits, cooling and steel | New topologies require new native adapters; no multiplication of old force |',
      '| Service | Explicit 57.6/43.2 km/h and acceleration/powered-zone alternatives alongside 72 km/h | New requirement identities; recompute trip time, dwell, headway, fleet and total infrastructure |',
      '| Equipment | Coated polycarbonate glazing, retained seals and thermal movement; modular HVAC | Include mounting and hot-weather capacity; supplier sheet/module mass is not installed train mass |','',
      '## Executed necessary-bound comparison','',
      '| Generation / proposal | Architecture / core | Accounted comparison/car | Temperature bound | Full-body model |',
      '|---|---|---|---|---|']
    for r in rows:
        b=r['bundle'];p=b['parameters'];s=r['bounds']['necessary_screens']
        lines.append(f"| g{r['generation']} / `{b['candidate_id'][:12]}` | {p['family']} / {p['core_id']} | {b['accounted_tare_comparison_kg_per_car']/1000:.3f} t | {s['supplier_continuous_temperature']} at {value['specification']['maximum_temperature_C']:.0f}°C | held |")
    lines += ['',
      f"The {len(rows)} distinct structural proposals include a matched four-core comparison and follow-ups changing panel support pitch, joint layout and honeycomb orientation. Converging revision paths share one physical definition and retain both ancestries. Material removed and added, faces, edges, aperture frames, splice stock and hardpoint stock are counted. Some stock remains in component-local frames awaiting installation; missing washers, load spreaders, resin/repair allowances and prices remain explicit. These subtotals cannot rank a complete railway.",'',
      'Supplier properties distinguish typical values, stated minima, source units, specimen thickness, cell axes and temperature claims. The 80°C core case is a research envelope, not a solved Baghdad roof temperature. Room-temperature shear values do not establish hot-load strength or fire approval. Honeycomb is not treated as isotropic foam.','',
      f"The motor plan generates {prop['candidate_proposal_count']} distinct physical proposals. Only supported single-fin, copper-wound linear-material geometries can reach the existing adapter. Supplier magnetic polarisation checkpoints are not silently converted into an accepted nonlinear B–H law. Actual available thrust, repeated thermal duty and installed prices stay unknown.",'',
      '## Validation before selection','',
      'The previous participating-body calculation remains laterally nonconverged. Diagnose boundary conditions, joint rotational restraint, mesh and load transfer before using a stronger material to mask a model defect. Small material and joint fixtures must pass their own analytical/reaction/mesh checks before new full-body comparisons.','',
      'Adhesive coupon shear is not a joint allowable, clip pullout classes are not a primary structural load path, and an unwelded alloy strength is not a welded-node strength. Attachment examples preserve unknown hardware masses. Glazing examples count sheet mass and thermal movement; pressure, retention, abrasion, cleaning, fire and emergency egress remain gates.','',
      f"Native follow-up packages attached: **{len(native)}**. Their immutable inputs, outputs, solver logs and manifests are retained in the indexed archive; detailed results remain conditional on each package's declared model and validity. A fixture pass is not full-train acceptance.",'',
      '[Complete comparison](results.json.gz) · [Compact summary](summary.json) · [Primary-source catalogues](catalogues.json) · [Native results](native-results.json) · [Native follow-up index](native-index.json) · [Receipt](manifest.json)','',
      '```bash','./osr design space build','./osr design space verify','```','',
      'Choose architecture first, reject necessary failures cheaply, validate its evaluator, then size it with native workers. Integrated selection still requires the same equipped mass, joints, force maps, brakes, civil loads, full journey and equal-service cost. The selected development train and 266 city packages are unchanged.','']
    for record in native_results:
        result=record['result']
        if result.get('schema')=='osr-expanded-motor-native-followup/1':
            lines += ['## New native motor follow-up','',
                f"Four centred 2D GetDP cases use the same normal-loaded car and counted rotational inertia: required launch thrust **{result['required_force_N_per_car']/1000:.3f} kN/car**.",'',
                '| Geometry | Conditional force at 20 m/s | Peak steel field at 20 m/s |','|---|---|---|']
            for row in result['proposal_results']:
                case=next(c for c in row['cases'] if c['case']['speed_m_s']==20.)
                lines.append(f"| {row['label']} | {case['metrics']['force_N']/1000:.3f} kN | {case['metrics']['maximum_steel_phasor_B_bound_T']:.3f} T |")
            lines += ['','Both remain below required thrust and outside the retained 1.3 T linear-material domain. Energy balance and current-density checks do not establish an available installed force map. Native dispatch chose unchanged-fin geometries; the longer-fin proposal remains an interface task.','']
        elif result.get('schema')=='osr-structural-core-coupons/1' and result.get('execution')=='completed':
            passed=sum(c.get('numerical_screen')=='pass' for c in result['cases'])
            lines += ['## Native sandwich method fixtures','',f"**{passed}/{len(result['cases'])}** checks pass: separate L/W affine shear and two sandwich bending/shear meshes. The fixture uses published directional core values with explicitly synthetic unreported constitutive regularisation and reference metal faces. This is numerical method evidence, not measured material correlation or a complete body pass. Original refused shear decks remain archived at their historical source revision; the correction bounds numeric field width.",'']
    if diagnosis is not None:
        lines += ['','## Retained body-model diagnosis','',
          f"The retained fine model has {diagnosis['graph']['physical_solid_nodes']} physical solid nodes in {diagnosis['graph']['physical_components']} connected component. The maximum lateral displacement occurs at node {diagnosis['maxima']['lateral']['node_id']}. The {sum(diagnosis['ideal_pad_rank_histogram'].values())} ideal clamp pads have rank 5: their two collinear transfer points leave one local rotation unconstrained. Connectivity alone therefore does not validate rotational restraint. This establishes a local model deficiency; its share of the full-body mode remains unresolved.",'',
          '[Diagnosis and next unit-moment/eigenmode tasks](model-diagnosis.json) · [Exact retained input/displacement data](model-diagnosis-inputs.tar.gz)','']
    lines += ['## Primary-source starting points','',
        '[AIREX PET grade data](https://www.3accorematerials.com/uploads/pdf/TDS-AIREX-T92-E-01.2026-EMEA.pdf) · [DIAB PVC grade data](https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf) · [Hexcel directional honeycomb properties](https://www.hexcel.com/wp-content/uploads/2026/01/HexWebHoneycombAttributesandProperties.pdf) · [Hydro rail extrusions](https://www.hydro.com/gb/global/aluminium/products/extruded-profiles/aluminium-extrusions-in-use/modern-trains-and-rail/) · [Metawell corrugated panels](https://www.metawell.com/en/applications/rail-vehicles/) · [3M adhesive coupon conditions](https://multimedia.3m.com/mws/media/2534142O/3m-scotch-weld-epoxy-adhesive-dp490-technical-data-sheet.pdf)','',
        'The catalogues retain precise grades, revisions, source units and available byte hashes. Where byte retrieval was refused, the missing document hash stays explicit. Product certification or a supplier coupon does not release this train.','']
    return '\n'.join(lines)


def native_package(folder,root=ROOT,*,expected=None,historical_source_commit=None):
    """Verify exact bytes/source before attaching any external native run."""
    root=Path(root);folder=Path(folder)
    if folder.is_symlink() or not folder.resolve().is_relative_to((root/'build/v06-loop').resolve()):raise ValueError('Ordinary explicit local research run required')
    m=json.loads((folder/'manifest.json').read_bytes());result=json.loads((folder/'result.json').read_bytes())
    if m['manifest_id']!=identity({n:v for n,v in m.items() if n!='manifest_id'}):raise ValueError('Native aggregate receipt differs')
    actual={p.relative_to(folder).as_posix():digest(p) for p in folder.rglob('*') if p.is_file() and p!=folder/'manifest.json'}
    expected_files=dict(m['files_sha256']);nested=m.get('nested_native_manifest_sha256',{})
    if set(expected_files)&set(nested):raise ValueError('Overlapping native payload partitions')
    expected_files.update(nested)
    if actual!=expected_files:raise ValueError('Native aggregate payload differs')
    if historical_source_commit is None:
        if any(digest(root/n)!=h for n,h in m['source_sha256'].items()):raise ValueError('Native aggregate source differs')
    else:
        import re,subprocess
        from hashlib import sha256
        if not re.fullmatch('[0-9a-f]{40}',historical_source_commit) or result.get('execution')!='completed_with_errors':raise ValueError('Pinned historical failure required')
        for name,h in m['source_sha256'].items():
            raw=subprocess.run(['git','show',historical_source_commit+':'+name],cwd=root,check=True,capture_output=True).stdout
            if sha256(raw).hexdigest()!=h:raise ValueError('Historical native source differs')
    for r in (m,result):
        if any(r.get(n) is not False for n in ('physical_accepted','engineering_accepted','manufacturing_release','operating_release')):raise ValueError('Native component evidence cannot release the train')
    if m['schema']=='osr-expanded-motor-native-manifest/1':
        from engineering.design_search import wheel_motor,propulsion_families
        if expected is None:raise ValueError('Motor follow-up requires explicit parent and proposal context')
        if any(r.get('parent_candidate_id')!=expected['parent_candidate_id'] or r.get('requirement_revision')!=expected['parent_requirement_revision'] for r in (m,result)):raise ValueError('Native motor parent/requirements differ')
        if result['mass_context']!=expected['vehicle_context']:raise ValueError('Native motor normal/rotating mass context differs')
        proposals={r['proposal']['proposal_id']:r['proposal'] for r in expected['propulsion_plan']['proposals']}
        input_record=json.loads((folder/'input.json').read_bytes())
        if identity({n:v for n,v in result.items() if n!='aggregate_evaluation_id'})!=result['aggregate_evaluation_id']:raise ValueError('Native motor evaluation identity differs')
        if identity({n:v for n,v in input_record.items() if n!='input_id'})!=input_record['input_id'] or input_record['input_id']!=result['input_id']:raise ValueError('Native motor input identity differs')
        if m['aggregate_evaluation_id']!=result['aggregate_evaluation_id'] or result['native_case_count']!=sum(len(r['cases']) for r in result['proposal_results']) or result['native_case_count']>4:raise ValueError('Bounded native motor identities differ')
        for row in result['proposal_results']:
            if row['actual_vehicle_mass_context']!=expected['vehicle_context'] or row['parent_candidate_id']!=expected['parent_candidate_id'] or row['requirement_revision']!=expected['parent_requirement_revision']:raise ValueError('Native child vehicle context differs')
            if row['proposal']!=proposals.get(row['proposal_id']):raise ValueError('Native physical proposal differs')
            if row['parameters']!=propulsion_families.wheel_motor_parameters(row['proposal']):raise ValueError('Native generated motor parameters differ')
            checked=wheel_motor.verify(folder/row['label'],root)
            if checked['evaluation_id']!=row['component_native_evaluation_id']:raise ValueError('Native motor component identity differs')
    elif m['schema']=='osr-structural-core-coupon-manifest/1':
        if result['native_cases']!=len(result['cases']) or result['native_cases']>4:raise ValueError('Bounded native coupon count differs')
        if historical_source_commit is None:
            if result['tool']!=m['tool'] or digest(result['tool']['ccx_path'])!=result['tool']['ccx_sha256']:raise ValueError('Native coupon binary context differs')
    return m,result,actual


def compact(value,native):
    return dict(schema='osr-expanded-design-space-summary/1',result_id=value['result_id'],parent_candidate_id=value['parent_candidate_id'],
        structural_proposals=len(value['structural_proposals']),propulsion_proposals=value['propulsion_plan']['candidate_proposal_count'],
        attachment_examples=len(value['attachment_examples']),glazing_examples=len(value['glazing_examples']),native_packages=len(native),
        full_body_native_dispatch=False,default_changed=False,whole_system_winner=None,**FLAGS)


def build(root=ROOT,output=None,*,native_dirs=None):
    from engineering.design_search import wheel_publication as previous
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    previous.verify(root/'docs/design-engine/v06-optimisation')
    value=assemble(root);native=[];native_results=[]
    if native_dirs is None:native_dirs=[root/p for p in value['specification']['native_package_roots'] if (root/p/'manifest.json').is_file()]
    if out.exists():
        preserved=root/'build/v06-loop/replaced-design-spaces'/digest(out/'manifest.json');preserved.parent.mkdir(parents=True,exist_ok=True)
        if preserved.exists():raise ValueError('Previous design-space package already retained; inspect before rebuilding')
        shutil.move(out,preserved)
    out.mkdir(parents=True)
    for folder in native_dirs:
        folder=Path(folder);manifest,result,files=native_package(folder,root,expected=value)
        name=folder.name+'.tar.gz';(out/name).write_bytes(previous.archive(folder,compact=True))
        native.append(dict(local_raw_directory=str(folder),archive=name,raw_files_sha256=files,native_manifest_id=manifest['manifest_id'],
            scope='Bounded component/model follow-up; consult its result and manifest for execution and validity',**FLAGS))
        native_results.append(dict(package=folder.name,result=result))
    for failure in value['specification'].get('retained_failures',[]):
        folder=root/failure['directory']
        if not folder.is_dir():continue
        manifest,result,files=native_package(folder,root,historical_source_commit=failure['source_commit'])
        name=folder.name+'-failed.tar.gz';(out/name).write_bytes(previous.archive(folder,compact=True))
        native.append(dict(local_raw_directory=str(folder),archive=name,raw_files_sha256=files,native_manifest_id=manifest['manifest_id'],historical_source_commit=failure['source_commit'],
            scope=failure['reason'],**FLAGS))
        native_results.append(dict(package=folder.name,historical_source_commit=failure['source_commit'],result=result))
    value['result_id']=identity(value)
    diagnosis=None;case=root/'build/v06-loop/dense-shell-normalfine-r1'
    if (case/'body.dat').is_file():
        from engineering.design_search import structural_families
        diagnosis=structural_families.diagnose_native(case)
        inputs=root/'build/v06-loop/body-diagnosis-inputs-final';inputs.mkdir(parents=True,exist_ok=True)
        for name in ('body.inp','body.dat','candidate.json'):
            target=inputs/name
            if target.exists() and digest(target)!=digest(case/name):raise ValueError('Retained model-diagnosis input changed')
            if not target.exists():shutil.copyfile(case/name,target)
        (out/'model-diagnosis.json').write_bytes(encoded(diagnosis));(out/'model-diagnosis-inputs.tar.gz').write_bytes(previous.archive(inputs))
    summary=compact(value,native)
    (out/'results.json.gz').write_bytes(gzip.compress(encoded(value),mtime=0))
    (out/'summary.json').write_bytes(encoded(summary));(out/'native-index.json').write_bytes(encoded(native))
    (out/'native-results.json').write_bytes(encoded(native_results))
    (out/'catalogues.json').write_bytes(encoded({n:value[n] for n in ('material_catalogue','joining_catalogue')}))
    (out/'README.md').write_text(readme(value,native,diagnosis,native_results))
    names=[PRODUCER,SPEC,'engineering/design_search/structural_families.py','engineering/design_search/propulsion_families.py',
        'engineering/design_search/joining_catalogue.py','engineering/design_search/wheel_families.py','engineering/design_search/wheel_motor.py',
        'docs/design-engine/v06-optimisation/manifest.json','docs/design-engine/v06-optimisation/comparison.json.gz','docs/design-engine/v06-optimisation/summary.json']
    manifest=dict(schema='osr-expanded-design-space-manifest/1',source_sha256={n:digest(root/n) for n in names},
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**FLAGS)
    manifest['manifest_id']=identity(manifest);(out/'manifest.json').write_bytes(encoded(manifest));return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({n:v for n,v in m.items() if n!='manifest_id'}):raise ValueError('Design-space receipt identity differs')
    if {p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='manifest.json'}!=m['files_sha256']:raise ValueError('Design-space payload differs')
    if any(digest(root/n)!=h for n,h in m['source_sha256'].items()):raise ValueError('Design-space source differs')
    value=json.loads(gzip.decompress((out/'results.json.gz').read_bytes()));replayed=assemble(root);replayed['result_id']=identity(replayed)
    if value!=replayed:raise ValueError('Replayed design definitions or necessary screens differ')
    native=json.loads((out/'native-index.json').read_bytes())
    if compact(value,native)!=json.loads((out/'summary.json').read_bytes()):raise ValueError('Design-space summary differs from proposals')
    if (out/'model-diagnosis.json').is_file():
        import tarfile,tempfile
        from engineering.design_search import structural_families
        with tempfile.TemporaryDirectory() as temporary:
            folder=Path(temporary)
            with tarfile.open(out/'model-diagnosis-inputs.tar.gz') as archive:
                for name in ('body.inp','body.dat','candidate.json'):
                    (folder/name).write_bytes(archive.extractfile(name).read())
            if structural_families.diagnose_native(folder)!=json.loads((out/'model-diagnosis.json').read_bytes()):raise ValueError('Retained model diagnosis does not reproduce')
    for record in (m,value,json.loads((out/'summary.json').read_bytes())):
        if any(record.get(n) is not v for n,v in FLAGS.items()):raise ValueError('Research cannot grant physical release')
    return dict(verified=True,manifest_id=m['manifest_id'],**json.loads((out/'summary.json').read_bytes()))
