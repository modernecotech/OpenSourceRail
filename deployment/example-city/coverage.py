"""Evidence-backed inventory of the OSR integration boundary, not code coverage."""
import ast
from collections import Counter
from fnmatch import fnmatchcase
import hashlib
import json
from pathlib import Path
import tomllib

ERP='deployment/erpnext/apps/osr_erpnext/osr_erpnext'

def leaves(value,prefix=''):
    if isinstance(value,dict) and value:
        for key,child in value.items():yield from leaves(child,prefix+'.'+key if prefix else key)
    elif isinstance(value,list) and value and all(isinstance(v,dict) for v in value):
        seen={}
        for child in value:
            for path,example in leaves(child,prefix+'[]'):seen.setdefault(path,example)
        yield from sorted(seen.items())
    else:yield prefix,value


def inventory(root):
    from osr_erpnext.component_catalogue import CATALOGUE
    rows={}
    def add(identity,source,kind,**details):
        if identity in rows:raise ValueError('Duplicate inventory ID: '+identity)
        rows[identity]=dict(id=identity,source=source,kind=kind,**details)
    for name,component in CATALOGUE.items():
        add('erp.component.'+name,ERP+'/component_catalogue.py','function',label=component['label'])
        def fields(specs,prefix):
            for field in specs:
                identity=prefix+'.'+field['fieldname']
                add(identity,ERP+'/component_catalogue.py','input',type=field['fieldtype'],required=bool(field['reqd']),
                    options=field['options'].split('\n') if field['fieldtype']=='Select' else [],minimum=field.get('minimum'))
                if field['fieldtype']=='Table':fields(field['fields'],identity+'[]')
        fields(component['fields'],'erp.input.'+name)
    for path in sorted((root/ERP).glob('*.py')):
        for node in ast.parse(path.read_text()).body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and any('frappe.whitelist' in ast.unparse(d) for d in node.decorator_list):
                add('erp.api.'+path.stem+'.'+node.name,path.relative_to(root).as_posix(),'function',arguments=[a.arg for a in node.args.args])
    for prefix,relative in [('planning','deployment/erpnext/config/generic.toml'),('supervision','deployment/supervision/config/generic.json'),('components.profile','deployment/erpnext/config/components.json')]:
        path=root/relative;value=tomllib.loads(path.read_text()) if path.suffix=='.toml' else json.loads(path.read_text())
        if prefix=='supervision':
            for template in value['templates'].values():
                for measure in template['measurements'].values():measure.setdefault('scale',1);measure.setdefault('offset',0)
                for alarm in template.get('alarms',[]):alarm.setdefault('priority','medium')
        for name,default in leaves(value):add(prefix+'.'+name,relative,'setting',default=default)
    for prefix,relative in [('gateway','services/integration/osr_integration/server.py'),('workbench','tools/automation/workbench-server.py'),('ops','tools/automation/ops-core-server.py')]:
        tree=ast.parse((root/relative).read_text());found=set()
        for method in ast.walk(tree):
            if not isinstance(method,ast.FunctionDef) or not method.name.startswith('do_'):continue
            for node in ast.walk(method):
                if not isinstance(node,(ast.Compare,ast.Call)):continue
                if isinstance(node,ast.Call) and not (isinstance(node.func,ast.Attribute) and node.func.attr in {'startswith','fullmatch','match'}):continue
                candidates=[n.value for n in ast.walk(node) if isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.startswith('/')]
                for path in candidates:
                    if prefix!='gateway' and not path.startswith('/api/'):continue
                    found.add((method.name[3:],path))
        for verb,path in sorted(found):add(prefix+'.'+verb+'.'+path,relative,'route')
    for prefix,relative in [('fuxa','services/integration/osr_integration/fuxa.py'),('engineering','services/integration/osr_integration/engineering.py')]:
        for node in ast.parse((root/relative).read_text()).body:
            if isinstance(node,ast.FunctionDef) and not node.name.startswith('_'):
                add(prefix+'.'+node.name,relative,'function',arguments=[a.arg for a in node.args.args+node.args.kwonlyargs])
    relative='tools/automation/workbench-server.py'
    for node in ast.walk(ast.parse((root/relative).read_text())):
        if not isinstance(node,ast.Call) or not node.args or not isinstance(node.args[0],ast.Constant) or not isinstance(node.args[0].value,str):continue
        name=node.args[0].value
        if isinstance(node.func,ast.Attribute) and node.func.attr=='add_argument':add('workbench.setting.'+name,relative,'setting')
        elif ast.unparse(node.func)=='os.environ.get' and name.startswith('OSR_'):add('workbench.setting.'+name,relative,'setting')
    controls=['disconnected','cooling_fault','local_remote_disabled','station_fault','battery_trip','aux_fault','cbm_service','points_detection_fault','crossing_motor_fault','faregate_denial',
              'factory_method','factory_cell_unavailable','factory_process_excursion','factory_cycle_progress_pct']
    for name in controls:add('controller.'+name,'tools/automation/supervision-simulator.py' if not name.startswith('factory_') else 'services/integration/osr_integration/manufacturing.py','setting')
    workflows={
        'payments':'Partial supplier payment, settlement, cancellation and ledger balance',
        'payroll':'Employee attendance, payroll calculation, posting and payment',
        'tax':'Tax configuration, calculation, statutory filing and correction',
        'capitalization':'Manufactured serial to capital Asset and depreciation',
        'replenishment-scheduler':'Stock threshold to scheduled native purchase request',
        'budget-enforcement':'Submitted budget to blocked/warned overspend transaction',
        'assignment-execution':'Enabled rule to actual task assignment and reassignment',
        'training-competence':'Training events, attendance, assessment and competence decision',
        'service-sla':'Working calendar, response deadline and SLA escalation',
        'engineering-desktop':'Edit FreeCAD/Bonsai/QGIS and propagate regenerated outputs to ERP and controllers',
        'load':'Simultaneous whole-city telemetry, operators and FUXA displays',
        'backup-restore':'Restore ERP database, files, gateway and FUXA into a fresh deployment',
        'hardware':'Physical controller bindings, calibration, permissives and independently accepted site tests',
        'multi-city-isolation':'Independent planning, ERP records, gateway packages and UI city context',
        'disposition':'Seven revision-disposition decisions and independent native outcome checks',
        'railway-handoff':'City Studio revision to simulator, OCC replay and linked OSR work',
    }
    for name,label in workflows.items():add('workflow.'+name,'deployment/example-city/coverage-plan.json','workflow',label=label)
    return sorted(rows.values(),key=lambda row:row['id'])


def signature(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def assess(rows,plan,reports):
    identities={row['id'] for row in rows};reviewed=set(plan['reviewed_ids'])
    drift={'added':sorted(identities-reviewed),'removed':sorted(reviewed-identities),
        'changed':sorted(row['id'] for row in rows if row['id'] in reviewed and signature(row)!=plan.get('reviewed_contracts',{}).get(row['id']))}
    unused=[rule['pattern'] for rule in plan['rules'] if not any(fnmatchcase(i,rule['pattern']) for i in identities)]
    result=[]
    for row in rows:
        rules=[r for r in plan['rules'] if fnmatchcase(row['id'],r['pattern'])]
        rule=rules[-1] if rules else {}
        observations=[]
        for selector in rule.get('evidence',[]):
            report=reports.get(selector['report'],{})
            if report.get('passed') is not True:continue
            for check in report.get('checks',[]):
                identity=check.get('id',check.get('name',''))
                if check.get('passed') is True and fnmatchcase(identity,selector['check']):
                    observations.append(dict(report=selector['report'],check=identity,level=check.get('level','base-scenario')))
        result.append({**row,'status':rule.get('status','partial') if observations else 'gap','evidence':observations,
            'remaining':rule.get('remaining','No mapped executed scenario for this inventory entry; add explicit boundary, permission and interaction checks.')})
    counts=dict(Counter(r['status'] for r in result))
    return dict(schema='osr-coverage-register/1',inventory_consistent=not any(drift.values()) and not unused,
        exhaustive=False,scope=plan['scope'],counts=counts,drift=drift,unused_rules=unused,rows=result)


def markdown(data):
    lines=['# Integration coverage register','',data['scope'],'',
        '**This is a coverage register, not a claim of exhaustive testing.** Each source-discovered entry is tracked even when it has no passing scenario. New entries fail the inventory review check until classified. Evidence requires a completed passing report; individual successes from a failed run are not credited.','',
        'Status: `scenario` means the function was exercised; `varied` means named values were changed and checked; `partial` means only part of the behavior is demonstrated; `gap` means no qualifying evidence. None means all combinations are covered.','',
        'Native ERP expansion checks run real hooks and ledger posting inside a rolled-back transaction. The live telemetry matrix pauses the example simulator and includes explicitly labelled controller-result fixtures.','',
        'Counts: '+', '.join(f'**{key}: {value}**' for key,value in sorted(data['counts'].items()))+'. Inventory consistent: **'+str(data['inventory_consistent']).lower()+'**.','',
        '## Remaining workflow gaps','', '| Workflow | Status | Next acceptance requirement |','|---|---|---|']
    for row in data['rows']:
        if row['kind']=='workflow':lines.append(f"| {row.get('label',row['id'])} | {row['status']} | {row['remaining']} |")
    lines+=['','## Function and setting inventory','', '| Entry | Status | Evidence | Remaining coverage |','|---|---|---|---|']
    for row in data['rows']:
        evidence='; '.join(dict.fromkeys(f"{e['report']}: {e['check']}" for e in row['evidence'][:3]))
        if len(row['evidence'])>3:evidence+=f"; +{len(row['evidence'])-3} observations (JSON)"
        clean=lambda s:str(s).replace('|','\\|').replace('\n',' ')
        lines.append('| '+' | '.join([f"`{row['id']}`",row['status'],clean(evidence or '—'),clean(row['remaining'])])+' |')
    return '\n'.join(lines)+'\n'


def generate(h):
    plan=json.loads((h.ROOT/'deployment/example-city/coverage-plan.json').read_text())
    reports={}
    for name,path in [('base','report.json'),('expansion','expansion-report.json'),('contracts','contract-report.json')]:
        target=h.OUTPUT/path
        if target.exists():reports[name]=json.loads(target.read_text())
    result=assess(inventory(h.ROOT),plan,reports)
    result['source_sha256']={p:hashlib.sha256((h.ROOT/p).read_bytes()).hexdigest() for p in sorted({r['source'] for r in result['rows']})}
    h.write(h.OUTPUT/'coverage.json',result);h.write(h.OUTPUT/'coverage.md',markdown(result))
    print(json.dumps(dict(inventory_entries=len(result['rows']),counts=result['counts'],inventory_consistent=result['inventory_consistent'],exhaustive=False)))
    if not result['inventory_consistent']:raise RuntimeError('Coverage inventory changed or a rule no longer matches; review coverage-plan.json')
    return result
