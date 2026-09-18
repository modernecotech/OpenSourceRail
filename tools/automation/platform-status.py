#!/usr/bin/env python3
"""Generate a single scoped status view from recorded CI and repository registers.

CI observations are explicitly historical, never inferred to qualify a newer commit.
"""
import argparse
from collections import Counter
import hashlib
from html import escape
import json
from pathlib import Path
import re
import tomllib

ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'docs/operating/status'


def build(root, evidence):
    workflows={}
    for row in sorted(evidence['workflows'],key=lambda r:(r['createdAt'],r['databaseId']),reverse=True):
        if row['workflowName'] in {'ci','kani','integrated-stack','example-city'}:
            workflows.setdefault(row['workflowName'],row)
    coverage=root/'deployment/example-city/coverage-register.md'
    counts=Counter(re.findall(r'^\| `[^`]+` \| (scenario|varied|partial|gap) \|',coverage.read_text(),re.M))
    deployment=json.loads((root/'engineering/analysis/deployment-summary.json').read_text())
    analyses=tomllib.loads((root/'engineering/analysis/analysis-register.toml').read_text())
    maturity=Counter(row['status'] for row in analyses['analysis'])
    paths=['deployment/example-city/coverage-register.md','engineering/analysis/deployment-summary.json',
           'engineering/analysis/analysis-register.toml']
    return dict(schema='osr-platform-status/1',
        scope='Recorded software checks, generated simulation candidates and canonical deployment registers have distinct scopes. No platform-wide acceptance is inferred.',
        workflows=list(workflows.values()),catalogue=evidence['catalogue'],
        catalogue_report_sha256=evidence['catalogue_report_sha256'],
        integration=dict(entries=sum(counts.values()),counts=dict(counts),exhaustive=False),
        canonical=dict(cities=deployment['city_count'],open_gates=deployment['open_gates_by_city_count']),
        analyses=dict(total=sum(maturity.values()),maturity=dict(maturity)),
        source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
        independent_platform_acceptance=False)


def render(data):
    def table(headers,rows):
        return '<table><thead><tr>'+''.join('<th>'+escape(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenSourceRail verification and acceptance status</title>
<style>body{font:16px/1.55 system-ui,sans-serif;max-width:1100px;margin:36px auto;padding:0 24px;color:#20333d;background:#f4f7f8}h1,h2{color:#12545c}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;padding:9px;border-bottom:1px solid #cbd8dc;vertical-align:top}th{background:#dfecef}section{margin:32px 0}code{overflow-wrap:anywhere}.notice{border-left:5px solid #ad6620;padding:14px;background:#fff5e6}a{color:#126575}</style>
<h1>Verification and acceptance status</h1>
<p class="notice">This is a generated record, not live CI. Results qualify only their stated commit and scope. Railway operating release and independent platform acceptance remain open.</p>
'''
    html+='<p>'+escape(data['scope'])+'</p><section><h2>Software checks</h2>'
    html+=table(['Workflow','Commit','Status','Observed run'],[(r['workflowName'],r['headSha'][:12],r['conclusion'] or r['status'],r['databaseId']) for r in data['workflows']])
    html+='<p>'+ ' · '.join('<a href="'+escape(r['url'],quote=True)+'">'+escape(r['workflowName'])+' run</a>' for r in data['workflows'])+'</p>'
    html+='<p>A later candidate needs new exact-commit checks. Successful CI does not provide independent safety acceptance.</p></section>'
    cat=data['catalogue']
    html+='<section><h2>City simulation and canonical deployment</h2>'
    html+=table(['Evidence','Scope','Result','Acceptance'],[
        ('Generated catalogue',f"{cat['selected']} candidates at {cat['commit'][:12]}",f"{cat['passed']} passed; {cat['failed']} failed; resilience tested: {cat['resilience_tested']}",'No canonical promotion or operating acceptance'),
        ('Canonical city registers',f"{data['canonical']['cities']} cities",'Outstanding gates listed below','Per-city reviewed evidence required')])
    html+=table(['Open canonical gate','Cities'],sorted(data['canonical']['open_gates'].items()))+'</section>'
    html+='<section><h2>Integration coverage</h2><p>Inventory entries describe tested scope; they are not code-coverage percentages or all possible settings.</p>'
    html+=table(['Evidence level','Entries'],sorted(data['integration']['counts'].items()))+'</section>'
    html+='<section><h2>Engineering analysis maturity</h2>'
    html+=table(['Maturity','Analyses'],[(name,data['analyses']['maturity'].get(name,0)) for name in ['planned','screening','calibrated','independently-checked','accepted']])+'</section>'
    html+='<p><a href="../review-follow-through.md">Review and remaining work</a> · <a href="../../../deployment/example-city/coverage-register.md">Coverage register</a> · <a href="status.json">Data and register hashes</a></p></html>\n'
    return html


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,default=DEFAULT/'evidence.json')
    parser.add_argument('--output',type=Path,default=DEFAULT)
    args=parser.parse_args();evidence=json.loads(args.evidence.read_text())
    if evidence.get('schema')!='osr-status-observations/1':raise ValueError('Unknown observation schema')
    result=build(ROOT,evidence)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'status.json').write_text(json.dumps(result,indent=2)+'\n')
    (args.output/'index.html').write_text(render(result))
    print('Generated',args.output)


if __name__=='__main__':main()
