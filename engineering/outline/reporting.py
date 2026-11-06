"""Render reader prices from verified compact outline/supply publications."""
import json
from pathlib import Path
from engineering.station_rail import ROOT
from . import coordinator,supply_economics

NAMES={'cable-capstan':'Cable / capstan','common-drive-rollers':'Common-drive rollers','compact-launch-LIM':'Compact LIM'}

def _block(text,start,end,replacement):
    a=text.index(start);b=text.index(end,a)
    return text[:a]+replacement+'\n\n'+text[b:]

def render(root=ROOT):
    root=Path(root);supply=root/'docs/design-engine/supply-economics';demand=root/'docs/design-engine/demand-outline'
    supply_economics.verify_compact(supply,root);coordinator.verify_compact(demand,root)
    s=json.loads((supply/'summary.json').read_bytes());d=json.loads((demand/'summary.json').read_bytes())
    rows=[r for r in s['variants'] if r['mechanism']=='cable-capstan']
    current=next(r for r in rows if r['scenario']=='project-make-buy')
    peak=['<!-- BEGIN calculated supply comparison -->','## Same-service 30 km comparison','',
        'All three rows retain 12 stations, 52 six-car trainsets, 120-second peak headway and the same physical quantities.','',
        '| Pricing scenario | Central installed capital | Central cost / route-km | Central 30-year NPV |',
        '| --- | --- | --- | --- |']
    labels={'reference-rates':'Original generic rates','china-bulk-buy':'China-origin bulk purchasing','project-make-buy':'Project-volume make/buy'}
    for r in rows:peak.append(f"| {labels[r['scenario']]} | US${r['installed_capital_usd']['base']/1e6:,.1f}m | US${r['price_per_route_km_usd']['base']/1e6:.2f}m | US${r['whole_life_npv_usd']['base']/1e6:,.1f}m |")
    costs=current['installed_capital_usd']
    peak += ['',f"The current project case spans US${costs['low']/1e6:,.1f}m / US${costs['base']/1e6:,.1f}m / US${costs['high']/1e6:,.1f}m, low/base/high. These are broad sensitivity cases, not confidence bounds or supplier offers.",'',
        f"Calculation identity: `{s['evaluation_id']}`.",'<!-- END calculated supply comparison -->']
    path=supply/'README.md';text=path.read_text()
    if '<!-- BEGIN calculated supply comparison -->' in text:
        text=_block(text,'<!-- BEGIN calculated supply comparison -->','## What changed','\n'.join(peak))
    else:text=text.replace('## What changed','\n'.join(peak)+'\n\n## What changed',1)
    path.write_text(text)
    table=['| Retained launch concept | Headway | Speed cap | Acceleration | Fleet including reserves | Central installed cost | Central cost / route-km |',
        '| --- | --- | --- | --- | --- | --- | --- |']
    for r in d['outlines']:
        table.append(f"| {NAMES[r['mechanism']]} | {r['headway_s']:g} s | {r['speed_kmh']:g} km/h | {r['acceleration_m_s2']:g} m/s² | {r['trainsets']} trains | US${r['installed_capital_usd']['base']/1e6:,.1f}m | US${r['price_per_route_km_usd']['base']/1e6:.2f}m |")
    cable=next(r for r in d['outlines'] if r['mechanism']=='cable-capstan');costs=cable['installed_capital_usd']
    table += ['',f"These are **Class C engineering estimates** using the [project-volume purchasing and manufacturing policy](../supply-economics/README.md). The cable outline takes approximately {cable['journey_minutes']:.2f} minutes one way. Installed low/base/high costs are US${costs['low']/1e6:,.1f}m / US${costs['base']/1e6:,.1f}m / US${costs['high']/1e6:,.1f}m; central 30-year NPV is US${cable['whole_life_npv_usd']['base']/1e6:,.1f}m. These are sensitivity cases, not confidence limits or supplier offers.",'',
        'The original generic-rate benchmark remains US$738.0m / US$24.6m per route-km with 52 trains and a 120-second headway for 8,280 nominal places/hour/direction. The updated supply comparison reprices that same service. This demand example has different requirements; compare pricing scenarios at equal service, and service choices under the same pricing basis. The Workbench retains all three selectable pricing bases.']
    path=demand/'README.md';text=path.read_text()
    # Counts belong to the verified current packet, not a previous timed run.
    text='\n'.join(
        (f"The current publication screened {d['counters']['screened']} service cases and produced {d['costed_cases']} complete cost cases, with {d['counters']['native_solver_jobs']} native solver jobs. Source-bound summaries are in [summary.json](summary.json); source and artifact bindings are in [manifest.json](manifest.json). Runtime measurements belong to private execution records and are not universal throughput claims."
         if line.startswith(('The reference run screened ', 'The current publication screened ')) else line)
        for line in text.splitlines())+'\n'
    path.write_text(_block(text,'| Retained launch concept','## Progressive acceptance','\n'.join(table)))
    path=root/'README.md';text=path.read_text();lines=text.splitlines();output=[]
    for line in lines:
        if line.startswith('The [demand-led outline workflow]'):
            line=f"The [demand-led outline workflow](docs/design-engine/demand-outline/README.md) connects a passenger brief to conditional service screening, complete provisional costs, production/resource quantities and an **‘outline accepted’** result. The Workbench explores service choices and three station-launch concepts under selectable pricing bases. Its illustrative 4,000-passenger/hour/direction project-volume case uses a 200-second service and costs a central **US${cable['price_per_route_km_usd']['base']/1e6:.2f}m/km**; this differs from the higher-capacity benchmark below. Supplier quotations and prototype validation remain later evidence requirements. Other approaches remain open under the transport-goal policy."
        if line.startswith('The [30 km / 12 station cost benchmark]'):
            line=line.replace('is the working reference for equal-service design analysis','preserves the original generic-rate comparison for equal-service design analysis')
        if line.startswith('The [project-volume supply comparison]'):continue
        output.append(line)
        if line.startswith('The [30 km / 12 station cost benchmark]'):
            output += ['',f"The [project-volume supply comparison](docs/design-engine/supply-economics/README.md) reprices those same 30 km, 12 stations and 52 trains using Chinese wholesale/manufacturer observations, landed costs and calculated manufacturing alternatives. Its current **Class C central installed estimate is US${current['installed_capital_usd']['base']/1e6:,.1f}m, or US${current['price_per_route_km_usd']['base']/1e6:.2f}m per route-km**. Fixed factories, shared premises, freight, QA, duties and future replacement setup are included once. Lower purchasing prices do not change physical acceptance or establish a globally best transport architecture."]
    clean=[]
    for line in output:
        if line or not clean or clean[-1]:clean.append(line)
    path.write_text('\n'.join(clean)+'\n')
    return dict(supply_evaluation_id=s['evaluation_id'],outline_evaluation_id=d['evaluation_id'])

if __name__=='__main__':print(json.dumps(render(),sort_keys=True))
