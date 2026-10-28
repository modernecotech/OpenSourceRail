"""Current inputs -> numerical checks -> explicit engineering closure frontier."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import gzip
import io
import json
import tarfile
import tempfile
import tomllib
import shutil

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded, identity, digest
from engineering.design_search import system_inventory, test_readiness, system_motion
from engineering.railway_twin import model, pipeline as parent
from . import FLAGS, evidence, domains, infrastructure, operating, motor

PRODUCER='engineering/railway_completion/coordinator.py'
SPEC='campaigns/engineering-completion.toml'
OUTPUT='docs/design-engine/engineering-closure'
PROTOCOLS={'installed-equipment':{'T01','T02','T03','T04','T05','T06','T07'},
    'body-structure':{'T02','T03','T04'},'independent-brakes':{'T06','T07'},
    'civil-and-site':{'T01','T09'},'whole-life-economics':{'T01','T08','T10'}}


def specification(root=ROOT):
    spec=tomllib.loads((Path(root)/SPEC).read_text())
    expected=dict(schema='osr-current-engineering-completion/1',revision='CURRENT-CLOSURE-1',
        reference_changes_allowed=False,default_family='gfrp_semimonocoque',default_distance_m=2000.,
        maximum_input_envelopes=32,maximum_motor_packages=8,automatic_physical_acceptance=False,
        authentication_from_imported_code_allowed=False,required_physical_protocols=[f'T{i:02}' for i in range(1,11)],
        required_domains=list(domains.REQUIRED_SCOPES))
    if spec!=expected:
        raise ValueError('Current closure scope, input bounds or non-promoting obligations differ')
    return spec


def sources(root=ROOT):
    root=Path(root);result=parent.sources(root)
    for p in sorted((root/'engineering/railway_completion').glob('*.py')):
        result[p.relative_to(root).as_posix()]=digest(p)
    for name in (SPEC,'osr-complete',OUTPUT+'/README.md'):
        result[name]=digest(root/name)
    if result[PRODUCER]!=digest(__file__):
        raise ValueError('Executing closure coordinator differs from source root')
    return dict(sorted(result.items()))


def _authenticated_ids(assessment):
    return {assessment['record_id'],*[r['sha256'] for r in assessment['raw_files']]}


def _scoped_domains(bundle,body,ledger,loaded,root):
    records=loaded['records'];outputs={};evaluations={}
    for domain in domains.REQUIRED_SCOPES:
        relevant=[r for r in records if r.get('schema')==domains.SCHEMA and r.get('domain')==domain]
        allowed=[a for a in loaded['assessments'] if a['authenticated'] and a['protocol_id'] in PROTOCOLS[domain]
                 and (domain=='whole-life-economics' or a.get('provenance_kind')!='commercial-quote')]
        trusted={value for a in allowed for value in _authenticated_ids(a)}
        result=domains.evaluate(bundle,body,ledger,records=relevant,authenticated=trusted,root=root)
        outputs[domain]=result['domains'][domain];evaluations[domain]=result['evaluation_id']
    return dict(domains=outputs,domain_evaluation_ids=evaluations,
        numerical_domains_supported=sum(r['state']=='supported-for-numerical-scope' for r in outputs.values()),**FLAGS)


def _contexts():
    return [('empty',dict(load='empty')),('normal',dict(load='normal')),('crowd',dict(load='crowd')),
        ('adverse-normal',dict(load='normal',grade_up_fraction=.02,headwind_m_s=10.,rail_adhesion=.025))]


def assess(root=ROOT,*,family='gfrp_semimonocoque',distance_m=2000.,input_root=None,input_manifest=None,
           authenticator=None,artifact_verifier=None,authentication_context_id=None,verifier_context_id=None,
           motor_packages=()):
    root=Path(root);spec=specification(root);epoch=sources(root)
    for callback,context,label in ((authenticator,authentication_context_id,'authentication'),(artifact_verifier,verifier_context_id,'numerical verifier')):
        if callback is not None and (not isinstance(context,str) or len(context)!=64 or any(x not in '0123456789abcdef' for x in context)):
            raise ValueError('Trusted application '+label+' context identity required')
    m=model.materialize(family,distance_m,root);bundle=m['bundle'];body=m['body']
    inv=system_inventory.evaluate(body,bundle_id=bundle['candidate_id'],source_root=root)
    ledger=model.ledger(m,inv,root)
    if input_manifest is None:
        input_manifest=dict(schema='osr-wheel-LIM-input-manifest/1',binding=evidence.binding(bundle),envelopes=[])
    loaded=evidence.load(input_root or root,input_manifest,bundle,authenticator=authenticator)
    evaluated=_scoped_domains(bundle,body,ledger,loaded,root)
    loads=infrastructure.derive(ledger['scene'],bundle,ledger)
    # Site records cannot erase already-counted wayside weight from footing loads.
    civil=evaluated['domains']['civil-and-site']
    if civil['state']!='missing':
        record=next(r for r in loaded['records'] if r.get('domain')=='civil-and-site')
        if record['data'].get('infrastructure_load_evaluation_id')!=loads['evaluation_id']:
            civil['state']='missing'
            civil['open_items'].append(dict(kind='current-known-wayside-loads-not-bound',evaluation_id=loads['evaluation_id']))
        for supplied,computed,needed in zip(record['data']['supports'],civil.get('supports',[]),loads['supports']):
            margin=computed['counted_superstructure_dead_reaction_N']+supplied['other_vertical_load_N']-needed['known_dead_reaction_N']
            if margin < -1e-6:
                civil['state']='fail'
                civil['open_items'].append(dict(kind='omitted-known-superstructure-or-wayside-load',
                    support_id=supplied['id'],missing_vertical_load_N=-margin))
    evaluated['numerical_domains_supported']=sum(r['state']=='supported-for-numerical-scope' for r in evaluated['domains'].values())
    maps={}
    for a in loaded['assessments']:
        r=a['record'];data=r.get('data',{})
        if r.get('schema')=='osr-wheel-operating-evidence/1' and data.get('scope')=='available-force-map':
            if not a['authenticated'] or a['protocol_id']!='T05':
                continue
            name=data['loading_context']
            if name in maps:
                raise ValueError('Explicitly select one force map per loading context')
            maps[name]=data
    motion=[]
    for name,overrides in _contexts():
        data=maps.get(name,{})
        controller=data.get('controller_overrides',{})
        allowed={'current_command_A','initial_current_A','brake_start_m','dt_s','maximum_time_s'}
        if not isinstance(controller,dict) or set(controller)-allowed:
            raise ValueError('Explicit bounded current/brake controller hypotheses required')
        value=operating.evaluate(bundle,data.get('map'),scenario_overrides=dict(overrides,**controller),
            assessments=loaded['assessments'],artifact_verifier=artifact_verifier,current_source_sha256=epoch)
        motion.append(dict(name=name,result=value))
    if set(maps)-{r[0] for r in _contexts()}:
        raise ValueError('Unknown force-map loading context')
    physical={protocol:[a['assessment_id'] for a in loaded['assessments'] if a['protocol_id']==protocol and a['physical_protocol_screen_passed']]
        for protocol in spec['required_physical_protocols']}
    frontier=[]
    for domain,result in evaluated['domains'].items():
        if result['state']!='supported-for-numerical-scope':
            frontier.append(dict(kind='engineering-input-or-design',domain=domain,state=result['state'],open_items=result['open_items']))
    proposal=evaluated['domains']['installed-equipment'].get('proposed_physical_definition_revision')
    if proposal is not None:
        frontier.append(dict(kind='physical-rematerialization',domain='installed-equipment',state='pending',
            proposed_physical_revision_id=evaluated['domains']['installed-equipment']['proposed_physical_revision_id'],
            instruction='A changed installed assembly needs its own geometry/BOM/CAD/brake/civil/control bundle and new scoped evaluations; parent results are not inherited'))
    for row in motion:
        if not row['result']['numerical_arrival_predicted']:
            frontier.append(dict(kind='force-driven-journey',domain=row['name'],state='held',reasons=row['result']['map_admission']['reasons']))
    for protocol,ids in physical.items():
        if not ids:
            frontier.append(dict(kind='authenticated-physical-programme',domain=protocol,state='missing'))
    for task in frontier:
        task['id']=task['kind']+'/'+task['domain']
        task['task_id']=identity(dict(candidate_id=bundle['candidate_id'],kind=task['kind'],domain=task['domain']))
    native=[]
    if len(motor_packages)>spec['maximum_motor_packages']:
        raise ValueError('Bounded motor package inventory required')
    for folder in motor_packages:
        check=motor.verify(folder,root=root,require_current_tool=False)
        result=evidence.parse((Path(folder)/'result.json').read_bytes())
        data=evidence.parse((Path(folder)/'input.json').read_bytes())
        if data['request']['bundle_id']!=bundle['candidate_id']:
            raise ValueError('Motor package uses another exact candidate')
        trace=result.get('trace',[])
        native.append(dict(evaluation_id=result['evaluation_id'],request_id=result['request_id'],execution=result['execution'],
            state=result.get('state'),verified=check['verified'],voltage_peak_V=data['request']['voltage_peak_V'],
            verification_mode='recorded-execution-integrity',verification_scope=check['verification_scope'],
            recorded_tool_identity=check['recorded_tool_identity'],numerical_replayed=False,
            current_tool_verified=False,native_reuse_eligible=False,
            speed_m_s=data['request']['speed_m_s'],steps=len(trace),phase_direction=data['request']['phase_direction'],
            final_thrust_N=None if not trace else trace[-1]['thrust_N'],
            peak_path_current_A=None if not trace else max(abs(i) for row in trace for i in row['path_currents_A']),
            available_operating_map=False))
    value=dict(schema='osr-current-engineering-closure/1',candidate_id=bundle['candidate_id'],
        bundle_definition_id=bundle['definition_id'],body_candidate_id=body['candidate_id'],family=family,distance_m=distance_m,
        input_manifest=input_manifest,input_manifest_id=identity(input_manifest),
        authentication_context_id=authentication_context_id,verifier_context_id=verifier_context_id,
        assessments=loaded['assessments'],domain_results=evaluated,infrastructure_loads=loads,
        motion=motion,physical_protocol_records=physical,native_component_runs=native,
        required_test_programme=test_readiness.build(bundle,root=root),
        software_adapters=['current-record-ingestion','scoped-external-authentication','independent-map-replay-gate',
            '20m-coupled-moving-motor','net-equipment-mass-and-inertia','structure-and-brake-calculations',
            'known-wayside-and-civil-loads','site-footing-checks','whole-life-cashflow-coverage'],
        frontier=frontier,engineering_evidence_ready_for_independent_decision=not frontier,
        engineering_complete=False,physical_design_complete=False,integrated_selection=None,
        source_sha256=epoch,scope='Dynamic current engineering inputs and numerical evidence; all release decisions remain external',**FLAGS)
    if sources(root)!=epoch:
        raise ValueError('Current closure source changed during assessment')
    value['native_component_runs'].sort(key=lambda r:r['evaluation_id'])
    value['evaluation_id']=identity(value)
    return value


def _capture_inputs(input_root,manifest):
    pending=[];seen={}
    def references(value):
        if isinstance(value,dict):
            if set(value)=={'path','sha256'}:
                pending.append(value)
            else:
                for item in value.values():references(item)
        elif isinstance(value,list):
            for item in value:references(item)
    references(manifest)
    while pending:
        ref=pending.pop();name=ref['path']
        if name in seen:
            if sha256(seen[name]).hexdigest()!=ref['sha256']:
                raise ValueError('Conflicting source bytes at one input path')
            continue
        raw=evidence.read_owned(input_root,ref)
        seen[name]=raw
        if len(seen)>256 or sum(map(len,seen.values()))>evidence.MAX_TOTAL:
            raise ValueError('Input retention package budget exceeded')
        if raw.lstrip().startswith((b'{',b'[')):
            references(evidence.parse(raw))
    return seen


def _files(folder):
    result={}
    for p in sorted(Path(folder).rglob('*')):
        if p.is_symlink():raise ValueError('Linked closure artifact refused')
        if p.is_file() and p!=Path(folder)/'manifest.json':
            result[p.relative_to(folder).as_posix()]=digest(p)
    return result


def generate(output,*,root=ROOT,**options):
    root=Path(root);target=Path(output)
    if target.exists():raise ValueError('Fresh immutable closure directory required')
    epoch=sources(root);value=assess(root,**options)
    target.mkdir(parents=True)
    inputs=_capture_inputs(options.get('input_root') or root,value['input_manifest'])
    for name,raw in inputs.items():
        p=target/'inputs'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    native_allowed={'manifest.json','input.json','input-sources.tar.gz','preflight.json','stdout.log','stderr.log',
        'worker-result.json','partial-trace.jsonl','result.json'}
    for original in options.get('motor_packages',()):
        original=Path(original)
        if any(p.is_symlink() or not p.is_file() or p.name not in native_allowed for p in original.iterdir()):
            raise ValueError('Ordinary bounded flat native package required')
        row=evidence.parse((original/'result.json').read_bytes())
        shutil.copytree(original,target/'native'/row['evaluation_id'])
    (target/'input-manifest.json').write_bytes(encoded(value['input_manifest']))
    (target/'report.json.gz').write_bytes(gzip.compress(encoded(value),mtime=0))
    (target/'input-sources.tar.gz').write_bytes(parent._input_archive(root,epoch))
    if sources(root)!=epoch:raise ValueError('Source changed during closure generation; partial output retained')
    manifest=dict(schema='osr-current-engineering-closure-package/1',evaluation_id=value['evaluation_id'],
        candidate_id=value['candidate_id'],family=value['family'],distance_m=value['distance_m'],
        authentication_context_id=value['authentication_context_id'],verifier_context_id=value['verifier_context_id'],
        files_sha256=_files(target),source_sha256=epoch,**FLAGS)
    manifest['manifest_id']=identity(manifest)
    (target/'manifest.json').write_bytes(encoded(manifest))
    return verify(target,root=root,authenticator=options.get('authenticator'),artifact_verifier=options.get('artifact_verifier'),
        authentication_context_id=options.get('authentication_context_id'),verifier_context_id=options.get('verifier_context_id'))


def summary(value):
    return dict(candidate_id=value['candidate_id'],evaluation_id=value['evaluation_id'],
        numerical_domains_supported=value['domain_results']['numerical_domains_supported'],
        authenticated_records=sum(r['authenticated'] for r in value['assessments']),
        admitted_force_maps=sum(r['result']['map_admission']['admitted'] for r in value['motion']),
        numerical_arrivals=sum(r['result']['numerical_arrival_predicted'] for r in value['motion']),
        native_component_runs=len(value['native_component_runs']),frontier_tasks=len(value['frontier']),
        engineering_evidence_ready_for_independent_decision=value['engineering_evidence_ready_for_independent_decision'],
        engineering_complete=False,physical_design_complete=False,**FLAGS)


def verify(output,*,root=ROOT,require_complete=False,authenticator=None,artifact_verifier=None,
           authentication_context_id=None,verifier_context_id=None):
    target=Path(output);manifest=evidence.parse((target/'manifest.json').read_bytes())
    if (manifest.get('schema')!='osr-current-engineering-closure-package/1'
        or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
        or manifest.get('source_sha256')!=sources(root) or manifest.get('files_sha256')!=_files(target)
        or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError('Closure source, payload, identity or disposition differs')
    if manifest['authentication_context_id']!=authentication_context_id or manifest['verifier_context_id']!=verifier_context_id:
        raise ValueError('Current external trust/replay context differs; reassess rather than reuse approval')
    imported=evidence.parse((target/'input-manifest.json').read_bytes())
    native=sorted((target/'native').iterdir()) if (target/'native').is_dir() else []
    expected=assess(root,family=manifest['family'],distance_m=manifest['distance_m'],
        input_root=target/'inputs',input_manifest=imported,authenticator=authenticator,artifact_verifier=artifact_verifier,
        authentication_context_id=authentication_context_id,verifier_context_id=verifier_context_id,motor_packages=native)
    stored=evidence.parse(gzip.decompress((target/'report.json.gz').read_bytes()))
    # Native entries are input-set records; their order is not an engineering choice.
    def native_order(value):
        copy=deepcopy(value);copy['native_component_runs']=sorted(copy['native_component_runs'],key=lambda r:r['evaluation_id'])
        copy.pop('evaluation_id');return copy
    if native_order(expected)!=native_order(stored) or stored.get('evaluation_id')!=identity({k:v for k,v in stored.items() if k!='evaluation_id'}):
        raise ValueError('Closure semantic replay differs')
    if manifest['evaluation_id']!=stored['evaluation_id'] or manifest['candidate_id']!=stored['candidate_id']:
        raise ValueError('Mixed closure evaluation/candidate')
    if gzip.decompress((target/'input-sources.tar.gz').read_bytes())!=gzip.decompress(parent._input_archive(root,sources(root))):
        raise ValueError('Retained closure sources differ')
    expected_files={'manifest.json','input-manifest.json','report.json.gz','input-sources.tar.gz'}
    expected_files.update('inputs/'+name for name in _capture_inputs(target/'inputs',imported))
    native_allowed={'manifest.json','input.json','input-sources.tar.gz','preflight.json','stdout.log','stderr.log',
        'worker-result.json','partial-trace.jsonl','result.json'}
    for folder in native:
        if any(not p.is_file() or p.name not in native_allowed for p in folder.iterdir()):
            raise ValueError('Unexpected native closure input artifact')
        result=evidence.parse((folder/'result.json').read_bytes())
        if folder.name!=result['evaluation_id']:
            raise ValueError('Native closure directory differs from exact evaluation')
        expected_files.update('native/'+folder.name+'/'+p.name for p in folder.iterdir())
    if set(_files(target))|{'manifest.json'}!=expected_files:
        raise ValueError('Unexpected or missing closure artifact inventory')
    if require_complete and not expected['engineering_evidence_ready_for_independent_decision']:
        raise parent.IncompleteDesign(expected['frontier'])
    return dict(verified=True,**summary(stored))


def publish(package,*,root=ROOT,output=None,**verification_options):
    result=verify(package,root=root,**verification_options)
    folder=Path(package);target=Path(output) if output is not None else Path(root)/OUTPUT
    target.mkdir(parents=True,exist_ok=True)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w') as archive:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                raw=path.read_bytes();item=tarfile.TarInfo(path.relative_to(folder).as_posix())
                item.size=len(raw);item.mtime=0;item.mode=0o644;archive.addfile(item,io.BytesIO(raw))
    name=result['evaluation_id']+'.tar.gz'
    (target/name).write_bytes(gzip.compress(stream.getvalue(),mtime=0))
    manifest=dict(schema='osr-current-engineering-closure-publication/1',source_sha256=sources(root),
        archive=name,archive_sha256=digest(target/name),validation=result,**FLAGS)
    manifest['publication_id']=identity(manifest)
    (target/'manifest.json').write_bytes(encoded(manifest))
    return manifest


def verify_archive(path,*,root=ROOT,require_complete=False,**verification_options):
    with tempfile.TemporaryDirectory(prefix='osr-completion-verify-') as temporary:
        with tarfile.open(path,'r:gz') as archive:
            members=archive.getmembers();names=[m.name for m in members]
            if (len(members)>512 or len(names)!=len(set(names)) or sum(m.size for m in members)>256*1024**2
                    or any(not m.isfile() or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members)):
                raise ValueError('Ordinary bounded closure archive paths required')
            archive.extractall(temporary,filter='data')
        return verify(temporary,root=root,require_complete=require_complete,**verification_options)


def verify_publication(root=ROOT,output=None,**verification_options):
    target=Path(output) if output is not None else Path(root)/OUTPUT
    manifest=evidence.parse((target/'manifest.json').read_bytes())
    if (manifest.get('schema')!='osr-current-engineering-closure-publication/1'
        or manifest.get('publication_id')!=identity({k:v for k,v in manifest.items() if k!='publication_id'})
        or manifest.get('source_sha256')!=sources(root) or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError('Closure publication source, identity or disposition differs')
    name=manifest['archive']
    if name!=manifest['validation']['evaluation_id']+'.tar.gz' or Path(name).name!=name or digest(target/name)!=manifest['archive_sha256']:
        raise ValueError('Closure publication archive identity differs')
    if verify_archive(target/name,root=root,**verification_options)!=manifest['validation']:
        raise ValueError('Closure publication semantic replay differs')
    return dict(manifest['validation'],publication_id=manifest['publication_id'])
