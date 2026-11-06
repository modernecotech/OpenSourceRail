#!/usr/bin/env python3
"""Summarise a verified city pricing execution against an immutable Git control."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from engineering.outline import completion
from engineering.station_rail.common import encoded,identity,digest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',required=True,type=Path)
    p.add_argument('--control',default='bf3373473583092fd1a701037b91c3ec79a37cd0')
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    manifest=completion.verify(args.state,root=ROOT)
    current=json.loads((args.state/'summary.json').read_bytes())
    control_raw=subprocess.check_output(['git','-C',str(ROOT),'show',args.control+':docs/design-engine/outline-completion/summary.json'])
    old={r['city']['slug']:r for r in json.loads(control_raw)['cities']}
    rows=[]
    for row in current['cities']:
        slug=row['city']['slug'];v=json.loads((args.state/'cities'/slug/'result.json').read_bytes());cost=v['cost']
        rows.append(dict(city=row['city'],route_km=row['route_km'],lines=row['lines'],trainsets=row['trainsets'],
            previous_capital_usd=old[slug]['installed_capital_usd'],installed_capital_usd=row['installed_capital_usd'],
            previous_whole_life_npv_usd=old[slug]['whole_life_npv_usd'],whole_life_npv_usd=row['whole_life_npv_usd'],
            annual_reserve_auxiliary_grid_kwh=cost['energy_ledger']['cases']['base']['reserve_vehicle_aux_grid_kwh'],
            local_cost_input_status=cost['local_cost_inputs']['status'],local_rates_verified=False,
            largest_capital_accounts=sorted(cost['capital_lines'],key=lambda r:-r['costs_usd']['base'])[:5],
            civil_comparison=row.get('civil_comparison'),cost_evaluation_id=cost['evaluation_id'],
            service_evaluation_id=v['service_evaluation']['evaluation_id']))
    value=dict(schema='osr-city-price-review/1',control_revision=args.control,control_summary_sha256=sha256(control_raw).hexdigest(),
        source_execution_manifest_id=manifest['manifest_id'],source_summary_sha256=digest(args.state/'summary.json'),
        producer_sha256=digest(__file__),cities=rows,city_count=len(rows),
        findings=['Reserve-fleet auxiliary electricity and charging losses are now costed.',
            'Accounting horizon and real discount rate follow the declared policy.',
            'Explicit operating wage/tariff overrides affect only their named accounts; unprovided local inputs retain transferred estimates.',
            'Same-route water-evidence civil alternatives include obstruction reserves and interface holds; headline civil allowances remain retained.',
            'Generic demand, site, equipment capability and local cost assumptions are not surveyed or supplier-validated.'],
        physical_accepted=False,engineering_accepted=False,selected_reference_changed=False)
    value['audit_id']=identity(value)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'results.json').write_bytes(encoded(value))
    examples=[r for slug in ('baghdad','kut','samawah') for r in rows if r['city']['slug']==slug]
    table='\n'.join('| '+ ' | '.join([r['city']['name'],f"{r['route_km']:.2f}",f"{r['installed_capital_usd']['base']/1e6:,.2f}",f"{r['whole_life_npv_usd']['base']/1e6:,.2f}",f"{r['civil_comparison']['installed_capital_usd']['base']/1e6:,.2f}",str(r['civil_comparison']['interface_hold_count'])])+' |' for r in examples)
    text=f'''# City price review — 6 November 2026

All {len(rows)} v0.6 city networks have been recalculated. These are complete, internally reconciled outline estimates under declared assumptions. They are not verified local construction budgets or qualified railway designs.

The corrected energy account includes reserve-fleet auxiliaries and charging losses. The accounting horizon and discount rate now follow the declared city policy, including short horizons with an explicitly empty renewal schedule. Named local operating tariff and paid-hour wage estimates can replace their individual accounts without discounting imported equipment or construction.

| City | Route km | Headline capital US$m | 30-year NPV US$m | Separate civil alternative US$m | Interface holds |
| --- | ---: | ---: | ---: | ---: | ---: |
{table}

The headline retains the mapped civil classes. The alternative traverses actual selected route coordinates through authenticated historical WorldCover/OSM water masks. Dry legacy bridge allowances become elevated construction plus a nonzero obstruction reserve. Wet at-grade or unsupported interfaces remain explicit holds. Roads, utilities, flooding, soil and clearance requirements are not resolved by a water mask. These figures therefore compare hypotheses; they do not establish savings that can be banked.

Each city page now exposes the price basis, largest capital allowances, electricity scenarios and annual reserve-fleet energy. Its `energy_budget.csv` and `local_cost_inputs.csv` are downloadable. Factory/make-buy, civil, staffing, delivery, fare/funding and geographic outputs remain linked in the city dossier.

The estimates retain the declared China-origin material/finished-supply and calculated local-production routes. Wholesale observations are not finished rail-grade quotations. No additional unsupported bulk discount has been applied. Outside Iraq, transferred rate scenarios remain explicit until scoped local inputs are supplied. Generic 4,000 peak passengers/hour/direction is a planning assumption, not a city demand forecast. Powered-axle research fallbacks are identified separately from the passive station-powered reference.

Reproduce with:

```sh
python -m engineering.outline complete --workers 3 --output /path/to/fresh-run
python -m engineering.outline complete-verify --replay --output /path/to/fresh-run
python tools/automation/report-city-price-review.py --state /path/to/fresh-run --output docs/design-engine/city-price-review
```

[Per-city audit and exact identities](results.json) · [Calculated outline methods](../outline-completion/README.md) · [City dossiers](../city-dossiers/index.json)

Execution manifest: `{manifest['manifest_id']}`. Audit: `{value['audit_id']}`. Control: `{args.control}`. Full numerical runs, historical source masks and interrupted trials are retained outside the published compact packet; their execution manifests and hashes identify the exact evidence.
'''
    (args.output/'README.md').write_text(text)
    print(json.dumps(dict(city_count=len(rows),audit_id=value['audit_id'])))

if __name__=='__main__':main()
