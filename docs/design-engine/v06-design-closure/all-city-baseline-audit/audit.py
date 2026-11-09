#!/usr/bin/env python3
"""Read committed city evidence and seal a private audit; never evaluate/reprice models."""
import argparse, ast, collections, datetime, gzip, hashlib, json, os, pathlib, subprocess, sys, tomllib


def encoded(v):
    return (json.dumps(v, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def digest(v):
    return hashlib.sha256(v).hexdigest()


def identity(v):
    return digest(encoded(v))


parser=argparse.ArgumentParser()
parser.add_argument('--repo', required=True)
parser.add_argument('--output', required=True)
a=parser.parse_args()
repo=pathlib.Path(a.repo).resolve(); out=pathlib.Path(a.output).resolve()
if out.exists(): raise SystemExit('Refusing to overwrite an audit packet')
if repo in out.parents: raise SystemExit('Audit output must be outside the source checkout')


def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


head=git('rev-parse','HEAD').decode().strip()
old=git('rev-parse','v0.4.0^{commit}').decode().strip()
release=git('rev-parse','codex/v061-release-20261108^{commit}').decode().strip()
source_index={}
proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)


def read(ref,path,role):
    key=ref+':'+path
    proc.stdin.write((key+'\n').encode()); proc.stdin.flush()
    header=proc.stdout.readline().decode().rstrip('\n').split()
    if len(header)!=3 or header[1]!='blob': raise RuntimeError('Not a Git blob: '+key)
    n=int(header[2]); raw=proc.stdout.read(n)
    if len(raw)!=n or proc.stdout.read(1)!=b'\n': raise RuntimeError('Truncated Git stream: '+key)
    record=source_index.setdefault(key,dict(commit=ref,path=path,git_blob_id=header[0],bytes=n,sha256=digest(raw),roles=[]))
    if role not in record['roles']: record['roles'].append(role)
    return raw


def obj(path,role='current-document',ref=head):
    return json.loads(read(ref,path,role))


def sealed(v,key):
    return v.get(key)==identity({k:x for k,x in v.items() if k!=key})


def tree(ref,prefix):
    raw=git('ls-tree','-r','-z',ref,'--',prefix)
    rows=[]
    for item in raw.split(b'\0'):
        if not item: continue
        meta,path=item.split(b'\t',1); mode,kind,oid=meta.decode().split()
        rows.append(dict(path=path.decode(),git_blob_id=oid,mode=mode,type=kind))
    return rows


errors=[]
index=obj('docs/design-engine/city-dossiers/index.json')
expected_scopes=None
model=read(head,'engineering/design_search/model_cost.py','cost-scope-definition')
for node in ast.parse(model).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCOPES' for t in node.targets): expected_scopes=set(ast.literal_eval(node.value))
if expected_scopes is None: raise RuntimeError('SCOPES definition unavailable')
current_top={}
for path in ('docs/design-engine/city-dossiers/manifest.json','docs/design-engine/city-atlas/manifest.json','docs/design-engine/city-atlas/summary.json','docs/design-engine/outline-completion/manifest.json','docs/design-engine/outline-completion/summary.json'):
    d=obj(path,'current-top-level-packet'); current_top[path]=dict(sha256=source_index[head+':'+path]['sha256'],identities={k:v for k,v in d.items() if k.endswith('_id') and isinstance(v,str)})
    for p,h in d.get('source_sha256',{}).items():
        if digest(read(head,p,'declared-producer-source'))!=h: errors.append([path,'producer-mismatch',p])
    if path.endswith('/summary.json'): current_top[path]['counts']={k:v for k,v in d.items() if k in ('requested','completed','pending','every_requested_city_priced','every_requested_city_compiled','outline_accepted_cities')}
counts=collections.Counter(); types=collections.Counter(); hist=collections.defaultdict(collections.Counter); linefields=collections.Counter(); workforce=collections.Counter(); manifests=[]; cities=[]
flags=('physical_accepted','engineering_accepted','manufacturing_release','operating_release','physical_journey_completed','timetable_qualified','independent_braking_qualified','movement_authority','procurement_approved')
for row in index['cities']:
    slug=row['city']['slug']; base=row['path']+'/engineering/outline'; mp=base+'/manifest.json'
    mr=read(head,mp,'city-manifest'); m=json.loads(mr)
    manifests.append((slug,digest(mr))); counts['manifests']+=1
    if not sealed(m,'manifest_id'): errors.append([slug,'manifest-identity'])
    if m['city_slug']!=slug: errors.append([slug,'manifest-city'])
    payload={}
    for name,h in m['files_sha256'].items():
        p=pathlib.PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts: raise RuntimeError('Unsafe manifest path')
        raw=read(head,base+'/'+name,'declared-city-payload')
        counts['payload_files']+=1; counts['payload_bytes']+=len(raw); types[name]+=1
        if digest(raw)!=h: errors.append([slug,'payload-hash',name])
        if name in ('summary.json','stations.csv'): payload[name]=raw
    for p,h in m['source_sha256'].items():
        if digest(read(head,p,'declared-producer-source'))!=h: errors.append([slug,'producer-hash',p])
    if digest(read(head,m['city_frontdoor_path'],'current-city-frontdoor'))!=m['city_frontdoor_sha256']: errors.append([slug,'frontdoor-hash'])
    ar=read(head,m['atlas_file'],'city-atlas-packet')
    if digest(ar)!=m['atlas_sha256']: errors.append([slug,'atlas-hash'])
    atlas=json.loads(gzip.decompress(ar))
    if not sealed(atlas,'packet_id') or atlas['packet_id']!=m['atlas_packet_id']: errors.append([slug,'atlas-identity'])
    rr=read(head,m['outline_file'],'city-outline-packet')
    if digest(rr)!=m['outline_sha256']: errors.append([slug,'outline-hash'])
    detail=json.loads(gzip.decompress(rr)); s=json.loads(payload['summary.json'])
    if not sealed(s,'analysis_id'): errors.append([slug,'analysis-identity'])
    if s['source_ids']['atlas_packet_id']!=m['atlas_packet_id'] or s['source_ids']['outline_evaluation_id']!=m['outline_evaluation_id']: errors.append([slug,'summary-bindings'])
    if atlas['identity']['reference_candidate_ids']!=s['source_ids']['reference_candidate_ids'] or detail['reference_candidate_ids']!=s['source_ids']['reference_candidate_ids']: errors.append([slug,'candidate-bindings'])
    scopes=set(s['costs']['capital_by_scope_usd'])
    if scopes!=expected_scopes: errors.append([slug,'cost-scope-set'])
    else: counts['14_scope_cities']+=1
    counts['city_maps']+=int('network.svg' in m['files_sha256'])
    counts['lines']+=len(s['lines']); counts['station_table_rows']+=len(payload['stations.csv'].decode().splitlines())-1
    counts['finance_enabled']+=int(s['finance']['enabled']); counts['debt_modelled']+=int(s['finance']['financing']['debt_modelled']); counts['access_enabled']+=int(s['access']['enabled'])
    counts['resource_only']+=int(s['delivery']['resource_envelope_only']); counts['schedule_executable']+=int(s['delivery']['executable_schedule']); counts['calendar_dates']+=int(s['delivery']['calendar_dates_assigned'])
    counts['total_grid_null']+=int(s['energy']['physical_total_grid_kwh_per_year'] is None)
    counts['priced_energy_cases']+=int(set(s['energy']['priced_supply_scenarios']['cases'])=={'low','base','high'})
    for f in flags: counts[f+'_true']+=int(s[f] is True)
    for key,value in [('local_rate_status',s['costs']['local_cost_inputs']['status']),('execution',s['evidence']['execution']),('evidence_maturity',s['evidence']['evidence_maturity']),('surveyed_demand',s['evidence']['surveyed_demand_available']),('selected_alignment_kind',s['source_ids']['selected_alignment_kind'])]: hist[key][str(value)]+=1
    ids=s['source_ids']['reference_candidate_ids']
    hist['reference_candidate_id'][ids['candidate_id']]+=1; hist['body_candidate_id'][ids['body_candidate_id']]+=1
    for line in s['lines']:
        for f in ('headway_s','active_trainsets','spare_trainsets','annual_train_km','mechanical_traction_kwh_per_year','auxiliary_load_kwh_per_year','peak_demand_pphpd','service_evaluation_id'): linefields[f]+=int(f in line)
        for f in ('headway_s','peak_demand_pphpd','normal_places_per_train','propulsion_kind','operating_days_per_year','operating_hours_per_day'): hist['line_'+f][str(line[f])]+=1
        counts['line_electrical_traction_null']+=int(line['electrical_traction_kwh_per_year'] is None)
        counts['line_available_force_true']+=int(line['actual_available_force_map_available'] is True)
        counts['line_braking_qualified_true']+=int(line['independent_braking_qualified'] is True)
    for wr in s['workforce']: workforce[wr['domain']]+=1
    cities.append(dict(slug=slug,path=row['path'],manifest_sha256=digest(mr),manifest_id=m['manifest_id'],summary_sha256=digest(payload['summary.json']),analysis_id=s['analysis_id'],lines=len(s['lines']),station_table_rows=len(payload['stations.csv'].decode().splitlines())-1,source_ids=s['source_ids'],local_rates=s['costs']['local_cost_inputs'],resource_envelope_only=s['delivery']['resource_envelope_only'],physical_grid_total_known=s['energy']['physical_total_grid_kwh_per_year'] is not None))
    if counts['manifests']%50==0: print('Audited committed cities:',counts['manifests'],flush=True)
oldtree=tree(old,'cities/catalogue'); oldreads=[r for r in oldtree if len(pathlib.PurePosixPath(r['path']).parts)==6 and r['path'].endswith('/README.md')]
oldcoverage=collections.Counter(); old_frontdoors=[]
for r in oldreads:
    raw=read(old,r['path'],'v04-city-frontdoor-field-check'); text=raw.decode()
    fields={f:needle in text for f,needle in {'network_map':'network-map.png','line_by_line_operations':'### Lines','energy':'## Energy','capital_and_funding':'## Capital And Funding','local_evidence':'## Local Evidence','regeneration':'## Local Files And Regeneration'}.items()}
    for f,present in fields.items(): oldcoverage[f]+=int(present)
    old_frontdoors.append(dict(path=r['path'],git_blob_id=r['git_blob_id'],sha256=digest(raw),fields=fields))
old_artifact_suffixes={'finance':'/engineering/finance/summary.json','GIS':'/engineering/gis/summary.json','simulation_validation':'/engineering/simulation/validation-summary.json','SUMO':'/engineering/sumo/summary.json','energy':'/engineering/energy/summary.json','operations_manifest':'-operations-manifest.json','digital_twin_readme':'/engineering/digital-twin/README.md'}
old_artifacts={kind:[r for r in oldtree if r['path'].endswith(suffix)] for kind,suffix in old_artifact_suffixes.items()}
feature_sources=[('docs/city-studio.md',old),('docs/design-engine/city-atlas/README.md',head),('docs/design-engine/city-dossiers/README.md',head),('engineering/development_baseline/planning.py',head),('engineering/outline/planning_geometry.py',head),('engineering/outline/city_cost_inputs.py',head),('engineering/outline/city-cost-inputs.toml',head),('engineering/city_reports/analysis.py',head),('docs/workbench/planning/planning.js',head),('docs/workbench/planning/README.md',head),('campaigns/v06-design-integration-closure.toml',head),('docs/design-engine/v06-design-closure/README.md',head),('docs/releases/v0.6.1.md',release),('engineering/software_release/bundle.py',release)]
for p,r in feature_sources: read(r,p,'feature-or-release-gate-source')
gate_paths=('campaigns/v06-design-integration-closure.toml','docs/design-engine/v06-design-closure/README.md')
working={p:(repo/p).read_bytes() for p in gate_paths}; gate=tomllib.loads(working[gate_paths[0]].decode())
oldgate=tomllib.loads(read(head,gate_paths[0],'committed-six-gate-program').decode())
consumer_cmd=['git','-C',str(repo),'grep','-l','v06-design-integration-closure\\|release_unpublished_until_required_work_closed',head,'--','*.py','*.toml','*.yml','*.md']
consumer=subprocess.run(consumer_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
proc.stdin.close(); proc.wait()
features=[
 {'feature':'City inventory and front doors','v04':'266 city READMEs and six checked front-door fields in every README','current':'266 cities and 21 artifact types per city; maps, 1565 lines and 13580 station-table rows','gap':'Not a detailed closure-candidate rebase; Wau path still uses Waw heading/slug.'},
 {'feature':'Operations and service','v04':'Per-line day/time operating controls and period capacity screens described in City Studio; operations manifests exist for 266 cities','current':'All lines expose headway, fleet, train-km, demand and energy; every line uses 4000 pphpd and 200 s with 276 places','gap':'Shared study controls; no qualified timetable, day-type timetable or surveyed OD assignment.'},
 {'feature':'Maps and alignment editability','v04':'Map layers, stop/line creation and retirement, locked anchors and editable alignment control points described','current':'266 SVG maps, GIS archives and interactive atlas; controlled stop/service/OD edits; backend replace-line-geometry supports explicit alignment coordinates and speed cap','gap':'Full former manual line/control-point and weekly calendar UI is not demonstrated as restored; no native round-trip completion asserted.'},
 {'feature':'Energy','v04':'Energy summaries exist in all 266 city trees','current':'266 nominal mechanical/auxiliary budgets and priced low/base/high supply cases','gap':'Physical grid totals and all 1565 line electrical-traction totals remain null; no available-force or independent-braking qualification.'},
 {'feature':'Manufacturing, civil and workforce','v04':'Shared deployment planning basis and business/digital-twin application features; explicit city digital-twin README only in Samawah','current':'266 delivery requirements, make/buy, procurement/resource quantities and workforce cases; 14 cost scopes','gap':'All 266 are resource envelopes; none is an executable or calendar-dated candidate-controlled production/construction schedule.'},
 {'feature':'Capital and funding','v04':'Capital/funding front-door section and finance summary in every city','current':'266 low/base/high scope costs and illustrative debt overlays','gap':'Transferred reference operating rates for all cities; no site/local price confirmation, dated draw schedule or financing approval.'},
 {'feature':'Revision/review and engineering playback','v04':'Immutable project revisions, semantic diffs, append-only reviews, engineering jobs, IFC/BCF and 4D playback described','current':'Source identities and immutable handoffs retained; current planning edits/repricing and downloads are exposed','gap':'Full former day-type/period-OD/review/IFC-4D/simulation playback equivalents require explicit current capability decisions; do not infer them from catalogue completeness.'}
]
review=dict(disposition='Consistent with the audit: the added required gate closes the scope omission in the committed six-gate programme.',working_required_work_ids=[w['id'] for w in gate['work'] if w.get('required')],committed_required_work_ids=[w['id'] for w in oldgate['work'] if w.get('required')],strengths=['Explicit complete 266-city scope and line-level service/energy/funding retention','Replaces universal service controls with sourced or bounded local scenarios','Requires exact candidate propagation through fleet, energy, civil and fourteen scopes','Permits calculated procurement/manufacturing comparisons without treating assumptions as quotes','Keeps demand, site, supplier, price and approval evidence distinct'],recommended_acceptance_mechanics=['Bind the sorted expected city registry and require a per-city source/candidate/evaluation/status record; include the Wau/Waw normalization explicitly.','Retain failed and held cities visibly. Gate completion concerns a coherent declared study or specific infeasibility, not a requirement that every architecture or city be feasible.','Have release verification consume the gate status and verify registry completeness and edit-to-reprice evidence; the audited committed programme has no code/workflow consumer found.','Interpret retained v0.4 front-door fields as current capability/content coverage; do not reuse historical numeric results or physical-pass labels.','Record applicability for square-loop or consolidation alternatives; comparison does not force a particular alignment or permit accessibility/safety trade-offs.'],not_evaluated=['No review of the actual new city calculations: none were run.','No native GIS or browser execution.','No physical, engineering, financial or supplier validation.'])
summary=dict(schema='osr-readonly-city-coverage-audit/1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),repository=str(repo),commit=head,old_tag_commit=old,planned_release_commit=release,read_only_scope='Git blobs, tree metadata and two working gate snapshots only; no source edits, numerical solves, cost recalculation or city regeneration.',isolation='Read-only instruction followed by audit code; no OS read-only sandbox or WORM storage is claimed.',counts=dict(counts),artifact_type_coverage=dict(types),line_field_coverage=dict(linefields),workforce_rows_by_domain=dict(workforce),histograms={k:dict(v) for k,v in hist.items()},errors=errors,ordered_manifest_set_digest=identity(sorted(manifests)),ordered_manifest_set_digest_recipe='SHA256 of UTF-8 json.dumps(sorted([(slug,SHA256(manifest_bytes)), ...]), sort_keys=True, separators=(comma,colon), allow_nan=False) plus newline; same canonical encoding as station_rail.common.identity.',top_level_packets=current_top,v04_frontdoor_count=len(oldreads),v04_field_coverage=dict(oldcoverage),v04_tree_artifact_counts={k:len(v) for k,v in old_artifacts.items()},v04_tree_coverage_semantics='Summary and operations artifact coverage uses committed tree existence/object IDs only; historical result correctness was not re-evaluated.',feature_comparison=features,gate_review=review,committed_gate_consumer_search=dict(command=consumer_cmd,returncode=consumer.returncode,stdout=consumer.stdout.decode(),stderr=consumer.stderr.decode()),working_gate_sources={p:dict(sha256=digest(raw),bytes=len(raw),git_head_blob=next(x['git_blob_id'] for x in source_index.values() if x['commit']==head and x['path']==p)) for p,raw in working.items()},bounded_next_action='Define a canonical detailed-candidate city adapter, then re-evaluate the existing five-line Samawah outline with declared candidate/route/service/local-rate assumptions and all fourteen scopes. Preserve its old record and failures. Only after validating that bounded path, apply the same adapter to the checkpointed 266-city registry. No ID-only substitution or pilot cost/km scaling.')
out.mkdir(parents=True,mode=0o700)
(out/'audit-summary.json').write_bytes(encoded(summary)); (out/'per-city-records.json').write_bytes(encoded(cities)); (out/'ordered-city-manifest-set.json').write_bytes(encoded(sorted(manifests)))
(out/'git-source-index.json').write_bytes(encoded(sorted(source_index.values(),key=lambda x:(x['commit'],x['path'])))); (out/'v04-frontdoor-fields.json').write_bytes(encoded(old_frontdoors)); (out/'v04-artifact-tree-coverage.json').write_bytes(encoded(old_artifacts))
(out/'audit.py').write_bytes(pathlib.Path(__file__).read_bytes())
for p,raw in working.items():
    dest=out/'reviewed-working-gate'/p; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(raw)
readme=f'''# All-city coverage audit\n\nCommitted evidence: `{head}`. Historical field comparison: `v0.4.0` (`{old}`). Planned release source: `{release}`.\n\n266 city manifests, {counts['lines']} lines, {counts['station_table_rows']} station-table rows and {counts['payload_files']} declared payload files ({counts['payload_bytes']} bytes) were checked. Identity/hash errors: {len(errors)}. Ordered manifest-set digest: `{summary['ordered_manifest_set_digest']}`.\n\nEvery line uses the declared 4,000 pphpd / 200-second study control and 276 places/train. All cities use transferred-reference operating rates and the earlier outline body. All cities have maps, fourteen cost scopes, energy cases, illustrative finance and resource/workforce records; none has a qualified timetable or executable construction schedule.\n\nThe reviewed working gate adds the necessary 266-city propagation scope; see audit-summary.json for its precise snapshot hashes, strengths and acceptance-mechanics recommendations. The committed programme contains only the original six gates.\n\nReproduce into a **new private output directory**:\n\n```sh\npython3 {out}/audit.py --repo {repo} --output /path/to/new/private/audit-packet\n```\n\nThe script reads committed blobs through `git cat-file --batch`, tree coverage through `git ls-tree -r -z`, refs through `git rev-parse`, and the two named working gate files. `git-source-index.json` lists the exact commit/path, Git blob ID, content SHA256 and role for every blob actually read. Historical summary-tree rows establish existence only. It imports no project model and performs no engineering or price calculations.\n\nAll packet files are sealed by manifest hashes and made read-only as an operational convention, not an OS-enforced immutable or authenticated physical-evidence store.\n'''
(out/'README.md').write_text(readme)
files={p.relative_to(out).as_posix():dict(sha256=digest(p.read_bytes()),bytes=p.stat().st_size) for p in sorted(out.rglob('*')) if p.is_file()}
seal=dict(schema='osr-private-readonly-audit-packet/1',source_commit=head,ordered_manifest_set_digest=summary['ordered_manifest_set_digest'],files=files,physical_acceptance=False,financial_validation=False)
seal['packet_id']=identity(seal)
(out/'manifest.json').write_bytes(encoded(seal))
for p in out.rglob('*'):
    if p.is_file(): p.chmod(0o444)
for p in sorted((x for x in out.rglob('*') if x.is_dir()),reverse=True): p.chmod(0o555)
out.chmod(0o555)
print(json.dumps(dict(packet_path=str(out),packet_id=seal['packet_id'],manifest_sha256=digest((out/'manifest.json').read_bytes()),summary_sha256=digest((out/'audit-summary.json').read_bytes()),source_index_sha256=digest((out/'git-source-index.json').read_bytes()),ordered_manifest_set_digest=summary['ordered_manifest_set_digest'],counts=dict(counts),errors=errors,working_gate_sha256={p:digest(b) for p,b in working.items()}),sort_keys=True),flush=True)
