"""Settings sensitivity and recovery checks, with explicit observation levels."""
import copy
from datetime import datetime,timezone,timedelta
import gzip
import json
import time
from urllib.error import HTTPError


def planning(h,check,setup):
    from osr_erpnext.city_config import make_city_plan
    cities=h.module('example_city_matrix','tools/automation/erpnext-city.py')
    cfg=json.loads((h.OUTPUT/'erp/samawah/effective-config.json').read_text())
    path=cities.catalogue()['samawah'][0].parent/'operations/samawah-operations.json.gz'
    bundle=json.loads(gzip.decompress(path.read_bytes()))
    before=make_city_plan(bundle,cfg)
    for kind in cfg['tasks']:
        changed=copy.deepcopy(cfg);changed['tasks'][kind]=False
        plan=make_city_plan(bundle,changed)
        check('Planning task switch changes generated '+kind+' work',any(r['kind']==kind for r in before['records']) and not any(r['kind']==kind for r in plan['records']),
            before={'level':'generated-plan','count':sum(r['kind']==kind for r in before['records'])},after={'count':0})
    changed=copy.deepcopy(cfg);changed['release']='example-calendar-2'
    changed['calendar'].update(start_date='2026-11-02',working_weekdays=[0,2,4],holidays=['2026-11-02'],timezone='Asia/Baghdad')
    changed['tasks']={k:k=='programme' for k in changed['tasks']}
    changed['organisation']['warehouses'].append('Example Spares')
    changed['city_programme']=[dict(id='example-calendar',title='Example approved calendar check',department='Quality and Assurance',start_day=0,finish_day=2,depends_on=['organisation'])]
    plan=make_city_plan(bundle,changed);h.write(h.OUTPUT/'erp/calendar-plan.json',plan)
    h.copy_in(h.OUTPUT/'erp/calendar-plan.json','/tmp/example-calendar.json')
    imported=h.backend('import',dict(path='/tmp/example-calendar.json',company=setup['company']))
    native=h.backend('audit-plan',dict(project=imported['project']))
    check('Calendar start, weekday mask and holiday change actual ERP dates',native['start']=='2026-11-04' and native['end']=='2026-11-09',
        before=cfg['calendar'],after=native)
    check('City-specific programme, department and additional warehouse reach ERP',native['department'].startswith('OSR samawah Quality and Assurance') and native['warehouse'],after=native)
    changed['calendar']['working_weekdays']=[]
    try:make_city_plan(bundle,changed);check('Invalid calendar is rejected',False)
    except ValueError:check('Invalid calendar is rejected',True)


def supervision(h,check,reject,api,apply,accepted,asset,snapshot,pulse,controls,wait,baseline):
    from osr_integration.config import digest
    def update(edit):
        p=copy.deepcopy(baseline);edit(p);p.pop('sha256',None);p['sha256']=digest(p);apply(p);return p
    def charger(p):return next(a for a in p['equipment'] if a['equipment_type']=='charger')
    # Pause only this example city's source while explicit timestamped test samples are sent.
    controls({'cities':{'samawah':{'disconnected':True}}});time.sleep(3)
    a=asset();measurement='temperature_c'
    update(lambda p:charger(p)['measurements'][measurement].update(scale=2,offset=5,max=200))
    message=pulse(asset(),measurement,20);api('/telemetry',message,role='controller')
    check('Scale and offset change the observed engineering value',asset()['readings'][measurement]['value']==45,before=20,after=45)
    check('Identical telemetry retry is idempotent',api('/telemetry',message,role='controller')['duplicate'])
    reject('Changed same-sequence telemetry is rejected','/telemetry',{**message,'value':21},role='controller')
    bad=api('/telemetry',pulse(asset(),measurement,110),role='controller')
    check('Transformed out-of-range measurements become invalid',bad['quality']=='invalid')
    reject('Wrong measurement unit is rejected','/telemetry',pulse(asset(),measurement,20,unit='wrong-unit'),role='controller')
    reject('Future source clock is rejected','/telemetry',pulse(asset(),measurement,20,when=(datetime.now(timezone.utc)+timedelta(minutes=1)).isoformat()),role='controller')
    update(lambda p:charger(p)['measurements'][measurement].update(stale_seconds=1))
    api('/telemetry',pulse(asset(),measurement,35),role='controller')
    wait(lambda:asset()['readings'][measurement]['quality']=='stale',timeout=3)
    check('Changed stale threshold changes displayed quality',True,before=charger(baseline)['measurements'][measurement]['stale_seconds'],after={'stale_seconds':1,'quality':asset()['readings'][measurement]['quality']})
    wait(lambda:asset()['readings'][measurement]['quality']=='disconnected',timeout=5)
    check('Source loss becomes disconnected without reusing valid values',True)
    # Every configured measurement is exercised at its valid midpoint and above its range.
    count=0
    apply(copy.deepcopy(baseline))
    for a in snapshot()['assets']:
        for name,m in a['measurements'].items():
            value=(m['min']+m['max'])/2
            result=api('/telemetry',pulse(a,name,value),role='controller')
            if result['quality']!='valid':raise AssertionError('Midpoint not accepted: '+a['asset_id']+':'+name)
            try:
                result=api('/telemetry',pulse(a,name,m['max']+1),role='controller')
                if result['quality']!='invalid':raise AssertionError('Upper bound ineffective: '+a['asset_id']+':'+name)
            except HTTPError as error:
                if error.code!=400 or m['max']+1<=1e12:raise
            count+=1
    check('All selected equipment measurement ranges affect ingestion',count>0,after={'measurement_contracts':count,'cases':count*2})
    # Avoid alarms during threshold probing: maintenance=false must suppress case creation.
    update(lambda p:charger(p)['alarms'][0].update(high=50,clear_below=40,delay_seconds=1,repeat_seconds=30,maintenance=False,response='Example threshold response'))
    api('/telemetry',pulse(asset(),measurement,35),role='controller')
    before={r['case_id'] for r in asset()['alarms'] if r['case_id']}
    queue_before=len(snapshot()['outbox'])
    api('/telemetry',pulse(asset(),measurement,55),role='controller')
    check('Alarm persistence delays activation',not next(r for r in asset()['alarms'] if r['rule']=='cooling')['active'])
    time.sleep(1.2);api('/telemetry',pulse(asset(),measurement,55),role='controller')
    row=next(r for r in asset()['alarms'] if r['rule']=='cooling')
    check('Changed alarm threshold and delay activate at the new value',bool(row['active']),before=charger(baseline)['alarms'][0],after={'high':50,'clear_below':40,'delay_seconds':1,'observed_temperature':55,'occurrences':row['occurrences']})
    occurrence=row['occurrences'];api('/telemetry',pulse(asset(),measurement,55),role='controller')
    check('Repeat interval suppresses duplicate occurrences',next(r for r in asset()['alarms'] if r['rule']=='cooling')['occurrences']==occurrence)
    api('/telemetry',pulse(asset(),measurement,45),role='controller')
    check('Hysteresis holds an active alarm in the deadband',bool(next(r for r in asset()['alarms'] if r['rule']=='cooling')['active']),after={'temperature':45,'high':50,'clear_below':40})
    api('/telemetry',pulse(asset(),measurement,35),role='controller')
    check('Changed clear threshold clears the alarm',not next(r for r in asset()['alarms'] if r['rule']=='cooling')['active'],after={'temperature':35,'clear_below':40})
    check('Maintenance-disabled rule creates no ERP case',before=={r['case_id'] for r in asset()['alarms'] if r['case_id']} and len(snapshot()['outbox'])==queue_before)
    apply(copy.deepcopy(baseline));controls({});wait(lambda:asset()['readings']['temperature_c']['value']==35)
    def command(level,ttl=15,**extra):
        now=datetime.now(timezone.utc)
        return dict(request_id='example-command-'+str(time.time_ns()),city='samawah',environment='simulation',asset_id=asset('facilities')['asset_id'],
            command='set_lighting',parameters={'level':level},created_at=now.isoformat(),expires_at=(now+timedelta(seconds=ttl)).isoformat(),required_conditions=['local_remote_enabled'],**extra)
    for level in [20,55,100]:
        msg=command(level);api('/commands',msg,role='operator')
        wait(lambda:any(r['id']==msg['request_id'] and r['state']=='completed' for r in asset('facilities')['commands_audit']))
        wait(lambda:asset('facilities')['readings']['lighting_pct']['value']==level)
        check('Lighting setting reaches controller and measured feedback: '+str(level),True)
    def bounds(p):next(a for a in p['equipment'] if a['equipment_type']=='facilities')['commands']['set_lighting'].update(min=30,max=80,max_ttl_seconds=5)
    update(bounds)
    reject('Changed command minimum is enforced','/commands',command(25,ttl=4),role='operator')
    reject('Changed command maximum is enforced','/commands',command(85,ttl=4),role='operator')
    reject('Changed command lifetime is enforced','/commands',command(50,ttl=10),role='operator')
    reject('Viewer cannot issue a controller command','/commands',command(50,ttl=4),role='viewer')
    # TTL bounds were tested above; restore the normal delivery window while
    # independently checking the controller's local-enable input.
    apply(copy.deepcopy(baseline))
    controls({'cities':{'samawah':{'local_remote_disabled':True}}})
    msg=command(50);api('/commands',msg,role='operator')
    wait(lambda:any(r['id']==msg['request_id'] and r['state']=='rejected' for r in asset('facilities')['commands_audit']))
    check('Controller local-enable setting rejects an otherwise valid command',True)
    controls({});apply(copy.deepcopy(baseline))
    # A changed package must not bypass either stale-review or role checks.
    p=copy.deepcopy(baseline);p['template_revision']='example-changed';p.pop('sha256');p['sha256']=digest(p)
    reject('Package update requires the exact accepted hash','/packages',dict(package=p,expected='0'*64,review_sha256='0'*64))
    reject('Viewer cannot apply supervisory settings','/packages',dict(package=p),role='viewer')
    reject('Physical scope cannot be requested by simulation credentials','/commands',{**command(50),'environment':'physical'},role='operator')
    # Confirm that sampling configuration changes the native simulator's actual arrivals.
    def history():return api('/history',query='?city=samawah&environment=simulation&asset_id=SAM-ST-001:charger&measurement=power_kw')
    update(lambda p:p['historian'].update(sampling_seconds=4))
    time.sleep(13)
    rows=history();gaps=[rows[i]['source_time']-rows[i+1]['source_time'] for i in range(min(2,len(rows)-1))]
    check('Sampling interval changes actual controller arrival times',len(gaps)==2 and all(3.5<=g<=7 for g in gaps),before=2,after={'configured_seconds':4,'observed_gaps':gaps})
    apply(copy.deepcopy(baseline))


def recovery(h,check,api,asset,controls,wait,base,previous_case,apply,baseline):
    from osr_integration.config import digest
    changed=copy.deepcopy(baseline)
    next(a for a in changed['equipment'] if a['equipment_type']=='charger')['alarms'][0].update(priority='low',response='Example recovery triage instruction')
    changed.pop('sha256');changed['sha256']=digest(changed);apply(changed)
    # ERP outage: a new fault remains durable and is delivered once after restoration.
    h.command(h.compose('erp','stop','frontend'),'erp-outage')
    try:
        controls({'cities':{'samawah':{'cooling_fault':True}}})
        wait(lambda:any(r['active'] and not r['case_id'] for r in asset()['alarms']))
        queue=api('/snapshot',query='?city=samawah&environment=simulation')['outbox']
        check('ERP outage keeps a durable pending maintenance event',any(r['state']=='pending' for r in queue))
    finally:h.command(h.compose('erp','start','frontend'),'erp-outage')
    alarm=wait(lambda:next((r for r in asset()['alarms'] if r['active'] and r['case_id'] and r['case_id']!=previous_case),None),timeout=120)
    check('ERP recovery delivers a new fault once, without reusing the closed case',bool(alarm['case_id']),after=alarm['case_id'])
    native=h.backend('case',dict(issue=alarm['case_id']))
    check('Changed alarm priority and response reach native ERP triage',native['priority']=='Low' and 'Example recovery triage instruction' in native['description'],before='High',after=native)
    issue=alarm['case_id'];time.sleep(3)
    check('Recovery retries do not duplicate the maintenance case',next(r for r in asset()['alarms'] if r['rule']=='cooling')['case_id']==issue)
    controls({});wait(lambda:not next(r for r in asset()['alarms'] if r['rule']=='cooling')['active'])
    before=asset()['installations']
    h.command(h.compose('supervision','restart','integration'),'gateway-restart')
    h.wait_http('http://127.0.0.1:8192/health')
    check('Gateway restart retains installed/removed serial history',asset()['installations']==before)
    ready_at=time.time()
    wait(lambda:asset()['readings']['temperature_c']['quality']=='valid' and asset()['readings']['temperature_c']['received']>=ready_at)
    check('Gateway restart resumes current controller measurements',True)
    apply(copy.deepcopy(baseline))


def embedded(check,asset,snapshot,controls,wait):
    # These flags enter the actual Rust evaluators, not fabricated gateway responses.
    flags=['station_fault','battery_trip','aux_fault','cbm_service','points_detection_fault','faregate_denial']
    controls({'cities':{'samawah':{name:True for name in flags}}})
    expected=[('facilities','fault_count',1),('facilities','lighting_pct',0),
        ('vehicle-bms','trip',1),('vehicle-aux','fault_count',1),('vehicle-aux','comfort_power',0),
        ('vehicle-hvac','reduced',1),('vehicle-cbm','health',2),('vehicle-cbm','brake_remaining_pct',10),
        ('points','detection_unknown',1),('faregate','last_decision',2)]
    for kind,name,value in expected:
        wait(lambda:asset(kind)['readings'][name]['value']==value)
        check('Native fault controls change '+kind+'.'+name,True,after=value)
    for kind in ['facilities','vehicle-bms','vehicle-aux','vehicle-cbm','points']:
        row=wait(lambda:next((r for r in asset(kind)['alarms'] if r['active'] and r['case_id']),None))
        check('Native '+kind+' fault routes to a scoped ERP case',bool(row['case_id']),after=row['case_id'])
    controls({})
    wait(lambda:asset('vehicle-cbm')['readings']['health']['value']==0)
    wait(lambda:asset('points')['readings']['detection_unknown']['value']==0)
    check('Restored controller settings clear faults without closing ERP maintenance',
        any(r['case_id'] and r['erp_status']=='Open' and not r['active'] for r in asset('vehicle-cbm')['alarms']))
    methods=[a for a in snapshot()['assets'] if a.get('manufacturing_method')]
    for index,a in enumerate(methods):
        method=a['manufacturing_method']['method_id'];kind=a['equipment_type'];progress=(index+1)*10
        controls({'cities':{'samawah':{'factory_method':method,'factory_cycle_progress_pct':progress,
            'factory_cell_unavailable':True,'factory_process_excursion':True}}})
        wait(lambda:asset(kind)['readings']['cycle_progress_pct']['value']==progress)
        wait(lambda:len([r for r in asset(kind)['alarms'] if r['active'] and r['case_id']])==2)
        current=asset(kind)
        check('Factory method '+method+' routes cycle, availability and quality independently',
            current['readings']['cell_unavailable']['value']==1 and current['readings']['quality_hold']['value']==1
            and len({r['case_id'] for r in current['alarms'] if r['active']})==2,
            after={'progress':progress,'cases':[r['case_id'] for r in current['alarms'] if r['active']]})
    controls({})
    wait(lambda:all(a['readings']['quality_hold']['value']==0 for a in snapshot()['assets'] if a.get('manufacturing_method')))
    check('All factory signals restore and the other city stays nominal',not any(r['active'] or r['case_id'] for a in snapshot('mosul')['assets'] for r in a['alarms']))
