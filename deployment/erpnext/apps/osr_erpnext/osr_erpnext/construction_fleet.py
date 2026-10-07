"""Reusable civil assets and competent shift crews mapped to native ERP records.

Pure planning validation; no purchase, allocation or qualification is approved
by creating a draft. The live ERP integration can consume these contracts.
"""
from __future__ import annotations
from datetime import date


def validate_transfers(allocations: list[dict]) -> None:
    for row in allocations:
        if date.fromisoformat(row['finish']) < date.fromisoformat(row['start']):
            raise ValueError('asset allocation finish precedes start')
        if row.get('transfer_days',0) < 0:
            raise ValueError('transfer duration must be non-negative')
    for i,a in enumerate(allocations):
        for b in allocations[i+1:]:
            if a['asset'] != b['asset']:
                continue
            first,second=sorted((a,b),key=lambda r:r['start'])
            from datetime import timedelta
            ready=date.fromisoformat(first['finish'])+timedelta(days=first.get('transfer_days',0))
            if date.fromisoformat(second['start']) <= ready:
                raise ValueError('asset allocations/transfer/recommissioning overlap')
            if second.get('compatibility_accepted') is not True:
                raise ValueError('subsequent-city compatibility not accepted')


def fleet_economics(purchase_usd: float, commissioning_usd: float, allocation_fraction: float,
                    residual_value_usd: float, transfer_usd: float) -> dict:
    if min(purchase_usd,commissioning_usd,residual_value_usd,transfer_usd)<0 or not 0 <= allocation_fraction <= 1 or residual_value_usd>purchase_usd:
        raise ValueError('invalid fleet economics')
    return dict(initial_cash_purchase_usd=purchase_usd+commissioning_usd,
                project_cost_allocation_usd=(purchase_usd-residual_value_usd)*allocation_fraction+commissioning_usd,
                residual_value_usd=residual_value_usd,transfer_cash_usd=transfer_usd)


def validate_crew_task(task: dict, workers: list[dict]) -> None:
    for field in ('department','unit','crew','task','front','shift','equipment'):
        if not task.get(field):
            raise ValueError(f'missing task hierarchy: {field}')
    selected=[w for w in workers if w['id'] in task['workers']]
    if len(selected)!=len(task['workers']):
        raise ValueError('missing qualified worker')
    for worker in selected:
        if worker.get('on_leave') or worker.get('crew')!=task['crew'] or worker.get('shift')!=task['shift']:
            raise ValueError('worker unavailable or assigned to another shift')
        if worker.get('equipment')!=task['equipment'] or worker.get('commissioning_supervised') is not True or worker.get('equipment_assessment_passed') is not True:
            raise ValueError('equipment-specific supervised qualification required')
        if date.fromisoformat(worker['competency_expires']) < date.fromisoformat(task['finish']):
            raise ValueError('competency expired')
    roles={w['role'] for w in selected}
    if not set(task['required_roles']).issubset(roles):
        raise ValueError('required crew role missing')


def asset_draft(asset_id: str, kind: str, front: str | None) -> dict:
    return dict(asset_id=asset_id,kind=kind,native_doctype='Asset',purchase_invoice=None,commissioning_record=None,
                approved_configurations=[],inspection_history=[],maintenance_history=[],spare_parts=[],
                crew_competencies=[],location='unassigned',available=False,project='Baghdad',front=front,
                tasks=['purchase','supervised-commissioning','equipment-assessment','inspection','maintenance','dismantle','ship','recommission'],
                native_records=['Asset','Purchase Invoice','Asset Maintenance','Project','Task','Training Program'],
                cash_purchase_usd=None,project_cost_allocation_usd=None,residual_value_usd=None)


def construction_custom_fields() -> dict:
    """Install lifecycle/crew handoffs on native Asset and Task records."""
    return {
        'Employee': [dict(fieldname='custom_osr_construction_authorisations',label='Controlled construction authorisations',fieldtype='Code',options='JSON',read_only=1,no_copy=1)],
        'Asset': [dict(fieldname='custom_osr_fleet_'+name,label=label,fieldtype=kind,options=options,read_only=1,no_copy=1)
                  for name,label,kind,options in (
                      ('kind','OSR construction equipment family','Data',None),
                      ('lifecycle','OSR construction fleet lifecycle evidence','Code','JSON'),
                      ('allocation','OSR front and transfer allocations','Code','JSON'),
                      ('purchase_usd','OSR initial cash purchase (USD)','Float',None),
                      ('project_cost_usd','OSR project cost allocation (USD)','Float',None),
                      ('residual_usd','OSR residual value (USD)','Float',None))],
        'Task': [dict(fieldname='custom_osr_construction_'+name,label=label,fieldtype=kind,options=options,read_only=1,no_copy=1)
                 for name,label,kind,options in (
                     ('department','OSR construction department','Link','Department'),
                     ('unit','OSR construction unit','Data',None),
                     ('front','OSR construction front','Data',None),
                     ('crew','OSR construction crew','Data',None),
                     ('shift','OSR construction shift','Int',None),
                     ('equipment','OSR construction equipment','Link','Asset'),
                    ('qualified_workers','OSR qualified worker/competence evidence','Code','JSON'),
                     ('release','OSR reviewed construction allocation','Link','OSR Construction Release'),
                     ('work_started_at','OSR actual work start (UTC)','Datetime',None),
                     ('work_closed_at','OSR actual work close (UTC)','Datetime',None),
                     ('handover','OSR handover and relief coverage','Code','JSON'))]}
