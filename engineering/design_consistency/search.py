"""Mixed research search with disjoint mandatory gates and independent holdouts."""
import math
import numpy as np
from osr_mech.engineering_definition import fingerprint
from osr_mech.rolling_stock import composite_panels as panel
from .analysis import mandatory_status


def evaluate(config,variables,*,pressure_pa=2000):
    grade=panel.coupled_core(config,int(variables['grade']));count=int(variables['supports']);core=float(variables['core_m']);crown=.05 if variables['curved'] else 0
    height=2.35 if crown else 3.45;span=(panel.roof_arc(height,crown)['arc_length_m']-.12)/(count-1)
    abd=panel.laminate_abd(panel.balanced_skin(.0015),core,.0002,config['glass']);r=panel.strip_response(abd,pressure_pa,span,core,grade['shear_pa'],stiffness_factor=.65,shear_factor=.5)
    c={**config,'core':{**config['core'],**grade}};network=panel.support_network(c,.994,panel.roof_arc(height,crown)['arc_length_m'],span)
    q=panel.panel_quantities(c,.994,height,.0015,core,crown=crown,insert_count=network['panel_attachment_count']);mass=q['installed_mass_kg']+network['mass_kg']
    checks={'deflection':'passed'if r['total_deflection_m']<=.005 else'failed','thermal':'failed'if crown and grade['continuous_max_temperature_c']<85 else'unknown',
        'fire':'unknown','fatigue':'unknown','joint_contact':'unknown','supplier_batch_and_hot_wet':'unknown','manufacturing':'unknown'}
    return dict(candidate_id=fingerprint(dict(variables=variables,config=config,pressure_pa=pressure_pa)),variables=variables,
        mass_kg=mass,attachment_count=network['panel_attachment_count'],deflection_m=r['total_deflection_m'],
        installed_cost_usd=None,lifecycle_cost_usd=None,carbon_kg_co2e=None,repair_minutes=None,
        checks=checks,status=mandatory_status(checks),qualified=False,
        objectives=[mass,float(network['panel_attachment_count'])],pressure_pa=pressure_pa)


def pareto(rows):
    # Unknown evidence is explicitly conditional, never a verified frontier.
    eligible=[r for r in rows if r['status']!='blocked']
    return [r['candidate_id']for r in eligible if not any(all(a<=b for a,b in zip(s['objectives'],r['objectives']))and any(a<b for a,b in zip(s['objectives'],r['objectives']))for s in eligible)]


def run(config,*,seeds=(11,29,47),evaluations=64):
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.core.variable import Real,Integer,Choice,Binary
    from pymoo.core.mixed import MixedVariableGA
    from pymoo.operators.survival.rank_and_crowding import RankAndCrowding
    from pymoo.optimize import minimize
    if evaluations<16 or len(set(seeds))<2:raise ValueError('multiple distinct seeds and usable budget required')
    class Problem(ElementwiseProblem):
        def __init__(self):
            super().__init__(vars=dict(core_m=Real(bounds=(.02,.03)),supports=Integer(bounds=(3,8)),grade=Choice(options=[60,80,100]),curved=Binary()),n_obj=2,n_ieq_constr=2)
            self.rows=[]
        def _evaluate(self,x,out,*args,**kwargs):
            values={k:(bool(v)if k=='curved'else int(v)if k in ('supports','grade')else float(v))for k,v in x.items()};r=evaluate(config,values);self.rows.append(r)
            out['F']=r['objectives'];out['G']=[r['deflection_m']/.005-1,1 if r['checks']['thermal']=='failed'else -1]
    trials=[]
    for seed in seeds:
        problem=Problem();minimize(problem,MixedVariableGA(pop_size=16,survival=RankAndCrowding()),termination=('n_eval',evaluations),seed=seed,verbose=False,copy_algorithm=False,copy_termination=False)
        rng=np.random.default_rng(seed);random=[]
        for i in range(len(problem.rows)):
            variables=dict(core_m=float(rng.uniform(.02,.03)),supports=int(rng.integers(3,9)),grade=int(rng.choice([60,80,100])),curved=bool(rng.integers(2)))
            random.append(evaluate(config,variables))
        ids=pareto(problem.rows);selected=[r for r in problem.rows if r['candidate_id']in ids]
        holdout=[evaluate(config,r['variables'],pressure_pa=3500)for r in selected]
        trials.append(dict(seed=seed,evaluation_count=len(problem.rows),candidates=problem.rows,random_benchmark=random,conditional_pareto=ids,holdout_pressure_pa=3500,holdout=holdout,
            optimisation_minimum_conditional_mass_kg=min((r['mass_kg']for r in selected),default=None),random_minimum_conditional_mass_kg=min((r['mass_kg']for r in random if r['status']!='blocked'),default=None)))
    return dict(schema='osr-mixed-evidence-search/1',config_sha256=fingerprint(config),algorithm='pymoo mixed-variable GA with Pareto survival',
        objectives=['installed mass','attachment count complexity proxy'],unresolved_objectives=['quoted installed/lifecycle cost','repair time','controlled carbon'],
        trials=trials,verified_pareto=[],physical_validation=False,production_released=False,global_optimum_claimed=False,
        refinement_required=['trimmed plate/contact solve','mesh convergence','ranking consistency versus detailed models','prototype correlation'])
