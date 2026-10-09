"""Bounded multi-seed Pareto search against an equal-budget random baseline.

The evaluator is a native reduced system, not a surrogate or a cost assertion.
Shortlists remain research results pending detailed confirmation and acceptance.
"""
from __future__ import annotations
from copy import deepcopy
import math
from pathlib import Path
import time

import numpy as np
from .contracts import encoded,identity,dependencies,load,sha,validate_study
from .workflow import candidate,environment
from .model import System,takeoff

VARIABLES=[('deck','top_m',.12,.24),('deck','bottom_m',.08,.18),('deck','wall_m',.10,.24),
           ('pier','wall_m',.15,.35),('pier','top_scale',.75,1.)]


def dominates(a,b):
    if a['violation']!=b['violation'] and (a['violation']>0 or b['violation']>0):return a['violation']<b['violation']
    return all(x<=y for x,y in zip(a['objectives'],b['objectives'])) and any(x<y for x,y in zip(a['objectives'],b['objectives']))


def fronts(rows):
    remaining=list(rows);result=[]
    while remaining:
        layer=[r for r in remaining if not any(dominates(s,r) for s in remaining if s is not r)]
        if not layer:raise ValueError('Pareto sorting failed')
        result.append(layer);ids={id(r) for r in layer};remaining=[r for r in remaining if id(r) not in ids]
    return result


def select(rows,count):
    chosen=[]
    for layer in fronts(rows):
        if len(chosen)+len(layer)<=count:chosen.extend(layer);continue
        distance={id(r):0. for r in layer}
        for objective in range(len(layer[0]['objectives'])):
            ordered=sorted(layer,key=lambda r:r['objectives'][objective])
            distance[id(ordered[0])]=distance[id(ordered[-1])]=math.inf
            extent=ordered[-1]['objectives'][objective]-ordered[0]['objectives'][objective]
            if extent:
                for i in range(1,len(ordered)-1):distance[id(ordered[i])]+=(ordered[i+1]['objectives'][objective]-ordered[i-1]['objectives'][objective])/extent
        chosen.extend(sorted(layer,key=lambda r:distance[id(r)],reverse=True)[:count-len(chosen)]);break
    return chosen


def run(study,output,*,seeds=(11,23,47),evaluations=48,population=12,wall_seconds=600,resume=False):
    validate_study(study)
    if output.exists() and not resume:raise ValueError('search output already exists')
    if not 16<=evaluations<=1000 or not 4<=population<=evaluations or not 1<=len(seeds)<=8 or not 10<=wall_seconds<=3600:
        raise ValueError('search budget outside registered bounds')
    output.mkdir(parents=True,exist_ok=resume);(output/'candidates').mkdir(exist_ok=resume);(output/'results').mkdir(exist_ok=resume)
    source=dependencies();native=environment();started=time.monotonic();cache={};events=[];all_rows=[];summaries=[]
    frozen=dict(study=study,source_hashes=source,native_environment=native,
                budgets=dict(seeds=list(seeds),evaluations=evaluations,population=population,wall_seconds=wall_seconds))
    elapsed_before=0.
    if resume:
        if load(output/'input.json')!=frozen:raise ValueError('search resume source/environment/input mismatch')
        checkpoint=load(output/'checkpoint.json')
        for relative,digest in checkpoint['file_hashes'].items():
            path=(output/relative).resolve()
            if not path.is_relative_to(output.resolve()) or not path.is_file() or sha(path)!=digest:raise ValueError('search checkpoint artifact mismatch')
        cache={r['candidate_id']:r for p in (output/'results').glob('*.json') for r in [load(p)]}
        import json
        events=[json.loads(line) for line in (output/'ledger.jsonl').read_text().splitlines()]
        elapsed_before=checkpoint['elapsed_s']
    else:(output/'input.json').write_bytes(encoded(frozen))
    prior_events={(e['seed'],e['method'],e['iteration']):e for e in events}
    reference=study['candidates'][1];parent=candidate(reference,study)
    (output/'candidates'/f'{parent["id"]}.json').write_bytes(encoded(parent))
    lower=np.asarray([r[2] for r in VARIABLES]);upper=np.asarray([r[3] for r in VARIABLES])
    def checkpoint():
        if dependencies()!=source:raise ValueError('search source changed during execution')
        paths=[output/'input.json',output/'ledger.jsonl',*list((output/'candidates').glob('*.json')),*list((output/'results').glob('*.json'))]
        payload=dict(elapsed_s=elapsed_before+time.monotonic()-started,
                     file_hashes={p.relative_to(output).as_posix():sha(p) for p in paths if p.exists()})
        temporary=output/'checkpoint.tmp';temporary.write_bytes(encoded(payload));temporary.replace(output/'checkpoint.json')
    def evaluate(vector,seed,method,iteration,parents):
        if elapsed_before+time.monotonic()-started>wall_seconds:raise TimeoutError('registered search campaign wall budget exhausted')
        design=deepcopy(reference);design['deck']['family']='hollow-box';design['pier']['family']='hollow-tapered'
        design['deck']['parameters']={};design['pier']['parameters']={}
        for (part,key,_,_),value in zip(VARIABLES,vector):design[part]['parameters'][key]=round(float(value),8)
        try:
            c=candidate(design,study,parents=parents,reason=f'{method} seed {seed} iteration {iteration}')
        except ValueError as error:
            identifier=identity(dict(rejected_definition=design,study_material=study['material']))
            row=dict(candidate_id=identifier,definition={k:design[k] for k in ('deck','pier')},variables=vector.tolist(),
                     objectives=[1e30]*3,violation=1e30,status='geometry-rejected',error=str(error),physical_release=False)
            cache[identifier]=row
            (output/'results'/f'{identifier}.json').write_bytes(encoded(row))
            event=dict(seed=seed,method=method,iteration=iteration,candidate_id=identifier,parents=list(parents),status='geometry-rejected')
            events.append(event)
            with (output/'ledger.jsonl').open('ab') as stream:stream.write(encoded(event).replace(b'\n',b'')+b'\n')
            checkpoint();return {**row,'seed':seed,'method':method}
        event=dict(seed=seed,method=method,iteration=iteration,candidate_id=c['id'],parents=list(parents),variables=vector.tolist())
        previous=prior_events.get((seed,method,iteration))
        if previous:
            if previous['candidate_id']!=c['id']:raise ValueError('resumed search trajectory differs from checkpoint')
            return {**cache[c['id']],'seed':seed,'method':method}
        if c['id'] in cache:
            row=cache[c['id']];event['status']='verified-cache-hit'
        else:
            try:
                s=deepcopy(study);s['analysis']['static_positions']=9
                results=[]
                for ground in s['ground_scenarios']:
                    model=System(c,s,ground,s['analysis']['meshes'][0]);results.append(model.static_envelope()['envelope'])
                q=takeoff(c,s)
                values=[q['installed_study_mass_kg'],max(r['relative_deck_deflection_m'] for r in results),max(r['foundation_settlement_m'] for r in results)]
                limit=s['research_limits']['suspended_mass_kg']
                violation=0. if limit is None else max(0.,q['suspended_mass_kg']/limit-1.)
                row=dict(candidate_id=c['id'],definition=c['definition'],variables=vector.tolist(),objectives=values,violation=violation,
                         status='completed',quantities=q,reduced_native_responses=results,engineering_feasibility='unresolved',physical_release=False)
                event['status']='completed'
            except (ValueError,RuntimeError) as error:
                row=dict(candidate_id=c['id'],definition=c['definition'],variables=vector.tolist(),objectives=[1e30]*3,violation=1e30,
                         status='failed',error=str(error),engineering_feasibility='unresolved',physical_release=False)
                event['status']='failed'
            cache[c['id']]=row
            (output/'candidates'/f'{c["id"]}.json').write_bytes(encoded(c))
            (output/'results'/f'{c["id"]}.json').write_bytes(encoded(row))
        events.append(event)
        with (output/'ledger.jsonl').open('ab') as stream:stream.write(encoded(event).replace(b'\n',b'')+b'\n')
        checkpoint()
        return {**row,'seed':seed,'method':method}
    timeout=False
    for seed in seeds:
        for method in ('random','pareto-evolution'):
            rng=np.random.default_rng(seed);rows=[];pool=[]
            try:
                for i in range(evaluations):
                    if method=='random' or i<population:
                        vector=rng.uniform(lower,upper);parents=[parent['id']]
                    else:
                        chosen=select(pool,min(population,len(pool)))
                        a,b,d=[chosen[j] for j in rng.choice(len(chosen),3,replace=False)]
                        vector=np.asarray(a['variables'])+.6*(np.asarray(b['variables'])-np.asarray(d['variables']))
                        vector=np.clip(vector+rng.normal(0.,.04,len(VARIABLES))*(upper-lower),lower,upper)
                        parents=list(dict.fromkeys([a['candidate_id'],b['candidate_id'],d['candidate_id']]))
                    row=evaluate(vector,seed,method,i,parents);rows.append(row);pool=select(pool+[row],population)
            except TimeoutError:
                timeout=True
            feasible=[r for r in rows if r['status']=='completed' and r['violation']==0.]
            front=fronts(feasible)[0] if feasible else []
            summaries.append(dict(seed=seed,method=method,requested_evaluations=evaluations,completed_evaluations=len(rows),
                                  provisional_feasibility_yield=len(feasible)/max(1,len(rows)),pareto_ids=[r['candidate_id'] for r in front],
                                  best_mass_kg=min((r['objectives'][0] for r in feasible),default=None)))
            all_rows.extend(rows)
            if timeout:break
        if timeout:break
    completed=[r for r in cache.values() if r['status']=='completed' and r['violation']==0.]
    shortlist=select(fronts(completed)[0],min(5,len(fronts(completed)[0]))) if completed else []
    report=dict(schema='osr-civil-search/1',source_hashes=source,native_environment=native,
                budgets=dict(seeds=list(seeds),evaluations_per_method=evaluations,population=population,wall_seconds=wall_seconds),
                elapsed_s=elapsed_before+time.monotonic()-started,status='budget-exhausted' if timeout else 'completed',
                variables=[dict(part=p,name=n,minimum=a,maximum=b) for p,n,a,b in VARIABLES],
                objective_names=['installed study mass kg','worst relative static deflection m','worst support settlement m'],
                methods=summaries,unique_native_evaluations=len(cache),shortlist=[r['candidate_id'] for r in shortlist],
                qualified_feasible_pareto_set=[],physical_release=False,
                detailed_confirmation_required=True,missing_requirements=['accepted strength/fatigue/seismic limits','measured soil/materials','supplier complete prices'])
    (output/'search.json').write_bytes(encoded(report));(output/'study.json').write_bytes(encoded(study))
    return report
