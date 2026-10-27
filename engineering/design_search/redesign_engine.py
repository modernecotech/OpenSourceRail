"""Execute grammar rewrites; a new topology gets a fresh physical identity."""
from . import design_grammar as grammar
from engineering.station_rail.common import identity


def revise(candidate,diagnosis,*,maximum=3):
    if diagnosis.get('candidate_id')!=candidate['candidate_id'] or diagnosis['diagnosis_id']!=identity({k:v for k,v in diagnosis.items() if k!='diagnosis_id'}):raise ValueError('Exact physical/diagnosis identity required')
    if type(maximum) is not int or not 1<=maximum<=4:raise ValueError('Bounded rewrite batch required')
    rows=[];tasks=[]
    for action in diagnosis['actions']:
        if action['operator'] is None:tasks.append(action);continue
        if len(rows)>=maximum:continue
        child=grammar.rewrite(candidate,action['operator'],reason=action['reason'])
        if child['candidate_id']==candidate['candidate_id']:continue
        rows.append(dict(operator=action['operator'],candidate=child,trigger_diagnosis_id=diagnosis['diagnosis_id']))
    return dict(schema='osr-executed-grammar-revisions/1',parent_candidate_id=candidate['candidate_id'],revisions=rows,model_and_measurement_tasks=tasks,
        physical_designs_generated=len(rows),integrated_selection=None)
