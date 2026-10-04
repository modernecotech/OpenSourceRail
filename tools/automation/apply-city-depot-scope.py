#!/usr/bin/env python3
"""Price line-local full-fleet depot requirements before scenario generation.

Stations locate planning interfaces, not accepted depot land. Maintenance bays
and storage slots are separate. Retained switches and turnbacks remain present.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import tomllib

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'lib/templates/city-operating-scope.toml'


def depot_plan(design, profile, config, capex, energy):
    dc=config['depots']; body=profile['length_m']; slot=body+dc['train_clearance_m']
    used=set(); sites=[]; items=[]
    legacy={r['station'] for r in design.get('depots',[])}
    for fleet in design['fleets']:
        line=fleet['line']; count=fleet['trainset_count']
        candidates=[r for r in design['stations'] if r['line']==line]
        if not candidates:raise ValueError('No station interface for '+line)
        candidates.sort(key=lambda r:(r['id'] not in legacy, r['s_m']))
        station=next((r for r in candidates if r['id'] not in used),None)
        if station is None:raise ValueError('No distinct depot interface for '+line)
        used.add(station['id']); tracks=math.ceil(count/dc['positions_per_track'])
        bays=math.ceil(count*dc['bay_hours_per_train_year']/(dc['workshop_days_year']*dc['workshop_hours_day']*dc['workshop_availability']))
        yard=(tracks*dc['positions_per_track']*slot+dc['site_access_track_m'])*dc['track_centres_m']*dc['yard_access_multiplier']
        shell=bays*slot*dc['workshop_bay_width_m']
        quantities=[('storage-track',count*slot,dc['track_usd_per_m']),('workshop-track',bays*slot,dc['track_usd_per_m']),
            ('site-access-track',dc['site_access_track_m'],dc['track_usd_per_m']),('turnouts',tracks+bays+2,dc['turnout_usd']),
            ('drainage-access',yard,dc['drainage_access_usd_per_m2']),('workshop-shell',shell,dc['workshop_shell_usd_per_m2']),
            ('workshop-process-equipment',bays,dc['workshop_equipment_usd_per_bay']),
            ('workshop-services',shell,dc['workshop_services_usd_per_m2']),('yard-lighting-fire',1,dc['yard_lighting_fire_usd_per_site']),
            ('office-stores',dc['office_stores_m2_per_site'],dc['office_stores_usd_per_m2']),('wash-plant',1,dc['wash_plant_usd_per_site']),
            ('wheel-lathe',1,dc['wheel_lathe_usd_per_site']),('rescue-isolation',1,dc['isolation_rescue_quarantine_usd_per_site']),
            # Full depot-main inventory, not just its difference from a small
            # passenger site. These equipment rates exclude unquoted installation.
            ('depot-pv',energy['pv_nameplate_kw'],capex['solar_power_plant']['utility_pv_usd_per_kw']),
            ('depot-stationary-storage',energy['storage_capacity_kwh']/500,capex['station_800v_module_usd']['stationary_lfp_500kwh'])]
        own=[dict(line=line,scope=k,quantity=q,reference_rate_usd=rate,cost_usd=q*rate,quotation=None) for k,q,rate in quantities]
        items.extend(own)
        sites.append(dict(station=station['id'],line=line,archetype='main-heavy',fleet_stalls=bays,
            storage_slots=count,storage_tracks=tracks,train_length_m=body,slot_length_m=slot,
            storage_track_m=count*slot,workshop_bays=bays,planning_land_area_m2=yard+shell+dc['office_stores_m2_per_site'],
            reference_cost_usd=round(math.fsum(r['cost_usd'] for r in own)),site_accepted=False,
            physical_release=False,land_cost_usd=None,utility_upgrade_cost_usd=None))
    if sum(r['storage_slots'] for r in sites)!=sum(r['trainset_count'] for r in design['fleets']):
        raise ValueError('Depot slots fail fleet reconciliation')
    return dict(schema_version=1,sites=sites,items=items,number_of_depots=len(sites),
        full_fleet_storage_slots=sum(r['storage_slots'] for r in sites),gross_reference_cost_usd=sum(r['reference_cost_usd'] for r in sites),
        station_stabling_capacity_credit=0,workshop_bays_are_storage=False,complete_installed_budget=False,
        limitations=['One planning depot interface per line; no accepted property, access alignment or launch capacity.',
                    'Full fleet including spares is stored separately from workload-sized maintenance bays.',
                    'Depot PV/storage equipment is priced once in depot capital; station charging cabinets remain in charging_microgrid.',
                    'Reference rates are shared USD-equivalent targets, not local installed quotations; land, grid upgrades, installation and approval remain open.'])


def apply(path):
    d=tomllib.loads(path.read_text());slug=d['city']['slug']
    if slug=='baghdad':return  # Dedicated revised scope retains its separate ledger.
    families={r['rolling_stock'] for r in d['lines']}
    if len(families)!=1:raise ValueError('One family is required by the city scenario')
    stock=ROOT/'lib/templates/rolling-stock.toml';cost=ROOT/'lib/templates/capex-costs.toml';power=ROOT/'lib/templates/energy-sites.toml'
    plan=depot_plan(d,tomllib.loads(stock.read_text())['profiles'][families.pop()],tomllib.loads(CONFIG.read_text()),
                    tomllib.loads(cost.read_text()),tomllib.loads(power.read_text())['tiers']['depot-main'])
    old_switches=[r for depot in d.get('depots',[]) for r in depot.get('switches',[])]
    blocks=[]
    for index,site in enumerate(plan['sites']):
        blocks.extend(['[[depots]]',*[f'{k} = {json.dumps(v)}' for k,v in site.items() if v is not None]])
        # All existing controlled switches survive exactly; ownership remains a
        # planning allocation. Additional yard roads need a real turnout design.
        if index==0:
            for switch in old_switches:
                blocks.extend(['[[depots.switches]]',*[f'{k} = {json.dumps(v)}' for k,v in switch.items()]])
        blocks.append('')
    text=path.read_text()
    depot_header=re.search(r'^\[\[depots\]\]\s*$',text,re.M)
    fleet_header=re.search(r'^\[\[fleets\]\]\s*$',text,re.M)
    if depot_header is None or fleet_header is None:raise ValueError('Missing controlled depot/fleet tables')
    start=depot_header.start();end=fleet_header.start()
    updated=text[:start]+'\n'.join(blocks)+'\n'+text[end:]
    updated=updated.replace('# [[depots]] — maintenance/defect facilities per RFC 0014; healthy sets stable at powered stations.',
        '# [[depots]] — one full-fleet planning depot per line; storage and workshop bays are separate, unaccepted requirements.')
    delta=plan['gross_reference_cost_usd']-d['costs']['depots_usd'];epc=tomllib.loads(cost.read_text())['overhead']['epc_fraction']
    net=d['costs']['total_usd']-d['costs']['epc_overhead_usd']+delta
    new_epc=round(net*epc);usd_to_eur=tomllib.loads(cost.read_text())['schema']['usd_to_eur']
    for key,value in [('depots_usd',plan['gross_reference_cost_usd']),('epc_overhead_usd',new_epc),('total_usd',round(net+new_epc))]:
        for name,amount in [(key,value),(key.replace('_usd','_eur'),round(value*usd_to_eur))]:
            updated,n=re.subn(r'^('+re.escape(name)+r'\s*=\s*)[^\s#]+',lambda m:m[1]+str(round(amount)),updated,count=1,flags=re.M)
            if n!=1:raise ValueError('Missing cost '+name)
    current=tomllib.loads(updated)
    if len(current['depots'])!=len(current['lines']):raise ValueError('Depot count differs from lines')
    path.write_text(updated)
    plan['sources_sha256']={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [path,CONFIG,stock,cost,power,Path(__file__)]}
    out=path.parent/'engineering/line-depots';out.mkdir(parents=True,exist_ok=True)
    (out/'summary.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
    rows=['# Line-local full-fleet depot planning scope','',*plan['limitations'],'',
          '| Line | Train length m | Storage slots | Workshop bays | Reference USD million |',
          '|---|---:|---:|---:|---:|']
    rows.extend(f"| {s['line']} | {s['train_length_m']} | {s['storage_slots']} | {s['workshop_bays']} | {s['reference_cost_usd']/1e6:.3f} |" for s in plan['sites'])
    (out/'README.md').write_text('\n'.join(rows)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--design',type=Path,required=True);a=p.parse_args();apply(a.design.resolve())
    print('Line-local depot quantities and capital applied: '+str(a.design))
if __name__=='__main__':main()
