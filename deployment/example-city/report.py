"""Standalone, escaped acceptance report; no external services or credentials."""
from html import escape
import json


def render(data, pictures):
    checks=data['checks'];passed=sum(bool(r['passed']) for r in checks)
    status='Passed' if data['passed'] is True else 'Failed' if data['passed'] is False else 'Running'
    rows=[]
    for row in checks:
        detail=json.dumps({'before':row.get('before'),'after':row.get('after')},indent=2,ensure_ascii=False)
        rows.append('<details><summary><b class="'+('good' if row['passed'] else 'bad')+'">'+('PASS' if row['passed'] else 'FAIL')+'</b> '+escape(row['name'])+'</summary><pre>'+escape(detail)+'</pre></details>')
    gallery=''.join('<a href="'+escape(name,quote=True)+'"><img alt="Example city Workbench evidence" src="'+escape(name,quote=True)+'"></a>' for name in pictures)
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Samawah integrated software acceptance</title><style>
body{font:16px/1.55 system-ui,sans-serif;max-width:1120px;margin:2rem auto;padding:0 1.2rem;color:#dae4ef;background:#101925}
a{color:#74c9ff}h1{line-height:1.2}details{padding:.65rem;background:#192637;margin:.4rem 0;border-radius:6px}summary{cursor:pointer}
.good{color:#7bddb4}.bad{color:#ff9b95}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}img{max-width:100%;border:1px solid #3b526b;margin:1rem 0}
</style><h1>Samawah integrated software acceptance</h1><p><strong>'''+status+f' · {passed}/{len(checks)} checks passed</strong></p>'+'''<p>Software simulation with selected live equipment and a separate whole-city contract sweep. Physical acceptance and whole-network real-time capacity are not asserted.</p>
<p><a href="http://127.0.0.1:8190/">Open example Workbench</a> · <a href="report.json">Machine-readable report</a> · <a href="full-network/report.json">Whole-city contracts and retention</a> · <a href="expansion-report.html">Expanded variable checks</a> · <a href="coverage.md">Function and setting coverage register</a></p>'''+('<p class="bad">'+escape(data['error'])+'</p>' if data.get('error') else '')+''.join(rows)+gallery+'</html>\n'
