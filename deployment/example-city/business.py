"""Native business outcomes and an independent post-transaction rollback audit."""
import json
import subprocess


def verify(h):
    if json.loads((h.OUTPUT/'report.json').read_text()).get('passed') is not True:
        raise RuntimeError('Complete the base example first')
    source=json.loads((h.OUTPUT/'native-records.json').read_text())
    before=h.backend('expansion-audit',{'source':source})
    report=dict(passed=False,checks=[])
    h.write(h.OUTPUT/'business-report.json',report)
    try:
        script='INPUT = '+repr(dict(site=h.SITE,source=source))+'\n'+(h.ROOT/'deployment/example-city/business-flows.py').read_text()
        result=subprocess.run(h.compose('erp','exec','-T','backend','env/bin/python'),input=script,text=True,capture_output=True,cwd=h.ROOT)
        h.write(h.OUTPUT/'business-flows.log',result.stdout+result.stderr)
        payload=next((json.loads(line.removeprefix('OSR_BUSINESS:')) for line in result.stdout.splitlines() if line.startswith('OSR_BUSINESS:')),None)
        if payload:report.update(payload)
        after=h.backend('expansion-audit',{'source':source})
        report['checks'].append(dict(id='business.rollback',name='business.rollback',passed=before==after,before=before,after=after,level='native-erp-rollback'))
        report['passed']=result.returncode==0 and payload is not None and payload.get('passed') is True and before==after
        if not report['passed']:raise RuntimeError('Native business check failed; inspect business-flows.log')
    except BaseException as error:
        report.update(passed=False,error=str(error));raise
    finally:h.write(h.OUTPUT/'business-report.json',report)
    print('PASS native business outcomes and rollback:',len(report['checks']),'checks')
