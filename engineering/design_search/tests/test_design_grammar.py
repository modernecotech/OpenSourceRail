from copy import deepcopy
import numpy as np
import pytest
from engineering.design_search import design_grammar as g,grammar_geometry as geometry,grammar_structure as structure,interface_graph,dfma,failure_diagnosis,redesign_engine


def test_five_recipes_generate_distinct_stock_and_preserve_apertures():
    rows=g.initial_candidates();assert len({c['candidate_id'] for c in rows})==5
    assert len({len(c['parts']) for c in rows})>=3
    for c in rows:
        g.validate(c);assert c['complete_installed_mass_kg'] is None
        a=interface_graph.assess(geometry.interface_projection(c))
        assert a['compatibility_status']=='unknown' and a['declared_functions_preserved']
        assert not any(i['code']=='opening-keepout-intersection' for i in a['issues'])
    semi=rows[1];assert all(p.get('laminate') for p in semi['parts'] if p['material_id']=='gfrp_skin_research')


def test_actual_mechanism_triggers_a_structurally_distinct_physical_rewrite():
    c=g.build(g.parameters());d=structure.diagnose_rigidity(c['structure']);assert d['mechanism_count']>0
    diagnosis=failure_diagnosis.diagnose(c,rigidity=d);r=redesign_engine.revise(c,diagnosis)
    child=next(x['candidate'] for x in r['revisions'] if x['operator']=='triangulate-underfloor')
    assert child['candidate_id']!=c['candidate_id'] and len(child['structure']['members'])>len(c['structure']['members'])
    assert structure.diagnose_rigidity(child['structure'])['mechanism_count']==0
    assert child['physical']['apertures']==c['physical']['apertures']
    assert child['parent_candidate_ids']==[c['candidate_id']]
    assert all(n['at_m'][2]<1. for n in child['structure']['nodes'])


def test_new_recipe_composes_productions_without_changing_source_or_initial_menu():
    registry=g.register_recipe('new_modular_honeycomb',dict(frame='gfrp_axial_research',shell='honeycomb-sandwich',ribs='modular'))
    p=g.parameters();p['family']='new_modular_honeycomb'
    c=g.build(p,recipes=registry);assert c['label']=='new_modular_honeycomb' and 'new_modular_honeycomb' not in g.RECIPES
    assert any(q['material_id']=='aluminium_core_reference' for q in c['parts'])
    assert len([q for q in c['parts'] if q['id'].startswith('roof/outer/')])>1


def test_roof_integration_preserves_functions_and_reduces_declared_manufactured_groups_only():
    c=g.build(g.parameters());child=g.rewrite(c,'integrate-roof-functions',reason='Test shared roof production')
    a,b=dfma.evaluate(c),dfma.evaluate(child)
    compare=interface_graph.compare_integration(geometry.interface_projection(c),geometry.interface_projection(child))
    assert compare['missing_functions']==[] and compare['dropped_function_obligations']==[]
    assert b['resolved_manufactured_component_count']<a['resolved_manufactured_component_count']
    assert child['complete_cost_USD'] is None and child['complete_installed_mass_kg'] is None


def test_length_and_layout_change_geometry_loads_and_requirement_context():
    c=g.build(g.parameters());child=g.rewrite(c,'change-body-length',reason='Shorter-car comparison')
    assert c['candidate_id']!=child['candidate_id'] and c['requirement_revision']!=child['requirement_revision']
    assert c['structure']['nodes']!=child['structure']['nodes']
    assert c['known_structure_stock_kg']!=child['known_structure_stock_kg']


def test_stock_tensor_is_symmetric_positive_and_tampered_geometry_is_rejected():
    c=g.build(g.parameters());r=geometry.mass_properties(c);J=np.array(r['known_gross_stock_inertia_kg_m2'])
    assert np.allclose(J,J.T) and min(np.linalg.eigvalsh(J))>0
    assert r['known_gross_stock_mass_kg']==pytest.approx(sum(q['mass_kg'] for q in c['parts']))
    wrong=deepcopy(c);wrong['parts'][0]['mass_kg']+=1
    with pytest.raises(ValueError):g.validate(wrong)
