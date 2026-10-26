from copy import deepcopy
import pytest
from engineering.design_search import section_proposals as s,body_revision as body
from engineering.station_rail import vehicle


@pytest.fixture(scope='module')
def reference():return vehicle.build()


def test_generic_proposals_are_unique_with_stable_prefix_and_retain_controls(reference):
    controls=body.definitions(reference);small=s.generate(reference,samples=6);large=s.generate(reference,samples=16)
    assert large[:6]==small and len(large)==16
    keys=[s._key(row['parameters']) for row in large]
    assert len(set(keys))==16 and not set(keys)&{s._key(row['parameters']) for row in controls}
    assert {'focused-material-redistribution','shifted-Halton-2-3'}=={r['generation']['method'] for r in large}
    assert len({r['parameters']['sill_depth_m'] for r in large})>5
    for r in large:
        assert body._definition(reference,r)==r['parameters']
        assert r['definition_id']==s.identity({n:v for n,v in r.items() if n!='definition_id'})


def test_actual_stock_geometry_matches_closed_form_hollow_rhs(reference):
    rows=s.generate(reference,samples=5)
    for row in rows:
        p=row['parameters'];b=p['sill_width_m'];h=p['sill_depth_m'];t=p['sill_wall_m'];m=row['geometry_metrics']
        area=b*h-(b-2*t)*(h-2*t);iy=(b*h**3-(b-2*t)*(h-2*t)**3)/12
        iz=(h*b**3-(h-2*t)*(b-2*t)**3)/12
        assert sum(x['mass_kg'] for x in m['sections'])==pytest.approx(m['sill_stock_mass_after_kg'])
        for section in m['sections']:
            assert section['area_m2']==pytest.approx(area)
            assert section['I_about_local_1_m4']==pytest.approx(iy)
            assert section['I_about_local_2_m4']==pytest.approx(iz)
            assert section['mass_kg']==pytest.approx(area*section['length_m']*2710.)
        assert m['sill_stock_delta_kg']==pytest.approx(m['sill_stock_mass_after_kg']-m['sill_stock_mass_before_kg'])


def test_generated_definition_materializes_consistent_physical_stock_without_response_claim(reference):
    row=s.generate(reference,samples=1)[0];v=body.materialize(reference,row)
    assert v['candidate_id']!=reference['candidate_id'] and v['body_revision']['definition_id']==row['definition_id']
    sections=body._sills(v);metrics=row['geometry_metrics']
    assert sum(m['mass_kg'] for m in sections)==pytest.approx(metrics['sill_stock_mass_after_kg'])
    assert v['mass']['accounted_tare_kg_per_car']==pytest.approx(reference['mass']['accounted_tare_kg_per_car']+v['body_revision']['stock_mass_delta_kg'])
    assert row['physical_response_estimate'] is None and row['strength_screen']==row['buckling_screen']=='unknown'
    assert row['dynamic_clearance_screen']==row['manufacturing_feasibility']=='unknown'
    assert not row['physical_accepted'] and row['complete_installed_mass_kg'] is None


def test_budget_definition_tamper_and_unsupported_material_are_refused(reference):
    assert s.generate(reference,samples=0)==[]
    for count in (-1,True,1.5,257):
        with pytest.raises(ValueError,match='sample budget'):s.generate(reference,samples=count)
    row=s.generate(reference,samples=1)[0];bad=deepcopy(row);bad['parameters']['sill_wall_m']=.02
    with pytest.raises(ValueError,match='mutated'):body.materialize(reference,bad)
    bad=deepcopy(row);bad['parameters']['material']='invented-unmodelled-material';bad['definition_id']=s.identity({n:v for n,v in bad.items() if n!='definition_id'})
    with pytest.raises(ValueError,match='Unsupported material'):body.materialize(reference,bad)
