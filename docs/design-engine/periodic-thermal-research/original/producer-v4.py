"""Bounded repeated-duty sensitivity from a retained synthetic P1 trace.

This is a train-aggregate scalar hypothesis, not a fixed-bank LIM model.  It
does not qualify forces, cooling, station occupation, the 900 m reference
winding or any physical railway.  Every external input has a caller-supplied
identity and the original 50-source epoch must be present unchanged.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import sys

REFERENCE = '756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
BUNDLE = '566f4f0e491e9968ca2beda0671d04a590c83329b27b95d86145d7ede4de6758'
MANIFEST = 'docs/design-engine/conditional-journey-study/manifest.json'
ARTIFACT = 'docs/design-engine/conditional-journey-study/candidates/' + BUNDLE + '.json.gz'
PRODUCER = 'engineering/design_search/periodic_thermal_research.py'
FLAGS = dict(physical_accepted=False, engineering_accepted=False,
    configuration_adopted=False, selected_reference_changed=False,
    manufacturing_release=False, operating_release=False,
    physical_journey_completed=False, available_motor_map_id=None)
REQUEST_KEYS = frozenset(('schema','reference_candidate_id','bundle_id','record_id',
    'output_evaluation_id','study_manifest_id','study_id','candidate_artifact_sha256',
    'source_epoch_id','headway_s','maximum_step_s'))
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_EXPANDED_BYTES = 16 * 1024 * 1024
MAX_SOURCE_BYTES = 128 * 1024 * 1024
MAX_SOURCE_FILES = 256
MAX_TRACE_STEPS = 12000
MAX_EVENT_PARTS = 100000
ABS_LOSS_BUDGET_J = .001
REL_LOSS_BUDGET = 1e-10


def _encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def _id(value):
    return hashlib.sha256(_encoded(value)).hexdigest()


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _hex(value):
    if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Externally pinned SHA-256 required')
    return value


def _number(value, label):
    if type(value) not in (float,int) or not math.isfinite(value):
        raise ValueError(label+' must be finite numeric')
    return float(value)


def _json(raw):
    def pairs(items):
        out={}
        for key,value in items:
            if key in out:raise ValueError('Duplicate JSON key')
            out[key]=value
        return out
    try:
        value=json.loads(raw,object_pairs_hook=pairs,
            parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON')))
    except (ValueError,UnicodeDecodeError) as error:
        raise ValueError('Invalid bounded JSON') from error
    if not isinstance(value,dict):raise ValueError('JSON object required')
    return value


def _relative(name):
    if not isinstance(name,str) or not name or '\\' in name:
        raise ValueError('Ordinary relative source path required')
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or str(path)!=name:
        raise ValueError('Ordinary relative source path required')
    return path


def _read(root,name,limit=MAX_FILE_BYTES):
    path=Path(root)/_relative(name)
    if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file():
        raise ValueError('Ordinary unlinked input required: '+name)
    if path.stat().st_size>limit:raise ValueError('Input byte budget exceeded: '+name)
    raw=path.read_bytes()
    if len(raw)>limit:raise ValueError('Input byte budget exceeded: '+name)
    return raw


def _request(request,expected_request_id):
    _hex(expected_request_id)
    if not isinstance(request,dict) or set(request)!=REQUEST_KEYS or _id(request)!=expected_request_id:
        raise ValueError('Externally pinned request identity differs')
    if request['schema']!='osr-periodic-thermal-request/1' or request['bundle_id']!=BUNDLE or request['reference_candidate_id']!=REFERENCE:
        raise ValueError('Exact selected-vehicle research bundle required')
    for key in ('record_id','output_evaluation_id','study_manifest_id','study_id','candidate_artifact_sha256','source_epoch_id'):
        _hex(request[key])
    period=_number(request['headway_s'],'headway');step=_number(request['maximum_step_s'],'maximum step')
    if not 1<=period<=600 or not .001<=step<=1 or period/step>600000:
        raise ValueError('Bounded positive headway and thermal step required')
    return period,step


def _identity(record,key,expected=None):
    if not isinstance(record,dict) or record.get(key)!=_id({k:v for k,v in record.items() if k!=key}):
        raise ValueError('Input identity differs: '+key)
    if expected is not None and record[key]!=expected:
        raise ValueError('Externally pinned identity differs: '+key)


def _inputs(root,request):
    manifest_raw=_read(root,MANIFEST);manifest=_json(manifest_raw)
    _identity(manifest,'manifest_id',request['study_manifest_id'])
    if manifest.get('schema')!='osr-conditional-journey-publication/2' or manifest.get('study_id')!=request['study_id']:
        raise ValueError('Retained conditional study identity differs')
    source=manifest.get('source_sha256')
    if not isinstance(source,dict) or not source or len(source)>MAX_SOURCE_FILES or _id(source)!=request['source_epoch_id']:
        raise ValueError('Externally pinned source epoch differs')
    total=0
    for name,wanted in sorted(source.items()):
        _hex(wanted);raw=_read(root,name);total+=len(raw)
        if total>MAX_SOURCE_BYTES or _sha(raw)!=wanted:raise ValueError('Original producer source differs: '+name)
    raw=_read(root,ARTIFACT)
    if (_sha(raw)!=request['candidate_artifact_sha256']
            or manifest.get('files_sha256',{}).get('candidates/'+BUNDLE+'.json.gz')!=_sha(raw)):
        raise ValueError('Externally pinned candidate payload differs')
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:expanded=f.read(MAX_EXPANDED_BYTES+1)
    except (OSError,EOFError) as error:raise ValueError('Invalid compressed candidate') from error
    if len(expanded)>MAX_EXPANDED_BYTES:raise ValueError('Expanded candidate byte budget exceeded')
    record=_json(expanded);_identity(record,'record_id',request['record_id'])
    output=record.get('output');_identity(output,'evaluation_id',request['output_evaluation_id'])
    if (record.get('bundle_id')!=BUNDLE or output.get('candidate_id')!=BUNDLE
            or output.get('bundle_id')!=BUNDLE or output.get('reference_candidate_id')!=REFERENCE
            or output.get('powered_windows_m')!=[[0.,500.]]
            or any(output.get(k) is not False for k in ('physical_accepted','engineering_accepted',
                'engineering_validated','approved_for_manufacture_or_operation','configuration_adopted',
                'manufacturing_release','operating_release','physical_journey_completed'))):
        raise ValueError('Selected research bundle, 500 m window or nonpromotion disposition differs')
    cases=output.get('cases')
    if not isinstance(cases,list) or [x.get('case') for x in cases]!=['low','base','high']:
        raise ValueError('Exact low/base/high retained case order required')
    for case in cases:
        _identity(case.get('scenario'),'scenario_id')
        _identity(case.get('force_map'),'evaluation_id',case.get('map_id'))
        _identity(case.get('forward'),'method_result_id')
        if (case.get('test_only') is not True or case.get('available_motor_map_id') is not None
                or case.get('physical_journey_completed') is not False
                or case['force_map'].get('evidence_kind')!='synthetic-method-test'
                or case['scenario'].get('powered_windows')!=[[0.,500.]]
                or case['force_map'].get('candidate_id')!=BUNDLE
                or case['forward'].get('test_only') is not True
                or any(case['forward'].get(k) is not False for k in ('physical_accepted','engineering_accepted',
                    'configuration_adopted','manufacturing_release','operating_release','physical_journey_completed'))):
            raise ValueError('Synthetic, non-promoting same-bundle case required')
    return record,manifest


def recover(trace,thermal,recorded_loss_J):
    """Recover force/power losses and cross-check forward-Euler temperatures."""
    if not isinstance(trace,list) or not trace or len(trace)>MAX_TRACE_STEPS:
        raise ValueError('Bounded nonempty original trace required')
    C=_number(thermal.get('capacity_J_K'),'capacity');H=_number(thermal.get('heat_rejection_W_K'),'conductance')
    ambient=_number(thermal.get('ambient_C'),'ambient');T=_number(thermal.get('initial_C'),'initial temperature')
    if C<=0 or H<0:raise ValueError('Positive capacity and nonnegative conductance required')
    t=0.;velocity=0.;intervals=[];signed=[];thermal_signed=[];clipped=[];bounds=[];differences=[];min_dt=math.inf
    for row in trace:
        end=_number(row.get('time_s'),'time');new=_number(row.get('temperature_C'),'temperature');dt=end-t
        if dt<=0:raise ValueError('Strictly increasing trace times required')
        min_dt=min(min_dt,dt)
        new_velocity=_number(row.get('speed_m_s'),'speed')
        electric=_number(row.get('electrical_input_W_train'),'electrical power')
        thrust=_number(row.get('thrust_N_train'),'thrust')
        if new_velocity<0:raise ValueError('Nonnegative velocity required')
        mechanical=thrust*(velocity+new_velocity)/2
        power_energy=(electric-mechanical)*dt
        rejected=H*(T-ambient)*dt
        temperature_energy=C*(new-T)+rejected
        thermal_bound=16*sys.float_info.epsilon*(C*(abs(T)+abs(new)+1)+abs(rejected)+1)
        power_bound=16*sys.float_info.epsilon*((abs(electric)+abs(mechanical))*dt+1)
        if power_energy < -power_bound:raise ValueError('Significant negative reconstructed loss')
        correction=max(0.,-power_energy)
        signed.append(power_energy);thermal_signed.append(temperature_energy);clipped.append(correction)
        bounds.append(thermal_bound+power_bound);differences.append(abs(power_energy-temperature_energy))
        intervals.append(dict(start_s=t,end_s=end,loss_W=(power_energy+correction)/dt))
        T=new;t=end;velocity=new_velocity
    expected=_number(recorded_loss_J,'recorded loss');signed_total=math.fsum(signed);correction_total=math.fsum(clipped)
    thermal_total=math.fsum(thermal_signed);difference_total=math.fsum(differences)
    budget=ABS_LOSS_BUDGET_J+REL_LOSS_BUDGET*abs(expected)
    if (expected<0 or abs(signed_total-expected)>budget or abs(thermal_total-expected)>budget
            or difference_total>budget or correction_total>budget):
        raise ValueError('Loss reconstruction, independent thermal check or clipping exceeds energy budget')
    return dict(intervals=intervals,trace_end_s=t,trace_final_C=T,minimum_timestep_s=min_dt,
        signed_loss_J=signed_total,recorded_loss_J=expected,loss_residual_J=signed_total-expected,
        thermal_inversion_loss_J=thermal_total,thermal_inversion_residual_J=thermal_total-expected,
        absolute_per_step_method_difference_J=difference_total,
        clipped_negative_energy_J=correction_total,negative_step_count=sum(x>0 for x in clipped),
        roundoff_bound_sum_J=math.fsum(bounds),energy_budget_J=budget,
        scope='Electrical input minus midpoint mechanical power, independently cross-checked against forward-Euler temperatures; no motor loss measurement')


def _fold(intervals,period,*,periodic,extra_boundary=None):
    """Split each independent loss interval at period boundaries, then overlay."""
    events={0.:[],period:[]};parts=0;index=0
    if extra_boundary is not None and 0<extra_boundary<period:events[extra_boundary]=[]
    for row in intervals:
        a=_number(row['start_s'],'start');end=_number(row['end_s'],'end');power=_number(row['loss_W'],'loss')
        if not 0<=a<end or power<0:raise ValueError('Nonnegative ordered loss intervals required')
        if not periodic:end=min(end,period)
        while a<end:
            if not periodic and a>=period:break
            turn=math.floor(a/period) if periodic else 0
            boundary=min(end,(turn+1)*period)
            if boundary<=a:raise ValueError('Cannot split bounded periodic interval')
            x=a-turn*period;y=boundary-turn*period
            x=max(0.,min(period,x));y=max(0.,min(period,y))
            events.setdefault(x,[]).append((index,power,True))
            events.setdefault(y,[]).append((index,power,False))
            parts+=1;index+=1
            if parts>MAX_EVENT_PARTS:raise ValueError('Periodic event budget exceeded')
            a=boundary
    active={};segments=[];max_active=0;points=sorted(events)
    for i,point in enumerate(points[:-1]):
        for key,power,add in events[point]:
            if add:active[key]=power
            else:active.pop(key,None)
        end=points[i+1]
        if end>point:
            q=math.fsum(active.values());count=sum(value>.01 for value in active.values())
            max_active=max(max_active,count);segments.append((point,end,q))
    return segments,max_active


def cycle(segments,prelaunch_J,C,H,ambient,initial,max_step_s,*,cooling_off_after_s=None):
    """Exact exponential cooling per constant-power segment, with energy audit."""
    T=initial+prelaunch_J/C;peak=T;peak_time=0.;heat=prelaunch_J;cooling=[];steps=0
    for a,b,q in segments:
        count=max(1,math.ceil((b-a)/max_step_s));h=(b-a)/count
        steps+=count
        if steps>MAX_EVENT_PARTS*8:raise ValueError('Thermal integration step budget exceeded')
        local_H=0. if cooling_off_after_s is not None and a>=cooling_off_after_s else H
        for i in range(count):
            old=T
            if local_H:
                z=local_H*h/C
                if not math.isfinite(z):raise ValueError('Nonfinite thermal segment')
                factor=(-math.expm1(-z)/z) if z else 1.
                # Avoid cancellation in 1 - (1-exp(-z))/z for small z.
                remainder=(z/2-z*z/6+z*z*z/24-z*z*z*z/120) if z<1e-5 else 1-factor
                T=old-(old-ambient)*z*factor+(q*h/C)*factor
                # Independently integrate H*(T(t)-ambient); do not infer this
                # from the stored-energy change used in the residual below.
                rejected=local_H*(old-ambient)*h*factor+q*h*remainder
            else:
                T=old+q*h/C;rejected=0.
            if not math.isfinite(T) or not math.isfinite(rejected):raise ValueError('Nonfinite thermal state')
            cooling.append(rejected);heat+=q*h
            if T>peak:peak=T;peak_time=a+(i+1)*h
    rejected=math.fsum(cooling);stored=C*(T-initial)
    residual=heat-rejected-stored
    budget=ABS_LOSS_BUDGET_J+REL_LOSS_BUDGET*max(abs(heat),abs(rejected),abs(stored))
    if abs(residual)>budget:raise ValueError('Thermal energy balance exceeds budget')
    return dict(initial_C=initial,final_C=T,peak_C=peak,peak_time_s=peak_time,
        energy_in_J=heat,cooling_rejected_J=rejected,stored_energy_change_J=stored,
        energy_residual_J=residual,energy_budget_J=budget,thermal_steps=steps)


def periodic(intervals,prelaunch_J,C,H,ambient,headway,max_step,*,prelaunch_s=0.,suppress_cooling_during_prelaunch=False):
    """Compare the first departure with the asymptotic phase-folded pulse."""
    C=_number(C,'capacity');H=_number(H,'conductance');ambient=_number(ambient,'ambient')
    prelaunch_J=_number(prelaunch_J,'prelaunch');headway=_number(headway,'headway');max_step=_number(max_step,'step')
    prelaunch_s=_number(prelaunch_s,'prelaunch duration')
    if C<=0 or H<0 or prelaunch_J<0 or headway<=0 or max_step<=0 or not 0<=prelaunch_s<=headway:
        raise ValueError('Invalid thermal period or physical hypothesis')
    stop=headway-prelaunch_s if suppress_cooling_during_prelaunch else None
    first_segments,_=_fold(intervals,headway,periodic=False,extra_boundary=stop)
    folded,max_active=_fold(intervals,headway,periodic=True,extra_boundary=stop)
    first=cycle(first_segments,prelaunch_J,C,H,ambient,ambient,max_step,cooling_off_after_s=stop)
    one=cycle(folded,prelaunch_J,C,H,ambient,ambient,max_step,cooling_off_after_s=stop)
    two=cycle(folded,prelaunch_J,C,H,ambient,ambient+1.,max_step,cooling_off_after_s=stop)
    A=two['final_C']-one['final_C'];B=one['final_C']-ambient
    if H==0 or (suppress_cooling_during_prelaunch and prelaunch_s==headway):
        status='no-steady-state-positive-heat' if one['energy_in_J']>0 else 'no-unique-steady-state'
        steady=None
    elif not 0<=A<1:
        raise ValueError('Unstable or unresolved periodic thermal map')
    else:
        initial=ambient+B/(1-A);steady=cycle(folded,prelaunch_J,C,H,ambient,initial,max_step,cooling_off_after_s=stop)
        steady['closure_residual_C']=steady['final_C']-initial
        if abs(steady['closure_residual_C'])>1e-7:raise ValueError('Periodic fixed-point closure differs')
        status='conditional-periodic-solution'
    # Segment subdivision does not alter the exact linear constant-power solution.
    unsplit=cycle(folded,prelaunch_J,C,H,ambient,ambient,headway,cooling_off_after_s=stop)
    difference=one['final_C']-unsplit['final_C']
    if abs(difference)>1e-7:raise ValueError('Exact cooling subdivision differs')
    return dict(status=status,first_cycle=first,steady_cycle=steady,headway_s=headway,
        phase_max_simultaneous_nonzero_pulses=max_active,power_activity_threshold_W=.01,
        affine_A=A,affine_B_K=B,exact_cooling_subdivision_difference_C=difference,
        phase_folded_segments=len(folded),prelaunch_duration_s=prelaunch_s,
        cooling_hypothesis='suppressed for the entire aggregate during the prelaunch interval' if suppress_cooling_during_prelaunch else 'continuous over the full headway')


def _completion_reason(forward,scenario):
    """A premature or interrupted journey cannot supply a complete pulse."""
    if forward.get('state')!='stopped':return str(forward.get('state','missing-state'))
    if forward.get('execution')!='completed-method-test' or forward.get('reason') is not None:
        return 'stopped-with-unresolved-execution'
    if (forward.get('predicted_stop_within_berth') is not True
            or abs(_number(forward.get('final_position_m'),'final position')
                -_number(scenario.get('distance_m'),'distance'))
               >_number(scenario.get('berth_tolerance_m'),'berth tolerance')
            or abs(_number(forward.get('final_speed_m_s'),'final speed'))>1e-7):
        return 'stopped-outside-declared-berth'
    return None


def evaluate(root,request,*,expected_request_id):
    period,step=_request(request,expected_request_id);producer=_sha(Path(__file__).read_bytes())
    record,manifest=_inputs(root,request);out=[]
    for case in record['output']['cases']:
        f=case['forward'];thermal=case['force_map']['thermal_model'];pre=case['prelaunch']
        C=_number(thermal.get('capacity_J_K'),'capacity');H=_number(thermal.get('heat_rejection_W_K'),'conductance')
        ambient=_number(thermal.get('ambient_C'),'ambient');pre_J=_number(pre.get('motor_loss_energy_J'),'prelaunch energy')
        duration=_number(pre.get('duration_s'),'prelaunch duration')
        if pre_J<0 or duration<0 or duration>period or C<=0 or H<0:
            raise ValueError('Bounded nonnegative prelaunch hypothesis required')
        if abs(thermal['initial_C']-(ambient+pre_J/C))>1e-9:
            raise ValueError('Recorded prelaunch is not the declared ambient adiabatic increment')
        reconstructed=recover(f['trace'],thermal,f['magnetic_loss_energy_J'])
        last=f['trace'][-1]
        if (abs(reconstructed['trace_end_s']-f['elapsed_s'])>1e-8 or abs(reconstructed['trace_final_C']-f['temperature_C'])>1e-9
                or abs(_number(last.get('position_m'),'trace position')-_number(f.get('final_position_m'),'final position'))>1e-8
                or abs(_number(last.get('speed_m_s'),'trace speed')-_number(f.get('final_speed_m_s'),'final speed'))>1e-8):
            raise ValueError('Trace and recorded end state differ')
        total=math.fsum((f['magnetic_loss_energy_J'],pre_J))
        if abs(total-case['trajectory_summary']['total_conditional_motor_loss_energy_J'])>reconstructed['energy_budget_J']:
            raise ValueError('Prelaunch loss must be added exactly once')
        incomplete=_completion_reason(f,case['scenario'])
        if incomplete is not None:
            result=dict(status='held-incomplete-trajectory',reason=incomplete,first_cycle=None,steady_cycle=None)
        else:
            result=dict(status='conditional-two-cooling-hypotheses',
                continuous_cooling=periodic(reconstructed['intervals'],pre_J,C,H,ambient,period,step,prelaunch_s=duration),
                prelaunch_cooling_suppressed=periodic(reconstructed['intervals'],pre_J,C,H,ambient,period,step,
                    prelaunch_s=duration,suppress_cooling_during_prelaunch=True))
        out.append(dict(case=case['case'],scenario_id=case['scenario']['scenario_id'],map_id=case['map_id'],
            original_method_result_id=f['method_result_id'],original_state=f['state'],
            thermal_hypothesis=thermal,prelaunch=pre,reconstruction=reconstructed,periodic=result))
    # Detect ordinary accidental changes during evaluation; no OS sandbox claimed.
    if _inputs(root,request)!=(record,manifest) or _sha(Path(__file__).read_bytes())!=producer:
        raise ValueError('Pinned inputs or producer changed during evaluation')
    assumptions=dict(headway_s=period,maximum_step_s=step,
        prelaunch='Each 1 s adiabatic prelaunch loss is added once at departure, not as an extra second; timing inside that second is unresolved',
        dynamics='Phase-folded synthetic train-aggregate loss, fixed across cycles; exact exponential cooling on constant-power segments, with separate continuous and whole-lump prelaunch-suppressed cooling hypotheses',
        overlap='Sum all phase-overlapping pulses; no fixed-bank, converter, feeder or receiving allocation',
        limits='No measured force/loss/cooling; no station occupancy, tail clearance, 900 m winding or physical qualification',
        numerical='Force/power loss cross-checked against forward-Euler temperature inversion, with explicit signed roundoff budget; exponential repeated-duty model is a separate assumption')
    value=dict(schema='osr-periodic-thermal-research/1',request_id=expected_request_id,
        reference_candidate_id=REFERENCE,bundle_id=BUNDLE,source_epoch_id=request['source_epoch_id'],
        source_count=len(manifest['source_sha256']),candidate_artifact_sha256=request['candidate_artifact_sha256'],
        original_evaluation_id=request['output_evaluation_id'],study_manifest_id=request['study_manifest_id'],
        producer_sha256=producer,assumption_id=_id(assumptions),assumptions=assumptions,cases=out,**FLAGS)
    value['evaluation_id']=_id(value)
    return value


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path)
    p.add_argument('--request',required=True,type=Path);p.add_argument('--expected-request-id',required=True)
    p.add_argument('--output',required=True,type=Path);args=p.parse_args(argv)
    if args.request.is_symlink() or not args.request.is_file() or args.request.stat().st_size>1024*1024:
        raise ValueError('Bounded ordinary external request required')
    request=_json(args.request.read_bytes());value=evaluate(args.root,request,expected_request_id=args.expected_request_id)
    with args.output.open('xb') as stream:stream.write(_encoded(value))
    print(json.dumps(dict(evaluation_id=value['evaluation_id'],request_id=value['request_id'],
        cases=[dict(case=c['case'],state=c['original_state'],status=c['periodic']['status']) for c in value['cases']],**FLAGS),sort_keys=True))


if __name__=='__main__':main()
