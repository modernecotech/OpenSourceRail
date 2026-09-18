"""Generated component input boundaries. These are schema checks, not native ERP runs."""
import copy


def verify(h):
    from osr_erpnext.component_catalogue import CATALOGUE,validate_inputs
    checks=[]
    def valid(fields):
        values={}
        for field in fields:
            kind=field['fieldtype'];name=field['fieldname']
            if kind=='Table':value=[valid(field['fields'])]
            elif kind in ['Float','Currency']:value=max(1,field.get('minimum',0))
            elif kind=='Select':value=field['options'].split('\n')[0]
            elif kind=='Date':value='2026-10-05'
            elif kind=='Datetime':value='2026-10-05 09:00:00'
            else:value='fixture'
            values[name]=value
        return values
    def observe(identity,component,values,accept):
        try:validate_inputs(component,values);accepted=True
        except ValueError:accepted=False
        check=dict(id='contract.'+identity,name='contract.'+identity,passed=accepted==accept,before={'expected_accept':accept},after={'accepted':accepted},level='schema-only')
        checks.append(check)
        if not check['passed']:raise AssertionError(check)
    for component,spec in CATALOGUE.items():
        baseline=valid(spec['fields'])
        observe('erp.component.'+component+'.valid',component,baseline,True)
        observe('erp.component.'+component+'.unknown-input',component,{**baseline,'unknown_input':1},False)
        def exercise(fields,path=()):
            for field in fields:
                name=field['fieldname'];kind=field['fieldtype'];location=path+(name,)
                identity='erp.input.'+component+'.'+'.'.join(str(k) if k!=0 else '[]' for k in location).replace('.[].','[].')
                def variant(label,value=None,accept=False,remove=False):
                    changed=copy.deepcopy(baseline);parent=changed
                    for key in location[:-1]:parent=parent[key]
                    if remove:parent.pop(name)
                    else:parent[name]=value
                    observe(identity+'.'+label,component,changed,accept)
                variant('missing',accept=not bool(field['reqd']),remove=True)
                variant('boolean',True)
                if kind in ['Float','Currency']:
                    minimum=field.get('minimum',0)
                    for label,value,accept in [('minimum',minimum,True),('below',minimum-1,False),('maximum',1e12,True),('above',1e12+1,False),('nan',float('nan'),False),('infinity',float('inf'),False)]:variant(label,value,accept)
                elif kind=='Table':
                    variant('empty',[]);variant('wrong-row',[1]);variant('101-rows',[valid(field['fields'])]*101)
                    exercise(field['fields'],location+(0,))
                elif kind=='Select':
                    for value in field['options'].split('\n'):variant('option-'+value,value,True)
                    variant('unknown-option','not-a-real-option')
                elif kind in ['Date','Datetime']:
                    variant('invalid-date','2026-02-30')
                    if kind=='Datetime':variant('timezone','2026-10-05T09:00:00+03:00')
                else:
                    limit=10000 if kind=='Small Text' else 140
                    variant('max-length','x'*limit,True);variant('over-length','x'*(limit+1));variant('blank',' ')
        exercise(spec['fields'])
    report=dict(schema='osr-component-contract-matrix/1',passed=True,exhaustive=False,checks=checks,scope='Every registered component input; declared required, type, numeric, length and enum boundaries only')
    h.write(h.OUTPUT/'contract-report.json',report)
    print('PASS',len(checks),'generated schema checks (not native end-to-end coverage)',flush=True)
    return report
