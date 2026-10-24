"""Vehicle carrier additions cannot duplicate guideway concrete or other scope."""
from copy import deepcopy
import math

import pytest

from engineering.design_search import families,twin
from engineering.ferrite_maglev import candidate_manufacturing as m,bim_field as b


@pytest.fixture(scope='module')
def variants():
    candidates=families.initial_families()
    return [(candidate,families.materialize(candidate,allow_incomplete=True)) for candidate in candidates]


def inventory_carrier_ids(candidate):
    geometry={row['id']:row for row in candidate['geometry']}
    return {row['geometry_id'] for row in candidate['installed_inventory'] if row['status']=='known'
            and row['scope']=='vehicle-per-car' and row.get('geometry_id') in geometry
            and geometry[row['geometry_id']]['material_id']=='carrier-steel'}


def test_real_families_have_only_actual_vehicle_rhs_wall_additions(variants):
    for (candidate,materialized),count in zip(variants,(0,64,80)):
        expected=inventory_carrier_ids(candidate)
        checked=m.additional_carrier_stock(materialized)
        assert len(expected)==len(checked)==count
        assert {part['id'] for part in checked}==expected
        assert all(part['scope']=='vehicle-per-car' and part['frame_id']=='vehicle'
                   and part['material_id']=='carrier-steel' for part in checked)
        rows=twin._additional_materials(materialized)
        assert len(rows)==count
        geometry={row['id']:row for row in candidate['geometry']}
        actual_mass=sum(row['unit_mass_kg'] for row in candidate['installed_inventory'] if row.get('geometry_id') in expected)
        assert sum(row['mass_kg'] for row in rows)==pytest.approx(actual_mass)
        assert sum(part['mass_kg'] for part in checked)==pytest.approx(
            sum(math.prod(geometry[key]['size_m'])*7850 for key in expected))
        assert not materialized['complete_installed_distribution']


@pytest.mark.parametrize('mutation',['guidebeam-concrete','wrong-material','wrong-scope','missing-wall','duplicate-wall','wrong-density'])
def test_all_addition_consumers_reject_nonvehicle_nonsteel_or_incomplete_stock(variants,mutation):
    _,source=variants[1];bad=deepcopy(source)
    if mutation=='guidebeam-concrete':
        bundle=bad['design_search_bundle']
        part=next(row for row in bundle['geometry'] if row['id']=='guidebeam/concrete/0')
        item=next(row for row in bundle['installed_inventory'] if row.get('geometry_id')==part['id'])
        bad['additional_stock'].append(dict(id=part['id'],kind='box',size_m=part['size_m'],at_m=part['at_m'],
            material='declared-carrier-steel',material_id='carrier-steel',density_kg_m3=7850.,
            volume_m3=math.prod(part['size_m']),mass_kg=item['unit_mass_kg'],cg_m=item['cg_m'],inertia_kg_m2=item['inertia_kg_m2']))
    elif mutation=='wrong-material':bad['additional_stock'][0]['material']='concrete'
    elif mutation=='wrong-scope':bad['additional_stock'][0].update(scope='guideway-per-span',frame_id='guidebeam')
    elif mutation=='missing-wall':bad['additional_stock'].pop()
    elif mutation=='duplicate-wall':bad['additional_stock'].append(deepcopy(bad['additional_stock'][0]))
    else:bad['additional_stock'][0]['density_kg_m3']=2500.
    for consume in (m.additional_carrier_stock,m.product_definition,b.exchange_parts,twin._additional_materials):
        with pytest.raises(ValueError):consume(bad)


def test_bim_beam_concrete_is_once_at_selected_span_and_never_carrier_stock(variants,monkeypatch):
    for candidate,materialized in variants:
        selection=candidate['architecture']['guidebeam']
        geometry={row['id']:row for row in candidate['geometry']}
        section=geometry['guidebeam/section-definition']['definition']
        concrete=[dict(id=row['id'],kind='box',size_m=row['size_m'],at_m=row['at_m'],material='concrete',
                       volume_m3=math.prod(row['size_m'])) for row in candidate['geometry'] if row['id'].startswith('guidebeam/concrete/')]
        # Isolate the addition/export contract; no structural or native solver
        # is repeated for this exact-stock/scope regression.
        resolved=dict(selection=selection,beam=dict(section=section),
            assumptions=dict(concrete=dict(density_kg_m3=2500.),rail_support=dict(beam_top_z_m=-1.6)))
        monkeypatch.setattr(m,'selected_beam',lambda *args,_value=resolved,**kwargs:_value)
        monkeypatch.setattr(m,'_civil_geometry',lambda value,_parts=concrete:dict(parts=_parts))
        parts=b.exchange_parts(materialized,include_rail_and_supports=True,allow_incomplete=True)
        native_concrete=[part for part in parts if part['material']=='concrete']
        assert len(native_concrete)==6
        assert sum(part['volume_m3'] for part in native_concrete)==pytest.approx(
            sum(row['unit_mass_kg'] for row in candidate['installed_inventory'] if row.get('geometry_id','').startswith('guidebeam/concrete/'))/2500.)
        assert max(part['at_m'][0]+part['size_m'][0] for part in native_concrete)==pytest.approx(selection['span_m'])
        added=[part for part in parts if part['exchange_scope'].startswith('Known added carrier stock')]
        assert {part['id'] for part in added}==inventory_carrier_ids(candidate)
        assert not any(part['id'].startswith('guidebeam/') for part in added)
