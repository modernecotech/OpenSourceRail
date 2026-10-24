"""Independent carrier takeoffs must exclude separately scoped concrete stock."""
from copy import deepcopy

import pytest

from engineering.design_search import contracts, families


@pytest.fixture(scope='module')
def alternatives():return families.initial_families()


@pytest.mark.parametrize('index,count',[(0,0),(1,64),(2,80)])
def test_added_stock_exactly_matches_physical_vehicle_inventory(alternatives,index,count):
    candidate=alternatives[index]
    geometry={part['id']:part for part in candidate['geometry']}
    inventory={row['geometry_id']:row for row in candidate['installed_inventory'] if row.get('geometry_id')}
    # Derive independently from physical material/frame/scope, not role tags or
    # materialize's own list. The concrete beam is a separate inventory scope.
    expected={uid for uid,part in geometry.items() if part['kind']=='box' and part['frame_id']=='vehicle'
        and part['material_id']=='carrier-steel' and uid in inventory and inventory[uid]['scope']=='vehicle-per-car'
        and inventory[uid]['status']=='known'}
    native=families.materialize(candidate,allow_incomplete=True)
    assert len(expected)==count
    assert {part['id'] for part in native['additional_stock']}==expected
    assert {part['id'] for part in native['additional_physical_regions']}==expected
    bom=[row for row in native['manufacturing_bom'] if row.get('component_scope')=='added-carrier-stock']
    assert {row['id'] for row in bom}==expected
    assert sum(part['mass_kg'] for part in native['additional_stock'])==pytest.approx(sum(inventory[uid]['unit_mass_kg'] for uid in expected))
    for part in native['additional_stock']:
        assert part['material_id']=='carrier-steel'
        assert part['material']=='declared-carrier-steel'
        assert part['density_kg_m3']==7850.
        assert part['mass_kg']==inventory[part['id']]['unit_mass_kg']
        assert part['cg_m']==inventory[part['id']]['cg_m']
    concrete=[part for part in geometry.values() if part['id'].startswith('guidebeam/concrete/')]
    assert len(concrete)==6
    assert all(part['role']=='guidebeam-concrete-stock' and part['material_id']=='concrete' and part['frame_id']=='guidebeam' for part in concrete)
    assert not any(part['id'].startswith('guidebeam/') for part in native['additional_stock'])


def test_generic_box_factory_does_not_assign_carrier_role():
    part,_=families._box('test-concrete',[1.,1.,1.],[0.,0.,0.],material='concrete',density=2500.)
    assert part.get('role') is None


def test_previous_misclassified_physical_definition_is_outside_fixed_domain(alternatives):
    old=deepcopy(alternatives[0])
    # Reproduce both historical mistakes to obtain the former physical ID.
    for part in old['geometry']:
        if part['id'].startswith('guidebeam/concrete/'):part['role']='added-carrier-stock'
    for row in old['installed_inventory']:
        if row.get('basis')=='exact solid-box integral at declared material density':row['basis']='exact solid-box integral at declared steel density'
    old['candidate_id']=contracts.identity(dict(units=contracts.UNITS,**{key:old[key] for key in contracts.PHYSICAL_KEYS}))
    contracts.validate_candidate(old)
    assert old['candidate_id']=='3e1cf25953f94d91e7e38e4a5da42d99eae6151bbd638a5342eb777484458674'
    with pytest.raises(families.UnsupportedCandidateDomain):families.materialize(old,allow_incomplete=True)
