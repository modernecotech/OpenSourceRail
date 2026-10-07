"""Current Iraq publication basis; financial comparators and unpriced studies stay distinct."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'design/component-catalogue/src'))
from osr_mech.provenance import input_revision

COUNTRY=ROOT/'cities/catalogue/west-asia/Iraq'
CITY=COUNTRY/'Baghdad'
BEGIN='<!-- OSR CURRENT IRAQ BASIS -->'
END='<!-- END OSR CURRENT IRAQ BASIS -->'
HISTORICAL_INTRO='The calculation below retains the earlier USD 7.581bn scope and its own assumptions. Its debt-clearance months and financial differences do not describe the current `local_positive` comparator or the unpriced accelerated scenario.'


def read(path):
    return json.loads(path.read_text())


def current_basis():
    study=CITY/'engineering/connected-build'
    programme=CITY/'engineering/programme-recalculation'
    case=read(programme/'local_positive.json')
    manifest=read(study/'manifest.json')
    civil=read(study/'civil.json');energy=read(study/'energy.json');costs=read(study/'costs.json')
    control=read(study/'energy-control.json') if (study/'energy-control.json').exists() else {'cases':{}}
    inputs=[Path(__file__),programme/'summary.json',programme/'local_positive.json',
            study/'manifest.json',study/'civil.json',study/'energy.json',study/'costs.json',
            ROOT/'lib/templates/precast-suppliers.json',ROOT/'lib/templates/precast-logistics.json']
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    for name in ('energy-control.json','station-passenger-demand.json','movement-profiles.json'):
        path=study/name
        if path.exists():hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    metrics=case['metrics']
    return dict(schema=1,as_of=manifest['assumptions']['schema']['as_of'],
        source_revision=input_revision(hashes),source_revision_kind='sha256-input-content',sources_sha256=hashes,
        financial_case=dict(id='local_positive',status='unquoted-retained-financial-comparator',
            capital_usd=metrics['total_capital_usd'],imported_invoices_usd=metrics['imported_invoices_usd'],
            local_capital_usd=metrics['total_capital_usd']-metrics['imported_invoices_usd'],
            government_share=metrics['government_share'],unfunded_support_iqd=metrics['unfunded_support_iqd'],
            terminal_debt_iqd=metrics['terminal_all_debt_iqd'],all_debt_cleared_month=metrics['all_debt_cleared_month'],
            financing_committed=metrics['financing_committed']),
        accelerated_case=dict(complete_installed_budget=costs['complete_installed_budget'],
            capital_usd=None,financing_required_usd=costs['financing_required_usd'],
            net_station_saving_usd=costs['net_station_savings_usd'],opening_accepted=False,
            launcher_purchase_allowance=costs['launcher_allowance'],
            construction={name:dict(days=row['days'],scope=row['scope'],qualified=False,
                completed_bays=sum(row['completed_bays'].values()),
                factory_peak_storage=row['supply_chain']['factory_peak_storage'])
                for name,row in civil['conditional_scenarios'].items()},
            energy={name:dict(minimum_soc=row['runs'][0]['minimum_soc'],
                unserved_traction_kwh=row['runs'][0]['totals']['unserved_traction_kwh'],
                service_qualified=False) for name,row in energy['cases'].items()},
            dispatch_shortfalls=len(energy['scheduled_dispatch_shortfalls']),
            controlled_energy={name:dict(dispatched_journeys=row['dispatched_journeys'],completed_journeys=row['completed_journeys'],
                missed_dispatches=len(row['missed_dispatches']),energy_held_journeys=row['distinct_energy_held_journeys'],
                minimum_soc=row['minimum_soc'],service_qualified=False) for name,row in control['cases'].items()},
            energy_duration_minutes=energy.get('duration_minutes'),
            stationary_grid_replenishment=energy.get('stationary_grid_replenishment',False),
            operating_distance_findings=energy.get('operating_distance_findings',[])),
        national_budget_usd=None,national_rollout_financed=False,
        factory_scope='Iraq has existing precast facilities and expertise; qualify contracted civil supply and price tooling/upgrades. Baghdad trainset assembly and component-process allowances remain in the financial comparator. Additional national plant capacity and transfer costs require separate scope reconciliation.',
        procurement_evidence=dict(named_suppliers=len(read(ROOT/'lib/templates/precast-suppliers.json')['suppliers']),
                                 qualified_contract_capacity_entered=False,supplier_quotations=0))


def current_header(basis=None):
    b=basis or current_basis();f=b['financial_case'];a=b['accelerated_case']
    duration=a.get('energy_duration_minutes')
    duration_text=f"{duration:,} continuous model minutes ({duration/1440:.2f} days)" if duration else 'the retained planning duty'
    recharge_text='a study strategy permitting grid replenishment within remaining site import capacity' if a['stationary_grid_replenishment'] else 'solar replenishment of stationary storage'
    debt_text='It records no month in which all debt is cleared.' if f['all_debt_cleared_month'] is None else f"All debt clears at model month {f['all_debt_cleared_month']}, conditional on the recorded funding assumptions."
    launcher_m=a['launcher_purchase_allowance']['central_cash_allowance_usd']/1e6
    construction='\n'.join(f"| {name} | {row['days']} | {row['scope']} |" for name,row in a['construction'].items())
    energy='\n'.join(f"| {name} | {row['minimum_soc']:.1%} | {row['unserved_traction_kwh']:,.0f} |" for name,row in a['energy'].items())
    controlled='\n'.join(f"| {name} | {row['completed_journeys']:,} | {row['missed_dispatches']:,} | {row['energy_held_journeys']:,} |" for name,row in a.get('controlled_energy',{}).items())
    return f'''{BEGIN}
## Current Iraq planning basis — {b['as_of']}

[Current country basis](CURRENT-PLANNING-BASIS.json) · [Baghdad summary](Baghdad/README.md) · [Connected design, production and energy study](Baghdad/engineering/connected-build/README.md).

The retained `local_positive` Baghdad financial comparator is **USD {f['capital_usd']/1e9:.3f}bn**, with **IQD {f['unfunded_support_iqd']/1e12:.3f}tn unsourced support** and **IQD {f['terminal_debt_iqd']/1e12:.3f}tn terminal debt**. {debt_text} Its prices and facilities are unquoted and uncommitted. It does not price the complete accelerated construction and battery scenario.

The accelerated scenario's complete CAPEX, financing, net island savings and accepted opening dates remain unknown. Its **USD {launcher_m:g}m / 18-launcher allowance covers purchase cash only**; freight, assembly, commissioning, transporters, lifting frames, temporary supports, spares, crews and relocations require separate scope-matched prices. The earlier delivered-and-commissioned interpretation is not used. No launcher saving is added to an installed civil rate before removing a verified matching embedded allowance.

{b['factory_scope']}

No current consolidated national budget or funded rollout is established. Other Iraqi city catalogue estimates and the earlier generic foreign-turnkey calculation remain separately identified comparators. Their differences are scenario arithmetic, not realised capital or interest savings. Baghdad's later scope cannot be mixed into an older national aggregate and presented as one complete budget.

### Construction sensitivities

| Case | Days for modelled running bays | Scope |
| --- | ---: | --- |
{construction}

These are conditional resource schedules. Station structures, special/closure spans, approved pier locations, delivery access and release evidence remain opening gates. Empty supplier/contract registers indicate missing qualifying evidence; they do not imply that Iraqi industry lacks capability.

### Chronological energy study

| Case, lower-solar duty | Minimum SOC | Unserved traction kWh |
| --- | ---: | ---: |
{energy}

The fixed-assignment diagnostic above uses both ring directions, declared dispatch stations and native rest-to-rest section timing. The current screen spans {duration_text}, including overnight state carry-over and {recharge_text}. Charge-rate, thermal and life inputs are unqualified profiles, so these results do not establish a chemistry advantage or suitability.

The separate [coupled energy/service controller](Baghdad/engineering/connected-build/energy-control.json) keeps reserve-limited trains at their actual stations, continues charging, and reflects their availability in subsequent dispatch opportunities.

| Controlled case | Completed journeys | Missed dispatch opportunities | Distinct energy-held journeys |
| --- | ---: | ---: | ---: |
{controlled}

Geometry/operating-distance findings remain recorded. Conflict-capable timetable, berth/depot access, transient traction and operational multi-day acceptance remain open. Current station passenger demand is unknown where no surveyed station/OD assignment has been entered; the common 3,000 pax/h value is retained only as a separate stress case.
{END}
'''


def funding_document(historical, basis=None):
    # Strip presentation contexts before retaining the original calculation.
    import re
    text=re.sub(r'<!-- OSR CURRENT SCOPE CONTEXT -->.*?<!-- END OSR CURRENT SCOPE CONTEXT -->\n\n?', '', historical,flags=re.S)
    if END in text:
        text=text.split('## Historical funding calculation — retained comparator',1)[-1].lstrip()
        if text.startswith(HISTORICAL_INTRO):
            text=text[len(HISTORICAL_INTRO):].lstrip()
    else:
        text=text.split('\n',1)[-1]
    return '# Iraq funding programme and Baghdad planning status\n\n'+current_header(basis)+'\n## Historical funding calculation — retained comparator\n\n'+HISTORICAL_INTRO+'\n\n'+text.lstrip()


def write_basis():
    b=current_basis()
    (COUNTRY/'CURRENT-PLANNING-BASIS.json').write_text(json.dumps(b,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return b
