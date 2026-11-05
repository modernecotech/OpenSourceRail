"""Render human readers from verified outline-completion publications."""
from pathlib import Path
import re

from engineering.station_rail import ROOT
from . import completion_publication as completion


def render(root=ROOT):
    root = Path(root)
    manifest,summary = completion.verify(root=root)
    rows = summary['cities']
    counts = summary['designs']['counts']
    begin,end = '<!-- BEGIN calculated outline coverage -->','<!-- END calculated outline coverage -->'
    mapped = sum(row['stations'] for row in rows)
    complexes = sum(row['operational_station_complexes'] for row in rows)
    changed = sum(row['selected_alignment_kind']!='original' for row in rows)
    variants = sum(len(row['alignment_comparison']) for row in rows)
    block = '\n'.join((begin,'## Current calculated coverage','',
        f"**{len(rows)} city networks**, **{sum(row['lines'] for row in rows)} lines** and "
        f"**{sum(row['route_km'] for row in rows):,.1f} route-km** have complete fourteen-scope "
        'installed and 30-year cost scenarios.', '',
        f"{mapped:,} retained map stop markers are represented by {complexes:,} operational station complexes. "
        f"The campaign priced {variants} original/revised alignment scenarios; {changed} revised alignments "
        'are retained for further outline detailing under the declared access and cost assumptions.', '',
        f"Design coverage also includes **{counts['railway-bundle']} railway bundles**, "
        f"**{counts['vehicle-body']} body outlines** and **{counts['civil-span']} civil spans**, "
        'each at its explicit component or system scope.', '',
        '| City example | Network km | Lines | Operational stop complexes | Trainsets | Central installed US$m | Central US$m / route-km |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
        *[f"| {r['city']['name']} | {r['route_km']:,.1f} | {r['lines']} | {r['operational_station_complexes']} | "
          f"{r['trainsets']} | {r['installed_capital_usd']['base']/1e6:,.1f} | "
          f"{r['price_per_route_km_usd']['base']/1e6:,.2f} |"
          for slug in ('samawah','baghdad','lyon','agra') for r in rows if r['city']['slug']==slug],
        '',f"Calculation `{summary['evaluation_id']}`; publication `{manifest['manifest_id']}`.",end))
    path = root/completion.PUBLICATION/'README.md'
    text = path.read_text()
    if begin in text:
        text = re.sub(re.escape(begin)+r'.*?'+re.escape(end),lambda _:block,text,flags=re.S)
    else:
        text = text.replace('## Methods',block+'\n\n## Methods',1)
    path.write_text(text)
    front = root/'README.md'
    text = front.read_text()
    start,stop = '<!-- BEGIN city outline completion -->','<!-- END city outline completion -->'
    paragraph = (start+'\nThe [priced city and design outlines](docs/design-engine/outline-completion/README.md) '
        f"cover **{len(rows)} mapped city networks and {sum(r['lines'] for r in rows)} lines**, "
        f"plus {counts['railway-bundle']} railway bundles, {counts['vehicle-body']} bodies and {counts['civil-span']} civil spans. "
        'The Workbench compares original, straighter and rounded square-ring proposals, joins close stop markers into operational complexes, '
        'and exposes fleet, manufacturing, construction and fourteen whole-life cost scopes. '
        'The local workflow edits and re-costs an outline, then exports a resource-leveled delivery plan and disabled business-system drafts. '
        'These are completed calculated outlines under explicit demand, site and rate assumptions; physical approval remains separate.\n'+stop)
    if start in text:
        text = re.sub(re.escape(start)+r'.*?'+re.escape(stop),lambda _:paragraph,text,flags=re.S)
    else:
        text = text.replace('## Current engineering and the next working-system milestone',
            '## Current engineering and the next working-system milestone\n\n'+paragraph,1)
    front.write_text(text)
    return dict(rendered=True,cities=len(rows),alignment_scenarios=variants,retained_revisions=changed)


if __name__=='__main__':
    print(render())
