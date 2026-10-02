#!/usr/bin/env python3
"""Reproducible equivalent-service lifecycle NPV, with unknown inputs retained.

This is an engineering comparison, not approval to remove equipment or export
savings into a city estimate. Currency and quantities require reviewed inputs.
"""
import argparse, json, math
from pathlib import Path

def number(value, name, missing):
    if value is None:missing.append(name);return None
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:raise ValueError('invalid '+name)
    return float(value)

def compare(model):
    missing=[];service=model['service_basis'];checked={k:number(v,'service.'+k,missing) for k,v in service.items()}
    for k in ('route_length_km','fleet','headway_seconds','years'):
        if checked[k] is not None and checked[k]<=0:raise ValueError('positive '+k+' required')
    for k in ('availability','discount_rate'):
        if checked[k] is not None and checked[k]>1:raise ValueError('invalid fraction '+k)
    if checked['years'] is not None and int(checked['years'])!=checked['years']:raise ValueError('whole analysis years required')
    totals=[0.0,0.0]
    for row in model['equipment']:
        if len(row['quantities'])!=2 or len(row['unit_costs'])!=2:raise ValueError('both equivalent options required')
        for i in range(2):
            q=number(row['quantities'][i],row['item']+'.quantity.'+str(i),missing)
            cost=number(row['unit_costs'][i],row['item']+'.unit_cost.'+str(i),missing)
            if q is not None and cost is not None:totals[i]+=q*cost
    lifecycle={}
    for option in model['options']:
        values=model['lifecycle'][option]
        lifecycle[option]={k:number(v,option+'.'+k,missing) for k,v in values.items()}
        for k in ('local_content_fraction','import_content_fraction'):
            if lifecycle[option][k] is not None and lifecycle[option][k]>1:raise ValueError('invalid content fraction')
        local,imported=(lifecycle[option][k] for k in ('local_content_fraction','import_content_fraction'))
        if local is not None and imported is not None and abs(local+imported-1)>1e-9:raise ValueError('content fractions must sum to one')
    for removal in model['equipment_removals']:
        if not removal.get('replacement_function') or not removal.get('accepted_evidence'):missing.append('unjustified equipment removal')
    report={'state':'incomplete-inputs','currency':model['currency'],'missing':missing,'equipment_totals':None,'lifecycle_npv':None,'savings':None,'city_cost_export_authorised':False}
    if missing:return report
    years=int(checked['years']);rate=checked['discount_rate'];factor=sum((1+rate)**(-year) for year in range(1,years+1))
    npv={}
    for i,option in enumerate(model['options']):
        v=lifecycle[option];initial=totals[i]+v['initial_spares_cost']+v['integration_cost']+v['assessment_cost']
        annual=(v['calibration_hours_per_year']+v['maintenance_hours_per_year'])*v['labour_cost_per_hour']+v['recovery_hours_per_year']*v['disruption_cost_per_hour']
        npv[option]=round(initial+annual*factor,2)
    report.update(state='comparison-unreviewed',equipment_totals=dict(zip(model['options'],totals)),lifecycle_npv=npv,savings=round(npv[model['options'][0]]-npv[model['options'][1]],2))
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('model',type=Path);a=p.parse_args();print(json.dumps(compare(json.loads(a.model.read_text())),indent=2))
