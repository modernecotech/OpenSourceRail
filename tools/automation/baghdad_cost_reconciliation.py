#!/usr/bin/env python3
"""Compare the reviewed Baghdad baseline with the same-alignment cost correction."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib

ROOT=Path(__file__).resolve().parents[2]
CITY=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad'
BASELINE='d4cd3db2cda7c770125713d9522b169d1d1edbd3'
CORRECTED_ALIGNMENT_BASELINE='a1a14f6d2936d9227836aff9c01de8a1fbb3d5c0'


def historical(revision,path):
    relative=path.relative_to(ROOT).as_posix()
    archive=CITY/'engineering/cost-reconciliation/baseline-sources.json.gz'
    if archive.is_file():
        retained=json.loads(gzip.decompress(archive.read_bytes()))
        if retained['revision']!=revision:raise ValueError('Baseline snapshot revision differs')
        row=retained['sources'][relative];raw=row['text'].encode()
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Baseline snapshot changed')
        return raw,row['sha256']
    raw=subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)
    return raw,hashlib.sha256(raw).hexdigest()


def retained_correction(paths):
    """Retain the actual last same-alignment correction before later route edits."""
    archive=ROOT/'engineering/network-planning/baghdad/corrected-alignment-sources.json.gz'
    archive.parent.mkdir(parents=True,exist_ok=True)
    if archive.is_file():
        snapshot=json.loads(gzip.decompress(archive.read_bytes()))
        if snapshot['revision']!=CORRECTED_ALIGNMENT_BASELINE:raise ValueError('Correction snapshot revision differs')
    else:
        rows={}
        for path in paths.values():
            relative=path.relative_to(ROOT).as_posix()
            raw=subprocess.check_output(['git','show',CORRECTED_ALIGNMENT_BASELINE+':'+relative],cwd=ROOT)
            rows[relative]=dict(text=raw.decode(),sha256=hashlib.sha256(raw).hexdigest())
        snapshot=dict(revision=CORRECTED_ALIGNMENT_BASELINE,sources=rows)
        packed=bytearray(gzip.compress((json.dumps(snapshot,sort_keys=True)+'\n').encode(),mtime=0));packed[9]=255
        archive.write_bytes(packed)
    corrected={}
    for name,path in paths.items():
        row=snapshot['sources'][path.relative_to(ROOT).as_posix()];raw=row['text'].encode()
        if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('Correction snapshot changed')
        corrected[name]=tomllib.loads(raw.decode()) if name=='design' else json.loads(raw)
    return corrected,archive


def generate(revision=BASELINE):
    paths=dict(design=CITY/'design.toml',case=CITY/'engineering/programme-recalculation/local_positive.json',
        finance=CITY/'engineering/finance/summary.json',people=CITY/'engineering/programme-recalculation/workforce.json')
    baseline={};records={};retained={}
    for name,path in paths.items():
        raw,digest=historical(revision,path);baseline[name]=tomllib.loads(raw.decode()) if name=='design' else json.loads(raw)
        records[path.relative_to(ROOT).as_posix()]=digest
        retained[path.relative_to(ROOT).as_posix()]=dict(text=raw.decode(),sha256=digest)
    current={name:tomllib.loads(path.read_text()) if name=='design' else json.loads(path.read_text()) for name,path in paths.items()}
    out=CITY/'engineering/cost-reconciliation';out.mkdir(exist_ok=True)
    archive=out/'baseline-sources.json.gz'
    if not archive.is_file():
        packed=bytearray(gzip.compress((json.dumps(dict(revision=revision,sources=retained),sort_keys=True)+'\n').encode(),mtime=0))
        packed[9]=255;archive.write_bytes(packed)
    changed=[key for key in ('lines','stations','fleets','depots') if baseline['design'][key]!=current['design'][key]]
    corrected,correction_archive=retained_correction(paths) if changed else (current,None)
    for key in ('lines','stations','fleets','depots'):
        if baseline['design'][key]!=corrected['design'][key]:raise ValueError('Same-alignment correction snapshot changed controlled '+key)
    old,new=baseline['case']['metrics'],current['case']['metrics']
    old_month=next(r for r in baseline['case']['monthly'] if r['month']==101)
    new_month=next(r for r in current['case']['monthly'] if r['month']==101)
    fx=tomllib.loads((ROOT/'lib/templates/baghdad-programme-recalculation.toml').read_text())['model']['iqd_per_usd']
    operating={key:dict(previous_annualised_usd=old_month[key]*12/fx,current_annualised_usd=new_month[key]*12/fx)
        for key in ('revenue_iqd','opex_iqd','extra_receipts_iqd')}
    operating['balance_before_debt']=dict(previous_annualised_usd=(old_month['revenue_iqd']+old_month['extra_receipts_iqd']-old_month['opex_iqd'])*12/fx,
        current_annualised_usd=(new_month['revenue_iqd']+new_month['extra_receipts_iqd']-new_month['opex_iqd'])*12/fx)
    source_paths=[Path(__file__),archive,ROOT/'lib/templates/baghdad-programme-recalculation.toml',*paths.values()]
    if correction_archive:source_paths.append(correction_archive)
    receipt=dict(schema='baghdad-cost-and-alignment-reconciliation/2',baseline_revision=revision,
        historical_sources_sha256=records,
        sources_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        controlled_routes_stations_fleets_and_depots_unchanged=not changed,
        same_alignment_monetary_correction_verified=True,
        same_alignment_correction_revision=CORRECTED_ALIGNMENT_BASELINE if changed else 'current-source',
        same_alignment_corrected_capital_usd=corrected['case']['metrics']['total_capital_usd'],
        subsequent_alignment_revision=dict(changed_controlled_fields=changed,
            previous_route_m=sum(l['length_m'] for l in corrected['design']['lines']),current_route_m=sum(l['length_m'] for l in current['design']['lines']),
            capital_delta_from_corrected_reference_usd=new['total_capital_usd']-corrected['case']['metrics']['total_capital_usd'],
            geometry_changes_are_not_search_score_cost_savings=True),
        traction_duty= dict(previous=baseline['finance']['operations_basis'],current=current['finance']['operations_basis']),
        previous_planning_capital_usd=old['total_capital_usd'],current_base_planning_capital_usd=new['total_capital_usd'],
        correction_is_a_realised_saving=False,complete_installed_budget=False,
        current_special_structure_increment_usd=None,
        previous_unfunded_support_iqd=old['unfunded_support_iqd'],current_unfunded_support_iqd=new['unfunded_support_iqd'],
        previous_terminal_debt_iqd=old['terminal_all_debt_iqd'],current_terminal_debt_iqd=new['terminal_all_debt_iqd'],
        previous_payroll_iqd=baseline['people']['reference_annual_loaded_payroll_iqd'],
        current_payroll_iqd=current['people']['reference_annual_loaded_payroll_iqd'],
        previous_workforce_fte=baseline['people']['reference_required_fte'],current_workforce_fte=current['people']['reference_required_fte'],
        capacity_led_paid_journeys={name:dict(previous=case['annual_paid_trips'],current=current['finance']['cases'][name]['annual_paid_trips'])
            for name,case in baseline['finance']['cases'].items()},
        previous_base_opex_components=baseline['finance']['annual_opex_usd'],current_base_opex_components=current['finance']['annual_opex_usd'],
        monthly_101_annualisation=operating,
        maintenance_basis='Capital-percentage allowance follows corrected base price; not a demonstrated reduction in physical maintenance tasks',
        energy_payroll_and_trip_quantities_are_not_reduced_by_search_score_correction=True,
        financing_committed=False,physical_release=False)
    out=CITY/'engineering/cost-reconciliation';out.mkdir(exist_ok=True)
    (out/'summary.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    snapshot_link=os.path.relpath(correction_archive,out) if correction_archive else 'baseline-sources.json.gz'
    text=f'''# Baghdad cost correction and subsequent alignment reconciliation

**Base planning allowance; complete installed price and financing remain unresolved.**

The original `{revision[:10]}` monetary correction is verified against the retained same-alignment `{receipt['same_alignment_correction_revision'][:10]}` reference. The current design subsequently changed controlled fields {', '.join(changed) if changed else 'none'}. The latest values below therefore include separately recorded alignment effects; they are not all attributed to a same-geometry price correction. Route-search scores remain excluded from prices.

| Measure | Reviewed baseline | Corrected base case |
|---|---:|---:|
| Programme allowance, USD bn | {old['total_capital_usd']/1e9:.3f} | {new['total_capital_usd']/1e9:.3f} |
| Unfunded support, IQD tn | {old['unfunded_support_iqd']/1e12:.3f} | {new['unfunded_support_iqd']/1e12:.3f} |
| Terminal debt, IQD tn | {old['terminal_all_debt_iqd']/1e12:.3f} | {new['terminal_all_debt_iqd']/1e12:.3f} |
| Operating FTE | {receipt['previous_workforce_fte']} | {receipt['current_workforce_fte']} |
| Loaded annual payroll, IQD bn | {receipt['previous_payroll_iqd']/1e9:.3f} | {receipt['current_payroll_iqd']/1e9:.3f} |

The allowance correction is not a supplier saving, accepted alternative or complete delivery budget. Special/segmental increments, actual foundations, installed grid/charging upgrades, land, utilities and other closure items remain unpriced. Maintenance follows the corrected capital-percentage allowance; physical inspection, replacement and access workloads still require independent quantities and prices. The correction grants no lower staffing, traction duty or surveyed demand requirement.

The same-alignment corrected reference capital is USD {corrected['case']['metrics']['total_capital_usd']/1e9:.6f}bn; the current alignment changes it by USD {new['total_capital_usd']-corrected['case']['metrics']['total_capital_usd']:,.2f} in the unquoted model. The current route is {receipt['subsequent_alignment_revision']['current_route_m']/1000:.4f} km against {receipt['subsequent_alignment_revision']['previous_route_m']/1000:.4f} km in that reference. [The retained corrected snapshot]({snapshot_link}) preserves the original stage when an alignment revision exists; its bytes are also in the companion planning archive.

The original baseline bytes are retained in [the source snapshot](baseline-sources.json.gz), so a fresh shallow checkout can reproduce this comparison offline. Month 101 comparisons in the [source-bound reconciliation](summary.json) annualise one nominal model month, rather than predicting a calendar year. Paid journeys remain capacity-led; no population-to-fare uplift is adopted. The [demand handoff](../demand-bridge/README.md), [energy closure](../delivery-closure/SITE-ENERGY.md), [clearance screen](../clearance/README.md) and [current programme ledger](../programme-recalculation/README.md) retain their separate acceptance gates.
'''
    (out/'README.md').write_text(text)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',default=BASELINE);a=p.parse_args();generate(a.baseline)
