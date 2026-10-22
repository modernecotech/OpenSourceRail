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
out=root/'engineering/assurance/v052-closure-development'

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
suite=read(root/'build/closure-final-suite.json')
log=(root/'build/closure-final-tests.log').read_bytes()
assert suite['schema']=='osr-executed-final-suite/1' and suite['command']==['./osr','test']
assert suite['exit_status']==0 and suite['source_unchanged'] is True
assert suite['source_sha256']==manifest['source_sha256'] and suite['log_sha256']==sha256(log).hexdigest()
assert suite['auxiliary_test_sources_unchanged'] is True
runner=runpy.run_path(str(root/'build/closure-final-driver.py'),run_name='audit_suite_driver')
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
portability=read(root/'build/closure-final-portability.json')
assert portability['git_source_and_packet_identity'] is True and portability['checked_files']>0 and portability['physical_release'] is False
journal=read(root/'build/closure-final-completed-refresh.json')
assert journal['schema']=='osr-maglev-workflow/1' and journal['state'] in {'idle; sources unchanged','implemented studies current; engineering closure open'}
assert stamp(journal['finished_utc'])>=finished
assert journal.get('finished_utc') and journal['stages'] and all(stage['state'] in {'verified-existing','rebuilt-and-verified'} for stage in journal['stages'])
flags(journal)
payload['executed-tests.txt.gz']=gzip.compress(log,mtime=0)
for source,target in [('build/closure-final-suite.json','test-source-receipt.json'),('build/closure-final-portability.json','git-source-portability.json'),
                      ('build/closure-final-baghdad-four-circuits.json.gz','baghdad-four-circuits.json.gz'),('build/closure-final-completed-refresh.json','refresh-run.json')]:
    attach(root/source,target)
baghdad_path=root/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/maglev/summary.json'
baghdad=read(baghdad_path);replay=compressed(root/'build/closure-final-baghdad-four-circuits.json.gz')
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
for source,target in [(root/receipt['generator_path'],'replay-generator.py'),(root/'build/closure-final-driver.py','suite-driver.py'),(Path(__file__),'assurance-generator.py')]:
    audit_sources[target]=dict(original_execution_path=source.resolve().relative_to(root).as_posix(),sha256=attach(source,target))
assert audit_sources['replay-generator.py']['sha256']==receipt['generator_sha256']
assert audit_sources['suite-driver.py']['sha256']==suite['auxiliary_test_source_sha256']['build/closure-final-driver.py']

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
summary=dict(schema='osr-v052-closure-development-verification/1',version=model.RELEASE_VERSION,verified_utc=datetime.now(timezone.utc).isoformat(),
    scope='Executed provisional fixed-line station/booster designs, source-bound native stock and moving/control simulations. Ideal force channels, assumed inertia/material/ground and supplier targets remain unqualified. No operating or manufacturing release.',
    rust_tests_passed=rust,python_tests_passed=int(python[-1]),full_suite_exit_status=0,
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
summary['closure_studies']=report['closure_studies']
summary['all_points_closed']=False
summary['remaining_acceptance_scope']='Complete equipped-body and joined/flexible-body design, detailed curved transitions/stations/terminal return geometry, route-wide restart/handover, complete cost and real ground/utility/site records remain open alongside qualified material/force/loss maps, physical hardware/timing/egress/recovery tests and authenticated independent dispositions. Prepared procedures and local offline studies are not acceptance.'
for folder in ('line-capacity','hub-access','qualification','assembled-body','shared-hub-layout','body-stiffness'):
    attach(base/folder/'manifest.json',folder+'-manifest.json')

# Separate fresh rigid-car sensitivity: the partial CAD mass is never treated
# as full AW3 mass and a lower lumped stiffness does not prove flexible bodies.
from engineering.ferrite_maglev import assembled_body,moving_train,body_stiffness
axial_root=root/'build/body-axial-sensitivity'
axial=read(axial_root/'summary.json');axial_receipt=read(axial_root/'receipt.json')
assert axial['schema']=='osr-rigid-car-body-axial-sensitivity/1'
assert axial_receipt['schema']=='osr-body-axial-sensitivity-receipt/1'
assert axial['source_sha256']==axial_receipt['source_sha256']
expected_axial_sources={**moving_train.sources(),**assembled_body.sources(),**body_stiffness.sources(),
    'build/body-axial-sensitivity/run.py':digest(axial_root/'run.py')}
assert axial['source_sha256']==expected_axial_sources
assert all(digest(root/name)==value for name,value in axial['source_sha256'].items())
assert axial['source_unchanged_after_execution'] is True and axial['retained_candidate_exact_current'] is True
assert axial['axial_screen']==assembled_body.axial_screen()
assert axial['full_aw3_car_mass_kg']==26200.0 and axial['full_train_mass_kg']==157200.0
assert axial['only_changed_assumption']=='coupler_stiffness_n_m'
assert axial['accepted_body_or_plant'] is False and axial['city_default_changed'] is False
flags(axial);flags(axial_receipt)
assert digest(root/axial['retained_result_file'])==axial['retained_result_sha256']
assert axial['retained_publication_verified'] is True
assert axial['retained_selected_candidate_sha256']==moving['moving_run']['candidate_sha256']
expected_axial_files={'run.py','summary.json','reference-100MN.json.gz','gross-series.json.gz','drilled-series.json.gz'}
assert set(axial_receipt['files_sha256'])==expected_axial_files and len(axial['runs'])==3
for name,value in axial_receipt['files_sha256'].items():
    assert digest(axial_root/name)==value
    attach(axial_root/name,'body-axial-'+name)
attach(axial_root/'receipt.json','body-axial-receipt.json')
payload['body-axial-reproduction.txt']=(
    'The retained body-axial-run.py is the exact driver originally executed as build/body-axial-sensitivity/run.py. '
    'The receipt keeps that original path and its SHA256; the audit copy has the same bytes. '
    'From the matching repository revision, create build/body-axial-sensitivity and copy this driver to '
    'build/body-axial-sensitivity/run.py, then run the exact command in body-axial-receipt.json. '
    'Native/compiled tools and the repository environment are required. The three JSON.gz files retain complete '
    'result traces. These are rigid-car full-AW3 sensitivity runs, not flexible-body or physical acceptance.\n').encode()
reference_assumptions=moving['moving_run']['assumptions']
expected_stiffness=[reference_assumptions['coupler_stiffness_n_m'],axial['axial_screen']['body_and_coupler_series_stiffness_n_m'],axial['axial_screen']['drilled_body_and_coupler_series_stiffness_n_m']]
actual_axial=[]
for run,stiffness in zip(axial['runs'],expected_stiffness):
    assert run['file'] in expected_axial_files and digest(axial_root/run['file'])==run['sha256']
    actual=compressed(axial_root/run['file']);candidate=dict(reference_assumptions,coupler_stiffness_n_m=stiffness)
    assert run['assumptions']==actual['assumptions']==candidate
    assert actual['feedback_enabled'] is True
    assert actual['sensor_bias_m']==candidate['sensor_bias_m']
    assert actual['configuration_revision']==candidate['configuration_revision']
    # This sensitivity changes only the longitudinal coefficient. Its complete
    # prescribed trajectory, guideway and integration window remain identical
    # to the independently verified current full-mass moving baseline.
    for key in ('trajectory','guideway','window','formation'):
        assert actual[key]==moving['moving_run'][key]
    assert actual['planned_moving_steps']==round(candidate['runtime_s']/candidate['step_s'])
    assert actual['completed_moving_steps']==actual['planned_moving_steps']
    assert actual['executed_duration_s']==candidate['runtime_s']
    assert actual['failure'] is None and actual['stop_seen'] is False
    assert run['candidate_sha256']==actual['candidate_sha256']==sha256(moving_train.encoded(candidate)).hexdigest()
    assert len(actual['trace'])==run['retained_trace_rows']>0
    assert run['confirmation_eligible']==moving_train.confirmation_eligible(actual)
    assert run['metrics']=={k:v for k,v in actual.items() if k not in body_stiffness.METRIC_EXCLUDE}
    flags(actual)
    assert actual['physical_output_authorised'] is False and actual['structural_acceptance'] is False
    body_stiffness.validate_trace_and_energy(actual,candidate)
    actual_axial.append(actual)
comparison_keys=('minimum_gap_m','maximum_gap_m','peak_coupler_force_n','peak_coupler_extension_m',
    'maximum_magnetic_phase_spread_degrees','maximum_longitudinal_relative_spread_m',
    'peak_module_force_n','peak_beam_displacement_m','completed_moving_steps','planned_moving_steps')
actual_comparisons=[]
for run,actual in zip(axial['runs'],actual_axial):
    assert all(type(actual[k]) in (int,float) and math.isfinite(actual[k]) for k in comparison_keys)
    actual_comparisons.append(dict(name=run['file'],stiffness_n_m=actual['assumptions']['coupler_stiffness_n_m'],
        metrics={k:actual[k] for k in comparison_keys},
        delta_from_fresh_reference={k:actual[k]-actual_axial[0][k] for k in comparison_keys},
        original_nominal_screen_pass=actual['study_pass'],confirmation_screen_pass=moving_train.confirmation_eligible(actual)))
actual_reference_delta={k:actual_axial[0][k]-moving['moving_run'][k] for k in comparison_keys}
assert axial['comparisons']==actual_comparisons
assert axial['fresh_reference_difference_from_retained']==actual_reference_delta
summary['body_axial_sensitivity']=dict(scope=axial['scope'],comparisons=actual_comparisons,
    fresh_reference_difference_from_retained=actual_reference_delta,
    full_aw3_car_mass_kg=axial['full_aw3_car_mass_kg'],full_train_mass_kg=axial['full_train_mass_kg'],
    source_current=True,source_unchanged_after_execution=True,receipt='body-axial-receipt.json',
    accepted_body_or_plant=False,city_default_changed=False,**model.FLAGS)

witness_controls=read(root/'build/body-stiffness-final-controls.json')
assert witness_controls['schema']=='osr-final-body-witness-controls/1'
assert witness_controls['source_sha256']==expected_axial_sources
assert witness_controls['sources_current_before_and_after'] is True
assert witness_controls['legacy_receipt_sha256']==digest(axial_root/'receipt.json')
assert witness_controls['physical_acceptance'] is False
assert witness_controls['audit_driver_path']=='build/body-stiffness-final-controls.py'
assert digest(root/witness_controls['audit_driver_path'])==witness_controls['audit_driver_sha256']
assert {(r['file'],r['control']) for r in witness_controls['controls']}=={
    (name,control) for name in ('reference-100MN.json.gz','gross-series.json.gz','drilled-series.json.gz')
    for control in ('zero-energy','zero-force','truncated-trace','mutated-witness')}
assert len(witness_controls['controls'])==12
assert all(r['rejected'] is True and r['reason'] for r in witness_controls['controls'])
for observed,run,actual in zip(witness_controls['legacy_runs'],axial['runs'],actual_axial):
    assert observed==dict(file=run['file'],candidate_sha256=actual['candidate_sha256'],
        frames=actual['completed_moving_steps'],trace_rows=len(actual['trace']),
        phase_degrees=actual['maximum_magnetic_phase_spread_degrees'])
assert len(witness_controls['legacy_runs'])==3
attach(root/'build/body-stiffness-final-controls.json','body-witness-controls.json')
attach(root/witness_controls['audit_driver_path'],'body-witness-controls-driver.py')
attach(root/'build/body-stiffness-final-controls.log','body-witness-controls.txt')
summary['body_witness_controls']=dict(controls=12,all_rejected=True,
    source_current=True,receipt='body-witness-controls.json',physical_acceptance=False)

negative_root=root/'build/line-capacity-final-negatives-receipt.json'
negative_receipt=read(negative_root)
assert negative_receipt['schema']=='osr-line-capacity-final-negative-receipt/1'
assert negative_receipt['canonical_manifest_sha256']==digest(base/'line-capacity/manifest.json')
assert all(digest(root/name)==value for name,value in negative_receipt['source_sha256'].items())
assert negative_receipt['physical_acceptance'] is False
assert {row['case'] for row in negative_receipt['controls']}=={'rehashed-readme','rehashed-scope','rehashed-open-gates'}
assert all(row['rejected'] is True and row['reason'] for row in negative_receipt['controls'])
assert negative_receipt['execution_log']=='build/line-capacity-final-negatives.log'
assert digest(root/negative_receipt['execution_log'])==negative_receipt['execution_log_sha256']
attach(negative_root,'capacity-presentation-negatives.json')
attach(root/'build/line-capacity-final-negatives.log','capacity-presentation-negatives.txt')
from engineering.ferrite_maglev import release_bundle
bundle=root/'build/closure-multipart-bundle'
bundle_manifest_bytes=(bundle/'RELEASE-MANIFEST.json').read_bytes()
bundle_digest=sha256(bundle_manifest_bytes).hexdigest()
bundle_record=json.loads(bundle_manifest_bytes)
bundle_checks=release_bundle.verify(bundle,expected_manifest_sha256=bundle_digest)
assert bundle_record['source_sha256']==suite['source_sha256']
assert bundle_record['commit']==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
tree={}
for entry in subprocess.check_output(['git','ls-tree','-rz','--full-tree','HEAD']).split(b'\0'):
    if entry:
        metadata,name=entry.split(b'\t',1)
        mode,kind,oid=metadata.split()
        if kind==b'blob' and mode in (b'100644',b'100755'):tree[name.decode()]=oid.decode()
assert all(tree.get(name)==value['git_blob_sha1'] for name,value in bundle_record['members'].items())
# The self-derived digest guards this read, not an independent signature.
# Every actual archive payload was checked against the trusted current Git tree.

assert bundle_checks['trusted_manifest_matched'] is True and bundle_checks['physical_release'] is False
payload['multipart-bundle-manifest.json.gz']=gzip.compress(bundle_manifest_bytes,mtime=0)
attach(bundle/'SHA256SUMS','multipart-bundle-SHA256SUMS.txt')
summary['multipart_bundle']=dict(**bundle_checks,commit=bundle_record['commit'],manifest_sha256=bundle_digest,
    current_git_tree_bound=True,signature_verified=False,manifest_anchor_scope='Local digest plus independent current HEAD tree comparison for every member; no external signature claimed',
    uncompressed_payload_bytes=bundle_record['uncompressed_payload_bytes'],
    shard_payload_limit_bytes=bundle_record['shard_payload_limit_bytes'],
    archive_files={name:dict(bytes=(bundle/name).stat().st_size,sha256=digest(bundle/name)) for name in bundle_record['shards']},
    artifact_location='Local ignored build/closure-multipart-bundle; checksum/manifest receipts retained here. Numbered archives are not duplicated in Git and no new GitHub release is announced.')
payload['summary.json']=encoded(summary)
payload['audit-notes.txt']=b'The previous development assurance remains historical; only this current full suite contributes to these pass counts. Copied wrappers are retained for audit. Original execution paths remain in their receipts. The suite invokes tracked ./osr test; the replay invokes tracked cities.replay_city with the retained parameters. Private/public comparison permits only source-matched solver residual diagnostics within 4 ULP and records actual differences; this is not a payload byte-equality claim. Native/moving media and numerical results do not constitute manufacturing, operation, physical validation or engineering acceptance. No Markdown file is added by this packaging step.\n'
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
