#!/usr/bin/env python3
"""Build a source-bound Baghdad detail register without changing cost or release authority."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
CITY = ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
OUT = CITY/'engineering/detail'
PARTS = ROOT/'engineering/data/baghdad-reference-parts.json'
ELECTRONICS = ROOT/'control-electronics/reference-integration.json'


def power_envelope(data: dict) -> dict:
    efficiency = data['conversion_efficiency']
    margin = data['capacity_margin']
    minimum_v = data['minimum_design_bus_v']
    if (not all(math.isfinite(v) for v in (efficiency, margin, minimum_v, data['selected_reference_supply_capacity_w']))
            or not 0 < efficiency <= 1 or margin < 0 or minimum_v <= 0):
        raise ValueError('invalid power sizing assumptions')
    output = sum(row['power_w'] for row in data['loads'])
    if any(not math.isfinite(row['power_w']) or row['power_w'] <= 0 for row in data['loads']):
        raise ValueError('invalid load')
    input_w = output/efficiency
    capacity_w = input_w*(1+margin)
    if data['selected_reference_supply_capacity_w'] < capacity_w:
        raise ValueError('reference supply envelope is undersized')
    pins = []
    for value in data['bench_gpio'].values():
        pins.extend(value if isinstance(value, list) else [value])
    exposed = set(range(23)) | {26, 27, 28}
    if any(type(pin) is not int or pin not in exposed for pin in pins) or len(set(pins)) != len(pins):
        raise ValueError('bench pins are unavailable or duplicated')
    return dict(simultaneous_output_w=output, input_envelope_w=input_w,
                minimum_capacity_w=capacity_w, selected_capacity_w=data['selected_reference_supply_capacity_w'],
                input_current_at_minimum_bus_a=input_w/minimum_v,
                capacity_current_at_minimum_bus_a=capacity_w/minimum_v,
                consumption_measurement_status='open; capacity is not sustained energy')


def build_register() -> dict:
    design_path = CITY/'design.toml'
    scenario_path = CITY/'baghdad.toml'
    profile_path = ROOT/'lib/templates/rolling-stock.toml'
    design = tomllib.loads(design_path.read_text())
    scenario = tomllib.loads(scenario_path.read_text())
    families = {line['rolling_stock'] for line in design['lines']}
    if families != {'metro-6car'}:
        raise ValueError('detail register requires the Baghdad six-car family')
    profile = tomllib.loads(profile_path.read_text())['profiles']['metro-6car']
    trainsets = sum(row['trainset_count'] for row in design['fleets'])
    bases = dict(trainset=trainsets, car=trainsets*profile['cars'], bogie=trainsets*profile['cars']*2,
                 station=len(design['stations']), site=len(scenario['sites']), plant=1,
                 **{'t-obs':trainsets*2, 't-ecu-s':trainsets*2,
                    'route-km':sum(row['length_m'] for row in design['lines'])/1000})
    source = json.loads(PARTS.read_text())
    rows = []
    ids = set()
    for original in source['parts']:
        row = dict(original)
        if row['id'] in ids or not (ROOT/row['source']).is_file():
            raise ValueError('duplicate part identity or absent source')
        ids.add(row['id'])
        if row['supplier_part_number'] is not None or row['unit_cost'] is not None:
            raise ValueError('unqualified register cannot silently release supplier or cost data')
        per = row['quantity_per_basis']
        if per is not None and (isinstance(per, bool) or not math.isfinite(per) or per <= 0):
            raise ValueError('invalid part quantity')
        multiplier = bases.get(row['basis'])
        row['quantity_network_reference'] = per*multiplier if per is not None and multiplier is not None else None
        row['quantity_status'] = 'reference-allocation-not-purchase-order' if row['quantity_network_reference'] is not None else 'project-schedule-or-supplier-freeze-required'
        rows.append(row)
    deployment_path = ROOT/'deployment/components.toml'
    deployment = tomllib.loads(deployment_path.read_text())['component']
    workspace_path = ROOT/'Cargo.toml'
    workspace = tomllib.loads(workspace_path.read_text())
    manifests = [ROOT/member/'Cargo.toml' for member in workspace['workspace']['members']]
    names = {tomllib.loads(p.read_text())['package']['name'] for p in manifests}
    allocated = [r['name'] for r in deployment]
    if len(set(allocated)) != len(allocated) or set(allocated) != names:
        raise ValueError('software allocation and Rust workspace disagree')
    sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
    from osr_erpnext.component_catalogue import CATALOGUE, merge_profiles
    generic_path = ROOT/'deployment/erpnext/config/components.json'
    city_components_path = CITY/'operations/erp-components.json'
    effective = merge_profiles(json.loads(generic_path.read_text()),json.loads(city_components_path.read_text()))
    sources = {design_path,scenario_path,profile_path,PARTS,ELECTRONICS,deployment_path,workspace_path,
               generic_path,city_components_path,Path(__file__),*manifests}
    sources.update(ROOT/row['source'] for row in rows)
    sources.update((ROOT/'control-electronics').rglob('*.md'))
    sources.add(ROOT/'design/component-catalogue/src/osr_mech/civil/slab.py')
    sources.update([CITY/'DETAILED-ENGINEERING.md', ROOT/'deployment/erpnext/compose.yaml',
                    ROOT/'deployment/erpnext/apps/osr_erpnext/osr_erpnext/component_catalogue.py',
                    ROOT/'docs/rfcs/0007-control-electronics-reference-designs.md',
                    ROOT/'docs/rfcs/0019-diy-electronics.md'])
    return dict(schema='org.opensourcerail.baghdad-detail.v1',city='Baghdad',family='metro-6car',
                engineering_release=False, cost_model_changed=False, finance_model_changed=False,
                quantity_bases=bases, family_profile=profile,
                quantity_boundary='Net mainline reference only. Child content is nested, not additive procurement. No sidings, depot tracks, turnout deductions, cutting/weld waste, spares or method zones invented.',
                parts=rows,software_allocations=deployment,
                software_boundary='Declared composition verified against workspace, not target-driver completeness or qualified deployment. osr-runtime remains design-tooling reference.',
                t_obs_power=power_envelope(json.loads(ELECTRONICS.read_text())),
                erp=dict(profile_valid=True,workflow_components=sorted(CATALOGUE),
                         enabled_city_instances=[dict(component=r['component'],key=r['key']) for r in effective['instances'] if r.get('enabled',True)],
                         boundary='Profiles/templates only; legal company, physical bindings, approved schedules, suppliers, stock and production BOMs remain deployment-owned. Reference parts are not auto-created as live ERP Items.'),
                sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)})


def parts_csv(register: dict) -> str:
    buffer = io.StringIO(newline='')
    fields = list(register['parts'][0])
    writer = csv.DictWriter(buffer,fieldnames=fields,lineterminator='\n')
    writer.writeheader(); writer.writerows(register['parts'])
    return buffer.getvalue()



def track_drawing() -> str:
    """Dimensioned envelope only; supplier drilling remains unreleased."""
    from osr_mech.civil.slab import direct_fixation_seat_positions
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="640" viewBox="0 0 900 640">',
             '<rect width="900" height="640" fill="white"/>', '<g font-family="sans-serif" fill="#142b40">',
             '<text x="45" y="40" font-size="23">BG-C-001 — OSR-ST6 reference arrangement</text>',
             '<text x="45" y="70" font-size="14">Dimensions in mm; reinforcement, supplier anchors and drill pattern unreleased.</text>',
             '<rect x="100" y="120" width="600" height="290" fill="#e2e7eb" stroke="#657384"/>',
             '<path d="M100 97H700 M100 90V106 M700 90V106" stroke="#142b40"/>',
             '<text x="356" y="91" font-size="16">6000</text>',
             '<path d="M75 120V410 M68 120H82 M68 410H82" stroke="#142b40"/>',
             '<text x="30" y="273" font-size="16">2900</text>']
    for y in (193.25,336.75):
        parts.append(f'<rect x="100" y="{y-19}" width="600" height="38" fill="#bccbd5"/>')
        for position in direct_fixation_seat_positions():
            parts.append(f'<rect x="{100+position/10-13}" y="{y-11}" width="26" height="22" fill="#253b53"/>')
        parts.append(f'<path d="M100 {y}H700" stroke="#d27b24" stroke-width="3"/>')
    for y,text in [(443,'Seat centres: 300 + 600 × i, i = 0…9; 20 seats per panel.'),
                   (470,'Rail lines schematic: actual head profile needed for 1435 running-face gauge.'),
                   (506,'Base: 250 thick; twin plinths: 380 × 160; two rows at 3500 track centres.'),
                   (533,'Concrete: 5.0796 m³; bare mass: 12.699 t. Troughs, steel and rigging separate.'),
                   (574,'Source: osr_mech.civil.slab; Baghdad detail register.'),
                   (604,'Reference only. Not a fabrication or setting-out drawing.')]:
        parts.append(f'<text x="100" y="{y}" font-size="14">{text}</text>')
    return ''.join(parts)+'</g></svg>\n'

def render(register: dict) -> str:
    bases = register['quantity_bases']; power = register['t_obs_power']
    lines = ['# Baghdad detailed component register', '',
             'Generated from the current city design, six-car profile, engineering parts and software/ERP contracts. Engineering release remains **false**. Cost and finance rates remain unchanged; unknown unit costs are open rather than zero.', '',
             f"Reference allocation: **{bases['trainset']:,} trainsets**, **{bases['car']:,} cars**, **{bases['bogie']:,} bogies**, **{bases['station']} stations**, **{bases['site']} energy sites** and **one** shared plant.", '',
             'See [complete parts CSV](parts.csv), [source-bound register](register.json), [dimensioned ST6 reference](slab-reference.svg) and [design and Iraqi manufacturing plan](../../DETAILED-ENGINEERING.md). The two-bogie-per-car allocation and repeated mechanical kit quantities are reference architecture, subject to Metro-6car family release. Nested wheelsets, clips and batteries are not extra charges on top of complete bought assemblies.', '',
             '## Track and parts quantities', '',
             'The rail reference covers net mainline running length only. Actual procurement additionally needs alignment method zones, switches, stabling, depot track and cutting/weld/spares schedules. Slab panel totals remain **unassigned** until constrained zones are measured; rail-seat child quantities require a seat installation schedule.', '',
             '| ID | Part / assembly | Basis | Per basis | Network reference | Route |', '|---|---|---|---:|---:|---|']
    for row in register['parts']:
        value = row['quantity_network_reference']
        fmt = f'{value:,.3f}'.rstrip('0').rstrip('.') if value is not None else 'Open'
        lines.append(f"| {row['id']} | {row['title']} | {row['basis']} ({row['unit']}) | {row['quantity_per_basis'] if row['quantity_per_basis'] is not None else 'Open'} | {fmt} | {row['procurement_route']} |")
    lines.extend(['', '## Corrected onboard power envelope', '',
                  f"T-OBS simultaneous output allocation is **{power['simultaneous_output_w']:.2f} W**; at 90% efficiency, input is **{power['input_envelope_w']:.2f} W**. A 25% sizing margin requires **{power['minimum_capacity_w']:.2f} W**, selecting a **{power['selected_capacity_w']} W reference capacity**. At the assumed 18 V minimum input, envelope current is **{power['input_current_at_minimum_bus_a']:.2f} A**, or **{power['capacity_current_at_minimum_bus_a']:.2f} A** including capacity margin. These are capacity assumptions, not energy-consumption measurements or qualified fuse/converter ratings.", '',
                  '## Software host allocation', '',
                  f"All **{len(register['software_allocations'])}** workspace packages have exactly one disposition record. This verifies inventory, not physical HAL, sensor driver, firmware timing or operational safety.", '',
                  '| Component | Disposition | Hosts |','|---|---|---|'])
    for row in register['software_allocations']:
        lines.append(f"| {row['name']} | {row['disposition']} | {', '.join(row['hosts'])} |")
    lines.extend(['','## ERP coverage', '',
                  'Validated workflow contracts: '+', '.join(register['erp']['workflow_components'])+'.', '',
                  'Enabled profile instances: '+', '.join(r['component']+'/'+r['key'] for r in register['erp']['enabled_city_instances'])+'. Other workflows exist in the app but require real deployment inputs before enablement. A valid reusable profile does not mean that production orders, maintenance assignments or capital budgets have been activated.', '',
                  register['erp']['boundary'], '',
                  'Source hashes bind this report to its exact inputs. Rebuild with `.venv/bin/python engineering/baghdad_detail.py`; verify with `--check`.', ''])
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    register=build_register()
    outputs={OUT/'register.json':json.dumps(register,indent=2,sort_keys=True)+'\n',OUT/'parts.csv':parts_csv(register),OUT/'README.md':render(register),OUT/'slab-reference.svg':track_drawing()}
    if args.check:
        if any(not p.is_file() or p.read_text()!=text for p,text in outputs.items()):
            raise SystemExit('Baghdad detail outputs are stale')
    else:
        OUT.mkdir(parents=True,exist_ok=True)
        for path,text in outputs.items():path.write_text(text)
    print(f"Validated {len(register['parts'])} detail rows and {len(register['software_allocations'])} software allocations; release remains false")

if __name__ == '__main__':main()
