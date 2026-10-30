"""Compact, source-bound publication of continuing adaptive research."""
from pathlib import Path
from collections import Counter
import gzip,io,json,shutil,tarfile
from hashlib import sha256
from engineering.station_rail import ROOT,vehicle
from engineering.station_rail.common import encoded,identity,digest
from . import adaptive_campaign as engine,joint_body

PRODUCER='engineering/design_search/adaptive_publication.py'


def _archive(folder):
    buf=io.BytesIO();kept={};omitted={}
    with tarfile.open(fileobj=buf,mode='w') as tar:
        for p in sorted(Path(folder).rglob('*')):
            if p.is_symlink():raise ValueError('Ordinary native files required')
            if not p.is_file():continue
            name=p.relative_to(folder).as_posix();h=digest(p)
            # Full displacement/stress fields stay in local immutable runs.
            # Their receipt hashes travel with reproducible inputs and logs.
            if p.suffix in ('.dat','.frd','.msh','.pre','.res','.pos','.12d','.eig'):omitted[name]=h;continue
            raw=p.read_bytes();kept[name]=h;t=tarfile.TarInfo(name);t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
        raw=encoded(dict(retained_sha256=kept,omitted_sha256=omitted,field_storage='Local immutable run or exact-source regeneration; no remote artifact object is claimed'))
        t=tarfile.TarInfo('archive-index.json');t.size=len(raw);t.mtime=0;t.mode=0o644;tar.addfile(t,io.BytesIO(raw))
    return gzip.compress(buf.getvalue(),mtime=0)


def summary(value,baseline):
    rows=[];defs={d['definition_id']:d for d in value['physical_definitions']}
    for r in value['results']:
        d=defs[r['definition_id']];crowd=next((c for c in r['native_cases'] if c['case']=='crowd'),{})
        rows.append(dict(candidate_id=r['candidate_id'],definition_id=r['definition_id'],section=d['name'],
            accounted_tare_kg_per_car=r['accounted_tare_kg_per_car'],
            mass_change_vs_previous_jointed_body_kg=r['accounted_tare_kg_per_car']-baseline['mass']['accounted_tare_kg_per_car'],
            normal_vertical_displacement_m=r['normal_vertical_displacement_m'],
            crowd_vertical_displacement_m=crowd.get('maximum_vertical_displacement_m'),crowd_mesh_confirmed=False,
            numerical_validity=r['numerical_validity'],integrated_suitability=r['integrated_suitability'],
            provisional_target_is_acceptance_gate=False,**engine.FLAGS))
    result=dict(schema='osr-adaptive-design-summary/1',campaign_id=value['campaign_id'],contract_id=value['contract_id'],
        variable_count=len(value['variable_registry']['variables']),domains=Counter(d['domain'] for d in value['variable_registry']['variables'].values()),
        baseline_candidate_id=baseline['candidate_id'],baseline_accounted_tare_kg_per_car=baseline['mass']['accounted_tare_kg_per_car'],
        baseline_normal_vertical_displacement_m=value['seed_observation']['observations']['body_vertical_displacement_m'],
        rows=rows,physical_definitions=len(defs),native_case_count=sum(len(r['native_cases']) for r in value['results']),
        research_frontier_items=len(value['frontier']),search_status=value['search_status'],
        integrated_selection=None,selected_reference_changed=False,city_packages_regenerated=0,**engine.FLAGS)
    return result


def readme(s):
    lines=['# Function-first adaptive design','',
      'The generator seeks a functioning railway under broad service, safety, accessibility, affordability and manufacturing requirements. Initial dimensions, material choices, support arrangements and provisional stiffness targets are hypotheses to investigate. A fixed list of four sill sizes or one global L/500 number is not a universal design space or acceptance rule.','',
      f"The extensible registry currently declares **{s['variable_count']} variables across {len(s['domains'])} domains**. Examples are not exhaustive. New descriptors can participate in revision planning without changing its fixed strategy table. A descriptor does not conjure material data or a valid solver; unsupported changes create bounded generator/evaluator/data tasks. The selected v0.6 reference is preserved.",'',
      '## What the engine changes','',
      '| Domain | Registered variables |','|---|---:|']
    for name,count in s['domains'].items():lines.append(f'| {name} | {count} |')
    lines += ['',
      'This includes material grades, foam/honeycomb/corrugated cores, cell directions, layups, structural topology, load paths, member proportions, joints and inserts; bogie arrangement and support positions; propulsion topology/windings/fin/gap/inverters; brakes; doors/windows/benches/floors/roofs/HVAC; formation, capacity, speed, spacing, powered zones; civil, stations, manufacturing, maintenance and recovery. Each change declares its interfaces and downstream geometry, mass, loads, heat, controls, service and economic recalculations.','',
      '## Different findings require different actions','',
      '- A provisional target exceedance prompts criterion justification and diverse physical experiments; it does not reject an architecture.','- A supported functional/physical limit violation prompts a redesign of the mechanism, load path, component or railway arrangement.','- Numerical nonconvergence or a model-domain exceedance prompts model repair or development before interpreting physical performance. Raising the retained linear-steel field bound does not create a nonlinear motor.','- Missing material, interface or installed-equipment evidence prompts targeted measurements/data work.','- Two recorded unsuccessful local changes cause escalation toward untried load paths, material arrangements or system architecture.','',
      '[Requirement policy](requirement-policy.json) separates mandatory obligations, preferences, revisable assumptions and numerical domains. Quantitative hard limits require a justified interface/material/function basis. Changing a target alone does not change geometry or establish improvement. Historical results retain their original criteria and identities.','',
      '## Executed material-redistribution experiment','',
      'The new counted rectangular-tube adapter accepts continuous depth and wall thickness within its declared construction/model domain. Those domain bounds can be extended through explicit geometry and numerical validation; they are not project-wide requirements. The two experiments keep the upper sill datum, support locations, passenger/crowd loads and joint topology while redistributing material. No reference geometry or old solver receipt is edited.','',
      '| Section | Accounted tare/car | Change versus previous jointed body | Normal vertical displacement | Mesh trend |',
      '|---|---:|---:|---:|---|']
    for row in s['rows']:
        u='Unconfirmed' if row['normal_vertical_displacement_m'] is None else f"{row['normal_vertical_displacement_m']*1000:.3f} mm"
        lines.append(f"| {row['section']} | {row['accounted_tare_kg_per_car']/1000:.3f} t | {row['mass_change_vs_previous_jointed_body_kg']:+.3f} kg | {u} | {row['numerical_validity']} |")
    lines += ['',
      f"The previous finite-area body accounts for {s['baseline_accounted_tare_kg_per_car']/1000:.3f} t/car and predicts {s['baseline_normal_vertical_displacement_m']*1000:.3f} mm normal displacement. Its former 25.6 mm comparison is advisory in the new policy, with integrated suitability unknown. Known-stock comparisons are not complete installed mass or a whole-railway optimum.",'',
      'Normal coarse/fine and crowd cases use the same actual candidate stock and load inventory. The crowd case has one mesh and is not independently mesh-confirmed. Thin-wall buckling, local stress, weld/HAZ and joint fatigue, actual material/bond allowables, flexible modes, dynamic clearances, manufacturing and physical correlation remain necessary work. Less deflection does not close those obligations.','',
      'The changed mass propagates into wheel/axle reactions, rotational-mass-aware 1.5/2/3 km required-force/energy profiles and crowd-sized box/twin/U concrete comparisons. These are required forces and preliminary civil quantities; no available nonlinear LIM map, physical journey or installed cost is invented.','',
      '## Continue instead of stopping at a failed screen','',
      'The campaign saves immutable per-case native results and a pending work frontier. Subsequent run invocations resume unfinished cases and then advance to new definitions, rather than repeatedly selecting the same first two. Focused redistribution and deterministic continuous-domain sampling generate additional exact-stock section proposals; the declared solver domain can be extended with a new validated adapter. Publication uses a zero-new-job budget. A per-invocation job/time budget controls resource use; it does not conclude that no working design exists, discard unfinished work or grant acceptance. Exact physics can be reused under a revised advisory policy when stock, loads, model source, mesh and solver bytes match. Reuse carries an explicit new context without changing the native receipt.','',
      'A working solution is not mathematically guaranteed for every combination of requirements. If local revisions do not improve supported margins, the next work changes a family/architecture or establishes missing evaluation capability. The engine never manufactures success by weakening an evidenced safety limit or assigning zero to missing equipment.','',
      '```bash','./osr design adaptive plan','./osr design adaptive run --max-jobs 1','./osr design adaptive run','./osr design adaptive publish','./osr design adaptive verify','```','',
      '[Summary](summary.json) · [Registry](variables.json) · [Campaign and coupled calculations](campaign.json.gz) · [Next frontier](frontier.json.gz) · [Native evidence](native-index.json) · [Checkpoint/resume](execution-demonstration.json) · [Receipt](manifest.json)','',
      'Native input decks, definitions, logs and responses summaries are retained. Large nodal/stress fields remain local or regenerate from their indexed SHA-256 receipts, rather than adding them to ordinary Git history. Physical, requirement, evaluation and selection identities remain separate.','']
    return '\n'.join(lines)


def build(root=ROOT,output=None):
    root=Path(root);value=engine.run(root,maximum_new_jobs=0);out=root/engine.OUTPUT if output is None else Path(output)
    if len(value['results'])<value['specification']['invocation_budget']['body_candidates'] or any(len(r['native_cases'])!=3 for r in value['results']):raise ValueError('Complete the requested native experiments before publishing this comparison')
    baseline=joint_body.materialize_finite_body(vehicle.build(root),root=root)
    if baseline['candidate_id']!=value['seed_observation']['candidate_id']:raise ValueError('Previous-body comparison identity differs')
    s=summary(value,baseline)
    if out.exists():
        target=root/'build/adaptive-design/replaced-publications'/digest(out/'manifest.json');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():raise ValueError('Previous publication already retained')
        shutil.move(out,target)
    out.mkdir(parents=True);(out/'native').mkdir();native=[];folder=root/'build/adaptive-design'/value['contract_id']
    for p in sorted((folder/'native').iterdir()):
        if not (p/'manifest.json').is_file():continue
        request=json.loads((p/'request.json').read_bytes());result=engine._native_record(p,request)
        archive='native/'+p.name+'.tar.gz';(out/archive).write_bytes(_archive(p))
        native.append(dict(job_id=p.name,request=request,evaluation_id=result['evaluation_id'],archive=archive,raw_summary=result,**engine.FLAGS))
    checkpoints={};historic={};execution_contract=None
    for name in ('canonical-checkpoint','completed-invocation'):
        p=root/'build/adaptive-design'/(name+'.json')
        r=json.loads(p.read_bytes())
        if (r.get('schema')!='osr-function-first-adaptive-campaign/1'
                or r.get('campaign_id')!=identity({k:v for k,v in r.items() if k!='campaign_id'})
                or r.get('selected_reference_changed') is not False
                or any(r.get(k) is not v for k,v in engine.FLAGS.items())):
            raise ValueError('Checkpoint identity or research disposition differs: '+name)
        if execution_contract is not None and r['contract_id']!=execution_contract:raise ValueError('Checkpoint and resumed execution must share their original source contract')
        execution_contract=r['contract_id']
        for path,h in r['source_sha256'].items():
            if digest(root/path)==h:continue
            old=root/'build/adaptive-design/coordinator-source-epochs'/h
            if not old.is_file() or digest(old)!=h:raise ValueError('Original execution source snapshot unavailable: '+path)
            artifact='historical-sources/'+h;(out/'historical-sources').mkdir(exist_ok=True);(out/artifact).write_bytes(old.read_bytes());historic[h]=dict(repository_path=path,artifact=artifact)
        checkpoints[name]=dict(contract_id=r['contract_id'],source_sha256=r['source_sha256'],new_native_jobs=r['new_native_jobs'],reused_native_jobs=r['reused_native_jobs'],search_status=r['search_status'],result_ids=[x['evaluation_id'] for x in r['results']],frontier_items=len(r['frontier']))
    checkpoints['current_context']=dict(contract_id=value['contract_id'],new_native_jobs=value['new_native_jobs'],reused_native_jobs=value['reused_native_jobs'],
        explanation='Current coordinator integrity guards and metadata can reuse the original source-identical numerical packets; no new solve is implied')
    files={'campaign.json.gz':gzip.compress(encoded(value),mtime=0),'summary.json':encoded(s),'variables.json':encoded(value['variable_registry']),
        'requirement-policy.json':encoded(value['requirement_policy']),'frontier.json.gz':gzip.compress(encoded(value['frontier']),mtime=0),
        'native-index.json':encoded(native),'execution-demonstration.json':encoded(checkpoints),'historical-source-index.json':encoded(historic),'README.md':readme(s).encode()}
    for name,raw in files.items():(out/name).write_bytes(raw)
    m=dict(schema='osr-adaptive-publication/1',source_sha256={**value['source_sha256'],PRODUCER:digest(root/PRODUCER)},
        files_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()},**engine.FLAGS)
    m['manifest_id']=identity(m);(out/'manifest.json').write_bytes(encoded(m));return verify(root,out)


def verify(root=ROOT,output=None):
    root=Path(root);out=root/engine.OUTPUT if output is None else Path(output);result=engine.verify(root,out)
    value=json.loads(gzip.decompress((out/'campaign.json.gz').read_bytes()));s=json.loads((out/'summary.json').read_bytes())
    if s!=summary(value,joint_body.materialize_finite_body(vehicle.build(root),root=root)):raise ValueError('Adaptive summary differs')
    for h,r in json.loads((out/'historical-source-index.json').read_bytes()).items():
        if digest(out/r['artifact'])!=h:raise ValueError('Original coordinator source snapshot differs')
    for row in json.loads((out/'native-index.json').read_bytes()):
        r=row['raw_summary']
        if r['evaluation_id']!=identity({k:v for k,v in r.items() if k!='evaluation_id'}):raise ValueError('Native summary identity differs')
        if any(digest(root/name)!=h for name,h in r['source_sha256'].items()):raise ValueError('Native physics source differs')
        with tarfile.open(out/row['archive']) as tar:
            index=json.loads(tar.extractfile('archive-index.json').read())
            for name,h in index['retained_sha256'].items():
                if sha256(tar.extractfile(name).read()).hexdigest()!=h:raise ValueError('Retained native bytes differ')
    return dict(result,variable_count=s['variable_count'],native_cases=s['native_case_count'],integrated_suitability='unknown')
