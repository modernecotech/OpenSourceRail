"""Package current executed evidence; no engineering or physical release."""
from datetime import datetime,timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
import gzip,io,json,math,os,re,runpy,struct,subprocess,sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engineering.ferrite_maglev import model,delivery,cities

root=model.ROOT
out=root/'engineering/assurance/v052-integrated-design'

def read(path):return json.loads(Path(path).read_bytes())
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def compressed_bytes(value):
    with gzip.GzipFile(fileobj=io.BytesIO(value),mode='rb') as stream:raw=stream.read(128*1024*1024+1)
    assert len(raw)<=128*1024*1024
    return json.loads(raw)
def compressed(path):return compressed_bytes(Path(path).read_bytes())

def field_study_differences(public,private,path=''):
    """Only a finite nonnegative solver residual diagnostic may differ by 4 ULP."""
    assert type(public) is type(private),('private/public value type differs',path)
    differences=[]
    if isinstance(public,dict):
        assert public.keys()==private.keys(),('private/public object keys differ',path)
        for key in public:differences.extend(field_study_differences(public[key],private[key],path+'/'+key))
    elif isinstance(public,list):
        assert len(public)==len(private),('private/public list size differs',path)
        for index,(left,right) in enumerate(zip(public,private)):
            differences.extend(field_study_differences(left,right,path+'/'+str(index)))
    elif isinstance(public,float):
        assert math.isfinite(public) and math.isfinite(private),('nonfinite private/public value',path)
        if public.hex()!=private.hex():
            assert re.fullmatch(r'/mesh_refinement/[0-9]+/linear_residual',path),('nondiagnostic float differs',path)
            assert public>=0 and private>=0,('negative diagnostic residual',path)
            bits=lambda value:struct.unpack('>Q',struct.pack('>d',value))[0]
            distance=abs(bits(public)-bits(private))
            assert distance<=4,('diagnostic residual exceeds 4 ULP',path,distance)
            differences.append(dict(path=path,canonical=public,private=private,absolute_delta=abs(public-private),
                ulp_distance=distance,maximum_allowed_ulp=4))
    else:
        assert public==private,('private/public value differs',path)
    return differences
def flags(record):assert all(record.get(key) is False for key in model.FLAGS)
def stamp(value):return datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()

# This one verifier checks the primary payload and all retained native, numerical,
# controller, hub and catalogue receipts. Reuse those verified data below.
manifest=delivery.verify()
manifest_digest=digest(delivery.OUTPUT/'manifest.json')
report=read(delivery.OUTPUT/'result.json')
assert report['source_sha256']==manifest['source_sha256']
assert report['version']==manifest['version']==model.RELEASE_VERSION
flags(manifest);flags(report)
suite=read(root/'build/v052-final-suite.json')
log=(root/'build/v052-final-tests.log').read_bytes()
assert suite['schema']=='osr-executed-final-suite/1' and suite['command']==['./osr','test']
assert suite['exit_status']==0 and suite['source_unchanged'] is True
assert suite['source_sha256']==manifest['source_sha256'] and suite['log_sha256']==sha256(log).hexdigest()
assert suite['auxiliary_test_sources_unchanged'] is True
runner=runpy.run_path(str(root/'build/v052-final-driver.py'),run_name='audit_suite_driver')
assert suite['auxiliary_test_source_sha256']==runner['auxiliary_snapshot'](manifest['source_sha256'])
assert all(digest(root/name)==value for name,value in suite['auxiliary_test_source_sha256'].items())
assert suite['physical_release'] is False
text=log.decode()
rust=sum(map(int,re.findall(r'test result: ok\. (\d+) passed;',text)))
python=re.findall(r'(\d+) passed(?:, [^\n]*?)? in [0-9.]+s',text)
assert rust>0 and python and int(python[-1])>0
started,finished=stamp(suite['started_utc']),stamp(suite['finished_utc'])
assert started<=finished

private_dir=Path.home()/'.local/state/opensourcerail/ferrite-maglev/latest'
private_manifest_bytes=(private_dir/'manifest.json').read_bytes()
private=json.loads(private_manifest_bytes)
assert not private_dir.is_symlink() and not (private_dir/'manifest.json').is_symlink()
assert private.keys()==manifest.keys()
assert {key:value for key,value in private.items() if key!='files_sha256'}=={key:value for key,value in manifest.items() if key!='files_sha256'}
flags(private)
assert set(private['files_sha256'])==set(manifest['files_sha256'])
assert {path.name for path in private_dir.iterdir()}==set(manifest['files_sha256'])|{'manifest.json'}
assert all(not (private_dir/name).is_symlink() and (private_dir/name).is_file() and digest(private_dir/name)==value for name,value in private['files_sha256'].items())
assert all(private['files_sha256'][name]==value for name,value in manifest['files_sha256'].items() if name!='field-study.json.gz')
private_field_bytes=(private_dir/'field-study.json.gz').read_bytes()
assert sha256(private_field_bytes).hexdigest()==private['files_sha256']['field-study.json.gz']
private_diagnostics=field_study_differences(compressed(delivery.OUTPUT/'field-study.json.gz'),compressed_bytes(private_field_bytes))
private_byte_equal=private_manifest_bytes==(delivery.OUTPUT/'manifest.json').read_bytes() and private['files_sha256']==manifest['files_sha256']
private_comparison=dict(schema='osr-private-public-diagnostic-comparison/1',source_match=True,byte_equal=private_byte_equal,
    equivalence='byte-identical' if private_byte_equal else 'diagnostic-roundoff-only',
    canonical_manifest_sha256=manifest_digest,private_manifest_sha256=sha256(private_manifest_bytes).hexdigest(),
    publication_schema=manifest['schema'],version=manifest['version'],family=manifest['family'],
    exact_metadata_and_source_map=True,exact_inventory=sorted(manifest['files_sha256']),own_payload_checksums_valid=True,
    all_other_payloads_byte_equal=True,field_study_diagnostic_differences=private_diagnostics,
    tolerance_scope='Only finite nonnegative /mesh_refinement/<index>/linear_residual diagnostics; at most 4 representable float steps. Every other decoded value is exact; no engineering guard or acceptance tolerance changes.',
    **model.FLAGS)
service=subprocess.check_output(['systemctl','--user','show','osr-primary-infrastructure.service','-p','Result','-p','ExecMainStatus','-p','ExecMainExitTimestamp','-p','ActiveState'],text=True)
service_fields=dict(line.split('=',1) for line in service.splitlines() if '=' in line)
assert service_fields['Result']=='success' and service_fields['ExecMainStatus']=='0'
timer=subprocess.check_output(['systemctl','--user','show','osr-primary-infrastructure.timer','-p','ActiveState','-p','TimersMonotonic','-p','NextElapseUSecMonotonic','-p','Unit'],text=True)
assert 'ActiveState=active' in timer and 'Unit=osr-primary-infrastructure.service' in timer
assert re.search(r'OnUnitActiveUSec=15min(?:\s|;|})',timer)

payload={
    'private-public-comparison.json':encoded(private_comparison),
    'private-publication-manifest.json':private_manifest_bytes,
    'private-field-study.json.gz':private_field_bytes,
}
def attach(source,target):
    path=Path(source);payload[target]=path.read_bytes();return sha256(payload[target]).hexdigest()

def fresh_test_artifact(path):
    # Browser scripts have no embedded timestamp; require this suite to have
    # actually refreshed their receipt and screenshots, then bind current bytes.
    value=Path(path).stat().st_mtime
    assert started-1<=value<=finished+1,(str(path),value,started,finished)

browser_root=root/'build/maglev-test-browser'
workbench_root=root/'build/maglev-test-workbench-browser'
browser=read(browser_root/'browser-check.json');workbench=read(workbench_root/'checks.json')
assert browser['version']==model.RELEASE_VERSION and browser['accepted_item_count']==0
assert browser['javascript_errors']==browser['external_requests']==browser['failed_requests']==[]
assert browser['mobile_overflow'] is False and browser['acceptance_gates_open']==len(report['gates'])
assert all(gate['state']=='open' and gate['accepted'] is False for gate in report['gates'])
assert workbench['primary_ui'] is True and workbench['links'] is True and workbench['mobile'] is True
assert workbench['errors']==workbench['external']==[] and workbench['physical_release'] is False

class PageMedia(HTMLParser):
    def __init__(self,*,allow_workbench_placeholders=False):
        super().__init__();self.images=[];self.videos=[];self.dynamic_images=[];self.image_count=0
        self.allow_workbench_placeholders=allow_workbench_placeholders
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='img':
            self.image_count+=1
            if 'src' in attrs:
                assert attrs['src'],('empty image src',attrs.get('id'))
                self.images.append(attrs['src'])
            else:
                assert self.allow_workbench_placeholders,('primary image lacks src',attrs.get('id'))
                assert attrs.get('id') in {'city-map','hub-map'} and 'hidden' in attrs,('unrecognised or visible image placeholder',attrs)
                assert attrs['id'] not in {image['id'] for image in self.dynamic_images},('duplicate image placeholder',attrs['id'])
                self.dynamic_images.append(dict(id=attrs['id'],hidden_in_source=True,static_src=None,
                    evidence='workbench-browser.json',verification='Source-bound executed browser checks validate runtime source assignment and loaded image dimensions'))
        if tag in {'a','source','video'}:
            value=attrs.get('href') or attrs.get('src')
            if value and urlsplit(value).path.endswith('.mp4'):self.videos.append(value)

def local_asset(value,base):
    parsed=urlsplit(value)
    assert not parsed.scheme and not parsed.netloc
    name=unquote(parsed.path)
    path=(root/name.lstrip('/') if name.startswith('/') else Path(base)/name).resolve()
    assert path.is_relative_to(root) and path.is_file() and not path.is_symlink()
    return path

html=PageMedia();html.feed((delivery.OUTPUT/'index.html').read_text())
assert sorted(html.images)==sorted(image['src'] for image in browser['images'])
assert all(image['loaded'] is True for image in browser['images'])
video_paths={local_asset(value,delivery.OUTPUT) for value in html.videos}
assert video_paths=={local_asset(video['href'],root) for video in browser['videos']}
assert all(video['status']==200 and video['bytes']==local_asset(video['href'],root).stat().st_size for video in browser['videos'])
assert browser['links'] and all(link['status']==200 for link in browser['links'])
ui=PageMedia(allow_workbench_placeholders=True);ui.feed((root/'docs/workbench/maglev/index.html').read_text())
assert {image['id'] for image in ui.dynamic_images}=={'city-map','hub-map'} and len(ui.dynamic_images)==2
assert workbench['images']==ui.image_count==len(ui.images)+len(ui.dynamic_images)==10
workbench_static={value:local_asset(value,root/'docs/workbench/maglev') for value in ui.images}
media={}
for path in {local_asset(value,delivery.OUTPUT) for value in html.images}|video_paths|set(workbench_static.values()):
    media[path.relative_to(root).as_posix()]=dict(sha256=digest(path),bytes=path.stat().st_size)
for folder,label,prefix,receipt in [(browser_root,'report','primary-study','browser-check.json'),(workbench_root,'workbench','workbench','checks.json')]:
    fresh_test_artifact(folder/receipt);attach(folder/receipt,label+'-browser.json')
    for variant in ('desktop','mobile'):
        name=(prefix+'-'+variant+'.png') if label=='report' else variant+'.png'
        path=folder/name;fresh_test_artifact(path)
        assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') and path.stat().st_size>1000
        attach(path,label+'-'+variant+'.png')

catalogue=read(cities.INDEX)
assert len(catalogue['cities'])==browser['city_count']==workbench['cities']==report['city_catalogue']['city_count']
portability=read(root/'build/v052-final-portability.json')
assert portability['git_source_and_packet_identity'] is True and portability['checked_files']>0 and portability['physical_release'] is False
journal=read(root/'build/maglev-workflow/latest.json')
assert journal['schema']=='osr-maglev-workflow/1' and journal['state'] in {'idle; sources unchanged','implemented studies current; engineering closure open'}
assert journal.get('finished_utc') and journal['stages'] and all(stage['state'] in {'verified-existing','rebuilt-and-verified'} for stage in journal['stages'])
flags(journal)
# Retain the rejected first run without mixing its counts or old source map
# with the accepted final suite. Its original receipt is copied unchanged.
initial_suite_path=root/'build/v052-initial-suite.json'
initial_log=(root/'build/v052-initial-tests.log').read_bytes()
initial_suite=read(initial_suite_path)
assert initial_suite['schema']=='osr-executed-final-suite/1' and initial_suite['command']==['./osr','test']
assert initial_suite['exit_status']!=0 and initial_suite['physical_release'] is False
assert initial_suite['source_unchanged'] is True and initial_suite['auxiliary_test_sources_unchanged'] is True
assert initial_suite['log_sha256']==sha256(initial_log).hexdigest()
assert stamp(initial_suite['started_utc'])<=stamp(initial_suite['finished_utc'])<=started
initial_failures=re.findall(r'^FAILED (\S+)',initial_log.decode(),flags=re.MULTILINE)
initial_reasons={
    'engineering/analysis/tests/test_ferrite_maglev_architecture_audit.py::test_current_tree_contains_only_current_vehicle_sources':
        'Owned corridor gzip evidence exceeded the former 64 MiB audit limit; correction applies the owned packet size bounds while retaining bounded streaming.',
    'engineering/analysis/tests/test_ferrite_maglev_cities.py::test_real_city_package_preserves_demand_and_binds_sources':
        'A strict equality assertion differed by one floating-point ULP in the city cost subtotal; correction uses an appropriately bounded numerical comparison.',
    'engineering/analysis/tests/test_ferrite_maglev_evacuation.py::test_unapproved_deletion_never_enters_reference_champion_selection':
        'The expected optimisation grid size remained 432 after the deliberate depth alternatives expanded it to 720; correction updates the independent expected grid.',
}
assert set(initial_failures)==set(initial_reasons) and len(initial_failures)==len(initial_reasons)
payload['initial-failed-executed-tests.txt.gz']=gzip.compress(initial_log,mtime=0)
attach(initial_suite_path,'initial-failed-source-receipt.json')
initial_notes=(
    'REJECTED INITIAL RUN — historical evidence only; not an accepted test result.\n'
    'The original log and source receipt are retained unchanged in content. Their old source identities are historical and are not claimed to match the corrected tree.\n'
    'Only executed-tests.txt.gz and test-source-receipt.json establish the final suite counts and acceptance. No initial-run count contributes to those fields.\n\n'
    +'\n'.join(name+'\n  '+reason for name,reason in initial_reasons.items())
    +'\n\nSeparate workflow correction: refresh the public overview before generating the Markdown inventory and reader book; an isolated first-pass heading regression covers the ordering.\n'
    'This correction history does not imply engineering, manufacturing, operating or physical acceptance.\n')
payload['initial-failed-run-notes.txt']=initial_notes.encode()
initial_history=dict(state='rejected initial history',excluded_from_final_pass_counts=True,
    exit_status=initial_suite['exit_status'],source_identity_scope='Historical source snapshot; not current corrected sources',
    log='initial-failed-executed-tests.txt.gz',receipt='initial-failed-source-receipt.json',notes='initial-failed-run-notes.txt',
    failures=[dict(test=name,reason=reason) for name,reason in initial_reasons.items()])
payload['executed-tests.txt.gz']=gzip.compress(log,mtime=0)
for source,target in [('build/v052-final-suite.json','test-source-receipt.json'),('build/v052-final-portability.json','git-source-portability.json'),
                      ('build/v052-final-baghdad-four-circuits.json.gz','baghdad-four-circuits.json.gz'),('build/maglev-workflow/latest.json','refresh-run.json')]:
    attach(root/source,target)
baghdad_path=root/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json'
baghdad=read(baghdad_path);replay=compressed(root/'build/v052-final-baghdad-four-circuits.json.gz')
assert replay['source_current'] is True and replay['normal_window_passed'] is True
assert all(digest(root/name)==value for name,value in replay['source_sha256'].items())
receipt=replay['assurance_receipt']
assert receipt['input_source_sha256']==replay['source_sha256'] and receipt['input_source_current_before_and_after'] is True
assert root/receipt['input_summary_path']==baghdad_path and digest(baghdad_path)==receipt['input_summary_sha256']
assert replay['compiled_plan_sha256']==sha256(json.dumps(baghdad,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
assert receipt['cycles']==4 and receipt['charger_efficiency']==.9 and receipt['missed_charge_events']==[]
assert replay['regeneration_available'] is False and all(line['cycles']==4 and abs(line['energy_ledger_residual_kwh'])<1e-7 for line in replay['lines'])
assert replay['emergency_reserve_passed'] is None and replay['protected_emergency_energy_kwh'] is None
assert replay['route_acceptance'] is False and replay['force_acceptance'] is False
flags(replay)
assert digest(root/receipt['generator_path'])==receipt['generator_sha256']

audit_sources={}
for source,target in [(root/receipt['generator_path'],'replay-generator.py'),(root/'build/v052-final-driver.py','suite-driver.py'),(Path(__file__),'assurance-generator.py')]:
    audit_sources[target]=dict(original_execution_path=source.resolve().relative_to(root).as_posix(),sha256=attach(source,target))
assert audit_sources['replay-generator.py']['sha256']==receipt['generator_sha256']
assert audit_sources['suite-driver.py']['sha256']==suite['auxiliary_test_source_sha256']['build/v052-final-driver.py']

base=root/'docs/design-engine/ferrite-maglev'
moving=compressed(base/'moving-train/result.json.gz');longer=compressed(base/'corridor/result.json.gz');dossier=compressed(base/'manufactured-dossier/dossier.json.gz')
# The one publication verification above already checked these packet receipts.
assert report['corridor_powered']['manifest_sha256']==digest(base/'corridor/manifest.json')
assert report['retained_evidence'][(base/'corridor/manifest.json').relative_to(root).as_posix()]==digest(base/'corridor/manifest.json')
hubs=compressed(base/'interchange-hubs/study.json.gz')
focused=next(value for value in hubs['variants'] if value['id']=='pair-031-040/line-9/midpoint')
hub_summary=dict(schema=hubs['schema'],baseline_stops=hubs['baseline']['operating_station_count'],unique_pairs=hubs['unique_pair_count'],
    shared_line_adjacencies=hubs['shared_line_adjacency_count'],placement_variants=len(hubs['variants']),network_alternatives=len(hubs['network_alternatives']),
    compact_hubs_proved=hubs['true_compact_candidate_count'],focused_investigation=dict(id=focused['id'],maximum_reference_access_arm_m=focused['maximum_reference_access_arm_m'],
        unique_reference_connector_m=focused['independently_counted_unique_connector_length_m'],price_scope_allowance_usd_per_reference_m=focused['operating_and_cost_comparison']['priced_scope_connector_allowance_usd_per_reference_m']),
    selected_variant=None,**model.FLAGS)
negative=moving['excessive_sensor_bias_negative_control']
assert moving['numerical_controls']['physical_gap_bias_counterexample_rejected'] is True and negative['completed_moving_steps']>0
assert negative['failure']=='independent physical gap outside envelope'

payload['media-proof.json']=encoded(dict(schema='osr-final-browser-media-evidence/1',publication_manifest_sha256=manifest_digest,
    report_image_count=len(html.images),report_video_count=len(video_paths),workbench_image_count=ui.image_count,
    workbench_static_images=[dict(src=src,path=path.relative_to(root).as_posix(),sha256=digest(path)) for src,path in workbench_static.items()],
    workbench_dynamic_image_placeholders=ui.dynamic_images,
    browser_receipt_sha256={name:sha256(payload[name]).hexdigest() for name in ('report-browser.json','workbench-browser.json')},
    files=media,source_generators={name:digest(root/name) for name in ('tools/automation/tests/verify-maglev-v05.mjs','tools/automation/tests/verify-maglev-workbench.mjs')},
    source_bound_to_executed_suite=True,**model.FLAGS))
payload['background-refresh.json']=encoded(dict(schema='osr-final-background-refresh-evidence/1',service_show=service,timer_show=timer,
    cadence_minutes=15,timer_active=True,last_exit_status=0,private_and_public_payloads_byte_equal=private_byte_equal,
    source_match=True,private_public_equivalence=private_comparison['equivalence'],private_public_comparison='private-public-comparison.json',publication_manifest_sha256=manifest_digest,
    scope='Source-change refresh of implemented digital studies; no autonomous physical acceptance',**model.FLAGS))
summary=dict(schema='osr-v052-integrated-development-verification/2',version=model.RELEASE_VERSION,verified_utc=datetime.now(timezone.utc).isoformat(),
    scope='Executed provisional fixed-line station/booster designs, source-bound native stock and moving/control simulations. Ideal force channels, assumed inertia/material/ground and supplier targets remain unqualified. No operating or manufacturing release.',
    rust_tests_passed=rust,python_tests_passed=int(python[-1]),full_suite_exit_status=0,
    initial_failed_run_history=initial_history,
    source_document_sha256=digest(root/'OpenSourceRail_Station_Powered_Maglev_Design_Specification.docx'),
    applicable_open_requirements=len(report['applicable_requirements']['requirements']),source_specification_requirements=len(report['source_specification']['requirements']),
    city_packages=len(catalogue['cities']),operating_strategy=report['operating_strategy'],baghdad_totals=baghdad['totals'],
    baghdad_lines=[dict(line=line['line'],selected_headway_seconds=line['selected_peak_headway_seconds'],retained_capacity_target_met=line['retained_capacity_target_met'],
        kinematic_holds=line['kinematic_holds'],operating_station_count=line['operating_plan']['operating_station_count'],spacing_conflicts=line['operating_plan']['spacing_conflicts'],
        boosters=line['operating_plan']['powered_top_up_zones']) for line in baghdad['lines']],
    repeated_services_replay=dict(source_current=True,normal_window_passed=True,protected_emergency_energy_accepted=False),
    moving_benchmark=dict(selected_candidate_sha256=moving['candidate_sha256'],numerical_controls=moving['numerical_controls'],evidence_role='retained-1000m-component-benchmark'),
    moving_physical_guard_negative=dict(completed_moving_steps=negative['completed_moving_steps'],minimum_physical_gap_m=negative['minimum_gap_m'],
        minimum_biased_sensed_gap_m=negative['minimum_gap_m']+negative['sensor_bias_m'],reason=negative['failure']),
    longer_corridors=report['corridor_powered'],interchange_hub_investigation=hub_summary,
    moving_confirmations={key:dict(candidate_sha256=value['run']['candidate_sha256'],profile_sha256=value['profile_sha256'],completed_moving_steps=value['run']['completed_moving_steps'],
        planned_moving_steps=value['run']['planned_moving_steps'],minimum_gap_m=value['run']['minimum_gap_m'],maximum_gap_m=value['run']['maximum_gap_m'],study_pass=value['run']['study_pass']) for key,value in longer['moving'].items()},
    manufactured_dossier=dict(requirements=dossier['closure']['requirement_count'],systems=dossier['closure']['system_count'],frame_reserve_allocation=dossier['primary_frame_families']['reserve_allocation'],complete_manufactured_system=False),
    retained_packet_manifest_sha256=report['retained_evidence'],publication_manifest_sha256=manifest_digest,audit_source_attachments=audit_sources,
    background_refresh=dict(cadence_minutes=15,timer_active=True,last_exit_status=0,private_and_public_payloads_byte_equal=private_byte_equal,
        source_match=True,private_public_equivalence=private_comparison['equivalence'],comparison='private-public-comparison.json',mode='Rebuild stale implemented studies; no autonomous physical acceptance'),
    accepted_engineering_items=0,physical_output_authorised=False,**model.FLAGS)
payload['summary.json']=encoded(summary)
payload['audit-notes.txt']=b'The first failed suite is retained separately as rejected history; its results never contribute to final pass counts. Copied wrappers are retained for audit. Original execution paths remain in their receipts. The suite invokes tracked ./osr test; the replay invokes tracked cities.replay_city with the retained parameters. Private/public comparison permits only source-matched solver residual diagnostics within 4 ULP and records actual differences; this is not a payload byte-equality claim. Native/moving media and numerical results do not constitute manufacturing, operation, physical validation or engineering acceptance. No Markdown file is added by this packaging step.\n'
assert model.sources()==manifest['source_sha256'] and digest(delivery.OUTPUT/'manifest.json')==manifest_digest
assert digest(private_dir/'manifest.json')==private_comparison['private_manifest_sha256']
assert all(digest(private_dir/name)==value for name,value in private['files_sha256'].items())
assert all(digest(root/name)==value for name,value in suite['auxiliary_test_source_sha256'].items())
checks={name:sha256(value).hexdigest() for name,value in sorted(payload.items())}
payload['checksums.json']=encoded(checks)
out.parent.mkdir(parents=True,exist_ok=True)
if out.exists():assert not out.is_symlink() and {path.name for path in out.iterdir()}<=set(payload)
with tempfile.TemporaryDirectory(prefix='.v052-assurance-',dir=out.parent) as temporary:
    stage=Path(temporary)
    for name,value in payload.items():(stage/name).write_bytes(value)
    out.mkdir(parents=True,exist_ok=True)
    for name in [*sorted(set(payload)-{'checksums.json'}),'checksums.json']:os.replace(stage/name,out/name)
print(json.dumps(dict(version=summary['version'],rust_tests_passed=rust,python_tests_passed=int(python[-1]),files=len(checks),physical_release=False),indent=2))
