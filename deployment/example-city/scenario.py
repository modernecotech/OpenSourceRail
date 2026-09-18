"""One connected city lifecycle, with before/after and negative configuration checks."""
import copy
from datetime import datetime, timezone
import json
import os
import subprocess
import signal
import time
from urllib.error import HTTPError
from urllib.parse import urlencode


def run(h):
    from osr_integration.config import digest
    from osr_integration.fuxa import project, deployment_review, validate_deployment_review
    from osr_integration.engineering import package as engineering_package, execution_proposal, ifc_overlay
    setup=json.loads((h.OUTPUT/'setup.json').read_text())
    credentials=json.loads((h.PRIVATE/'integration.json').read_text())
    principals={p['role']:p for p in credentials['principals'] if p['subject']!='samawah-only'}
    gateway='http://127.0.0.1:8192';workbench='http://127.0.0.1:8190'
    results=[];started=datetime.now(timezone.utc).isoformat();processes=[]
    run_id=datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    if (h.OUTPUT/'run-started.json').exists():raise RuntimeError('This example already ran; use example-city reset, then setup and run for a clean repeat')
    h.write(h.OUTPUT/'run-started.json',dict(run=run_id,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.ROOT,text=True).strip(),clean_source=not bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=h.ROOT,text=True).strip())))
    def save(passed=None,error=None):
        report=dict(schema='osr-city-e2e/1',city='samawah',environment='simulation',started_at=started,
            finished_at=datetime.now(timezone.utc).isoformat() if passed is not None else None,passed=passed,error=error,checks=results,
            coverage={'erp':'full city planning baseline','live':'one station, one vehicle, one plant and existing child points',
                'control_city':'mosul','physical_acceptance':False},ports=h.PORTS)
        h.write(h.OUTPUT/'report.json',report)
        renderer=h.module('example_report','deployment/example-city/report.py')
        h.write(h.OUTPUT/'report.html',renderer.render(report,[p.name for p in sorted(h.OUTPUT.glob('workbench-*.png'))]))
    def check(name,condition,before=None,after=None):
        results.append(dict(name=name,passed=bool(condition),before=before,after=after));save()
        print(('PASS ' if condition else 'FAIL ')+name,flush=True)
        if not condition:raise AssertionError(name)
    def api(path,data=None,role='viewer',query=''):
        return h.request_json(gateway+path+query,data,{'Authorization':'Bearer '+principals[role]['token']})
    def reject(name,path,data,role='engineer'):
        try:
            result=api(path,data,role)
            check(name,path=='/commands' and result.get('state')=='rejected',after=result)
        except HTTPError as error:check(name,error.code in [400,403],after={'http_status':error.code})
    def snapshot(city='samawah'):return api('/snapshot',query='?'+urlencode(dict(city=city,environment='simulation')))
    def asset(kind='charger',city='samawah'):
        return next(a for a in snapshot(city)['assets'] if a['equipment_type']==kind and a['configuration_status']=='active')
    def wait(predicate,timeout=75):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            result=predicate()
            if result:return result
            time.sleep(1)
        raise AssertionError('Timed out waiting for a downstream effect')
    def resign(p):p.pop('sha256',None);p['sha256']=digest(p);return p
    accepted={}
    def apply(p):
        scope=p['city'];old=accepted.get(scope)
        if old:
            review=api('/packages/preview',dict(package=p),role='engineer')
            result=api('/packages',dict(package=p,expected=old['sha256'],review_sha256=review['sha256']),role='engineer')
        else:result=api('/packages',dict(package=p),role='engineer')
        accepted[scope]=copy.deepcopy(p)
        h.write(h.OUTPUT/'supervision'/scope/'simulation/package.json',p)
        return result
    def launch(name,args,env=None):
        stream=(h.OUTPUT/(name+'.log')).open('a')
        proc=subprocess.Popen(args,cwd=h.ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
        processes.append((name,proc,stream));return proc
    def controls(value):h.write(h.PRIVATE/'controls.json',value,True)
    def export():
        data=h.backend('snapshot');h.write(h.PRIVATE/'operating-twins.json',data,True);return data
    def pulse(a,name,value,unit=None,quality='valid',sequence=None,when=None):
        return dict(city='samawah',environment='simulation',asset_id=a['asset_id'],measurement=name,source_id='simulator',
            sequence=sequence or time.time_ns(),source_timestamp=when or datetime.now(timezone.utc).isoformat(),
            unit=unit or a['measurements'][name]['unit'],quality=quality,value=value)
    cfg=json.loads((h.PRIVATE/'fuxa.json').read_text())
    def fuxa(path,body=None,role='admin'):
        token=h.request_json('http://127.0.0.1:1981/api/signin',dict(username=role,password=cfg[role+'_password']))['data']['token']
        return h.request_json('http://127.0.0.1:1981'+path,body,{'x-access-token':token})
    try:
        sup=h.module('example_supervision_runtime','tools/automation/supervision.py')
        network=h.module('example_network','deployment/example-city/network.py').verify(h,sup,setup['company'],setup['projects']['samawah'])
        check('Complete city equipment contracts reach the native evaluator and historian',network['passed'],after=network)
        # Rebuild the real geometry/GIS evidence manifest from tracked source artifacts.
        manifest=json.loads((h.ROOT/'deployment/example-city/engineering.json').read_text())
        engineering=engineering_package(h.ROOT,manifest)
        h.write(h.OUTPUT/'supervision/samawah/engineering.json',engineering)
        check('CAD, IFC and GIS artifacts reopen with exact content hashes',all((h.ROOT/r['path']).is_file() for r in engineering['artifacts']),after=[dict(path=r['path'],sha256=r['sha256']) for r in engineering['artifacts']])
        state=h.backend('seed',dict(project=setup['projects']['samawah'],run=run_id,raw_per_unit=2,rate=10))
        mapping=dict(engineering_sha256=engineering['sha256'],review_reference='example-independent-conversion-review',items=[dict(component_type_id='station-charger',erp_item_code=state['item'],production_bom=state['bom'],uom='Nos',conversion_rule='2 cooling modules per example charger',inspection_reference='example-cooling-inspection',drawing_reference=engineering['artifacts'][0]['sha256'])])
        proposal=execution_proposal(engineering,mapping)
        mapped=h.backend('mapping',dict(project=state['project'],proposal=proposal));h.write(h.OUTPUT/'execution-proposal.json',proposal)
        check('Exact engineering revision maps to native Item and production BOM',bool(mapped['mappings']),after=mapped)
        for city in ['samawah','mosul']:
            p=sup.city_package(city,first_site=True,first_vehicle=True,first_plant=True,
                polling_scope='site' if city=='mosul' else 'asset')
            for a in p['equipment']:
                a['company_id']=state['company'];a['erp_project']=setup['projects'][city]
                if city=='samawah' and a['equipment_type']=='charger':a['erp_asset_id']=state['asset'];a['erp_item_code']=state['item']
            apply(resign(p))
            h.write(h.OUTPUT/'profiles'/(city+'.json'),dict(company=state['company'],erp_project=setup['projects'][city],preferred_supervision_site='SAM-ST-001' if city=='samawah' else 'MOS-ST-001'))
        scoped=next(p for p in credentials['principals'] if p['subject']=='samawah-only')
        try:
            h.request_json(gateway+'/snapshot?city=mosul&environment=simulation',headers={'Authorization':'Bearer '+scoped['token']})
            check('A city-scoped reader cannot access the control city',False)
        except HTTPError as error:check('A city-scoped reader cannot access the control city',error.code==403)
        baseline=copy.deepcopy(accepted['samawah']);control_hash=accepted['mosul']['sha256']
        check('City-specific family selects applicable factory methods',len([a for a in baseline['equipment'] if a.get('manufacturing_method')])==9 and not any(a.get('manufacturing_method') for a in accepted['mosul']['equipment']))
        ifc=next(o for r in engineering['artifacts'] for o in r.get('ifc_objects',[]) if o['entity'] not in {'IFCPROJECT','IFCSITE'})
        overlay=ifc_overlay(engineering,[dict(ifc_global_id=ifc['global_id'],asset_id='SAM-ST-001:charger',erp_asset_id=state['asset'],erp_item_code=state['item'])])
        h.write(h.OUTPUT/'ifc-overlay.json',overlay)
        check('IFC selection resolves the same physical position and ERP Asset',overlay['bindings'][0]['erp_asset_id']==state['asset'])
        # Actual planning import effects, including preserving operator edits on repeat import.
        h.copy_in(h.OUTPUT/'erp/samawah/plan.json','/tmp/example-plan.json')
        task=h.backend('task-change',dict(project=state['project'],path='/tmp/example-plan.json'))
        check('ERP reimport preserves changed task progress and status',task['reimport_preserved'],after=task)
        for name in ['components','procurement','lifecycle']:
            script=(h.ROOT/('deployment/erpnext/tests/verify-'+name+'.py')).read_text()
            h.command(h.compose('erp','exec','-T','-e','OSR_TEST_SITE='+h.SITE,'backend','env/bin/python'),'native-'+name,stdin=script)
            check('Isolated native '+name+' adapters and negative cases pass with rollback',True)
        matrix=h.module('example_matrix','deployment/example-city/matrix.py')
        matrix.planning(h,check,setup)
        buying=h.backend('procure',dict(source=state,ordered=10,received=6,rate=10))
        check('Changed ordered/received quantities reach delivery and invoice actuals',buying['outstanding_qty']==4 and buying['invoice_total']==60,before={'ordered':10,'received':6,'rate':10},after=buying)
        made=h.backend('manufacture',dict(source=state,run=run_id,planned=3,produced=2,raw_per_unit=2))
        check('BOM consumption, partial production, inspection and native serials agree',made['planned']==3 and made['produced']==2 and len(set(made['serials']))==2,after=made)
        h.write(h.OUTPUT/'native-records.json',dict(**state,**buying,**made))
        export()
        desired=project(list(accepted.values()),workbench_url='http://127.0.0.1:8190');review=deployment_review(fuxa('/api/project'),list(accepted.values()),workbench_url='http://127.0.0.1:8190')
        validate_deployment_review(fuxa('/api/project'),list(accepted.values()),review,workbench_url='http://127.0.0.1:8190')
        fuxa('/api/project',desired);h.write(h.OUTPUT/'fuxa-review.json',review)
        check('Reviewed FUXA import covers both city packages',len(desired['devices'])==sum(len({a['site_id'] for a in p['equipment']}) if p.get('fuxa_polling_scope','asset')=='site' else len(p['equipment']) for p in accepted.values()),after={'devices':len(desired['devices'])})
        controls({})
        for name,args,env in h.host_commands(fresh=True):launch(name,args,env)
        h.wait_http(workbench+'/api/workbench/services')
        wait(lambda:asset()['readings']['temperature_c']['quality']=='valid')
        check('Native Rust controller reaches the isolated city gateway',asset()['readings']['power_kw']['value']==180,after=asset()['readings']['power_kw']['value'])
        matrix.supervision(h,check,reject,api,apply,accepted,asset,snapshot,pulse,controls,wait,baseline)
        # Restore baseline before the connected lifetime; fault must reach this manufactured Asset.
        apply(copy.deepcopy(baseline));controls({})
        delivered=h.backend('transfer',dict(source=state,moves=[{'serial':made['serials'][0],'from':state['warehouse'],'to':state['installed_warehouse']}]))
        check('Produced serial moves to the installed-equipment warehouse in native stock',True,after=delivered)
        base=dict(city='samawah',environment='simulation',asset_id='SAM-ST-001:charger',engineering_revision=baseline['engineering_revision'],references=['example:'+run_id,'work-order:'+made['work_order'],'inspection:'+made['inspection'],'installation-stock:'+delivered['stock_entry']])
        for kind,role,extra in [('design-review','engineer',{}),('execution-release','reviewer',{}),('installation','engineer',{'serial':made['serials'][0]}),('commissioning-test','inspector',{'result':'pass'}),('commissioning-release','reviewer',{'test_id':run_id+'-commissioning-test'})]:
            api('/evidence',dict(base,id=run_id+'-'+kind,kind=kind,**extra),role=role)
        check('Produced serial is installed and independently simulation-commissioned',asset()['installations'][0]['serial']==made['serials'][0],after=asset()['lifecycle_state'])
        controls({'cities':{'samawah':{'cooling_fault':True}}})
        alarm=wait(lambda:next((r for r in asset()['alarms'] if r['active'] and r['case_id']),None))
        check('Controller fault creates ERP Issue for the manufactured/installed charger',bool(alarm['case_id']),after={'issue':alarm['case_id'],'occurrence':alarm['occurrences']})
        reject('Read-only user cannot acknowledge an alarm','/alarms/acknowledge',dict(city='samawah',environment='simulation',asset_id='SAM-ST-001:charger',rule='cooling',occurrence=alarm['occurrences']),role='viewer')
        api('/alarms/acknowledge',dict(city='samawah',environment='simulation',asset_id='SAM-ST-001:charger',rule='cooling',occurrence=alarm['occurrences']),role='operator')
        repaired=h.backend('repair',dict(source=state,issue=alarm['case_id'],run=run_id,parts=1,downtime=2,evidence='example:'+run_id,stock_entry=made['stock_entry']))
        check('Native repair consumes the purchased spare and keeps railway release separate',repaired['consumed']==1 and not repaired['railway_release'] and repaired['priority']=='High',after=repaired)
        controls({});wait(lambda:not next(r for r in asset()['alarms'] if r['rule']=='cooling')['active'])
        wait(lambda:next(r for r in asset()['alarms'] if r['rule']=='cooling')['erp_status']=='Closed')
        api('/evidence',dict(base,id=run_id+'-maintenance',kind='maintenance'),role='maintainer')
        exchanged=h.backend('transfer',dict(source=state,moves=[{'serial':made['serials'][0],'from':state['installed_warehouse'],'to':state['return_warehouse']},{'serial':made['serials'][1],'from':state['warehouse'],'to':state['installed_warehouse']}]))
        check('Replacement and removed serial agree with native stock locations',True,after=exchanged)
        api('/evidence',dict(base,id=run_id+'-replacement',kind='installation',serial=made['serials'][1],replaces_serial=made['serials'][0]),role='engineer')
        reject('Replacement cannot reuse the earlier commissioning test','/evidence',dict(base,id=run_id+'-wrong-release',kind='commissioning-release',test_id=run_id+'-commissioning-test'),role='reviewer')
        api('/evidence',dict(base,id=run_id+'-replacement-test',kind='commissioning-test',result='pass'),role='inspector')
        api('/evidence',dict(base,id=run_id+'-replacement-release',kind='commissioning-release',test_id=run_id+'-replacement-test'),role='reviewer')
        removed=api('/affected',query='?'+urlencode(dict(city='samawah',environment='simulation',serial=made['serials'][0])))
        check('Replacement preserves removed serial history and needs fresh independent release',removed[0]['removed'] is not None,after={'old':made['serials'][0],'new':made['serials'][1]})
        quantities=h.backend('stock-audit',dict(source=state))
        check('Native stock reconciles receipt, manufacture, repair, installation and replacement',quantities=={'raw_remaining':1,'finished_in_stores':0,'installed':1,'returned':1},after=quantities)
        check('Samawah changes do not change Mosul equipment or ERP alarm state',not any(r['active'] or r['case_id'] for a in snapshot('mosul')['assets'] for r in a['alarms']))
        export()
        # Browser checks use the actual native records and services, without mocked routes.
        h.command(['node','deployment/example-city/verify-ui.mjs'],'ui')
        browser=json.loads((h.OUTPUT/'ui-report.json').read_text())
        check('Workbench, ERP, FUXA, engineering evidence and lifecycle agree in the browser',browser['passed'],after=browser['checks'])
        matrix.embedded(check,asset,snapshot,controls,wait)
        matrix.recovery(h,check,api,asset,controls,wait,base,alarm['case_id'],apply,baseline)
        review=api('/packages/preview',dict(package=accepted['mosul']),role='viewer')
        check('Control city package remains at its exact accepted revision',review['status']=='no-change' and review['baseline_sha256']==control_hash)
        control=h.backend('control-audit',dict(project=setup['projects']['mosul']))
        count=sum(json.loads((h.OUTPUT/'erp/mosul/summary.json').read_text())['task_counts'].values())
        check('Control city native ERP tasks and transactions remain unchanged',control=={'tasks':{'Open':count},'issues':0,'work_orders':0,'stock_entries':0},after=control)
        export();controls({})
        save(True)
        h.write(h.PRIVATE/'processes.json',[dict(name=n,pid=p.pid) for n,p,_ in processes],True)
        print('PASS complete city scenario; example remains available at '+workbench,flush=True)
        processes=[] # Explicitly retain the reviewable example services.
    except BaseException as error:
        try:h.write(h.OUTPUT/'failure-snapshot.json',{city:snapshot(city) for city in ['samawah','mosul']})
        except Exception:pass  # Preserve the original failure if the gateway is unavailable.
        controls({});save(False,str(error));raise
    finally:
        for name,proc,stream in processes:
            if proc.poll() is None: os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            stream.close()
