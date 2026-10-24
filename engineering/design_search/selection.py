"""Purpose-specific Pareto selection; failed experiments cannot become baselines."""
from .contracts import FLAGS, MATURITY, finite, identity, inventory_summary, validate_candidate, validate_result


def pareto(rows,objectives):
    """Minimise declared finite objective names; unknowns are not zero."""
    if not objectives:raise ValueError('declared Pareto objectives required')
    for row in rows:
        for name in objectives:finite(row['metrics'].get(name),'objective '+name)
    def dominates(a,b):
        av=[a['metrics'][name] for name in objectives];bv=[b['metrics'][name] for name in objectives]
        return all(x<=y for x,y in zip(av,bv)) and any(x<y for x,y in zip(av,bv))
    return [row for row in rows if not any(dominates(other,row) for other in rows)]


def select(candidates,results,*,purpose,policy):
    """Policy names critical evaluators, objectives, maturity and confirmations."""
    if purpose not in ('next-experiment','integrated-baseline'):raise ValueError('explicit selection purpose required')
    if not isinstance(policy,dict) or not policy.get('policy_id') or not policy.get('objectives'):raise ValueError('named declared selection policy required')
    objective_weights=policy['objectives']
    for name,weight in objective_weights.items():finite(weight,'objective weight',True)
    by_candidate={candidate['candidate_id']:validate_candidate(candidate) for candidate in candidates}
    by_evaluation={result['evaluation_id']:validate_result(result) for result in results}
    if len(by_evaluation)!=len(results):raise ValueError('unique evaluation results required')
    grouped={key:[] for key in by_candidate};rejections={};rankable=[]
    for result in results:
        if result['candidate_id'] not in grouped:raise ValueError('selection result has an unknown physical candidate')
        if result['requirement_revision']!=by_candidate[result['candidate_id']]['requirement_revision']:raise ValueError('mixed requirement revisions')
        grouped[result['candidate_id']].append(result)
    for candidate_id,candidate in by_candidate.items():
        rows=grouped[candidate_id];primary=[row for row in rows if row['purpose']!='confirmation'];reasons=[]
        metrics={}
        hypothesis=policy.get('required_hypothesis',policy.get('hypothesis'))
        if hypothesis is not None and any(any(row['request']['hypothesis'].get(key)!=value for key,value in hypothesis.items()) for row in primary):
            reasons.append('incompatible-declared-hypothesis')
        for name in {row['request']['evaluator_id'] for row in primary}:
            contexts={identity({key:row['request'][key] for key in ('hypothesis','settings','mesh','scenario','evaluator_sources','environment')})
                      for row in primary if row['request']['evaluator_id']==name}
            if len(contexts)>1:reasons.append('ambiguous-primary-context:'+name)
        for result in primary:
            for name,value in result['metrics'].items():
                if name in metrics and metrics[name]!=value:
                    aggregation=policy.get('metric_aggregation',{}).get(name)
                    if aggregation=='max':metrics[name]=max(metrics[name],value);continue
                    if aggregation=='min':metrics[name]=min(metrics[name],value);continue
                    reasons.append('conflicting-unaggregated-metric:'+name);continue
                metrics[name]=value
        if any(metrics.get(name) is None for name in objective_weights):reasons.append('missing-objective')
        if purpose=='integrated-baseline':
            critical=policy.get('critical_evaluators',[])
            if not critical:raise ValueError('integrated baseline requires explicit critical evaluators')
            minimum=policy.get('minimum_maturity','coupled-numerical')
            if minimum not in MATURITY:raise ValueError('known minimum maturity required')
            if MATURITY[minimum]<MATURITY['coupled-numerical']:raise ValueError('integrated baseline cannot lower the coupled numerical maturity floor')
            if not inventory_summary(candidate)['complete_installed_distribution']:reasons.append('incomplete-installed-inventory')
            selected=[]
            for name in critical:
                matches=[row for row in primary if row['request']['evaluator_id']==name]
                if len(matches)!=1:reasons.append('missing-or-ambiguous-critical:'+name);continue
                row=matches[0];selected.append(row)
                if row['execution_status']!='executed' or row['numerical_status']!='converged' or row['screen_status']!='pass':reasons.append('critical-not-pass:'+name)
                if MATURITY[row['maturity']]<MATURITY[minimum]:reasons.append('insufficient-maturity:'+name)
                if policy.get('require_confirmation',True):
                    links=[*row['confirmation_evaluation_ids'],*policy.get('confirmation_links',{}).get(row['evaluation_id'],[])]
                    confirmations=[by_evaluation[key] for key in links if key in by_evaluation]
                    good=[item for item in confirmations if item['candidate_id']==candidate_id and item['purpose']=='confirmation'
                        and item['screen_status']=='pass' and item['request']['settings'].get('confirmation_of')==row['evaluation_id']
                        and (item['request']['scenario']!=row['request']['scenario'] or item['request']['evaluator_sources']!=row['request']['evaluator_sources'])
                        and (policy.get('required_confirmation_scope') is None or item['request']['settings'].get('verification_scope')==policy['required_confirmation_scope'])
                        and (policy.get('required_confirmation_scope')!='independent-domain'
                             or set(item['request']['evaluator_sources'].values())!=set(row['request']['evaluator_sources'].values()))]
                    if not good:reasons.append('missing-independent-confirmation:'+name)
            contexts={row['request']['settings'].get('coupling_context_id') for row in selected}
            if None in contexts or len(contexts)!=1:reasons.append('incompatible-or-missing-coupling-context')
        elif not any(row['execution_status'] in ('executed','refused') for row in primary):reasons.append('no-executed-evidence')
        if reasons:rejections[candidate_id]=reasons
        else:rankable.append(dict(candidate_id=candidate_id,metrics={name:finite(metrics[name],name) for name in objective_weights},evaluation_ids=sorted(row['evaluation_id'] for row in rows)))
    frontier=pareto(rankable,list(objective_weights)) if rankable else []
    ranked=sorted(frontier,key=lambda row:(sum(row['metrics'][name]*weight for name,weight in objective_weights.items()),row['candidate_id']))
    value=dict(schema='osr-design-selection/1',purpose=purpose,policy=policy,
        candidate_ids=sorted(by_candidate),evaluation_ids=sorted(by_evaluation),pareto_candidate_ids=[row['candidate_id'] for row in frontier],
        selected_candidate_id=ranked[0]['candidate_id'] if ranked else None,rejections=rejections,
        status='selected-for-'+purpose if ranked else 'no-eligible-candidate',global_optimum_proven=False,**FLAGS)
    value['selection_id']=identity(value);return value
