"""Actual Rust ATP regressions and candidate-bound wheel/station predicates.

Readiness inputs and ATP decisions remain explicit fixtures; no physical motion
or brake plant is represented. Replay verifies every typed output predicate.
"""
from pathlib import Path
import json
import subprocess
from . import ROOT,FLAGS
from .common import encoded,identity,digest,source_map

IDS=('selection_id','candidate_id','body_candidate_id','support_component_id','propulsion_component_id')
CRATES=('osr-core','osr-atp','osr-interlocking','osr-tcms','osr-door-control','osr-station-scada')
SCOPE='Actual inherited Rust regressions and configuration-bound wheel/station interface predicates; supplied readiness and ATP decisions are fixtures. No braking plant or motion authority.'
FIXTURE_SCOPE='wheel/station interface predicate fixture; brake plant and motion not simulated'


def sources(root):
    root=Path(root);names=['Cargo.toml','Cargo.lock','engineering/station_rail/controls.py']
    for crate in CRATES:
        names += [p.relative_to(root).as_posix() for p in (root/'crates'/crate).rglob('*')
                  if p.is_file() and p.suffix in ('.rs','.toml')]
    return source_map(root,names)


def requests(record):
    base=dict(selected_configuration=list(bytes.fromhex(record['candidate_id'])),
        observed_configuration=list(bytes.fromhex(record['candidate_id'])),
        authority_valid=True,localisation_known=True,train_integrity_known=True,
        communications_fresh=True,doors_locked=True,brake_channels_healthy=True,
        essential_supply_ready=True,departure_drive_ready=True,station_drive_required=True,
        receiving_drive_ready=True,receiving_berth_reserved=True,
        independent_brake_profile_valid=True,stopped=True,
        parking_brake_proved=True,wheel_slide_active=False)
    rows=[('nominal_predicates',{},'Release','Release',True)]
    for key in ('authority_valid','localisation_known','train_integrity_known',
        'communications_fresh','doors_locked','brake_channels_healthy',
        'essential_supply_ready','receiving_drive_ready','receiving_berth_reserved',
        'independent_brake_profile_valid'):
        rows.append((key+'_lost',{key:False,'stopped':False},'Release','Emergency',False))
    rows += [
        ('configuration_mismatch',dict(observed_configuration=[0]*32),'Release','Emergency',False),
        ('ATP_emergency',{},'Emergency','Emergency',False),
        ('ATP_service',{},dict(Service=500),dict(Service=500),False),
        ('wheel_slide',dict(wheel_slide_active=True),'Release',dict(Service=1000),False),
        ('no_departure_power',dict(departure_drive_ready=False),'Release','Emergency',False),
        ('launch_power_lost',dict(departure_drive_ready=False,stopped=False,parking_brake_proved=False),
            'Release','Emergency',False),
        ('coasting_without_departure_power',dict(departure_drive_ready=False,station_drive_required=False,
            stopped=False,parking_brake_proved=False),'Release','Release',False),
        ('coasting_ATP_emergency',dict(departure_drive_ready=False,station_drive_required=False,
            stopped=False,parking_brake_proved=False),'Emergency','Emergency',False),
        ('no_parking_proof',dict(parking_brake_proved=False),'Release','Release',False),
    ]
    return [dict(case=name,request=dict(inputs=dict(base,**change),atp=atp),
        expected_brake=brake,expected_launch=launch) for name,change,atp,brake,launch in rows]


def expected_response(row):
    """Complete oracle for these bounded contract cases, not a brake-plant model."""
    i=row['request']['inputs'];brake=row['expected_brake'];launch=row['expected_launch']
    independent=(i['selected_configuration']==i['observed_configuration'] and all(i[k]
        for k in ('authority_valid','localisation_known','train_integrity_known',
            'communications_fresh','doors_locked','brake_channels_healthy',
            'essential_supply_ready','independent_brake_profile_valid')))
    receiver=i['receiving_drive_ready'] and i['receiving_berth_reserved']
    inhibit=(not independent or not receiver or not i['departure_drive_ready'] or
        not i['station_drive_required'] or (i['stopped'] and not launch) or brake!='Release')
    return dict(outcome=dict(launch_permissive=launch,mechanical_brake=brake,
        station_thrust_inhibit=inhibit,support_power_required=False,
        recovery_required_if_off_zone=i['stopped']),
        physical_output_authorised=False,scope=FIXTURE_SCOPE)


def regression_command():
    return ['cargo','test','--locked',*sum((['-p',c] for c in CRATES[1:]),[])]


def result_definition(record):
    rows=[dict(case=row['case'],passed=True,returncode=0) for row in requests(record)]
    return dict(schema='osr-v06-native-wheel-controls/1',
        **{k:record[k] for k in IDS},evaluation_id=record['evaluation_id'],
        controls=len(rows),all_controls_pass=True,rows=rows,
        regression_command=regression_command(),scope=SCOPE,
        physical_train_simulated=False,development_default=True,**FLAGS)


def check_response(actual,row):
    # Canonical bytes retain JSON boolean/number type differences (Python's
    # ordinary equality otherwise treats True==1 and False==0 as equal).
    if encoded(actual)!=encoded(expected_response(row)):
        raise ValueError('Native complete wheel disposition differs: '+row['case'])


def run(output,record,root=ROOT):
    root=Path(root);output=Path(output)
    if output.exists():raise ValueError('Preserve native execution; use a fresh output directory')
    output.mkdir(parents=True);before=sources(root)
    test=subprocess.run(regression_command(),cwd=root,capture_output=True,timeout=300)
    (output/'regressions.stdout').write_bytes(test.stdout)
    (output/'regressions.stderr').write_bytes(test.stderr)
    if test.returncode:raise RuntimeError('Rust regressions failed; logs retained')
    build=subprocess.run(['cargo','build','--locked','-p','osr-atp','--example','wheel_station_contract'],
        cwd=root,capture_output=True,timeout=240)
    (output/'build.stdout').write_bytes(build.stdout);(output/'build.stderr').write_bytes(build.stderr)
    if build.returncode:raise RuntimeError('Wheel interface compilation failed; logs retained')
    for row in requests(record):
        raw=encoded(row['request']);(output/(row['case']+'.request.json')).write_bytes(raw)
        executed=subprocess.run([str(root/'target/debug/examples/wheel_station_contract')],
            input=raw,capture_output=True,cwd=root,timeout=15)
        (output/(row['case']+'.stdout.json')).write_bytes(executed.stdout)
        (output/(row['case']+'.stderr')).write_bytes(executed.stderr)
        if executed.returncode:raise RuntimeError('Wheel fixture failed: '+row['case'])
        check_response(json.loads(executed.stdout),row)
    if sources(root)!=before:raise ValueError('Native source changed during execution')
    result=result_definition(record)
    (output/'result.json').write_bytes(encoded(result))
    receipt=dict(source_sha256=before,
        files_sha256={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file()},**FLAGS)
    receipt['manifest_id']=identity(receipt)
    (output/'manifest.json').write_bytes(encoded(receipt));return result


def verify(output,record,root=ROOT):
    output=Path(output)
    m=json.loads((output/'manifest.json').read_bytes())
    r=json.loads((output/'result.json').read_bytes())
    if m['manifest_id']!=identity({k:v for k,v in m.items() if k!='manifest_id'}):
        raise ValueError('Native receipt identity differs')
    if sources(root)!=m['source_sha256']:raise ValueError('Native wheel control source differs')
    files={p.name:digest(p) for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}
    if files!=m['files_sha256']:raise ValueError('Native wheel control payload differs')
    if any(r.get(k) is not v or m.get(k) is not v for k,v in FLAGS.items()):
        raise ValueError('Native fixtures cannot grant release')
    if encoded(r)!=encoded(result_definition(record)):
        raise ValueError('Native wheel result, identities, dispositions or case inventory differ')
    expected_files={'regressions.stdout','regressions.stderr','build.stdout','build.stderr','result.json'}
    for row in requests(record):
        expected_files.update(row['case']+suffix for suffix in ('.request.json','.stdout.json','.stderr'))
        if (output/(row['case']+'.request.json')).read_bytes()!=encoded(row['request']):
            raise ValueError('Native request differs')
        check_response(json.loads((output/(row['case']+'.stdout.json')).read_bytes()),row)
    if set(files)!=expected_files:raise ValueError('Native case/log file inventory differs')
    return r
