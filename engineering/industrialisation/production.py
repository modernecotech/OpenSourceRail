"""Work-order trace validation and process-window checks for local manufacturing."""
from __future__ import annotations
from .common import artifact,finite,timestamp,fingerprint,ROOT


def process_window(samples,minimum,maximum,minimum_duration_s,maximum_gap_s):
    if minimum is None or maximum is None or minimum_duration_s is None or maximum_gap_s is None:
        return dict(status='open-process-window',within_window=None,production_released=False)
    lo,hi=finite(minimum,'process minimum'),finite(maximum,'process maximum')
    hold=finite(minimum_duration_s,'minimum hold',0.);gap=finite(maximum_gap_s,'maximum sampling gap',1e-9)
    if lo>hi or len(samples)<2:raise ValueError('ordered process window and at least two samples required')
    last=None;start=None;within=True;gaps=True
    for t,value in samples:
        t=finite(t,'process time',0.);value=finite(value,'process observation')
        if last is not None and t<=last:raise ValueError('ordered process timestamps required')
        if start is None:start=t
        if last is not None and t-last>gap:gaps=False
        within=within and lo<=value<=hi;last=t
    passed=within and gaps and last-start>=hold
    return dict(status='ready-for-independent-review' if passed else 'process-window-failed',within_window=within,
        sampling_complete=gaps,recorded_duration_s=last-start,minimum_duration_s=hold,
        record_checks_passed=passed,production_released=False)


def traveler_template(package):
    return dict(schema='osr-factory-traveler-record/1',package_sha256=fingerprint(package),
        configuration_sha256=package['configuration_sha256'],asset_id=package['asset_id'],work_order=None,record_id=None,
        operations=[dict(id=r['id'],instance_id=r['instance_id'],part_revision=r['part_revision'],serial=r['serial'],batch=r['batch'],
            operator=None,inspector=None,performed_at=None,disposition='not-performed',evidence=[],open_ncr_ids=[]) for r in package['operations']],
        production_released=False)


def assess_traveler(package,record,root=ROOT):
    required={'schema','package_sha256','configuration_sha256','asset_id','work_order','record_id','operations','production_released'}
    if set(record)!=required or record['schema']!='osr-factory-traveler-record/1' or record['production_released'] is not False:
        raise ValueError('traveler contract invalid or attempted automatic release')
    if record['package_sha256']!=fingerprint(package) or record['configuration_sha256']!=package['configuration_sha256'] or record['asset_id']!=package['asset_id']:
        raise ValueError('traveler targets a stale or different build configuration')
    expected={r['id']:r for r in package['operations']};actual={r['id']:r for r in record['operations']}
    if set(actual)!=set(expected) or len(actual)!=len(record['operations']):raise ValueError('complete unique operation coverage required')
    blockers=[];completed={};seen_measurements=set()
    if package['state'] not in ('as-built','as-maintained') or not package['asset_id']:blockers.append('identified physical configuration required')
    if not record['work_order'] or not record['record_id']:blockers.append('work order and record identity missing')
    if not package['full_component_coverage']:blockers.append('unresolved full-train component allocation')
    for identifier,row in actual.items():
        target=expected[identifier]
        for key in ('instance_id','part_revision','serial','batch'):
            if row[key]!=target[key]:raise ValueError('traveler physical part/revision identity changed')
        if row['disposition']!='performed' or not row['operator'] or not row['inspector'] or not row['performed_at']:
            blockers.append(identifier+': unperformed or unsigned');continue
        if row['operator']==row['inspector']:raise ValueError('operator cannot independently inspect own work')
        if not (row['serial'] or row['batch']):blockers.append(identifier+': physical serial/batch missing')
        if row['open_ncr_ids']:blockers.append(identifier+': unresolved nonconformance')
        if target['acceptance_limits'] is None:blockers.append(identifier+': released acceptance criteria missing')
        kinds=[]
        for ref in row['evidence']:
            artifact(ref,root);kinds.append(ref['kind'])
            if ref['kind']=='measurement':
                identity=(ref['path'],ref['sha256'])
                if identity in seen_measurements:raise ValueError('measurement evidence reused across operations without a scoped record')
                seen_measurements.add(identity)
        if not set(target['required_evidence_kinds'])<=set(kinds):blockers.append(identifier+': missing required evidence')
        if target['special_process']:
            window=target['released_process_window']
            if window is None:blockers.append(identifier+': qualified special-process window missing')
            else:
                artifact(window['procedure'],root,kind='procedure')
                result=process_window(row.get('process_samples',[]),window['minimum'],window['maximum'],window['minimum_duration_s'],window['maximum_gap_s'])
                if not result.get('record_checks_passed',False):blockers.append(identifier+': special-process trace outside/without released window')
        completed[identifier]=timestamp(row['performed_at'])
    for identifier,when in completed.items():
        for predecessor in expected[identifier]['predecessors']:
            if predecessor not in completed or completed[predecessor]>when:blockers.append(identifier+': predecessor hold point not satisfied')
    return dict(schema='osr-factory-traveler-assessment/1',record_sha256=fingerprint(record),blockers=sorted(set(blockers)),
        ready_for_independent_quality_review=not blockers,production_released=False,physical_validation=False,
        native_erp_records_changed=False)
