"""Gap/temperature profiles use bounded workers, never assume capacity is hover."""
import json
from pathlib import Path
import time
from . import ROOT,FLAGS
from .common import identity,write,inventory,unaccepted
from hashlib import sha256

GAPS=(.012,.028,.044,.060)
TEMPERATURES=(20.,80.)
BUDGET=dict(max_new_points=16,seconds_per_point=300,total_seconds=900)


def source_snapshot(root=ROOT):
    """Numerical dependencies only; reporting prose cannot change these fields."""
    from . import screen,common
    result=screen.source_snapshot(root)
    for path in (Path(__file__),Path(common.__file__),Path(__file__).parent/'tests/test_operating.py'):
        name=path.relative_to(Path(__file__).resolve().parents[2]).as_posix()
        if path.is_symlink():raise ValueError('ordinary operating sources required')
        result[name]=sha256(path.read_bytes()).hexdigest()
    return dict(sorted(result.items()))


def schedule(bundles):
    rows=[dict(candidate_id=b['physical_id'],gap_m=g,temperature_C=t,current_A=0.) for b in bundles for t in TEMPERATURES for g in GAPS]
    controlled=next((b for b in bundles if b['parameters'].get('winding_layout')=='differential'),None)
    if controlled:
        rows += [dict(candidate_id=controlled['physical_id'],gap_m=.044,temperature_C=80.,current_A=i) for i in (-15.,15.)]
    return rows


def run(output,*,root=ROOT,bundles,baseline_rows):
    from . import candidates,screen
    root=Path(root).resolve();output=Path(output).absolute()
    if len(bundles)!=2 or len({b['physical_id'] for b in bundles})!=2:raise ValueError('two distinct physical candidates required')
    for b in bundles:candidates.validate(b,root)
    before=source_snapshot(root)
    if output.is_symlink() or any(p.is_symlink() for p in output.parents):raise ValueError('ordinary fresh output required')
    output.mkdir(parents=True,exist_ok=False)
    request=dict(schema='osr-halbach-operating/1',root=str(root),bundles=bundles,baseline_rows=baseline_rows,
                 source_sha256=before,schedule=schedule(bundles),budget=BUDGET,**FLAGS)
    request['request_id']=identity(request);write(output/'request.json',request)
    rows=[];started=time.monotonic();new_count=0;by_id={b['physical_id']:b for b in bundles}
    for number,point in enumerate(request['schedule']):
        b=by_id[point['candidate_id']];label=f'point-{number:02d}'
        old=next((r for r in baseline_rows if r['candidate_id']==b['physical_id']),None)
        if point['gap_m']==.012 and point['temperature_C']==80 and point['current_A']==0 and old is not None:
            screen.validate_point(old,b,root);value=old;reused=True
        else:
            new_count+=1
            if new_count>16:raise ValueError('new point budget exceeded')
            currents={} if point['current_A']==0 else {c['id']:point['current_A'] for c in b['circuits']}
            entry=dict(candidate=b,scenario=screen._scenario(b,point['gap_m'],point['temperature_C'],currents),
                       settings=screen.SETTINGS,source_sha256=screen.source_snapshot(root))
            value=screen._execute(output/label,entry,root,min(300.,max(0.,900-time.monotonic()+started)));reused=False
        rows.append(dict(point=point,case=label,reused_nominal=reused,result=value))
    if source_snapshot(root)!=before:raise ValueError('operating sources changed during execution')
    result=dict(schema=request['schema'],request_id=request['request_id'],rows=rows,source_sha256=before,
                new_field_points=new_count,scope='Exploratory 12–60 mm states. Boarding height, capture, tolerances and actual gap travel remain unqualified.',**FLAGS)
    write(output/'result.json',result);write(output/'manifest.json',dict(source_sha256=before,files_sha256=inventory(output,('manifest.json',)),**FLAGS))
    verify(output,root=root);return result


def verify(output,*,root=ROOT):
    from . import candidates,screen
    d=Path(output);r=json.loads((d/'request.json').read_bytes());v=json.loads((d/'result.json').read_bytes());m=json.loads((d/'manifest.json').read_bytes())
    for record in (r,v,m):unaccepted(record)
    if r['request_id']!=identity({k:x for k,x in r.items() if k!='request_id'}) or v['request_id']!=r['request_id']:raise ValueError('operating identity differs')
    if r['source_sha256']!=source_snapshot(root) or v['source_sha256']!=r['source_sha256'] or m['source_sha256']!=r['source_sha256']:raise ValueError('operating source differs')
    if r['budget']!=BUDGET or r['schedule']!=schedule(r['bundles']) or [q['point'] for q in v['rows']]!=r['schedule']:raise ValueError('operating schedule differs')
    if m['files_sha256']!=inventory(d,('manifest.json',)):raise ValueError('operating payload differs')
    bundles={b['physical_id']:b for b in r['bundles']}
    if len(bundles)!=2:raise ValueError('two exact candidates required')
    for b in bundles.values():candidates.validate(b,root)
    new=0
    for number,row in enumerate(v['rows']):
        point=row['point'];b=bundles[point['candidate_id']];value=row['result']
        if row['case']!=f'point-{number:02d}' or value['candidate_id']!=b['physical_id']:raise ValueError('operating membership differs')
        if row['reused_nominal']:
            original=next(q for q in r['baseline_rows'] if q['candidate_id']==b['physical_id'])
            if value!=original or point['gap_m']!=.012 or point['temperature_C']!=80 or point['current_A']!=0:raise ValueError('operating reuse differs')
        else:
            new+=1;entry=json.loads((d/row['case']/'input.json').read_bytes())
            currents={} if point['current_A']==0 else {c['id']:point['current_A'] for c in b['circuits']}
            expected=dict(candidate=b,scenario=screen._scenario(b,point['gap_m'],point['temperature_C'],currents),settings=screen.SETTINGS,source_sha256=screen.source_snapshot(root))
            if entry!=expected:raise ValueError('operating input differs')
            if 'execution' in value:
                execution=json.loads((d/row['case']/'execution.json').read_bytes())
                if execution!=value['execution'] or not 0<execution['deadline_s']<=300:raise ValueError('operating worker execution differs')
                if value['execution_status']=='completed' and (execution['returncode']!=0 or execution['timed_out']):raise ValueError('unsuccessful worker cannot receive force credit')
        if value.get('execution_status')=='completed':
            if not row['reused_nominal'] and 'execution' not in value:raise ValueError('completed worker execution receipt required')
            screen.validate_point(value,b,root)
            raw=value['raw_result']['operating_point'];currents={} if point['current_A']==0 else {c['id']:point['current_A'] for c in b['circuits']}
            if raw!=dict(gap_m=point['gap_m'],temperature_C=point['temperature_C'],currents_A=currents,lateral_m=0.,roll_rad=0.):raise ValueError('operating scenario differs')
            if not row['reused_nominal'] and json.loads((d/row['case']/'point.json').read_bytes())!={k:x for k,x in value.items() if k!='execution'}:raise ValueError('operating point file differs')
        elif value.get('comparison'):raise ValueError('unexecuted point cannot claim force')
    if new!=v['new_field_points'] or new>16:raise ValueError('operating budget differs')
    return dict(current=True,points=len(v['rows']),**FLAGS)
