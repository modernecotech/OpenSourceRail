from copy import deepcopy
import pytest
from engineering.design_search import system_selection as s


def row(cid,mass,count,*,scope='a'*64,interval=None):
    return dict(candidate_id=cid*64,comparison_scope_id=scope,quantities={
        'mass':dict(value=mass,interval=interval,unit='kg',scope='same-nominal-stock'),
        'count':dict(value=count,unit='count',scope='same-declared-operations')})


def test_actual_dominance_preserves_tradeoffs_and_equal_alternatives():
    rows=[row('1',10.,5),row('2',12.,7),row('3',8.,8),row('4',10.,5)]
    r=s.pareto(rows,{'mass':'min','count':'min'})
    assert set(r['nondominated_candidate_ids'])=={'1'*64,'3'*64,'4'*64}
    assert dict(dominator='1'*64,dominated='2'*64) in r['dominance_edges']
    assert r['economic_winner'] is None and r['qualified_winner'] is None and not r['physical_accepted']


def test_missing_prices_or_quantities_never_become_zero_or_eliminate_unknown_candidates():
    rows=[row('1',1.,1),row('2',None,1)]
    r=s.pareto(rows,{'mass':'min','count':'min'})
    assert len(r['nondominated_candidate_ids'])==2 and not r['dominance_edges'] and r['unknown_objectives']
    r=s.pareto([row('1',10.,1),row('2',12.,2)],{'missing_installed_cost':'min'})
    assert len(r['nondominated_candidate_ids'])==2


def test_interval_dominance_is_robust_and_overlaps_remain_incomparable():
    r=s.pareto([row('1',10.,1,interval=[9.,12.]),row('2',11.,2,interval=[10.,13.])],{'mass':'min','count':'min'})
    assert not r['dominance_edges'] and len(r['nondominated_candidate_ids'])==2
    r=s.pareto([row('1',9.,1,interval=[8.,10.]),row('2',13.,2,interval=[12.,14.])],{'mass':'min','count':'min'})
    assert r['nondominated_candidate_ids']==['1'*64]
    r=s.pareto([row('1',15.,1,interval=[14.,16.]),row('2',10.,1,interval=[9.,11.])],{'mass':'max'})
    assert r['nondominated_candidate_ids']==['1'*64]


def test_scope_unit_and_receipt_guards_keep_incompatible_or_invalid_rows_out_of_dominance():
    a=row('1',1.,1);b=row('2',10.,10,scope='b'*64)
    assert len(s.pareto([a,b],{'mass':'min'})['nondominated_candidate_ids'])==2
    b['comparison_scope_id']=a['comparison_scope_id'];b['quantities']['mass']['unit']='t'
    assert len(s.pareto([a,b],{'mass':'min'})['nondominated_candidate_ids'])==2
    bad=deepcopy(a);bad['quantities']['mass']['interval']=[2.,1.]
    with pytest.raises(ValueError,match='ordered uncertainty'):s.pareto([bad],{'mass':'min'})
    bad=deepcopy(a);bad['evaluation_id']='f'*64
    with pytest.raises(ValueError,match='identity'):s.pareto([bad],{'mass':'min'})
    with pytest.raises(ValueError,match='One aggregate'):s.pareto([a,a],{'mass':'min'})
