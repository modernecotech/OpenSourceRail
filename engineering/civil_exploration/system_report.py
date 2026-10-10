"""Reviewable whole-system choices, Pareto plots and standalone exploration UI."""
from __future__ import annotations
from collections import Counter
import csv
import html
import json
from pathlib import Path

from osr_mech.civil.exploration import geometry,foundation_geometry
from .contracts import ROOT,HERE,encoded,load,sha

COLOURS={'concrete':'#91a8b6','frp':'#e49432','steel':'#416dac','uhpc':'#7957a4'}


def label(choice):
    fibre=(' + '+choice['fibre_material'].upper()) if choice.get('fibre_material') and (choice['beam'] in ('hybrid-shell','frp-composite-I') or choice['pier']=='double-skin-hybrid') else ''
    return f"{choice['beam']} {choice['span_m']:g} m / {choice['material']}{fibre} / {choice['pier']} / {choice['foundation']} / {choice['beam_method']} / {choice['connection_scheme']}"


def diagram(config):
    from .systems import engineering_seeds
    parts=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 730">',
           '<title>Parametric beam, pier and foundation research choices</title>',
           '<rect width="1100" height="730" fill="#f6f8fa"/>',
           '<text x="20" y="25" font-family="sans-serif" font-size="18" fill="#16364d">Complete viaduct choices — research geometry, qualification open</text>']
    def text(x,y,value,size=11):parts.append(f'<text x="{x:g}" y="{y:g}" text-anchor="middle" font-family="sans-serif" font-size="{size}" fill="#173549">{html.escape(value)}</text>')
    def section(s,xc,baseline,scale):
        roles=s.get('material_roles',['concrete']*len(s['regions']))
        for r,role in zip(s['regions'],roles):
            parts.append(f'<rect x="{xc+(r["y_m"]-r["width_m"]/2)*scale:.5f}" y="{baseline-(r["z_m"]+r["height_m"]/2)*scale:.5f}" width="{r["width_m"]*scale:.5f}" height="{r["height_m"]*scale:.5f}" fill="{COLOURS[role]}" stroke="#284657" stroke-width="0.6"/>')
    for i,choice in enumerate(engineering_seeds(config)[:len(config['beams'])]):
        x=110+(i%5)*220;y=55+(i//5)*150
        d=dict(deck=dict(family=choice['beam'],span_m=20.,parameters=choice['beam_parameters']),pier=dict(family='solid',height_m=8.,parameters={}))
        s=geometry(d)['deck'][1];text(x,y,choice['beam'],12);section(s,x,y+90,48.)
        text(x,y+108,f"A {s['area_m2']:.3f} m² · Iy {s['inertia_y_m4']:.3f} m⁴",10)
    text(550,365,'Pier cross sections (mid-height); taper and segment joints require separate qualification',12)
    for i,pier in enumerate(config['piers']):
        parameters={k:(a+b)/2 for k,(a,b) in pier['bounds'].items()}
        d=dict(deck=dict(family='pi',span_m=20.,parameters={}),pier=dict(family=pier['id'],height_m=8.,parameters=parameters))
        s=geometry(d)['pier'][4];x=(i+.5)*1100/len(config['piers']);section(s,x,492.,40.)
        text(x,388,pier['id'],10);text(x,508,f"A {s['area_m2']:.3f} m²",10)
    text(550,537,'Foundation plans; illustrative sizes, actual ground selection remains open',12)
    for i,option in enumerate(config['foundations']):
        f=foundation_geometry(option['parameters']);L,W,_=f['cap_dimensions_m'];x=(i+.5)*1100/len(config['foundations']);y=602.;scale=72/max(L,W)
        parts.append(f'<rect x="{x-L*scale/2:g}" y="{y-W*scale/2:g}" width="{L*scale:g}" height="{W*scale:g}" fill="#dfe7ed" stroke="#456274"/>')
        for p in f['piles']:
            px=x+p['centre_xy_m'][0]*scale;py=y+p['centre_xy_m'][1]*scale;d=p['diameter_m']*scale
            if p.get('shape')=='square':parts.append(f'<rect x="{px-d/2:g}" y="{py-d/2:g}" width="{d:g}" height="{d:g}" fill="#91a8b6" stroke="#416dac"/>')
            else:
                parts.append(f'<circle cx="{px:g}" cy="{py:g}" r="{d/2:g}" fill="#91a8b6" stroke="#416dac"/>')
                if p.get('inner_diameter_m'):parts.append(f'<circle cx="{px:g}" cy="{py:g}" r="{p["inner_diameter_m"]*scale/2:g}" fill="#f6f8fa"/>')
        text(x,553,option['id'],9);text(x,654,f"{L:g} × {W:g} m; {len(f['piles'])} piles",9)
    for i,(role,colour) in enumerate(COLOURS.items()):
        x=100+i*255;parts.append(f'<rect x="{x:g}" y="689" width="14" height="14" fill="{colour}"/>');text(x+100,701,role,12)
    parts.append('</svg>');return '\n'.join(parts)+'\n'


def compact_rows(rows):
    selected=[]
    for r in rows:
        item={k:r[k] for k in ('package_id','choice','status','violation')}
        if r['status']=='completed':
            q=r['quantities'];c=r['construction']
            item.update(candidate_id=r['candidate_id'],installed_mass_kg=q['installed_study_mass_kg'],
                        max_lift_mass_kg=c['maximum_lift_mass_kg'],service_beam_mass_kg=q['fabricated_beam_mass_kg'],
                        beam_units=c['beam_units'],pier_units=c['pier_units'],cap_units=c['cap_units'],
                        concrete_m3=q['concrete_m3'],deck_material_volumes_m3=q['deck_material_volumes_m3'],
                        pier_material_volumes_m3=q['pier_material_volumes_m3'],pile_length_m=q['pile_length_m'],
                        scenarios=r['scenarios'],actual_installed_cost_usd=r['actual_installed_cost_usd'],
                        actual_unpriced_scope=r['actual_unpriced_scope'],research_violations=r['research_violations'],
                        worst_relative_deflection_m=max(p['response']['relative_deck_deflection_m'] for p in r['native_responses']),
                        worst_foundation_settlement_m=max(p['response']['foundation_settlement_m'] for p in r['native_responses']))
        else:item['error']=r.get('error')
        selected.append(item)
    return selected


def pareto_plot(report,rows):
    sid=next(iter(report['winners']));good=[r for r in rows if r['status']=='completed' and r['violation']==0.]
    if not good:return '<svg xmlns="http://www.w3.org/2000/svg"><text y="20">No provisional passes</text></svg>\n'
    xs=[r['scenarios'][sid]['installed_cost_usd']/1e6 for r in good];ys=[r['quantities']['installed_study_mass_kg']/1e6 for r in good]
    xmin,xmax=min(xs)*.95,max(xs)*1.05;ymin,ymax=min(ys)*.95,max(ys)*1.05
    pareto=set(report['screening_winners'][sid]['pareto_ids']);confirmed=set(report['winners'][sid]['pareto_ids'])
    svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 510">','<rect width="800" height="510" fill="white"/>',
         '<text x="400" y="27" text-anchor="middle" font-family="sans-serif" font-size="17">Cost–mass–time tradeoffs: synthetic scenario, research constraints</text>',
         '<path d="M80 50V440H760" fill="none" stroke="#38556a"/>']
    for i in range(6):
        x=80+i*680/5;y=440-i*390/5
        svg += [f'<text x="{x:g}" y="462" text-anchor="middle" font-family="sans-serif" font-size="11">{xmin+i*(xmax-xmin)/5:.2f}</text>',
                f'<text x="65" y="{y:g}" text-anchor="end" font-family="sans-serif" font-size="11">{ymin+i*(ymax-ymin)/5:.2f}</text>']
    days=[r['scenarios'][sid]['working_days'] for r in good];dmin,dmax=min(days),max(days)
    for r,x,y,d in zip(good,xs,ys,days):
        hue=210-170*(d-dmin)/max(1,dmax-dmin);stroke='#152938' if r['package_id'] in pareto else 'none';radius=5. if r['package_id'] in confirmed else 3.
        svg.append(f'<circle cx="{80+680*(x-xmin)/(xmax-xmin):g}" cy="{440-390*(y-ymin)/(ymax-ymin):g}" r="{radius:g}" fill="hsl({hue:g},65%,50%)" stroke="{stroke}"><title>{html.escape(label(r["choice"]))} · ${x*1e6:,.0f} · {y*1000:,.0f} t · {d:g} working days</title></circle>')
    svg += ['<text x="415" y="492" text-anchor="middle" font-family="sans-serif" font-size="12">Installed scenario cost (million USD; no supplier quotes)</text>',
            '<text transform="translate(18 265) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="12">Installed study mass (thousand tonnes)</text>',
            f'<text x="95" y="69" font-family="sans-serif" font-size="11">Blue → orange: {dmin:g} → {dmax:g} working days; outlined = reduced Pareto; large = confirmed shortlist Pareto</text>','</svg>']
    return '\n'.join(svg)+'\n'


def markdown(report,rows,config):
    by_id={r['package_id']:r for r in rows};counts=Counter(r['choice']['beam'] for r in rows if r['status']=='completed')
    lines=['# Complete viaduct system exploration','',
           f"Baghdad target. Common scope: **{report['scope']['route_length_m']:g} m, double track**. {report['distinct_packages']} distinct packages, {report['evaluated_attempts']} evaluation attempts, {report['provisional_passes']} provisional screening passes.",
           '', '**Actual supplier costs are unknown. No engineering-qualified cheapest design or global optimum is claimed.**',
           'The static load is the retained infrastructure full-train allowance spread over the retained train length. It is not an actual axle pattern or dynamic envelope.',
           '', f"Winner basis: {report['winner_basis']}. Price and productivity scenarios are synthetic assumptions; masses follow canonical material regions and full package quantities.",
           'Material strength/prestress/fatigue capacity remains unresolved. Gross stresses are retained without an invented material-independent acceptance limit.',
           '', '| Scenario | Objective | Beam / pier / foundation / method | Installed cost USD | Installed mass t | Working days | Largest lift t |',
           '|---|---|---|---:|---:|---:|---:|']
    for sid,winners in report['winners'].items():
        for objective in ('cheapest','lightest','fastest'):
            r=by_id.get(winners[objective])
            if r:
                s=r['scenarios'][sid];lines.append(f"| {sid} | {objective} | {label(r['choice'])} | {s['installed_cost_usd']:,.0f} | {r['quantities']['installed_study_mass_kg']/1000:,.1f} | {s['working_days']:g} | {r['construction']['maximum_lift_mass_kg']/1000:.1f} |")
            else:lines.append(f'| {sid} | {objective} | No converged provisional candidate | — | — | — | — |')
    lines += ['', '## Family coverage','', '| Beam family | Native completed packages | Model / evidence maturity |','|---|---:|---|']
    lines += [f"| {b['id']} | {counts[b['id']]} | Research; gross elastic properties, actual supplier details and physical validation open |" for b in config['beams']]
    lines += ['', '## Detailed confirmation','',
              f"{len(report['shortlist'])} shortlisted packages; {sum(r.get('convergence_passed',False) for r in report['refinements'])} completed converged three-mesh solids and 3D frame checks.",
              '3D models include two separate tracks, flexible transverse hollow caps, finite bearing translations/roll and coupled foundation translation/rotation. Both-track and single-track uniform loading are retained at three deck meshes for both soil scenarios.',
              'Composite connector sensitivity compares noncomposite, partial interaction and strong-connector behaviour; connector values are unmeasured assumptions. These checks do not supply bond failure or cyclic/fire evidence.',
              '', '## Document work packages and remaining acceptance','', '| Package | Implemented software / retained output | External acceptance still required |','|---|---|---|']
    software={1:'source-bound Baghdad planning inputs and explicit qualification blockers',2:'strict candidate inputs, package/candidate IDs, immutable results and modification events',
              3:'ten beam, six pier, nine foundation options, material compatibility and bounded search',4:'shared disjoint CAD/IFC solids, net material quantities, shipping/lift unit centres',
              5:'analytical/native component checks, foundation reciprocity/energy and three-level refinement',6:'native CalculiX nodal/stress parsers and complete 3D force/displacement fields',
              7:'native nonlinear component benchmarks and coupled geometry-specific elastic pile groups',8:'uniform planning sensitivity, separate 3D tracks/caps, method/stage schedules and construction units',
              9:'complete material/plant/labour/overhead/maintenance/replacement bills and three conditional scenarios',10:'bounded seeded runs, checked checkpoints, sealed raw data, multipart archive and verified restore',
              11:'equal-budget random/evolution search, Pareto sets, scenario reversals and a diverse shortlist',12:'three-mesh actual-section solids, orthotropic materials and connector-slip/torsion diagnostics',
              13:'candidate-specific instrumented physical-test protocols and existing calibration/holdout workflow',14:'sealed change proposal and pointers to the existing controlled change/structural release process'}
    for i,text in software.items():
        evidence=('actual instrumented tests, laboratories, independent reviewer and acceptance' if i in (5,13,14) else 'project inputs, applicable domain and responsible independent engineering acceptance')
        lines.append(f'| C{i:02d} | {text} | {evidence} |')
    lines += ['', '## Open qualification inputs','']
    lines += [f"- **{r['id']}** ({r['owner']}): {r['required']} — {r['status']}." for r in report['qualification_inputs']['missing_inputs']]
    lines += ['', '## Further model domains','']
    lines += ['- '+x+'.' for x in report['remaining_model_domains']]
    lines += [f"- {x['id']}: {x['reason']}; {x['status']}." for x in report['unimplemented_options']]
    lines += ['', 'Actual soil, supplier train records, material/connection details, quotations, physical tests and independent acceptance determine whether any shortlisted package is adoptable. Physical and operating release remain false.','']
    return '\n'.join(lines)


def interactive(report,rows):
    data=json.dumps(dict(report=report,rows=compact_rows(rows)),allow_nan=False).replace('<','\\u003c')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Complete viaduct choices</title>
<style>body{font:16px system-ui;margin:30px auto;padding:0 20px;max-width:1500px;background:#f5f8fa;color:#173549}h1{font-size:28px}label{display:inline-block;margin:12px 20px 12px 0}select{padding:8px;border:1px solid #8dabbc;border-radius:4px}table{border-collapse:collapse;width:100%;background:white;font-size:13px}td,th{text-align:left;padding:9px;border-bottom:1px solid #dce4e9}th{position:sticky;top:0;background:#dfeaf0}section{padding:15px;background:#e4edf3;border-radius:8px}button{padding:8px;cursor:pointer}details{margin:20px 0}#table{overflow:auto;max-height:70vh}.warn{background:#fff1d7}small{color:#476776}svg{max-height:420px;width:100%}</style>
<h1>Complete viaduct choices</h1><section class="warn">Baghdad research study. Supplier costs, axle positions and site qualification remain open. The priced cases below are synthetic comparisons. Static uniform loading does not establish railway capacity, fatigue or dynamic performance.</section>
<p id="summary"></p><label>Commercial/productivity scenario <select id="scenario"></select></label><label>Beam family <select id="family"><option value="">All</option></select></label><label>Show <select id="verdict"><option value="pass">Provisional research passes</option><option value="all">All retained packages</option><option value="short">Detailed shortlist</option></select></label><label>Sort by <select id="sort"><option value="cost">Scenario cost</option><option value="mass">Installed mass</option><option value="days">Working days</option><option value="lift">Largest lifting unit</option></select></label>
<p id="scope"></p><section id="leaders"></section><p><small>Click a choice to review quantities, model response, constraint failures and unpriced scope. Search results are bounded; no global optimum or engineering-qualified winner is claimed.</small></p>
<div id="table"><table><thead><tr><th>Choice / system</th><th>Material</th><th>Pier / foundation</th><th>Construction / continuity</th><th>Scenario USD</th><th>Mass t</th><th>Working days</th><th>Largest lift t</th><th>Research screen</th></tr></thead><tbody id="rows"></tbody></table></div><details id="detail"><summary>Selected candidate evidence</summary><pre id="evidence" style="white-space:pre-wrap"></pre></details><script id="data" type="application/json">'''+data+'''</script><script>
const data=JSON.parse(document.getElementById('data').textContent), report=data.report, rows=data.rows;
const $=id=>document.getElementById(id), scenarios=Object.keys(report.winners);for(const id of scenarios){const o=new Option(id,id);$('scenario').add(o)}for(const f of [...new Set(rows.map(r=>r.choice.beam))].sort())$('family').add(new Option(f,f));
$('summary').textContent=`${report.scope.route_length_m} m of double-track viaduct · ${report.distinct_packages} distinct packages · ${report.provisional_passes} provisional passes · ${report.shortlist.length} shortlisted packages.`;
function metric(r,key,s){if(r.status!=='completed')return Infinity;return key==='cost'?r.scenarios[s].installed_cost_usd:key==='days'?r.scenarios[s].working_days:key==='lift'?r.max_lift_mass_kg:r.installed_mass_kg}
function show(){const s=$('scenario').value, f=$('family').value, v=$('verdict').value, key=$('sort').value, w=report.winners[s];$('scope').textContent='Price and lead-time basis: synthetic assumptions. Actual Baghdad supplier price remains unknown. '+report.winner_basis+'.';
$('leaders').textContent=['cheapest','lightest','fastest'].map(k=>{const r=rows.find(r=>r.package_id===w[k]);return k+': '+(r?r.choice.beam+' '+r.choice.span_m+' m / '+r.choice.pier+' / '+r.choice.foundation:'unresolved')}).join(' · ');
const visible=rows.filter(r=>(!f||r.choice.beam===f)&&(v==='all'||v==='short'&&report.shortlist.includes(r.package_id)||v==='pass'&&r.status==='completed'&&r.violation===0)).sort((a,b)=>metric(a,key,s)-metric(b,key,s));$('rows').replaceChildren();
for(const r of visible){const tr=document.createElement('tr'),c=r.choice,ok=r.status==='completed';const values=[c.beam+' '+c.span_m+' m',c.material+(c.beam==='hybrid-shell'||c.beam==='frp-composite-I'||c.pier==='double-skin-hybrid'?' + '+c.fibre_material.toUpperCase():'')+' / support '+c.support_material,c.pier+' / '+c.foundation,c.beam_method+' / '+c.connection_scheme,ok?r.scenarios[s].installed_cost_usd.toLocaleString(undefined,{maximumFractionDigits:0}):'—',ok?(r.installed_mass_kg/1000).toFixed(1):'—',ok?r.scenarios[s].working_days.toFixed(1):'—',ok?(r.max_lift_mass_kg/1000).toFixed(1):'—',ok?(r.violation===0?'Provisional pass':'Limit exceeded'):'Execution failed'];for(const x of values){const td=document.createElement('td');td.textContent=x;tr.append(td)}tr.tabIndex=0;tr.style.cursor='pointer';const inspect=()=>{$('evidence').textContent=JSON.stringify(r,null,2);$('detail').open=true;$('detail').scrollIntoView({behavior:'smooth'})};tr.onclick=inspect;tr.onkeydown=e=>{if(e.key==='Enter')inspect()};$('rows').append(tr)}}for(const id of ['scenario','family','verdict','sort'])$(id).onchange=show;show();
</script></html>'''


def render(report,rows,config,output):
    (output/'comparison.md').write_text(markdown(report,rows,config))
    (output/'report.html').write_text(interactive(report,rows))
    (output/'system-choices.svg').write_text(diagram(config));(output/'pareto.svg').write_text(pareto_plot(report,rows))
    with (output/'comparison.csv').open('w',newline='') as stream:
        fields=['package_id','beam','span_m','material','pier','foundation','beam_method','scenario','installed_cost_usd','whole_life_cost_usd','installed_mass_kg','max_lift_mass_kg','working_days','research_screen','actual_installed_cost_usd']
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for r in rows:
            if r['status']!='completed':continue
            for sid,s in r['scenarios'].items():
                writer.writerow(dict(package_id=r['package_id'],**{k:r['choice'][k] for k in ('beam','span_m','material','pier','foundation','beam_method')},scenario=sid,
                                     installed_cost_usd=s['installed_cost_usd'],whole_life_cost_usd=s['whole_life_cost_usd'],installed_mass_kg=r['quantities']['installed_study_mass_kg'],
                                     max_lift_mass_kg=r['construction']['maximum_lift_mass_kg'],working_days=s['working_days'],research_screen='provisional-pass' if r['violation']==0 else 'limit-exceeded',actual_installed_cost_usd=r['actual_installed_cost_usd']))


def export(bundle,output,generator,*,update_readme=False):
    from .systems import verify
    report=verify(bundle);frozen=load(bundle/'input.json');rows=[load(p) for p in sorted((bundle/'results').glob('*.json'))]
    if not report['numerical_refinement_passed']:raise ValueError('retained full review requires completed numerical refinements')
    payload=dict(schema='osr-civil-complete-system-review/1',generator=generator.relative_to(ROOT).as_posix(),generator_sha256=sha(generator),
                 consumer='engineering/analysis/tests/test_civil_system_choices.py',report=report,rows=compact_rows(rows),
                 option_register=frozen['config'],scenarios=frozen['scenarios'],report_sha256=sha(bundle/'report.json'),seal_sha256=sha(bundle/'seal.json'),
                 promotion=load(bundle/'promotion/proposal.json'),physical_tests=load(bundle/'physical-tests/test-programme.json'),
                 artifacts={name:sha(bundle/name) for name in ('system-choices.svg','pareto.svg','comparison.csv','report.html')})
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(encoded(payload))
    output.with_suffix('.md').write_text(markdown(report,rows,frozen['config']))
    for name in ('system-choices.svg','pareto.svg'):(output.parent/name).write_bytes((bundle/name).read_bytes())
    if update_readme:
        path=ROOT/'README.md';text=path.read_text();begin='<!-- GENERATED: complete viaduct choices -->';end='<!-- END GENERATED: complete viaduct choices -->'
        if begin not in text or end not in text:raise ValueError('root README viaduct review markers absent')
        index={r['package_id']:r for r in rows};sid=next(iter(report['winners']));w=report['winners'][sid]
        block=[begin,f"Executed comparison: **{report['distinct_packages']} distinct complete packages**, **{report['evaluated_attempts']} evaluations**, **{len(report['shortlist'])} detailed packages**, using **{report['scope']['route_length_m']:g} m of double track**.",'',
               '| Conditional objective | Beam | Pier | Foundation | Synthetic installed cost | Installed study mass | Working time |','|---|---|---|---|---:|---:|---:|']
        for key in ('cheapest','lightest','fastest'):
            r=index.get(w[key])
            if r:block.append(f"| {key.capitalize()} in `{sid}` | {r['choice']['beam']} {r['choice']['span_m']:g} m, {r['choice']['material']} | {r['choice']['pier']} | {r['choice']['foundation']} | ${r['scenarios'][sid]['installed_cost_usd']:,.0f} | {r['quantities']['installed_study_mass_kg']/1000:,.1f} t | {r['scenarios'][sid]['working_days']:g} working days |")
        block += ['', 'These are the best confirmed research choices found within the declared search budget and synthetic price/productivity scenarios. Supplier-priced cheapest design, railway qualification and global optimality remain unresolved. All physical and operating release flags remain false.',end]
        before,rest=text.split(begin,1);_,after=rest.split(end,1);path.write_text(before+'\n'.join(block)+after)
    return payload
