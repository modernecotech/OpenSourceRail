"""Repeatable additional native and live interaction checks against the retained city."""
import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
import json
import subprocess
import time
from urllib.error import HTTPError
from urllib.parse import urlencode


def run(h):
    from osr_integration.config import digest
    previous=json.loads((h.OUTPUT/'report.json').read_text())
    if previous.get('passed') is not True:raise RuntimeError('Complete the base example scenario first')
    report=dict(schema='osr-city-expansion/1',passed=None,started_at=datetime.now(timezone.utc).isoformat(),checks=[],exhaustive=False)
    def save():
        h.write(h.OUTPUT/'expansion-report.json',report)
        h.write(h.OUTPUT/'expansion-report.html',h.module('expansion_html','deployment/example-city/report.py').render(report,[]))
    def check(identity,condition,before=None,after=None,level='live-http'):
        report['checks'].append(dict(id=identity,name=identity,passed=bool(condition),before=before,after=after,level=level));save()
        if not condition:raise AssertionError(identity)
        print('PASS '+identity,flush=True)
    cfg=json.loads((h.PRIVATE/'integration.json').read_text())
    principals={p['role']:p for p in cfg['principals'] if p['subject']!='samawah-only'}
    url='http://127.0.0.1:8192'
    def api(path,data=None,role='viewer',**query):
        return h.request_json(url+path+('?' + urlencode(query) if query else ''),data,{'Authorization':'Bearer '+principals[role]['token']})
    def snap(city='samawah'):return api('/snapshot',city=city,environment='simulation')
    def reject(identity,path,data,role='controller'):
        try:
            response=api(path,data,role)
            check(identity,path=='/commands' and response.get('state')=='rejected',after={'state':response.get('state'),'reason':response.get('reason')})
        except HTTPError as error:check(identity,error.code in [400,403],after={'http_status':error.code})
    baseline=json.loads((h.OUTPUT/'supervision/samawah/simulation/package.json').read_text())
    control=json.loads((h.OUTPUT/'supervision/mosul/simulation/package.json').read_text())
    current=baseline
    controls=h.PRIVATE/'controls.json';original_controls=json.loads(controls.read_text())
    def resign(p):
        p=copy.deepcopy(p);p.pop('sha256',None);p['sha256']=digest(p);return p
    def apply(p):
        nonlocal current
        p=resign(p);review=api('/packages/preview',{'package':p},'engineer')
        response=api('/packages',dict(package=p,expected=current['sha256'],review_sha256=review['sha256']),'engineer');current=p;return response
    def asset(kind='charger'):return next(a for a in snap()['assets'] if a['equipment_type']==kind and a['configuration_status']=='active')
    def sample(a,name,value,quality='valid',**extra):
        return dict(city='samawah',environment='simulation',asset_id=a['asset_id'],measurement=name,source_id='simulator',sequence=time.time_ns(),source_timestamp=datetime.now(timezone.utc).isoformat(),unit=a['measurements'][name]['unit'],value=value,quality=quality,**extra)
    def command(level=60,seconds=20):
        now=datetime.now(timezone.utc)
        return dict(request_id='matrix-'+str(time.time_ns()),city='samawah',environment='simulation',asset_id='SAM-ST-001:facilities',command='set_lighting',parameters={'level':level},created_at=now.isoformat(),expires_at=(now+timedelta(seconds=seconds)).isoformat(),required_conditions=['local_remote_enabled'])
    def wait(predicate,seconds=30):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            result=predicate()
            if result:return result
            time.sleep(.2)
        raise AssertionError('Timed out waiting for downstream observation')
    changed=False
    try:
        check('scope.initial-baseline',api('/packages/preview',{'package':baseline})['status']=='no-change')
        # A true global source pause lets HTTP tests drive controller result/expiry deterministically.
        changed=True;h.write(controls,{'disconnected':True},True);time.sleep(3)
        testing=copy.deepcopy(baseline)
        for a in testing['equipment']:a['alarms']=[]
        apply(testing)
        for a in current['equipment']:
            for name,m in a['measurements'].items():
                for label,value,expected in [('below',m['min']-1,'invalid'),('min',m['min'],'valid'),('max',m['max'],'valid'),('above',m['max']+1,'invalid')]:
                    try:
                        result=api('/telemetry',sample(a,name,value),'controller')
                        okay=result.get('quality')==expected
                    except HTTPError as error:
                        okay=expected=='invalid' and abs(value)>1e12 and error.code==400;result={'http_status':error.code}
                    check('telemetry.boundary.'+a['asset_id']+'.'+name+'.'+label,okay,before={'value':value,'min':m['min'],'max':m['max']},after=result)
        # Full Cartesian matrix over these declared dimensions, not all platform variables.
        cases=0
        for scale in [-2,0]:
            p=copy.deepcopy(testing);next(a for a in p['equipment'] if a['equipment_type']=='charger')['measurements']['temperature_c']['scale']=scale
            reject('configuration.invalid-scale.'+str(scale),'/packages/preview',{'package':resign(p)},'engineer')
        for scale in [.5,1,2]:
            for offset in [-5,5]:
                p=copy.deepcopy(testing);a=next(a for a in p['equipment'] if a['equipment_type']=='charger')
                a['measurements']['temperature_c'].update(scale=scale,offset=offset,min=-50,max=50)
                apply(p)
                for raw in [-30,0,30]:
                    for quality in ['valid','invalid','stale','disconnected']:
                        transformed=raw*scale+offset;expected='invalid' if not -50<=transformed<=50 else quality
                        result=api('/telemetry',sample(a,'temperature_c',raw,quality),'controller')
                        observed=asset()['readings']['temperature_c']
                        cases+=1
                        check('telemetry.interaction.'+str(cases),result['quality']==expected and observed['value']==transformed and observed['quality']==expected,before={'scale':scale,'offset':offset,'raw':raw,'source_quality':quality},after={'value':observed['value'],'quality':observed['quality']})
        apply(testing);a=asset()
        for quality in ['invalid','stale','disconnected']:
            result=api('/telemetry',sample(a,'temperature_c',None,quality),'controller')
            check('telemetry.null.'+quality,result['quality']==quality and asset()['readings']['temperature_c']['value'] is None)
        reject('telemetry.null.valid','/telemetry',sample(a,'temperature_c',None))
        message=sample(a,'temperature_c',35);api('/telemetry',message,'controller')
        later=sample(a,'temperature_c',35);later['source_timestamp']=(datetime.fromisoformat(message['source_timestamp'])-timedelta(seconds=1)).isoformat()
        reject('telemetry.timestamp.regression','/telemetry',later)
        for label,override in [('negative-sequence',{'sequence':-1}),('boolean-sequence',{'sequence':True}),('sequence-overflow',{'sequence':2**63}),('unknown-quality',{'quality':'good'}),('wrong-source',{'source_id':'other-controller'}),('boolean-value',{'value':True})]:
            reject('telemetry.reject.'+label,'/telemetry',{**sample(a,'temperature_c',35),**override})
        # Concurrent identical samples must produce one history row.
        message=sample(a,'temperature_c',36)
        with ThreadPoolExecutor(max_workers=8) as pool:responses=list(pool.map(lambda _:api('/telemetry',message,'controller'),range(8)))
        check('telemetry.concurrent-idempotency',sum(not r['duplicate'] for r in responses)==1,after={'requests':8,'inserted':sum(not r['duplicate'] for r in responses)})
        # Pending commands bind the configuration review; only one competing package wins.
        request=command();api('/commands',request,'operator')
        check('command.repeat-idempotency',api('/commands',request,'operator')['state']=='requested')
        reject('command.changed-retry','/commands',{**request,'parameters':{'level':70}},'operator')
        p=copy.deepcopy(testing);next(a for a in p['equipment'] if a['equipment_type']=='facilities')['commands']['set_lighting']['max']=80;p=resign(p)
        review=api('/packages/preview',{'package':p})
        check('command.pending-blocks-rule-change',bool(review['application']['blockers']))
        reject('command.pending-rule-apply','/packages',dict(package=p,expected=current['sha256'],review_sha256=review['sha256']),'engineer')
        reject('command.illegal-completion','/controller/result',dict(request_id=request['request_id'],state='completed',result='out of order'))
        for state in ['accepted','completed']:
            result=api('/controller/result',dict(request_id=request['request_id'],state=state,result='fixture result'),'controller')
            check('command.transition.'+state,result['state']==state,level='live-http-controller-fixture')
        check('command.terminal-retry',api('/controller/result',dict(request_id=request['request_id'],state='completed',result='fixture result'),'controller')['state']=='completed',level='live-http-controller-fixture')
        reject('command.terminal-rewrite','/controller/result',dict(request_id=request['request_id'],state='failed',result='changed'))
        for label,override in [('expired',{'expires_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()}),('missing-permissive',{'required_conditions':[]}),('extra-parameter',{'parameters':{'level':60,'extra':1}}),('boolean-level',{'parameters':{'level':True}}),('future-created',{'created_at':(datetime.now(timezone.utc)+timedelta(seconds=10)).isoformat()})]:
            reject('command.reject.'+label,'/commands',{**command(),**override},'operator')
        request=command(seconds=1);api('/commands',request,'operator');time.sleep(1.2)
        pending=api('/controller/commands',role='controller')
        observed=next(c for c in asset('facilities')['commands_audit'] if c['id']==request['request_id'])
        check('command.expiry-while-source-offline',request['request_id'] not in [c['request_id'] for c in pending] and observed['state']=='failed',after={'state':observed['state'],'reason':observed['result']})
        for role in ['viewer','operator','reviewer','inspector','maintainer']:
            reject('permission.telemetry.'+role,'/telemetry',sample(a,'temperature_c',35),role)
            reject('permission.package.'+role,'/packages',dict(package=current),role)
        # Competing reviews of two different changes against one baseline.
        proposals=[]
        for interval in [3,4]:
            p=copy.deepcopy(testing);p['historian']['sampling_seconds']=interval;p=resign(p)
            proposals.append(dict(package=p,expected=current['sha256'],review_sha256=api('/packages/preview',{'package':p})['sha256']))
        def race(proposal):
            try:return api('/packages',proposal,'engineer')
            except HTTPError as error:return {'http_status':error.code}
        with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(race,proposals))
        winners=[i for i,r in enumerate(responses) if r.get('created')]
        if len(winners)==1:current=proposals[winners[0]]['package']
        check('configuration.concurrent-review',len(winners)==1 and sum(r.get('http_status')==400 for r in responses)==1,after=responses)
        apply(testing)
        # Quality interrupts pending alarm persistence and cannot clear active faults.
        p=copy.deepcopy(testing);a=next(a for a in p['equipment'] if a['equipment_type']=='charger')
        a['alarms']=[dict(id='matrix-temperature',measurement='temperature_c',high=50,clear_below=40,delay_seconds=1,repeat_seconds=1,priority='low',response='Matrix fixture',maintenance=False)]
        apply(p)
        def alarm():return next(r for r in asset()['alarms'] if r['rule']=='matrix-temperature')
        api('/telemetry',sample(a,'temperature_c',35),'controller')
        api('/telemetry',sample(a,'temperature_c',55),'controller');time.sleep(.6)
        api('/telemetry',sample(a,'temperature_c',55,'invalid'),'controller');time.sleep(.6)
        api('/telemetry',sample(a,'temperature_c',55),'controller')
        check('alarm.invalid-interrupts-persistence',not alarm()['active'])
        time.sleep(1.1);api('/telemetry',sample(a,'temperature_c',55),'controller')
        check('alarm.reestablished-persistence',bool(alarm()['active']))
        occurrence=alarm()['occurrences']
        ack=dict(city='samawah',environment='simulation',asset_id=a['asset_id'],rule='matrix-temperature',occurrence=occurrence)
        api('/alarms/acknowledge',ack,'operator')
        api('/telemetry',sample(a,'temperature_c',35,'invalid'),'controller')
        check('alarm.invalid-cannot-clear',bool(alarm()['active']))
        time.sleep(1.1);api('/telemetry',sample(a,'temperature_c',55),'controller');time.sleep(1.1);api('/telemetry',sample(a,'temperature_c',55),'controller')
        check('alarm.repeat-increments-occurrence',alarm()['occurrences']>occurrence)
        reject('alarm.stale-acknowledgement','/alarms/acknowledge',ack,'operator')
        api('/telemetry',sample(a,'temperature_c',35),'controller')
        check('alarm.clear-without-erp',not alarm()['active'] and not alarm()['case_id'])
        apply(baseline);h.write(controls,original_controls,True)
        wait(lambda:asset()['readings']['power_kw']['quality']=='valid')
        check('scope.control-package-unchanged',api('/packages/preview',{'package':control})['status']=='no-change')
        contracts=h.module('example_contract_matrix','deployment/example-city/contracts.py').verify(h)
        check('contracts.registered-input-boundaries',contracts['passed'],after={'checks':len(contracts['checks'])},level='schema-only')
        # Run all eight adapters and actual payment posting inside one rollback transaction.
        source=json.loads((h.OUTPUT/'native-records.json').read_text())
        before_native=h.backend('expansion-audit',{'source':source})
        script='INPUT = '+repr(dict(site=h.SITE,source=source))+'\n'+(h.ROOT/'deployment/example-city/erp-expansion.py').read_text()
        result=subprocess.run(h.compose('erp','exec','-T','backend','env/bin/python'),input=script,text=True,capture_output=True,cwd=h.ROOT)
        h.write(h.OUTPUT/'native-expansion.log',result.stdout+result.stderr)
        payload=next((json.loads(line.removeprefix('OSR_EXPANSION:')) for line in result.stdout.splitlines() if line.startswith('OSR_EXPANSION:')),None)
        if payload:
            h.write(h.OUTPUT/'native-expansion.json',payload);report['checks'].extend(payload['checks']);save()
        if result.returncode or not payload or not payload['passed']:raise RuntimeError('Native expansion failed; see native-expansion.log')
        after_native=h.backend('expansion-audit',{'source':source})
        check('erp.rollback-restores-records-and-invoice',before_native==after_native,before=before_native,after=after_native,level='native-erp-rollback')
        report['passed']=True
    except BaseException as error:
        report.update(passed=False,error=str(error));raise
    finally:
        try:
            if changed:
                try:apply(baseline)
                finally:h.write(controls,original_controls,True)
                ready=time.time();wait(lambda:asset()['readings']['power_kw']['quality']=='valid' and asset()['readings']['power_kw']['received']>=ready)
                check('restore.baseline-and-fresh-source',True)
        except BaseException as error:
            report.update(passed=False,restoration_error=str(error));raise
        finally:
            report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    print('PASS expanded city checks; original configuration restored',flush=True)
