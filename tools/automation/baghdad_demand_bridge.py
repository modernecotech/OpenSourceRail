#!/usr/bin/env python3
"""Account for surveyed OD journeys without turning transfers into paid trips."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import tomllib

from city_access import transfer_audit

ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'


def account_journeys(design, journeys, *, tariff='integrated-journey'):
    if tariff not in ('integrated-journey','charged-per-boarding'):
        raise ValueError('An explicit supported tariff is required')
    network=transfer_audit(design)
    direct={frozenset(p['lines']) for p in network['pairs'] if p['minimum_transfers']==1}
    lines={r.get('id') or r['name'] for r in design['lines']}
    load={name:0. for name in lines};paid=boardings=receipts=0.;seen=set()
    for row in journeys:
        uid=row['journey_id'];path=row['line_path'];count=row['annual_journeys'];fare=row['fare_iqd']
        if uid in seen:raise ValueError('Duplicate OD cohort ID')
        seen.add(uid)
        if not path or any(line not in lines for line in path):raise ValueError('Unknown or empty route')
        if any(frozenset((a,b)) not in direct for a,b in zip(path,path[1:])):
            raise ValueError('Route requires an undeclared passenger transfer')
        if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in (count,fare)):
            raise ValueError('Invalid journey count or fare')
        charges=1 if tariff=='integrated-journey' else len(path)
        paid+=count;boardings+=count*len(path);receipts+=count*fare*charges
        for name in path:load[name]+=count
    return dict(annual_unique_paid_journeys=paid,annual_train_boardings=boardings,
        annual_fare_receipts_iqd=receipts,line_boardings=load,tariff=tariff,
        line_boardings_are_not_section_peak_loads=True,forecast_accepted=False)


def generate(od_path=None):
    design_path=CITY/'design.toml';access_path=CITY/'engineering/access/summary.json';finance_path=CITY/'engineering/finance/summary.json'
    sources=[Path(__file__),ROOT/'tools/automation/city_access.py',design_path,access_path,finance_path]
    design=tomllib.loads(design_path.read_text());access=json.loads(access_path.read_text());finance=json.loads(finance_path.read_text())
    out=CITY/'engineering/demand-bridge';out.mkdir(exist_ok=True)
    accounting=None
    if od_path:
        data=json.loads(od_path.read_text())
        if not data.get('survey_source') or not data.get('survey_date'):
            raise ValueError('OD input requires source and survey date; synthetic inputs cannot be labelled surveyed')
        accounting=account_journeys(design,data['journeys'],tariff=data['tariff'])
        retained=out/'retained-od.json';retained.write_bytes(od_path.read_bytes());sources.append(retained)
    result=dict(schema='baghdad-demand-bridge/1',status='survey-handoff-not-a-demand-forecast',
        sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        population_source=access['population'],capacity_led_receipt_basis=finance['revenue_basis'],
        od_accounting=accounting,surveyed_jobs_and_destinations=None,verified_station_entrances=None,
        entrance_walking_time_catchments=None,measured_od_journeys=None,
        accepted_route_choice_and_section_peak_loads=None,financial_receipt_uplift_iqd=0.,
        fare_transfers_create_extra_paid_journeys=False,service_resize_accepted=False,
        demand_forecast_accepted=False,finance_baseline_replaced=False)
    (out/'summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'README.md').write_text('''# Baghdad access, demand and paid journeys

**Status: survey handoff; no calibrated demand forecast or revenue uplift.**

Native population pixels → verified station entrances/walking times → jobs/destinations and surveyed OD journeys → route choice → section/time train loads → unique paid journeys → collected fare receipts.

The [retained access report](../access/README.md) counts radial unions in 2020 pixels. Rivers, motorways, walls, crossing availability and station vertical access need an entrance-based walking network. The retained OSM export contains selected arterial geometry and building/water polygons; it is not a complete pedestrian graph or entrance survey. Do not route through private premises, infer a crossing from coincident lines or count a 2 km feeder catchment as convenient walking coverage. Jobs, entrances and OD observations remain missing.

The current financial paid-trip assumption remains capacity-led. Shorter lines and different catchments do not automatically preserve or increase patronage. `baghdad_demand_bridge.py --od <survey.json>` validates explicit line paths against declared transfers and reports unique paid journeys, train boardings, line boardings and fare receipts separately. An integrated fare charges each journey once; only an explicitly declared boarding tariff charges its legs. The source and survey date are required. Aggregated annual line boardings are not peak section loads, unique people or a validated route-choice forecast.

Before adopting receipts, independently qualify the OD evidence and sampling/expansion weights, income/concession response, entrances and accessible walking paths, waiting/transfer time, route choice, peak section capacity, fare caps and collection losses. Re-size service/fleet/energy/OPEX together and regenerate the financial ledger. No survey, jobs, path, peak load or additional income is fabricated to close the gap.

[Source-bound handoff and accounting](summary.json).
''')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--od',type=Path);a=p.parse_args();generate(a.od)
