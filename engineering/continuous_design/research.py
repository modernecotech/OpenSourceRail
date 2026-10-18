"""Persistent Pareto alternatives, constraint margins and versioned champions.

Manufacturing effort is a counted-parts proxy, never labour time or quoted cost.
Research champions retain their evidence level and exact parent-system checks.
"""
import json
import math
import time

from engineering.twin_workflow import core
from . import evidence, tasks, eligibility


def initialise(store):
    store.db.executescript("""
        CREATE TABLE IF NOT EXISTS observations (
            key TEXT PRIMARY KEY, baseline TEXT NOT NULL, lane TEXT NOT NULL,
            kind TEXT NOT NULL, context TEXT NOT NULL, concept TEXT NOT NULL,
            study_pass INTEGER NOT NULL, level TEXT NOT NULL, mass REAL,
            effort REAL, margin REAL, objectives TEXT NOT NULL, failures TEXT NOT NULL,
            pareto INTEGER NOT NULL DEFAULT 0, native_confirmed INTEGER NOT NULL DEFAULT 0,
            finished REAL NOT NULL);
        CREATE INDEX IF NOT EXISTS observations_scope ON observations(baseline,kind,context,study_pass,pareto);
        CREATE TABLE IF NOT EXISTS champions (
            id INTEGER PRIMARY KEY, baseline TEXT NOT NULL, kind TEXT NOT NULL, context TEXT NOT NULL,
            key TEXT NOT NULL, predecessor TEXT, reason TEXT NOT NULL,
            parent_checks TEXT NOT NULL, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS promotions (
            child TEXT PRIMARY KEY, baseline TEXT NOT NULL, context TEXT NOT NULL,
            task_key TEXT NOT NULL, reason TEXT NOT NULL, created REAL NOT NULL);
    """)
    store.db.commit()


def dominates(a, b):
    # Only compare available objectives with the same documented meaning.
    names = [k for k in ("mass", "effort") if a[k] is not None and b[k] is not None]
    pairs=[(a[k],b[k]) for k in names]
    if 'objectives' in a.keys() and 'objectives' in b.keys():
        first=json.loads(a['objectives']).get('manufacturing_metrics',{})
        second=json.loads(b['objectives']).get('manufacturing_metrics',{})
        for key in ('rectangular_scrap_m2','setup_count','fixture_count','inspection_count','operation_count','destructive_joint_count','blocked_replacement_count'):
            if type(first.get(key)) in (int,float) and type(second.get(key)) in (int,float):
                pairs.append((first[key],second[key]))
    return bool(pairs) and all(x<=y for x,y in pairs) and any(x<y for x,y in pairs)


def observe(store, key):
    row=store.db.execute("SELECT * FROM jobs WHERE key=?",(key,)).fetchone()
    if store.db.execute("SELECT 1 FROM observations WHERE key=?",(key,)).fetchone():
        return
    task=json.loads(row["task"]); kind=task["kind"]; result=store.result(row)
    assessment=result.get("assessment",{}); parameters=task["parameters"]
    context=parameters.get("context_id",assessment.get("context_id",kind))
    geometry=assessment.get("geometry",{}); parts=geometry.get("parts",[])
    mass=result.get("metrics",{}).get("mass_kg")
    if type(mass) not in (int,float) or not math.isfinite(mass): mass=None
    effort=len(parts) if parts else (assessment.get("metrics",{}).get("links_each_stem"))
    concept=assessment.get("candidate_family",kind)+":"+str(parameters.get("variables",{}).get("maximum_stock_piece_length_m","declared-route"))
    margins=evidence.margins(result.get("check_details",[])); margin=margins[0]["signed_normalised_distance"] if margins else None
    level=result.get("verification",{}).get("evaluated_level","legacy_unlabelled")
    if kind in {'integration-coupling','integration-protocol'}:
        root,span=context.split("/")
        context=root.split("-gross-addition-")[0]+"/"+span
        mass=result["metrics"]["gross_added_mass_kg"]
        effort=result["assessment"]["objectives"]["mass_kg"]
        concept="gross-mass-static-coupling"
    objectives=dict(mass_kg=mass,manufacturing_part_count_proxy=effort if kind not in {'integration-coupling','integration-protocol'} else None,
        coupled_civil_mass_kg=effort if kind in {'integration-coupling','integration-protocol'} else None,
        quoted_cost=None,assembly_time_seconds=None,cost_evidence=None,minimum_constraint_margin=margin,
        nearest_constraints=margins[:5],missing_objectives=["sourced cost","measured assembly time"])
    objectives['manufacturing_metrics']=result.get('manufacturing_process',{}).get('metrics',{})
    store.db.execute("INSERT INTO observations(key,baseline,lane,kind,context,concept,study_pass,level,mass,effort,margin,objectives,failures,finished) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (key,row["baseline"],row["lane"],kind,context,concept,int(result["study_pass"]),level,mass,effort,margin,
            json.dumps(objectives),json.dumps(result.get("failed_checks",[])),row["finished"] or time.time()))
    if kind.endswith("-confirmation"):
        child=parameters["child"]
        if result.get("verification",{}).get("levels",{}).get("native_geometry",{}).get("state")=="passed":
            store.db.execute("UPDATE observations SET native_confirmed=1 WHERE key=?",(child,))
        eligibility.refresh(store,row['baseline'])
        parent=store.db.execute("SELECT context FROM observations WHERE key=?",(child,)).fetchone()
        if parent:
            source=store.db.execute('SELECT task FROM jobs WHERE key=?',(child,)).fetchone()
            child_kind=json.loads(source['task'])['kind']
            champion=store.db.execute("SELECT j.* FROM champions c JOIN jobs j ON c.key=j.key WHERE c.baseline=? AND c.context=? AND c.kind=? ORDER BY c.id DESC LIMIT 1",(row["baseline"],parent["context"],child_kind)).fetchone()
            if champion and not store.db.execute("SELECT 1 FROM promotions WHERE child=?",(champion["key"],)).fetchone():
                promote_candidate(store,champion,json.loads(champion["task"]),store.result(champion))
        return
    eligible=kind in (tasks.CONFIRMABLE|{'integration-coupling','integration-protocol'}) and result["study_pass"] and mass is not None and eligibility.Resolver(store,row['baseline']).state(key)['eligible']
    if eligible:
        peers=list(store.db.execute("SELECT * FROM observations WHERE baseline=? AND kind=? AND context=? AND study_pass=1 AND mass IS NOT NULL",
            (row["baseline"],kind,context)))
        resolver=eligibility.Resolver(store,row['baseline'])
        peers=[p for p in peers if resolver.state(p['key'])['eligible']]
        current=next(p for p in peers if p["key"]==key)
        # Different structural/manufacturing concepts keep their own frontier.
        frontier=not any(p["concept"]==concept and dominates(p,current) for p in peers)
        if frontier:
            store.db.execute("UPDATE observations SET pareto=1 WHERE key=?",(key,))
            for peer in peers:
                if peer["concept"]==concept and dominates(current,peer):
                    store.db.execute("UPDATE observations SET pareto=0 WHERE key=?",(peer["key"],))
        prior=store.db.execute("SELECT c.*,o.mass,o.effort FROM champions c JOIN observations o ON c.key=o.key WHERE c.baseline=? AND c.kind=? AND c.context=? ORDER BY c.id DESC LIMIT 1",
            (row["baseline"],kind,context)).fetchone()
        if prior and not eligibility.Resolver(store,row['baseline']).state(prior['key'])['eligible']:
            prior=None
        if prior is None or mass < prior["mass"]-1e-9 or (mass==prior["mass"] and effort is not None and prior["effort"] is not None and effort<prior["effort"]):
            reason="Initial passing research candidate" if prior is None else "Lower modeled mass with unchanged implemented checks; cost/time remain unknown"
            store.db.execute("INSERT INTO champions(baseline,kind,context,key,predecessor,reason,parent_checks,created) VALUES(?,?,?,?,?,?,?,?)",
                (row["baseline"],kind,context,key,prior["key"] if prior else None,reason,
                    json.dumps(dict(checks=result.get("checks",{}),children=result.get("children",[]),level=level)),time.time()))
    active_path=store.workspace/"active.json"
    active=core.read(active_path)["baseline_sha256"] if active_path.exists() else row["baseline"]
    if kind in tasks.CONFIRMABLE and row["baseline"]==active:
        promote_candidate(store,row,task,result)


def promote_candidate(store,row,task,result,*,final=False):
    context=task["parameters"]["context_id"]
    if result.get("search_blocked"):
        return
    if task['kind'] in tasks.STUDY_KINDS and not result.get('physical_contract_sha256'):
        # A rejected installation has no exact physical model to confirm.
        return
    existing=list(store.db.execute("SELECT * FROM promotions WHERE baseline=? AND context=?",(row["baseline"],context)))
    if any(p["child"]==row["key"] for p in existing):return
    pending=store.db.execute("SELECT COUNT(*) FROM promotions p JOIN jobs j ON p.task_key=j.key WHERE p.baseline=? AND p.context=? AND j.status IN ('queued','running','deferred')",(row["baseline"],context)).fetchone()[0]
    if pending>=4:return
    if len(existing)>=4 and not final:
        previous=store.db.execute("SELECT MIN(o.mass) FROM promotions p JOIN observations o ON p.child=o.key WHERE p.baseline=? AND p.context=? AND o.study_pass=1",(row["baseline"],context)).fetchone()[0]
        mass=result.get("metrics",{}).get("mass_kg")
        if not result["study_pass"] or previous is None or mass is None or mass>=.95*previous:
            return
    if not result["study_pass"] and any(p["reason"]=="representative adverse candidate" for p in existing):
        return
    if result["study_pass"]:
        obs=store.db.execute("SELECT pareto FROM observations WHERE key=?",(row["key"],)).fetchone()
        if not final and not obs["pareto"]:
            return
    reason="Final best candidate after context idle/stagnation" if final else "Pareto candidate for higher-fidelity confirmation" if result["study_pass"] else "representative adverse candidate"
    kind=(tasks.KINDS[task['kind']]+'-study-confirmation') if task['kind'] in tasks.STUDY_KINDS else task["kind"].replace("-detail","-confirmation")
    value=tasks.task(kind,dict(child=row["key"]),reason,parent=row["key"])
    store.enqueue(value,row["baseline"],priority=-10)
    store.db.execute("INSERT OR IGNORE INTO promotions(child,baseline,context,task_key,reason,created) VALUES(?,?,?,?,?,?)",
        (row["key"],row["baseline"],context,tasks.identity(value,row["baseline"]),reason,time.time()))


def confirm_final_candidates(store,baseline,*,now=None,stagnation_seconds=900):
    """Confirm the exact best revision after idle/stagnation, regardless of 5%."""
    now=time.time() if now is None else now
    added=0
    for champion in eligibility.champions(store,baseline):
        if champion['kind'] not in tasks.CONFIRMABLE:
            continue
        context=champion['context']
        pending=store.db.execute("SELECT COUNT(*) FROM jobs WHERE baseline=? AND json_extract(task,'$.kind')=? AND json_extract(task,'$.parameters.context_id')=? AND status IN ('queued','running','deferred')",
            (baseline,champion['kind'],context)).fetchone()[0]
        if pending and now-champion['created']<stagnation_seconds:
            continue
        if store.db.execute('SELECT 1 FROM promotions WHERE child=?',(champion['key'],)).fetchone():
            continue
        row=store.db.execute('SELECT * FROM jobs WHERE key=?',(champion['key'],)).fetchone()
        promote_candidate(store,row,json.loads(row['task']),store.result(row),final=True)
        added+=bool(store.db.execute('SELECT 1 FROM promotions WHERE child=?',(champion['key'],)).fetchone())
    return added


def summary(store,baseline):
    resolver=eligibility.Resolver(store,baseline)
    counts=dict(evaluated=0,rejected=0,analytically_passing=0,native_confirmed=0,
        numerically_confirmed=0,executable_verified=0,integrated=0,adopted_for_research=0)
    for row in store.db.execute("SELECT * FROM observations WHERE baseline=?",(baseline,)):
        counts["evaluated"]+=1;counts["rejected"]+=not row["study_pass"]
        counts["analytically_passing"]+=bool(row["study_pass"] and row["level"]=="analytical_screening")
        counts["native_confirmed"]+=bool(row["native_confirmed"] or (row["study_pass"] and row["level"]=="native_geometry"))
        counts["numerically_confirmed"]+=bool(row["study_pass"] and row["level"] in {"numerical_confirmation","numerical_robustness"})
        counts["executable_verified"]+=bool(row["study_pass"] and row["level"]=="executable_verification")
        counts["integrated"]+=bool(row["study_pass"] and row["kind"] in {'integration-coupling','integration-protocol'} and resolver.state(row['key'])['eligible'])
    champions=eligibility.champions(store,baseline,resolver)
    counts["adopted_for_research"]=sum(c["kind"] in {'integration-coupling','integration-protocol'} for c in champions)
    latest=store.db.execute("SELECT MAX(created) FROM champions WHERE baseline=?",(baseline,)).fetchone()[0]
    confirmed=store.db.execute("SELECT MAX(finished) FROM observations WHERE baseline=? AND kind LIKE '%-confirmation' AND study_pass=1",(baseline,)).fetchone()[0]
    useful=max([t for t in (latest,confirmed) if t is not None],default=None)
    dispositions=dict(store.db.execute('SELECT state,COUNT(*) FROM integration_dispositions WHERE baseline=? GROUP BY state',(baseline,)))
    return dict(counts=counts,counts_overlap=True,champions=champions,integration_dispositions=dispositions,last_useful_improvement_unix=useful,
        last_champion_change_unix=latest,last_higher_fidelity_confirmation_unix=confirmed,
        adoption_scope="Versioned research shortlist for the declared checks; all release gates remain open",
        pareto_count=store.db.execute("SELECT COUNT(*) FROM observations WHERE baseline=? AND pareto=1",(baseline,)).fetchone()[0])


def tradeoffs(store,baseline,lane):
    resolver=eligibility.Resolver(store,baseline)
    return [dict(key=r["key"],context=r["context"],concept=r["concept"],verification_level=r["level"],
        native_confirmed=bool(r["native_confirmed"]),objectives=json.loads(r["objectives"])) for r in store.db.execute(
        "SELECT * FROM observations WHERE baseline=? AND lane=? AND pareto=1 ORDER BY mass,key",(baseline,lane)) if resolver.state(r['key'])['eligible']][:8]


def coverage(store,baseline,lane):
    kind=lane+"-detail"
    if lane not in {"mechanical","civil"}:return {}
    domains=tasks.domain_description(lane)[kind]["variables"]
    result={}
    for name,choices in domains.items():
        values=[r[0] for r in store.db.execute("SELECT DISTINCT json_extract(task,?) FROM jobs WHERE baseline=? AND json_extract(task,'$.kind')=?",('$.parameters.variables.'+name,baseline,kind)) if r[0] is not None]
        result[name]=dict(explored_values=sorted(values),unexplored_values=[x for x in choices if x not in values])
    return result


def progress_signature(store,baseline,lane):
    champion=store.db.execute("SELECT MAX(c.id) FROM champions c JOIN observations o ON c.key=o.key WHERE c.baseline=? AND o.lane=?",(baseline,lane)).fetchone()[0]
    failures=[r[0] for r in store.db.execute("SELECT DISTINCT f.value FROM observations o,json_each(o.failures) f WHERE o.baseline=? AND o.lane=? ORDER BY f.value",(baseline,lane))]
    native=store.db.execute("SELECT COUNT(DISTINCT context) FROM observations WHERE baseline=? AND lane=? AND native_confirmed=1",(baseline,lane)).fetchone()[0]
    return dict(baseline=baseline,lane=lane,champion_revision=champion,failure_categories=failures,
        native_contexts=native,coverage=coverage(store,baseline,lane))


def priority(store,value):
    if value["parent"]:
        parent=store.db.execute("SELECT study_pass,pareto FROM observations WHERE key=?",(value["parent"],)).fetchone()
        if parent and parent["study_pass"] and parent["pareto"]:return 5
    return 15
