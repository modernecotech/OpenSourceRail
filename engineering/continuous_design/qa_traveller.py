"""Unit/revision/serial-specific QA plans; simulated hold points are not tests."""
from engineering.twin_workflow import core

STAGES=('design','factory','transport','installed')
REQUIRED={
    'design':['unit-definition','handling-and-connections'],
    'factory':['material-trace','dimensions','embedded-interfaces'],
    'transport':['damage-and-identity'],
    'installed':['positive-lock','survey','interface-test'],
}


def requirements(unit):
    values={stage:list(tests) for stage,tests in REQUIRED.items()}
    if unit.get('service_type')=='drainage':values['factory'].append('leak-and-fall-test')
    if unit.get('service_type') in {'power','data'}:values['factory'].append('continuity-isolation-and-identification')
    if unit.get('process')=='precast':values['factory'].append('strength-and-curing')
    if unit.get('process')=='site-concrete':values['installed'].append('strength-and-curing')
    if unit.get('pile_installation',{}).get('method')=='driven':
        values['installed']+=['pile-driving-record','pile-installation-acceptance']
    return values


def template(unit):
    return dict(schema='osr-unit-qa-events/2',unit_id=unit['id'],unit_revision=unit['revision'],serial=None,batch=None,
        required=requirements(unit),material_certificates=[],records=[],
        dimensional_plan=[dict(axis=axis,nominal_extent_m=unit['bounds_m'][1][i]-unit['bounds_m'][0][i],tolerance_m=None,measured_value_m=None) for i,axis in enumerate('xyz')],
        installed_survey=[dict(axis=axis,measured_coordinate_m=None,approved_tolerance_m=None) for axis in 'xyz'],
        status='unexecuted; serial, measured results and independent acceptance required',manufacturing_release=False)


def event(record):
    """Content identity makes exact replay idempotent; it authenticates nobody."""
    if 'event_id' in record:raise ValueError('event identity is derived from immutable content')
    return dict(record,event_id=core.digest(record))


def assess(unit,traveller,*,interface_revision=None):
    expected=requirements(unit)
    if traveller.get('unit_id')!=unit['id'] or traveller.get('unit_revision')!=unit['revision']:
        return dict(state='stale',retest=list(STAGES),reason='manufactured unit definition/revision changed',accepted=False)
    records=traveller.get('records',[]);coverage={};retest=[];issues=[];unresolved=[];dispositions=[]
    if not isinstance(records,list) or len(records)>10000 or any(not isinstance(r,dict) for r in records):
        return dict(state='hold',retest=list(STAGES),event_issues=['bounded list of event records required'],accepted=False)
    for record in records:
        if record.get('event_id') and record['event_id']!=core.digest({k:v for k,v in record.items() if k!='event_id'}):
            issues.append('corrupt event: '+str(record.get('stage'))+'/'+str(record.get('test')))
    for stage,tests in expected.items():
        matching={};invalid_failure=False
        for record in records:
            if record.get('stage')!=stage:continue
            if record.get('unit_revision')!=unit['revision'] or record.get('serial')!=traveller.get('serial'):continue
            if not traveller.get('serial'):continue
            if stage in {'design','installed'} and record.get('interface_revision')!=interface_revision:continue
            if record.get('test') not in tests:continue
            if stage in {'design','installed'} and not interface_revision:
                issues.append('missing interface revision: '+stage+'/'+str(record.get('test')));continue
            identifier=record.get('event_id');content={k:v for k,v in record.items() if k!='event_id'}
            digest=record.get('evidence_sha256')
            if (not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest)
                or not isinstance(record.get('qualified_reviewer'),str) or not record['qualified_reviewer'].strip()
                or identifier!=core.digest(content) or type(record.get('sequence')) is not int or record['sequence']<1
                or not isinstance(record.get('event_type'),str) or record.get('event_type') not in {'test','disposition'}
                or not isinstance(record.get('state'),str) or record.get('state') not in ({'passed','failed','unknown'} if record.get('event_type')=='test' else {'closed'})
                or any(not isinstance(record.get(field,[]),list) or any(not isinstance(v,str) for v in record.get(field,[])) for field in ('retests','supersedes','failure_event_ids','retest_event_ids'))):
                issues.append('invalid/legacy event: '+stage+'/'+str(record.get('test')))
                invalid_failure |= record.get('state')=='failed';continue
            matching[identifier]=record  # identical replays collapse, never reorder evidence
        states=[];closed=[]
        for test in tests:
            events={key:r for key,r in matching.items() if r['test']==test}
            if len({r['sequence'] for r in events.values()})!=len(events):issues.append('conflicting sequence: '+stage+'/'+test)
            test_events={key:r for key,r in events.items() if r['event_type']=='test'}
            failures={key:r for key,r in test_events.items() if r['state']=='failed'}
            # A pass cannot erase a failure, even via a supersedes declaration.
            # Each failure needs a later applicable retest and explicit disposition.
            for key,failure in failures.items():
                for disposition_id,disposition in events.items():
                    if disposition['event_type']!='disposition' or disposition.get('state')!='closed' or not isinstance(disposition.get('reason'),str) or not disposition['reason'].strip():continue
                    if key not in disposition.get('failure_event_ids',[]):continue
                    retests=[test_events[rid] for rid in disposition.get('retest_event_ids',[]) if rid in test_events]
                    if any(r['state']=='passed' and key in r.get('retests',[]) and failure['sequence']<r['sequence']<disposition['sequence'] for r in retests):
                        closed.append(key);dispositions.append(disposition_id);break
            open_failures=set(failures)-set(closed);unresolved.extend(sorted(open_failures))
            superseded=set()
            for key,r in test_events.items():
                for previous in r.get('supersedes',[]):
                    old=test_events.get(previous)
                    if old is None or old['test']!=r['test'] or old['sequence']>=r['sequence']:
                        issues.append('invalid supersession: '+key)
                    else:superseded.add(previous)
            active=[r for key,r in test_events.items() if key not in superseded and key not in closed]
            states.append('failed' if open_failures else 'passed' if active and all(r['state']=='passed' for r in active) else 'unknown')
        if invalid_failure:states=['failed']*len(states);unresolved.append('invalid/legacy failure in '+stage)
        coverage[stage]=dict(required=tests,states=dict(zip(tests,states)),complete=all(s=='passed' for s in states))
        if not coverage[stage]['complete']:retest.append(stage)
    state='failed' if unresolved else 'passed-records' if not retest and not issues else 'hold'
    if issues:retest=list(dict.fromkeys(retest+[stage for stage in STAGES if any(stage+'/' in issue for issue in issues)]))
    return dict(state=state,coverage=coverage,retest=retest,
        unresolved_failure_event_ids=sorted(set(unresolved)),disposition_event_ids=sorted(set(dispositions)),event_issues=sorted(set(issues)),
        accepted=False,scope='Record consistency/coverage only; evidence hashes and reviewer claims still require authenticated external verification')
