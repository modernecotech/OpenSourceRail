"""Publish the executed structural grammar without granting body acceptance."""
from pathlib import Path
from hashlib import sha256
import gzip,io,json,tarfile,shutil
from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded,identity,digest
from . import generative_campaign as engine,design_grammar as grammar,grammar_structure,material_database,grammar_coupling,remit

PRODUCER='engineering/design_search/generative_publication.py'
OUTPUT='docs/design-engine/generative-structure'
FLAGS=grammar.FLAGS


def source_map(value,root=ROOT):
    result={**value['source_sha256'],**material_database.source_map(),PRODUCER:digest(Path(root)/PRODUCER)}
    for c in value['candidates']:result.update(c['sources'])
    for e in value['evaluations']:result.update(e['DFMA']['source_sha256'])
    for name in ('requirement_policy','architecture_demand'):
        path='engineering/design_search/'+name+'.py';result[path]=digest(Path(root)/path)
    for name in ('common','braking','civil'):
        path='engineering/station_rail/'+name+'.py';result[path]=digest(Path(root)/path)
    if any(digest(Path(root)/path)!=h for path,h in result.items()):raise ValueError('A transitive physical dependency changed after campaign execution')
    return result


def check_propagation(value):
    evaluations={e['candidate_id']:e for e in value['evaluations']}
    for c in value['candidates']:
        p=c['parameters']
        if c['requirement_revision']!=remit.context(length_m=p['length_m'],width_m=p['width_m'],cars=p['cars'])['requirement_revision']:raise ValueError('Functional requirement context changed')
        if evaluations[c['candidate_id']]['coupled_accounts']!=grammar_coupling.evaluate(c):raise ValueError('Same-candidate motion/civil propagation differs')


def read_campaign(root=ROOT):
    root=Path(root);contract=identity(dict(sources=engine.sources(),specification=engine.specification(),native=True,cad=True))
    folder=root/'build/generative-design/campaigns'/contract
    value=json.loads((folder/'result.json').read_bytes())
    if value['campaign_id']!=identity({k:v for k,v in value.items() if k!='campaign_id'}) or value['source_sha256']!=engine.sources():raise ValueError('Execute the source-matched generative campaign first')
    return folder,value


def archive(folder):
    """Retain inputs/results/logs and index large locally retained field/CAD data."""
    buf=io.BytesIO();kept={};omitted={}
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_symlink():raise ValueError('Ordinary native evidence files required')
            if not p.is_file():continue
            if '__pycache__' in p.parts:continue
            name=p.relative_to(folder).as_posix();h=digest(p)
            if p.suffix.lower() in ('.dat','.frd','.12d','.step','.fcstd','.fcstd1'):
                omitted[name]=h;continue
            raw=p.read_bytes();kept[name]=h;t=tarfile.TarInfo(name);t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
        raw=encoded(dict(retained_sha256=kept,omitted_sha256=omitted,
            storage='Large fields and native CAD remain in local immutable runs, or reproduce with exact sources and indexed inputs; no remote artifact storage is claimed'))
        t=tarfile.TarInfo('archive-index.json');t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
    return gzip.compress(buf.getvalue(),mtime=0)


def carry_failed_method_epoch(previous, output, *, root=ROOT, native_index=None, epochs=None):
    """Carry immutable failed-method archives forward when local solver files were cleaned."""
    previous=Path(previous);output=Path(output);root=Path(root)
    native_index=[] if native_index is None else native_index
    epochs={} if epochs is None else epochs
    manifest=json.loads((previous/'manifest.json').read_bytes())
    actual={p.relative_to(previous).as_posix():digest(p) for p in previous.rglob('*')
        if p.is_file() and p!=previous/'manifest.json'}
    if (manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or manifest.get('files_sha256')!=actual):
        raise ValueError('Prior generative publication must verify before retaining its method epoch')
    old_index=json.loads((previous/'native-index.json').read_bytes())
    source_epochs=json.loads((previous/'source-epochs.json').read_bytes())
    failed=[row for row in old_index if row.get('kind')=='failed-method-epoch']
    required={'fixtures-r1/axial-s1','fixtures-r1/axial-s2',
              'fixtures-r1/tripod-s1','fixtures-r1/tripod-s2'}
    if {row.get('name') for row in failed}!=required:
        raise ValueError('Prior publication does not contain the exact four failed-method fixtures')
    for row in failed:
        archive_path=previous/row['archive']
        if (not archive_path.is_file()
                or digest(archive_path)!=manifest['files_sha256'].get(row['archive'])):
            raise ValueError('Retained failed-method archive is missing or changed')
        with tarfile.open(archive_path,mode='r:gz') as tar:
            members=tar.getmembers()
            if any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members):
                raise ValueError('Retained method archive contains an unsafe entry')
            files={m.name:m for m in members}
            archive_index=json.loads(tar.extractfile('archive-index.json').read())
            raw_manifest=json.loads(tar.extractfile('manifest.json').read())
            raw_result=json.loads(tar.extractfile('result.json').read())
            if (raw_manifest!=row['raw_manifest'] or raw_result!=row['raw_result']
                    or raw_manifest.get('manifest_id')!=identity({k:v for k,v in raw_manifest.items() if k!='manifest_id'})):
                raise ValueError('Retained method archive identity differs from its index')
            recorded={k:v for k,v in raw_manifest.get('files_sha256',{}).items() if k!='manifest.json'}
            archived={**archive_index.get('retained_sha256',{}),**archive_index.get('omitted_sha256',{})}
            archived.pop('manifest.json',None)
            if recorded!=archived:
                raise ValueError('Retained method archive does not cover its recorded payload')
            for name,h in archive_index.get('retained_sha256',{}).items():
                if name not in files or sha256(tar.extractfile(name).read()).hexdigest()!=h:
                    raise ValueError('Retained method archive payload hash differs')
            if any(name in files for name in archive_index.get('omitted_sha256',{})):
                raise ValueError('Omitted historical solver fields unexpectedly appear in the archive')
        # Historical sources remain pinned by hash and never become current inputs.
        for repository_path,h in row['raw_result'].get('source_sha256',row['raw_manifest'].get('source_sha256',{})).items():
            current=root/repository_path
            if current.is_file() and digest(current)==h:
                continue
            cached=source_epochs.get(h)
            candidates=[]
            if cached:
                candidates.append(previous/cached['artifact'])
            candidates.append(root/'build/generative-design/source-epochs'/h)
            source=next((p for p in candidates if p.is_file() and digest(p)==h),None)
            if source is None:
                raise ValueError(f'Retained method source epoch is unavailable: {repository_path}')
            relative='historical-sources/'+h
            target=output/relative;target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and digest(target)!=h:
                raise ValueError('Historical source cache collision')
            if not target.exists():shutil.copyfile(source,target)
            epochs[h]=dict(repository_path=repository_path,artifact=relative)
        target_name=f'native/{len(native_index)}.tar.gz'
        target=output/target_name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(archive_path,target)
        native_index.append({**row,'archive':target_name})
    return native_index,epochs


def find_retained_method_publication(root=ROOT):
    """Find a single intact prior packet that carries the pinned failed r1 fixtures."""
    root=Path(root);base=root/'build/generative-design/replaced-publications'
    required={'fixtures-r1/axial-s1','fixtures-r1/axial-s2',
              'fixtures-r1/tripod-s1','fixtures-r1/tripod-s2'}
    matches=[]
    if not base.is_dir():return None
    for previous in sorted(p for p in base.iterdir() if p.is_dir()):
        index_path=previous/'native-index.json';manifest_path=previous/'manifest.json'
        if not index_path.is_file() or not manifest_path.is_file():continue
        try:
            index=json.loads(index_path.read_bytes())
            failed=[row for row in index if row.get('kind')=='failed-method-epoch']
        except (OSError,ValueError,TypeError):
            continue
        if {row.get('name') for row in failed}==required:
            signature=tuple(sorted((row['name'],row['raw_manifest'].get('manifest_id'),
                                    row['raw_result'].get('evaluation_id')) for row in failed))
            matches.append((previous,signature))
    if not matches:return None
    if len({signature for _,signature in matches})!=1:
        raise ValueError('Multiple distinct failed-method archives are retained; choose the exact source epoch')
    return matches[-1][0]


def summary(value):
    evaluations={r['candidate_id']:r for r in value['evaluations']};rows=[]
    for c in value['candidates']:
        e=evaluations[c['candidate_id']]
        rows.append(dict(label=c['label'],candidate_id=c['candidate_id'],parent_ids=c['parent_candidate_ids'],
            gross_structure_stock_kg=c['known_structure_stock_kg'],mechanism_count=e['rigidity']['mechanism_count'],
            manufactured_occurrences=e['DFMA']['resolved_manufactured_component_count'],
            full_body_evaluator='unavailable',integrated_suitability='unknown'))
    r=dict(schema='osr-generative-structure-summary/1',campaign_id=value['campaign_id'],contract_id=value['contract_id'],
        candidate_count=len(rows),initial_recipe_count=5,rewrite_count=len(value['executed_rewrites']),rows=rows,
        CAD_case_count=len(value['CAD_results']),native_design_case_count=sum(r['native_jobs_used'] for r in value['native_results']),
        method_fixture_case_count=len(value['method_admission']['evaluation_ids']),
        native_design_results=[dict(candidate_id=r['candidate_id'],execution=r['execution'],numerical_validity=r.get('numerical_validity'),
            subdivisions=r['subdivisions'],maximum_displacement_m=r.get('maximum_displacement_m'),
            reference_relative_error=r.get('reference_displacement_relative_error'),
            force_relative_residual=r.get('force_relative_residual'),moment_relative_residual=r.get('moment_relative_residual'),
            energy_relative_residual=r.get('energy_relative_residual'),engineering_screen=r.get('engineering_screen')) for r in value['native_results']],
        integration_stock_difference_kg=value['integration_comparison']['DFMA']['known_stock_subtotal_difference_kg'],
        complete_installed_mass_kg=None,complete_installed_CG_m=None,complete_installed_inertia_kg_m2=None,whole_life_cost_USD=None,
        model_scope=grammar_structure.SCOPE,integrated_selection=None,selected_reference_changed=False,city_packages_regenerated=0,**FLAGS)
    return r


def readme(s):
    lines=['# Executed generative structural design','',
        'The selected v0.6 railway is a reference, not the boundary of the design space. This new layer generates physical stock, load-path graphs, apertures, material assignments, joints, typed interfaces and assembly operations. Five initial recipes compose shared productions; a new recipe can combine those productions without adding another hardcoded body mesh. New primitive types and unsupported physics still require a generator/evaluator development task.','',
        f"**{s['candidate_count']} physical candidates, {s['rewrite_count']} executed rewrites, {s['CAD_case_count']} native CAD exports and {s['native_design_case_count']} native axial design calculations.** Four independent native method fixtures passed. No complete carriage, physical journey or economic winner is qualified.",'',
        '## What can actually change','',
        'The demonstrated productions vary aluminium versus research GFRP members, skin versus foam/honeycomb sandwich layers, rib spacing, repeated modular segments, underfloor triangulation, member proportions and separate versus shared roof/PV/channel manufacture. Car length, width, formation and support positions are explicit parameters with new requirement contexts. The existing 102-variable adaptive registry covers further railway domains; a descriptor is distinct from an executable, validated adapter.','',
        'The current competition preserves the 17 m reference envelope, passenger accommodation and door/window openings. A separate test generates a shorter body and propagates its geometry, stock and requirement context. Passenger fitout itself remains an unlocated source-bound account, so a new length is a research proposal rather than an accepted seating or evacuation layout.','',
        '| Generated recipe | Gross body stock | Pin-graph mechanisms | Declared manufactured groups |',
        '|---|---:|---:|---:|']
    for r in s['rows']:lines.append(f"| {r['label']} | {r['gross_structure_stock_kg']:.1f} kg | {r['mechanism_count']} | {r['manufactured_occurrences']} |")
    lines += ['',
        '**These are gross body-stock subtotals, not vehicle tare.** Prismatic members are untrimmed nominal stock and can overlap at nodes. Joint cuts, actual joint hardware, fasteners, installed fitout positions and complete geometry remain unresolved. Known-stock CG and inertia are calculated; complete installed mass, CG and inertia are unknown.','',
        '## A failure produces an actual new load path','',
        'The initial underfloor is explicitly pin-jointed. Its rectangular cells have 49 mechanisms, so this particular axial load path cannot carry the declared load without further restraint or a different joint model. The engine diagnoses this conditional design failure, inserts physical diagonals below passenger openings, assigns a fresh physical identity, rebuilds stock and loads, and evaluates the child. It does not add fictitious ground restraints or reject all frame/sandwich bodies.','',
        'The rewritten graph has zero mechanisms. Two CalculiX T3D2 runs, with one and two axial subdivisions per member, agree with an independent stiffness-matrix solution and satisfy force, moment and energy residual checks. Maximum displacement is about 30.35 mm in this **underfloor-only axial hypothesis**. This is not comparable to the previous complete-body displacement and is not a pass/fail judgement against L/500.','',
        'The subdivision test checks straight-member axial invariance, not shell/solid mesh convergence. Pin joints carry no bending moments; real tube-end cuts, joint stiffness, local/global buckling, member strength, floor load introduction, laminate behaviour, fatigue, modes, thermal effects, fire and physical correlation remain open. The other shell/monocoque recipes have geometry and stock, but lack a suitable full-body evaluator. Their pin-graph mechanisms do not establish that their manufactured bonded or rigid-jointed bodies would fail.','',
        '## Numerical errors produce model repair','',
        'The first independent tripod subdivision run exposed an input-writer error: a long oblique constraint exceeded CalculiX input-line capacity. That failed execution and its exact producer are retained. The writer was corrected, then all four new axial-bar/tripod fixtures were rerun successfully. The bar fixture includes a load at its restrained node to independently check the solver reaction convention. The corrected method is admitted only for its axial scope.','',
        '## Integration, materials and manufacture','',
        f"A separate rewrite integrates roof/PV/channel stock into fewer declared manufacturing groups, changing the counted subtotal by {s['integration_stock_difference_kg']:+.2f} kg. Required function tags remain covered; equivalent performance, net installed savings, fabrication feasibility, repair consequences and cost are unproven. Another rewrite changes rib positions. Both are executed geometry experiments, not automatic acceptance.",'',
        'The material search filters retained primary supplier facts by component function, stock form, temperature, directional properties and declared processes. PET/PVC foams, aluminium/aramid honeycombs, joining products and equipment leads retain missing hot/wet, fatigue, fire and design-allowable data. Current GFRP axial stiffness is an explicit research assumption; no isotropic substitute is used to qualify a laminate. A honeycomb density does not supply a full orthotropic law.','',
        'The interface graph checks units, frames, directions, declared capacities, simultaneous demands, aperture keepouts, function coverage and assembly dependencies. Unsupported interface capacity or unlocated equipment remains unknown. DFMA generates fabrication/join/inspection operations and distinguishes geometric prisms from declared manufactured occurrences. Unknown tooling, labour, purchased price, QA, access and repair data remain unknown.','',
        '## Same-candidate propagation and continuation','',
        'Each design carries one physical identity through actual nominal solids, stock mass properties, load graph, CAD, interface checks, assembly, required-motion profiles and preliminary civil comparisons. Changed counted mass propagates into 1.5/2/3 km required-force/energy calculations and box/twin/U crowd-load studies. This is account propagation, not a converged force–motion–thermal simulation: actual moving LIM capability, full installed vehicle properties and installed economics remain missing.','',
        'The coordinator resumes exact-source native/CAD packets under bounded jobs/time. It preserves model-development tasks and all rejected/interrupted/invalid evidence. OpenMDAO, pymoo, build123d and Dakota are optional tools, not evidence: none was executed for this competition. FreeCAD and CalculiX performed the native work. A general autonomous search over every railway subsystem remains further work.','',
        '```bash','./osr design generative plan','./osr design generative run','./osr design generative publish','./osr design generative verify','```','',
        '[Summary](summary.json) · [Complete generated campaign](campaign.json.gz) · [Materials](materials.json.gz) · [Native/CAD index](native-index.json) · [Source epochs](source-epochs.json) · [Manifest](manifest.json)','',
        'Large native fields and CAD solids stay in indexed local runs or regenerate from exact-source inputs. Small input decks, geometry definitions, logs, results, checks and full raw-payload hashes are retained here. No remote artifact store or physically released design is claimed. The selected reference and all 266 city packages are unchanged.','']
    return '\n'.join(lines)


def build(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output)
    previous_path=None
    if out.exists():
        previous=json.loads((out/'manifest.json').read_bytes())
        if all(digest(root/p)==h for p,h in previous['source_sha256'].items()):return verify(root,out)
        if previous['manifest_id']!=identity({k:v for k,v in previous.items() if k!='manifest_id'}) or previous['files_sha256']!={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}:raise ValueError('Changed publication payload must be investigated before replacement')
    folder,value=read_campaign(root);check_propagation(value)
    if out.exists():
        previous_path=root/'build/generative-design/replaced-publications'/previous['manifest_id'];previous_path.parent.mkdir(parents=True,exist_ok=True)
        if previous_path.exists():raise ValueError('Previous publication already retained')
        shutil.move(out,previous_path)
    out.mkdir(parents=True);(out/'native').mkdir();epochs={};native=[]
    packages=[('design/'+p.name,p,'current-design') for p in sorted((folder/'native').iterdir())]
    packages += [('CAD/'+p.name,p,'current-CAD') for p in sorted((folder/'cad').iterdir())]
    reuse_failed_epoch=False
    for epoch in ('r1','r2'):
        base=root/'build/generative-design'/('native-benchmarks-'+epoch)
        local=[p for p in sorted(base.iterdir()) if p.is_dir() and (p/'manifest.json').is_file()] if base.is_dir() else []
        if epoch=='r1' and not local:
            reuse_failed_epoch=True
        else:
            packages += [('fixtures-'+epoch+'/'+p.name,p,'failed-method-epoch' if epoch=='r1' else 'current-method') for p in local]
    for i,(name,p,kind) in enumerate(packages):
        manifest=json.loads((p/'manifest.json').read_bytes());result=json.loads((p/'result.json').read_bytes())
        if manifest['manifest_id']!=identity({k:v for k,v in manifest.items() if k!='manifest_id'}):raise ValueError('Raw packet receipt differs')
        if manifest['files_sha256']!={q.relative_to(p).as_posix():digest(q) for q in p.rglob('*') if q.is_file() and q.name!='manifest.json' and '__pycache__' not in q.parts}:raise ValueError('Raw packet files differ')
        for path,h in result.get('source_sha256',manifest.get('source_sha256',{})).items():
            if digest(root/path)==h:continue
            original=root/'build/generative-design/source-epochs'/h
            if digest(original)!=h:raise ValueError('Retained original producer unavailable')
            target='historical-sources/'+h;(out/'historical-sources').mkdir(exist_ok=True);(out/target).write_bytes(original.read_bytes());epochs[h]=dict(repository_path=path,artifact=target)
        target='native/'+str(i)+'.tar.gz';(out/target).write_bytes(archive(p));native.append(dict(name=name,kind=kind,archive=target,raw_manifest=manifest,raw_result=result))
    if reuse_failed_epoch:
        if previous_path is None:
            previous_path=find_retained_method_publication(root)
        if previous_path is None:
            raise ValueError('Historical r1 method fixtures require a prior immutable publication archive')
        native,epochs=carry_failed_method_epoch(previous_path,out,root=root,native_index=native,epochs=epochs)
    s=summary(value)
    files={'campaign.json.gz':gzip.compress(encoded(value),mtime=0),'materials.json.gz':gzip.compress(encoded(material_database.catalogue()),mtime=0),
        'summary.json':encoded(s),'native-index.json':encoded(native),'source-epochs.json':encoded(epochs),'README.md':readme(s).encode()}
    for name,raw in files.items():(out/name).write_bytes(raw)
    m=dict(schema='osr-generative-structure-publication/1',source_sha256=source_map(value,root),
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**FLAGS)
    m['manifest_id']=identity(m);(out/'manifest.json').write_bytes(encoded(m));return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/OUTPUT if output is None else Path(output);m=json.loads((out/'manifest.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):raise ValueError('Publication receipt differs')
    if any(digest(root/p)!=h for p,h in m['source_sha256'].items()):raise ValueError('Generative publication source changed')
    if m['files_sha256']!={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json'}:raise ValueError('Generative publication payload changed')
    value=json.loads(gzip.decompress((out/'campaign.json.gz').read_bytes()));s=json.loads((out/'summary.json').read_bytes())
    if value['campaign_id']!=identity({k:v for k,v in value.items() if k!='campaign_id'}) or s!=summary(value):raise ValueError('Campaign or summary identity differs')
    check_propagation(value)
    ids=set()
    for c in value['candidates']:grammar.validate(c);ids.add(c['candidate_id'])
    if len(ids)!=len(value['candidates']) or {e['candidate_id'] for e in value['evaluations']}!=ids:raise ValueError('Candidate/evaluation identities differ')
    if any(r['parent_id'] not in ids or r['candidate_id'] not in ids or r['parent_id']==r['candidate_id'] for r in value['executed_rewrites']):raise ValueError('Rewrite ancestry differs')
    if any(s.get(k) is not False for k in FLAGS) or s['integrated_selection'] is not None:raise ValueError('Research cannot inherit acceptance')
    epochs=json.loads((out/'source-epochs.json').read_bytes())
    for h,r in epochs.items():
        if digest(out/r['artifact'])!=h:raise ValueError('Historical producer differs')
    for row in json.loads((out/'native-index.json').read_bytes()):
        with tarfile.open(out/row['archive']) as tar:
            index=json.loads(tar.extractfile('archive-index.json').read());manifest=json.loads(tar.extractfile('manifest.json').read());result=json.loads(tar.extractfile('result.json').read())
            if manifest!=row['raw_manifest'] or result!=row['raw_result']:raise ValueError('Native index differs from retained bytes')
            if manifest['files_sha256']!={k:v for k,v in {**index['retained_sha256'],**index['omitted_sha256']}.items() if k!='manifest.json'}:raise ValueError('Native archive does not cover original receipt')
            for name,h in index['retained_sha256'].items():
                if sha256(tar.extractfile(name).read()).hexdigest()!=h:raise ValueError('Native retained bytes differ')
            for path,h in result.get('source_sha256',manifest.get('source_sha256',{})).items():
                if digest(root/path)!=h and h not in epochs:raise ValueError('Native producer source missing')
    return dict(manifest_id=m['manifest_id'],campaign_id=s['campaign_id'],candidate_count=s['candidate_count'],native_design_case_count=s['native_design_case_count'],CAD_case_count=s['CAD_case_count'],integrated_suitability='unknown',**FLAGS)
