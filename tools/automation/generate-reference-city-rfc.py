#!/usr/bin/env python3
"""Publish the current Samawah reference without retaining stale network totals."""
from pathlib import Path
import argparse
import hashlib
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/city-generation/src'))
from osr_scenario.stats import compute_stats
from osr_scenario.generator import _BATTERY_USABLE_FRACTION
DESIGN=ROOT/'cities/catalogue/west-asia/Iraq/Samawah/design.toml'
SCENARIO=DESIGN.with_name('samawah.toml')
OUTPUT=ROOT/'docs/rfcs/0003-samawah-reference-deployment.md'


def build():
    d=tomllib.loads(DESIGN.read_text());scenario=tomllib.loads(SCENARIO.read_text());stats=compute_stats(DESIGN)
    fleet={r['line']:r for r in d['fleets']}
    line_rows=[]
    for line in d['lines']:
        name=line['name'];stock=fleet[name]
        line_rows.append(f"| {name} | {line['length_m']/1000:.3f} | {sum(s['line']==name for s in d['stations'])} | {stock['trainset_count']} |")
    civil={kind:sum(s['to_station_m']-s['from_station_m'] for s in d['civil_segments'] if s['class']==kind)/1000
           for kind in ['at-grade','elevated','bridge']}
    civil_rows=[f'| {kind} | {km:.3f} |' for kind,km in civil.items()]
    sources=[DESIGN,SCENARIO,ROOT/'design/city-generation/src/osr_scenario/stats.py',
             ROOT/'design/city-generation/src/osr_scenario/generator.py',Path(__file__).resolve()]
    fingerprint=hashlib.sha256(b''.join(p.read_bytes() for p in sources)).hexdigest()
    battery=scenario['consist']['battery_capacity_kwh'];reserve=100*(1-_BATTERY_USABLE_FRACTION)
    totals=stats.as_markdown_table().replace(f'~{stats.route_km:.0f} km',f'{stats.route_km:.3f} km')
    return '\n'.join([
        '# RFC 0003 — Samawah Current Reference Deployment','',
        '**Status:** Controlled planning example; construction and operating releases remain open.',
        f'<!-- GENERATED CURRENT REFERENCE: {fingerprint} -->','',
        'Regenerate with `python3 tools/automation/generate-reference-city-rfc.py`. The city design and scenario are the controlled inputs; this RFC reports their current quantities. [Earlier planning figures and brownfield observations](../reference/history/samawah-pre-core-planning.md) remain explicitly historical.', '',
        '## 1. Purpose','',
        f"Samawah is an Iraqi reference instance of the shared deployment model. Its retained catalogue population is {d['city']['population']:,}; the population and income proxies are planning inputs. The example uses the same geometry, energy, fleet, staffing and factory rules as other catalogue cities. Baghdad retains its own funding programme; its government share, Chinese USD credit and IQD bond structure are not applied to Samawah.",'',
        '[Current city summary](../../cities/catalogue/west-asia/Iraq/Samawah/README.md) · [Controlled design](../../cities/catalogue/west-asia/Iraq/Samawah/design.toml) · [Scenario](../../cities/catalogue/west-asia/Iraq/Samawah/samawah.toml)','',
        '## 2. Existing assets and local investigation','',
        'The earlier railway-yard and workshop observations are candidates for a site census, tooling audit, ownership/access review and material testing. They do not establish usable capacity, recovered-component acceptance or a capital saving. Any brownfield proposal must close the releases in [RFC 0027](0027-brownfield-pilot-asset-recovery.md). The current full-fleet depot requirement is retained until a verified site alternative replaces it.', '',
        '## 3. Current generated network','',
        '### 3.1 Lines','',
        '| Line | Route km | Platform records | Total trainsets |','|---|---:|---:|---:|',*line_rows,'',
        '![Current Samawah network](../../cities/catalogue/west-asia/Iraq/Samawah/samawah-network-map.png)','',
        'The central planning concept straightens and elevates suitable core corridors. Analytical curve controls are recorded where verified by the generator; unsuitable fragments retain explicit geometry-review gates. Outer corridors retain their controlled routing seeds. Property rights, utilities, foundations, clearances and station footprints remain project investigations.', '',
        '### 3.2 Transfers and platform siting','',
        f'The current design records {stats.interchange_count} multi-line interchange groups. Platform IDs remain distinct on their own lines. Declared transfers and bounded dry-bank moves preserve the checked walking legs; they do not demonstrate a surveyed paid-area connection, accessible footprint or stable bank. [Water screen](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/alignment/station-water-screen.json) · [Alignment review](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/alignment/core-realignment.json).','',
        '### 3.3 Revenue and finance','',
        'Use the [current finance ledger](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/finance/summary.json) for fare assumptions, commercial income, graded payroll, energy and financing sensitivities. These are planning estimates, rather than observed ridership or committed funding. Generic country finance is a fixed-price steady-state screen; Baghdad’s indexed monthly cashflow studies remain separate.', '',
        '### 3.4 System totals','',totals,'',
        'Station totals count the unique listed platform records, including individual interchange platforms. Revenue fleet is the controlled peak requirement; reserve roles and any service-rotation stock remain separate in the design. A full-fleet planning depot is provided for each line and sized to the actual train count and consist length.', '',
        '### 3.5 Civil quantities','',
        '| Civil class | Route km |','|---|---:|',*civil_rows,'',
        'These are route kilometres for a double-track system. Geometry and unit-cost targets do not release pi-beam prestress, complete-member lifting masses, foundations, bridge interaction or temporary works. [Civil standard](0011-civil-infrastructure-design-standard.md).', '',
        '## 4. Operations, trainsets and labour','',
        f"The controlled consist uses {scenario['consist']['car_count']} cars and {battery:g} kWh gross battery capacity. Its {reserve:g}% protected reserve leaves {battery*(1-reserve/100):g} kWh above that reserve before operational derates. Climate/HVAC, ageing, charging availability and service recovery are checked separately; a static battery calculation cannot establish full-day performance.",'',
        'Timetables, dwell and fleet roles come from the scenario. [Operating evidence](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/simulation/validation-summary.json) records the actual model inputs, executable and outputs. Native station dispatch remains a software planning screen; full-depot access, launch throughput, local operating qualification and physical acceptance remain releases.', '',
        'Each listed station/platform has two posts and two normal eight-hour shifts, plus cover for the actual service window, weekends, leave, training and sickness. Role-based wages start at 150% of the configured country income proxy, with higher technical/management grades and employer allowances. [Operating-scope controls](../../lib/templates/city-operating-scope.toml) and the finance ledger retain the reconciled headcounts and payroll.', '',
        '## 5. Factories, energy and acceptance','',
        'The [factory plan](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/factory/README.md) is sized to this city’s actual order and vehicle family. Facility readiness is 18 months; qualification, serial manufacture and integrated acceptance follow it. A civil completion date is not automatically an opening date. National factory sharing requires a separately committed production sequence.', '',
        'Use the [current energy study](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/energy/summary.json), [line-depot quantities](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/line-depots/summary.json), and [operations package](../../cities/catalogue/west-asia/Iraq/Samawah/operations/samawah-operations-manifest.json). Depot PV/storage is priced once per site. Buffered snapshots, grid-only diagnostics and native duty-cycle evidence have distinct scopes. Supplier, installation, utility, maintenance, independent-check and authority approvals remain open.', '',
        '[Architecture](../ARCHITECTURE.md) · [Construction QA](0028-construction-quality-assurance.md) · [Maintenance system](0029-maintenance-schedule-system.md)',''])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();text=build()
    if a.check:
        if OUTPUT.read_text()!=text:raise ValueError('Stale current Samawah reference RFC')
    else:OUTPUT.write_text(text)
    print('Current Samawah reference RFC: quantities bound to controlled design/scenario')

if __name__=='__main__':main()
