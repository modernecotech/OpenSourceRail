"""Portable comparison Workbench generated from verified campaign membership."""
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import tarfile

from . import campaign, contracts, selection

OUTPUT = campaign.ROOT/'docs/design-engine/design-search'


def summary(value):
    """Expose engineering context without turning omitted stock into zero."""
    rows=[]
    for candidate in value['candidates']:
        results=[row for row in value['results'] if row['candidate_id']==candidate['candidate_id']]
        rows.append(dict(candidate_id=candidate['candidate_id'], label=candidate.get('label',''),
            architecture=candidate['architecture'], lineage=candidate['lineage'],
            mass=contracts.mass_properties(candidate),
            inventory=contracts.inventory_summary(candidate),
            evaluations=[{key:row[key] for key in ('evaluation_id','execution_status','numerical_status',
                'screen_status','maturity','metrics','constraints','diagnostics')} |
                dict(evaluator=row['request']['evaluator_id'],hypothesis=row['request']['hypothesis']) for row in results],
            baseline_rejections=value['integrated_baseline']['rejections'].get(candidate['candidate_id'],[])))
    return dict(campaign_id=value['campaign_id'],candidates=rows,
        next_experiment=value['next_experiment'],integrated_baseline=value['integrated_baseline'],
        confirmation_scope='Independent stock arithmetic and source integrity; domain physics is not independently confirmed.',
        twin_scope='One magnetic module coupon, one selected guidebeam span and counted per-car carrier stock; incomplete installed vehicle.',
        qualification=value['qualification'],**contracts.FLAGS)


PAGE='''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenSourceRail candidate comparison</title>
<style>body{font:17px/1.5 system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#16313d;background:#fafbf9}a{color:#006d74}h1,h2{line-height:1.2}select{font:inherit;max-width:100%;padding:.6rem}article{background:white;border:1px solid #c5d4d4;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.83rem}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:.5rem;border-bottom:1px solid #ddd}code{overflow-wrap:anywhere}.hold{background:#fff3dc;padding:1rem}svg{width:100%;max-width:460px;height:190px}</style>
<nav><a href="../../workbench/maglev/">System Workbench</a> · <a href="../../../engineering/design_search/README.md">Reproduction and contracts</a> · <a href="comparison.json.gz">Complete evidence</a></nav>
<h1>Connected engineering alternatives</h1>
<p>Simple fixed lines, affordable construction and high passenger throughput guide the comparison. Every domain uses one physical candidate identity. Unknown installed equipment remains visible.</p>
<p class="hold" id="disposition"></p><label>Inspect candidate <select id="choice"></select></label>
<article id="candidate"></article><h2>Declared selection policy</h2><pre id="policy"></pre>
<h2>Verification and scope</h2><p id="scope"></p><p>These calculations do not change physical qualification dispositions. Rejected alternatives and ancestry are retained in the complete evidence package.</p>
<script id="data" type="application/json">__DATA__</script>
<script>
const data=JSON.parse(document.getElementById('data').textContent), $=id=>document.getElementById(id);
function node(tag,text,parent){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;parent.append(n);return n;}
$('disposition').textContent='Integrated baseline: '+data.integrated_baseline.status+'. Next experiment: '+(data.next_experiment.selected_candidate_id||'none')+'. Physical acceptance: open.';
$('policy').textContent=JSON.stringify(data.next_experiment.policy,null,2);
$('scope').textContent=data.confirmation_scope+' '+data.twin_scope;
for(const c of data.candidates){const o=node('option',c.label||c.candidate_id.slice(0,16),$('choice'));o.value=c.candidate_id;}
function show(){const c=data.candidates.find(c=>c.candidate_id===$('choice').value), p=$('candidate');p.replaceChildren();
node('h2',c.label||'Candidate',p);node('code',c.candidate_id,p);
node('h3','Architecture and mass',p);node('pre',JSON.stringify({architecture:c.architecture,mass:c.mass,inventory:c.inventory},null,2),p);
node('h3','Evaluated constraints',p);const t=node('table',undefined,p),head=node('tr',undefined,t);for(const v of ['Evaluator','Execution','Numerical','Screen','Maturity'])node('th',v,head);
for(const r of c.evaluations){const tr=node('tr',undefined,t);for(const k of ['evaluator','execution_status','numerical_status','screen_status','maturity'])node('td',r[k],tr);const d=node('details',undefined,p);node('summary',r.evaluator+' — margins, assumptions and reasons',d);node('pre',JSON.stringify(r,null,2),d);}
node('h3','Why this is not an integrated baseline',p);node('pre',JSON.stringify(c.baseline_rejections,null,2),p);
node('h3','Revision and assembly consequences',p);node('pre',JSON.stringify(c.lineage,null,2),p);
node('p','Yaw bearings, slides, retention, cooling and complete removal paths require installed detail. Partial stock drawings cannot establish a complete assembly sequence or a complete cost.',p);
const a=node('a','Research twin, when compiled',p);a.href='../design-search-twins/'+c.candidate_id+'/README.md';}
$('choice').value=data.next_experiment.selected_candidate_id||data.candidates[0].candidate_id;$('choice').onchange=show;show();
</script></html>'''


def publish(campaign_id, *, state=campaign.STATE, output=OUTPUT, check=False):
    value=campaign.compare(campaign_id,state=state)
    definition=campaign.definition(campaign_id,state=state)
    view=summary(value)
    data=json.dumps(view,sort_keys=True,allow_nan=False).replace('<','\\u003c').replace('&','\\u0026')
    readme=f'''# Coordinated design research

OpenSourceRail develops simple fixed-line ferrite maglev for affordable construction, local repair and high passenger throughput. This campaign connects actual carrier stock, selected beam/span, current magnetic calculations and delivery quantities through one physical candidate definition.

Campaign `{campaign_id}` evaluated **{len(value['candidates'])} physical alternatives** in **{len(value['results'])} primary calculations**, retaining **{len(value['confirmations'])} independent arithmetic/source checks**. The next-experiment selection is `{value['next_experiment']['selected_candidate_id']}`. **Integrated baseline: {value['integrated_baseline']['status']}. Physical acceptance remains open.**

[Interactive comparison](index.html) · [Complete immutable evidence](comparison.json.gz) · [Candidate contracts and reproduction](../../../engineering/design_search/README.md)

The research twin contains one module coupon, the selected guidebeam span and counted per-car carrier stock. Installed joints, cooling, protection, complete mass distribution, correlated field maps and coupled thermal/deformation behavior remain incomplete. Arithmetic/source confirmation does not independently validate domain physics. No city defaults or qualification dispositions are changed.

The six-car Baghdad context retains 120 normal passengers per car and a 14,400 passengers/hour/direction comparison floor, requiring 180-second headway. Formation and operating changes must carry their platform, charging, fleet, evacuation and civil consequences.

```bash
./osr design campaign create campaigns/carrier-beam.toml
./osr design campaign run {campaign_id}
./osr design campaign compare {campaign_id}
./osr design campaign publish {campaign_id}
```

This publication binds evaluator sources and campaign membership. A source revision requires a new campaign; interrupted jobs resume only with matching inputs. The digital jobs complete independently of the held physical qualification programme.
'''
    files={'index.html':PAGE.replace('__DATA__',data).encode(),
        'README.md':readme.encode(), 'comparison.json.gz':gzip.compress(contracts.encoded(value),mtime=0),
        'campaign.json':contracts.encoded(definition)}
    # Keep worker inputs, results, logs and receipts available after a fresh clone.
    buffer=io.BytesIO()
    state=Path(state);folder=state/'campaigns'/campaign_id
    retained={path.relative_to(state).as_posix():path for path in folder.rglob('*')
              if path.is_file() and path.name!='runner.lock'}
    if folder.is_dir():
        # Exact caches may refer to a sealed worker in an earlier campaign.
        # Retain that package too, so the publication survives a fresh clone.
        for row in value['results']+value['confirmations']:
            receipt=state/'cache-receipts'/(row['evaluation_id']+'.json')
            record=json.loads(receipt.read_bytes());retained[receipt.relative_to(state).as_posix()]=receipt
            attempt=campaign._relative_attempt(state,record['attempt_path'])
            retained.update({path.relative_to(state).as_posix():path for path in attempt.rglob('*') if path.is_file()})
        records=[('selection',value[name]['selection_id']) for name in ('next_experiment','integrated_baseline')]
        for row in value['candidates']:records.extend([('candidate',row['candidate_id']),('candidate-context',contracts.identity(row))])
        for row in value['results']+value['confirmations']:records.extend([('evaluation',row['evaluation_id']),('evaluation-request',row['evaluation_id'])])
        for kind,key in records:
            path=state/'registry'/kind/(key+'.json');retained[path.relative_to(state).as_posix()]=path
    with tarfile.open(fileobj=buffer,mode='w') as archive:
        for name,path in sorted(retained.items()):
            if path.is_symlink():raise ValueError('ordinary campaign evidence files required')
            raw=path.read_bytes();info=tarfile.TarInfo(name)
            info.size=len(raw);info.mode=0o644;info.mtime=0;archive.addfile(info,io.BytesIO(raw))
    files['run-evidence.tar.gz']=gzip.compress(buffer.getvalue(),mtime=0)
    before=definition['source_sha256']
    receipt=dict(schema='osr-design-comparison-publication/1',campaign_id=campaign_id,
        source_sha256=before,files_sha256={k:sha256(v).hexdigest() for k,v in files.items()},**contracts.FLAGS)
    files['manifest.json']=contracts.encoded(receipt)
    if campaign.source_epoch()!=before:raise ValueError('campaign sources changed during publication')
    output=Path(output)
    if check:
        for name,raw in files.items():
            if not (output/name).is_file() or (output/name).read_bytes()!=raw:raise ValueError('stale candidate comparison: '+name)
    else:
        for name,raw in files.items():
            destination=output/name;destination.parent.mkdir(parents=True,exist_ok=True)
            temporary=destination.with_suffix(destination.suffix+'.pending');temporary.write_bytes(raw);temporary.replace(destination)
    return dict(campaign_id=campaign_id,output=str(output),candidates=len(value['candidates']),integrated_baseline=value['integrated_baseline']['status'])


def verify(output=OUTPUT):
    """Check published evidence without relying on ignored local run state."""
    output=Path(output);receipt=json.loads((output/'manifest.json').read_bytes())
    if receipt['source_sha256']!=campaign.source_epoch():raise ValueError('candidate comparison sources changed; run a new campaign')
    for name,digest in receipt['files_sha256'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or sha256((output/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('candidate comparison payload differs: '+name)
    value=json.loads(gzip.decompress((output/'comparison.json.gz').read_bytes()))
    definition=json.loads((output/'campaign.json').read_bytes())
    if (definition.get('source_sha256')!=receipt['source_sha256'] or definition.get('campaign_id')!=receipt['campaign_id']
            or contracts.identity({key:item for key,item in definition.items() if key!='campaign_id'})!=receipt['campaign_id']):
        raise ValueError('published campaign definition or source binding differs')
    if value['campaign_id']!=receipt['campaign_id']:raise ValueError('comparison campaign differs')
    if any(receipt.get(key) is not False or value.get(key) is not False for key in contracts.FLAGS):
        raise ValueError('research publication cannot assert physical or engineering acceptance')
    for row in value['candidates']:contracts.validate_candidate(row)
    for row in value['results']+value['confirmations']:
        contracts.validate_result(row)
        if any(receipt['source_sha256'].get(name)!=digest for name,digest in row['request']['evaluator_sources'].items()):
            raise ValueError('published evaluator sources differ from campaign')
    for name,rows,purpose in [('next_experiment',value['results'],'next-experiment'),
                             ('integrated_baseline',value['results']+value['confirmations'],'integrated-baseline')]:
        if selection.select(value['candidates'],rows,purpose=purpose,policy=value[name]['policy'])!=value[name]:
            raise ValueError('published selection does not reproduce')
    return dict(campaign_id=value['campaign_id'],candidates=len(value['candidates']),current=True,**contracts.FLAGS)


def build_default():
    created=campaign.create(campaign.ROOT/'campaigns/carrier-beam.toml')
    campaign_id=created['campaign_id']
    completed=campaign.run(campaign_id)
    if completed['state']!='completed':raise ValueError('candidate campaign held: '+completed['state'])
    publish(campaign_id)
    return verify()
