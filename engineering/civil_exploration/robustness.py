"""Declared range scenarios, native shortlist reruns and ranking reversals."""
from __future__ import annotations
from copy import deepcopy
from .contracts import encoded
from .workflow import candidate
from .model import System,takeoff

SCENARIOS=[('nominal',1.,1.,1.),('lower-stiffness',.8,1.,1.),('higher-stiffness',1.2,1.,1.),
           ('heavier-material',1.,1.1,1.),('lighter-material',1.,.9,1.),
           ('softer-foundation',1.,1.,.5),('stiffer-foundation',1.,1.,2.)]


def run(candidates,study,output):
    if output.exists():raise ValueError('robustness output already exists')
    output.mkdir(parents=True);rows=[];rankings={}
    for name,stiffness,density,ground_factor in SCENARIOS:
        ranked=[]
        for original in candidates:
            s=deepcopy(study);s['analysis']['static_positions']=9
            s['material']=deepcopy(original['material']);s['material']['youngs_modulus_pa']*=stiffness;s['material']['density_kg_m3']*=density
            s['mass_allowances']=original['mass_allowances'];s['foundation']=original['foundation']
            for g in s['ground_scenarios']:
                for key in ('axial_stiffness_n_m','lateral_stiffness_n_m','rotational_stiffness_nm_rad'):g[key]*=ground_factor
            c=candidate(original['definition'],s,parents=[] if name=='nominal' else [original['id']],reason='declared uncertainty scenario '+name)
            responses=[System(c,s,g,16).static_envelope()['envelope'] for g in s['ground_scenarios']]
            q=takeoff(c,s)
            result=dict(scenario=name,nominal_candidate_id=original['id'],scenario_candidate=c,
                        uncertainty_inputs=dict(modulus_factor=stiffness,density_factor=density,ground_stiffness_factor=ground_factor),
                        installed_mass_kg=q['installed_study_mass_kg'],suspended_mass_kg=q['suspended_mass_kg'],
                        worst_relative_deflection_m=max(r['relative_deck_deflection_m'] for r in responses),
                        worst_settlement_m=max(r['foundation_settlement_m'] for r in responses),physical_release=False)
            rows.append(result);ranked.append(result)
        rankings[name]=[r['nominal_candidate_id'] for r in sorted(ranked,key=lambda r:(r['worst_relative_deflection_m'],r['installed_mass_kg']))]
    reversals=[name for name,ranking in rankings.items() if ranking!=rankings['nominal']]
    report=dict(schema='osr-civil-robustness/1',scenario_basis='illustrative engineering ranges, not probability distributions or measured uncertainty',
                results=rows,deflection_rankings=rankings,ranking_reversals=reversals,physical_release=False,qualified_feasible_pareto_set=[])
    (output/'robustness.json').write_bytes(encoded(report))
    return report
