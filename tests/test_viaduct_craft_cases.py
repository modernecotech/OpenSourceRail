from copy import deepcopy
import pytest
from engineering.design_search import civil_shape_geometry as geometry
from engineering.design_search.craft_backends import viaduct_cases as cases
from engineering.station_rail.common import identity


def test_twelve_candidates_preserve_six_families_and_exact_canonical_ids():
    rows=cases.portfolio()
    assert len(rows)==12 and len({r['candidate_id'] for r in rows})==12
    assert {r['family'] for r in rows}==set(geometry.FAMILIES)
    for row in rows:
        assert cases.validate(row)
        physical=geometry.generate(row['family'],row['profile'])
        assert row['physical_definition']==physical
        assert row['candidate_id']==physical['candidate_id']
        q=geometry.quantities(physical)
        assert row['expected']['total_volume_m3']==pytest.approx(q['total_nominal_volume_m3'])
        assert row['expected']['total_nominal_stock_mass_kg']==pytest.approx(q['total_nominal_stock_mass_kg'])
        assert row['manufacturing_basis']['complete_installed_mass_kg'] is None
        assert row['manufacturing_basis']['boundary_surface_is_not_mould_contact'] is True
        assert all(row[k] is False for k in cases.FLAGS)


def test_stepped_cells_materials_and_positions_are_not_display_smoothing():
    row=cases.build('variable_depth_box')
    assert len(row['physical_definition']['cells'])==20 and len(row['entities'])==80
    assert row['entities'][4]['geometry']['at_m']==[1.,0.,0.]
    assert row['entities'][4]['geometry']['length_m']==1.
    h=cases.build('hybrid_steel_concrete')
    assert {e['material'] for e in h['entities']}=={'research_concrete','structural_steel'}
    assert h['reinforcement_or_composite_stiffness_credit'] is False


@pytest.mark.parametrize('change',[
    lambda r:r.update(candidate_id='different'),
    lambda r:r['entities'][0]['geometry'].update(length_m=19.),
    lambda r:r['expected'].update(total_nominal_stock_mass_kg=0.),
    lambda r:r.update(unresolved_installed_items=[]),
    lambda r:r.update(physical_accepted=True),
])
def test_resealed_mixed_or_promoted_case_is_rejected(change):
    r=deepcopy(cases.build('reference_box'));change(r)
    r['case_definition_id']=identity({k:v for k,v in r.items() if k!='case_definition_id'})
    with pytest.raises(ValueError):cases.validate(r)
