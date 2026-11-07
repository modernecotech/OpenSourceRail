from copy import deepcopy
import pytest
from engineering.design_search.craft_backends import viaduct_cases as cases,viaduct_cad as cad
from engineering.station_rail.common import identity


def fixture(case):
    return deepcopy(dict(bodies=[dict(id=n,closed=True,valid=True,solid_count=1,volume_m3=p['volume_m3'],
        center_of_mass_m=p['centroid_m'],bbox_m=dict(min=p['bounds_m'][0],max=p['bounds_m'][1])) for n,p in case['expected']['part_measures'].items()]))


def test_plan_and_exact_reference_do_not_change_physical_candidate():
    case=cases.build('folded_plate');p=cad.plan(case)
    assert p['candidate_id']==case['candidate_id']
    assert p['evaluation_id']==identity({k:v for k,v in p.items() if k!='evaluation_id'})
    assert p['limits']['maximum_native_processes']==16
    m=fixture(case);r=cad.compare(case,m,exact=True,associate=True)
    assert r['comparison_passed'] and r['source_names_preserved']
    assert r['nominal_material_mass_kg']==pytest.approx(case['expected']['total_nominal_stock_mass_kg'])
    for i,b in enumerate(m['bodies']):b['id']='product'+str(i)
    r=cad.compare(case,m,exact=True,associate=True)
    assert r['comparison_passed'] and not r['source_names_preserved']
    assert all(r[k] is False for k in cad.FLAGS)


@pytest.mark.parametrize('change',[
    lambda m:m['bodies'].pop(),
    lambda m:m['bodies'][0].update(volume_m3=1e20),
    lambda m:m['bodies'][0].update(closed=False),
    lambda m:m['bodies'][0].update(valid=False),
    lambda m:m['bodies'][0].update(center_of_mass_m=[float('nan'),0,0]),
])
def test_exact_correspondence_rejects_bad_or_missing_solids(change):
    c=cases.build('reference_box');m=fixture(c);change(m)
    with pytest.raises(ValueError):cad.compare(c,m,exact=True,associate=True)


def test_generated_source_names_are_required_and_bounds_cannot_compensate():
    c=cases.build('reference_box');m=fixture(c);m['bodies'][0]['id']='different'
    with pytest.raises(ValueError):cad.compare(c,m)
    m=fixture(c);m['bodies'][0]['bbox_m']['max'][0]=19.
    with pytest.raises(ValueError):cad.compare(c,m,exact=True,associate=True)
