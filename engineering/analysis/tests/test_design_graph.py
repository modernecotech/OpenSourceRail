import pytest
from engineering.design_engine.graph import validate,affected


def graph():
    return {'nodes':[{'id':'source:material.json','depends_on':[]},{'id':'source:prose.md','depends_on':[]},
        {'id':'candidate','depends_on':['source:material.json']},{'id':'solve','depends_on':['candidate']},{'id':'report','depends_on':['solve']}]}


def test_material_change_invalidates_declared_transitive_closure_but_prose_does_not():
    assert affected(graph(),['material.json'])==['candidate','report','solve']
    assert affected(graph(),['prose.md'])==[]


def test_lineage_cycles_and_unknown_dependencies_are_rejected():
    g=graph();g['nodes'][0]['depends_on']=['report']
    with pytest.raises(ValueError,match='cycle'):validate(g)
    g=graph();g['nodes'][2]['depends_on']=['missing']
    with pytest.raises(ValueError):validate(g)
