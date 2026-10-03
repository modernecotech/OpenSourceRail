"""Move civil work towards full-fleet handover within the existing CPM graph.

Preserves the chosen crews, lane order, durations, prerequisites and opening
dates. This is an investment-timing proposal, never permission to defer surveys,
permits or land release. Physical approval remains an external release gate.
"""
from collections import defaultdict


def align_infrastructure_to_fleets(tasks, buffer_days):
    if type(buffer_days) is not int or buffer_days < 0:
        raise ValueError('civil handover buffer must be a nonnegative whole day count')
    by_uid={r['manufacturing_uid']:r for r in tasks}
    successors=defaultdict(list)
    for r in tasks:
        for uid in r['schedule_predecessor_uids'].split(';'):
            uid=uid.strip()
            if uid:
                if uid not in by_uid:raise ValueError('missing scheduled predecessor')
                successors[uid].append(r['manufacturing_uid'])
    stock=defaultdict(int);infra=defaultdict(int)
    for r in tasks:
        if r.get('line'):
            target=stock if r['asset_type']=='rolling-stock' else infra
            target[r['line']]=max(target[r['line']],r['planned_finish_day'])
        r['unphased_start_day']=r['planned_start_day']
        r['unphased_finish_day']=r['planned_finish_day']
        r['civil_rephased']=False
    if set(stock)!=set(infra):raise ValueError('civil and fleet line scopes differ')
    shared_original=max((r['planned_finish_day'] for r in tasks if not r.get('line') or r['asset_type'] in ('depot','depots-production')),default=0)
    targets={line:max(infra[line],stock[line]-buffer_days) for line in stock}
    shared_target=max(shared_original,min(stock.values())-buffer_days)
    # All resource predecessors finish before their successors. Reversing the
    # existing scheduled order therefore gives a valid dependency-backward pass.
    for r in sorted(tasks,key=lambda r:(r['unphased_start_day'],r['manufacturing_uid']),reverse=True):
        if r['asset_type'] in ('rolling-stock','system'):continue
        uid=r['manufacturing_uid']
        deadline=shared_target if not r.get('line') or r['asset_type'] in ('depot','depots-production') else targets[r['line']]
        finish=min([deadline,*[by_uid[s]['planned_start_day']-1 for s in successors[uid]]])
        start=finish-int(r['duration_days'])+1
        if start<r['unphased_start_day']:
            raise ValueError('handover target would accelerate existing resource graph')
        r.update(planned_start_day=start,planned_finish_day=finish,
                 planned_start_basis=f'project_day_{start}',planned_finish_basis=f'project_day_{finish}',
                 civil_rephased=start!=r['unphased_start_day'])
        r['total_float_days']=r['late_start_day']-start
        if r['total_float_days']<0:raise ValueError('rephasing exceeded available CPM float')
        r['is_critical']=r['total_float_days']==0
    for r in tasks:
        for uid in r['schedule_predecessor_uids'].split(';'):
            if uid.strip() and by_uid[uid.strip()]['planned_finish_day']>=r['planned_start_day']:
                raise ValueError('rephasing violated a work or resource predecessor')
    lines=[]
    for line in sorted(stock):
        finish=max(r['planned_finish_day'] for r in tasks if r.get('line')==line and r['asset_type']!='rolling-stock')
        if max(finish,stock[line])!=max(infra[line],stock[line]):raise ValueError('rephasing changed an opening milestone')
        lines.append(dict(line=line,original_infrastructure_day=infra[line],rephased_infrastructure_day=finish,
                          fleet_completion_day=stock[line],original_idle_working_days=max(0,stock[line]-infra[line]),
                          rephased_idle_working_days=max(0,stock[line]-finish)))
    return dict(status='conditional-full-fleet-civil-rephasing-not-construction-release',
                handover_buffer_working_days=buffer_days,line_completions=lines,
                shifted_work_packages=sum(r['civil_rephased'] for r in tasks),
                resource_lanes_and_durations_unchanged=True,full_fleet_and_opening_dates_unchanged=True,
                caveat='Latest feasible task offsets under the existing graph; survey, land, permits, utilities, access and contract release must be separately approved. Capital prices remain un-escalated.')
