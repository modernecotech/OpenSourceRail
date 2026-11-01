import pytest

from engineering.design_search import civil_beam as beam


def cell(start=0.,end=10.,ei=2e8,q=10000.):
    return dict(x_start_m=start,x_end_m=end,EI_Nm2=ei,distributed_load_N_m=q)


def test_uniform_load_matches_closed_form_reactions_moment_and_deflection():
    l,ei,q = 10.,2e8,10000.
    r = beam.analyse([cell()],[])
    assert r["reaction_left_N"]==r["reaction_right_N"]==q*l/2
    assert r["maximum_sagging_moment_Nm"]==pytest.approx(q*l*l/8)
    assert r["maximum_sagging_moment_x_m"]==l/2
    assert r["maximum_absolute_shear_N"]==q*l/2
    assert r["deflection_at_observation_m"]==pytest.approx(5*q*l**4/(384*ei))
    assert r["force_residual_N"]==r["moment_residual_Nm"]==0


def test_central_point_load_and_support_load_cancellation():
    l,ei,p = 10.,2e8,100000.
    r = beam.analyse([cell(q=0)], [dict(x_m=l/2,force_N=p)])
    assert r["maximum_sagging_moment_Nm"]==pytest.approx(p*l/4)
    assert r["deflection_at_observation_m"]==pytest.approx(p*l**3/(48*ei))
    support = beam.analyse([cell(q=0)],[dict(x_m=0,force_N=p),dict(x_m=l,force_N=2*p)], [0,5,10])
    assert support["reaction_left_N"]==p and support["reaction_right_N"]==2*p
    assert support["maximum_absolute_shear_N"]==support["maximum_sagging_moment_Nm"]==0
    assert support["deflection_at_observation_m"]==[0,0,0]


def test_superposition_and_unit_force_reciprocity():
    cells = [cell()]
    points = [dict(x_m=3.,force_N=80000.),dict(x_m=8.,force_N=30000.)]
    q_only = beam.analyse(cells,[],3.7)
    p_only = beam.analyse([cell(q=0)],points,3.7)
    combined = beam.analyse(cells,points,3.7)
    assert combined["deflection_at_observation_m"]==pytest.approx(
        q_only["deflection_at_observation_m"]+p_only["deflection_at_observation_m"])
    influence = beam.deflection_influence(cells,3.7)
    assert sum(point["force_N"]*influence(point["x_m"]) for point in points)==pytest.approx(p_only["deflection_at_observation_m"])
    assert influence(8.)==pytest.approx(beam.deflection_influence(cells,8.)(3.7))
    assert influence(0)==influence(10)==0


def test_symmetric_stepped_ei_matches_independent_piecewise_antiderivative():
    ei1,ei2,a,l,p = 1e8,3e8,2.,10.,50000.
    cells = [cell(0,a,ei1,0),cell(a,l-a,ei2,0),cell(l-a,l,ei1,0)]
    r = beam.analyse(cells,[dict(x_m=l/2,force_N=p)])
    expected = p/6*(a**3/ei1+((l/2)**3-a**3)/ei2)
    assert r["deflection_at_observation_m"]==pytest.approx(expected)


def test_per_cell_extrema_resolve_different_distributed_loads_and_union_maximum():
    r = beam.analyse([cell(0,4,q=2),cell(4,10,q=6)],[])
    # R_left = 44 - (8*2 + 36*7)/10 = 17.2 N. Shear remains
    # positive through cell one and vanishes 9.2/6 m into cell two.
    first,second = r["per_cell_extrema"]
    assert first["x_start_m"]==0 and first["x_end_m"]==4
    assert first["maximum_sagging_moment_x_m"]==4
    assert first["maximum_sagging_moment_Nm"]==pytest.approx(17.2*4-2*4**2/2)
    advance = 9.2/6
    expected = 52.8+9.2*advance-6*advance**2/2
    assert second["maximum_sagging_moment_x_m"]==pytest.approx(4+advance)
    assert second["maximum_sagging_moment_Nm"]==pytest.approx(expected)
    assert max(row["maximum_sagging_moment_Nm"] for row in r["per_cell_extrema"])==r["maximum_sagging_moment_Nm"]


def test_subdivision_offset_and_point_load_equilibrium():
    points = [dict(x_m=2.2,force_N=17000.),dict(x_m=7.4,force_N=33000.)]
    original = beam.analyse([cell()],points,[0,2,5,9,10])
    split = beam.analyse([cell(0,3),cell(3,6),cell(6,10)],points,[0,2,5,9,10])
    for key in ("reaction_left_N","reaction_right_N","maximum_sagging_moment_Nm",
            "maximum_sagging_moment_x_m","maximum_absolute_shear_N","deflection_at_observation_m"):
        assert split[key]==pytest.approx(original[key])
    assert original["force_residual_N"]==pytest.approx(0,abs=1e-9)
    assert original["right_support_internal_moment_residual_Nm"]==pytest.approx(0,abs=1e-9)
    shifted = beam.analyse([cell(20,30)], [dict(x_m=p["x_m"]+20,force_N=p["force_N"]) for p in points],25)
    assert shifted["deflection_at_observation_m"]==pytest.approx(original["deflection_at_observation_m"][2])


def test_global_deflection_bound_matches_closed_form_and_bounds_all_sampled_observations():
    l,ei,q = 10.,2e8,10000.
    upper = beam.deflection_upper_bound([cell()],[])
    assert upper==pytest.approx(q*l**4/(60*ei))
    r = beam.analyse([cell()],[],[i*l/100 for i in range(101)])
    assert max(r["deflection_at_observation_m"])<upper
    cells = [cell(0,3,ei/2,q/2),cell(3,8,ei*2,q),cell(8,10,ei,q/3)]
    points = [dict(x_m=2.3,force_N=20000),dict(x_m=8.4,force_N=40000)]
    upper = beam.deflection_upper_bound(cells,points)
    r = beam.analyse(cells,points,[i*l/100 for i in range(101)])
    assert max(r["deflection_at_observation_m"])<=upper


@pytest.mark.parametrize("cells,points,observation",[
    ([],[],None),([cell(ei=0)],[],None),([cell(ei=float("nan"))],[],None),
    ([cell(q=-1)],[],None),([cell(0,3),cell(4,10)],[],None),
    ([cell(0,3),cell(2,10)],[],None),([cell(3,0)],[],None),
    ([cell()],None,None),([cell()],[dict(x_m=-.1,force_N=1)],None),
    ([cell()],[dict(x_m=2,force_N=-1)],None),([cell()],[],11),
    ([cell()],[],[]),([cell()],[],float("inf")),
    ([dict(x_start_m=0,x_end_m=10,distributed_load_N_m=10)],[],None)])
def test_invalid_or_unknown_inputs_rejected(cells,points,observation):
    with pytest.raises(ValueError):beam.analyse(cells,points,observation)


def test_nonrepresentable_input_and_derived_response_overflow_are_rejected():
    with pytest.raises(ValueError,match="Finite"):
        beam.analyse([cell(ei=10**500)],[])
    with pytest.raises(ValueError,match="Finite"):
        beam.analyse([cell()], [dict(x_m=5,force_N=10**500)])
    for operation in (beam.analyse,beam.deflection_upper_bound):
        with pytest.raises(ValueError,match="Finite derived"):
            operation([cell(0,20,ei=1e-320,q=1)],[])
        with pytest.raises(ValueError,match="Finite derived"):
            operation([cell(0,20,ei=1,q=1e308)],[])
    influence = beam.deflection_influence([cell(0,20,ei=1e-320,q=0)],10)
    with pytest.raises(ValueError,match="Finite derived"):
        influence(10)
