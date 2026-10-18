"""Independent Hermite beam FEM for declared linear gross-bending hypotheses.

This is candidate-specific numerical confirmation of a 1D equivalent model.
Connections are ideal supports/rigid EI sharing. Shells, welds, cracking,
prestress resistance, soil interaction and train-track dynamics stay unverified.
"""
import math

from engineering.twin_workflow import core


def solve(length, supports, ei, *, divisions=24, uniform=0., points=(), clamp=False):
    import numpy as np
    if not (math.isfinite(length) and length > 0 and math.isfinite(ei) and ei > 0):
        raise ValueError("positive finite beam and rigidity required")
    xs = sorted(set([length*i/divisions for i in range(divisions+1)] + list(supports) +
                    [float(x) for x, force in points if 0 <= x <= length] + [length/2]))
    n = len(xs); k = np.zeros((2*n, 2*n)); f = np.zeros(2*n)
    for i, (left, right) in enumerate(zip(xs, xs[1:])):
        h = right-left
        element = ei/h**3*np.array([[12,6*h,-12,6*h], [6*h,4*h*h,-6*h,2*h*h],
            [-12,-6*h,12,-6*h], [6*h,2*h*h,-6*h,4*h*h]])
        k[2*i:2*i+4,2*i:2*i+4] += element
        f[2*i:2*i+4] -= uniform*np.array([h/2,h*h/12,h/2,-h*h/12])
    for x, force in points:
        if 0 <= x <= length:
            f[2*xs.index(float(x))] -= force
    fixed = [2*xs.index(x) for x in supports]
    if clamp:
        fixed += [v+1 for v in fixed]
    free = [i for i in range(2*n) if i not in fixed]
    u = np.zeros(2*n)
    u[free] = np.linalg.solve(k[np.ix_(free,free)], f[free])
    reactions = k @ u-f
    total = uniform*length+sum(force for x, force in points if 0 <= x <= length)
    return dict(nodes_m=xs, displacement_rotation=u.tolist(),
        reactions=[dict(x_m=xs[i//2], dof="translation" if i%2==0 else "rotation", value=float(reactions[i])) for i in fixed],
        maximum_nodal_deflection_m=float(max(abs(u[::2]))), midspan_deflection_m=float(abs(u[2*xs.index(length/2)])),
        force_balance_relative_error=float(abs(sum(reactions[i] for i in fixed if i%2==0)-total)/max(total,1.)),
        input=dict(length_m=length,supports_m=list(supports),ei_nm2=ei,uniform_n_m=uniform,
            point_loads_n=list(points),divisions=divisions,clamped=clamp))


def benchmarks():
    L, EI, q, force = 4., 4e6, 1000., 3000.
    rows = []
    for name, kwargs, expected in (
        ("simple-udl",dict(supports=[0.,L],uniform=q),5*q*L**4/(384*EI)),
        ("cantilever-tip",dict(supports=[0.],points=[(L,force)],clamp=True),force*L**3/(3*EI))):
        actual = solve(L,ei=EI,divisions=8,**kwargs)
        error = abs(actual["maximum_nodal_deflection_m"]/expected-1)
        rows.append(dict(id=name,expected_m=expected,relative_error=error,passed=error<1e-7))
    return rows


def confirm(kind, assessment, output):
    from . import tasks
    module, mapping = tasks.contexts(kind)
    if kind == "mechanical-detail":
        context = mapping[assessment["configuration_id"]]
        length, supports = context["body_length_m"], context["support_x_m"]
        load_cases = assessment["metrics"]["load_case_responses"]
        cases = [dict(id=r["id"], ei=r["beam"]["ei_n_m2"], uniform=r["beam"]["uniform_load_n_m"],
            points=[], expected=r["beam"]["maximum_abs_deflection_m"], measurement="maximum_nodal_deflection_m") for r in load_cases]
    else:
        context = assessment["context_record"]
        length=context["span_m"];supports=[0.,length]
        assumptions=core.read(core.ROOT/"engineering/generative_design/data/civil-detail-space.json")["assumptions"]
        ei=assumptions["concrete_modulus_pa"]*assessment["geometry"]["beam_section"]["inertia_x_m4"]
        response=assessment["metrics"]["live_midspan_deflection"]
        origin=response["governing_origin_m"]
        points=[(origin+a["x_m"],a["force_n"]) for a in context["applied_axles"] if 0 <= origin+a["x_m"] <= length]
        cases=[dict(id="moving-axles-at-recorded-midspan-extremum",ei=ei,uniform=0.,points=points,
            expected=response["deflection_m"],measurement="midspan_deflection_m")]
    checks={}; records=[]
    for case in cases:
        results=[]
        for divisions in (16,32):
            row=solve(length,supports,case["ei"],uniform=case["uniform"],points=case["points"],divisions=divisions)
            core.write(output/(case["id"]+f"-mesh-{divisions}.json"),row,exclusive=True)
            results.append(row)
        coarse,fine=results; measurement=case["measurement"]
        agreement=abs(fine[measurement]/case["expected"]-1)
        refinement=abs(fine[measurement]/coarse[measurement]-1)
        checks[case["id"]+"/analytical-agreement"]=agreement<.02
        checks[case["id"]+"/mesh-refinement"]=refinement<.02
        checks[case["id"]+"/equilibrium"]=fine["force_balance_relative_error"]<1e-7
        adverse=solve(length,supports,case["ei"],uniform=1.1*case["uniform"],
            points=[(x,1.1*f) for x,f in case["points"]],divisions=32)
        checks[case["id"]+"/linear-adverse-response"]=abs(adverse[measurement]/fine[measurement]-1.1)<1e-7
        core.write(output/(case["id"]+"-adverse.json"),adverse,exclusive=True)
        records.append(dict(case=case,agreement_relative_error=agreement,refinement_relative_change=refinement))
    controls=benchmarks(); checks["independent-closed-form-benchmarks"]=all(r["passed"] for r in controls)
    report=dict(checks=checks,cases=records,benchmarks=controls,
        scope=__doc__.strip(),research_comparison_tolerance=.02,accepted_properties=False,**core.FLAGS)
    core.write(output/"numerical-confirmation.json",report,exclusive=True)
    return report
