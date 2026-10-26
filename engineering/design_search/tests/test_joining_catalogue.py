from math import pi
import pytest
from engineering.design_search import joining_catalogue as c


def test_coupon_data_is_not_a_joint_allowable_or_selected_material():
    r=c.catalogue();assert len(r['entries'])>=8
    for e in r['entries']:
        assert e['design_allowable_Pa'] is None and not e['automatic_substitution_eligible']
        assert e['qualification_status']=='unknown' and not e['physical_accepted']
        assert e['unit_price_USD'] is None
    bond=next(e for e in r['entries'] if e['id']=='bonded-flange-dp490')
    assert bond['coupon']['typical_stress_Pa']==pytest.approx(23.001e6,rel=.0001)
    assert bond['hot_coupon']['typical_stress_Pa']<bond['coupon']['typical_stress_Pa']/2
    assert r['sources']['dp490']['raw_document_sha256'] is None
    assert len(r['sources']['diab-hp']['raw_document_sha256'])==64


def test_current_core_density_and_temperature_are_explicit():
    e=next(e for e in c.catalogue()['entries'] if e['id']=='divinycell-hp60-current')
    assert e['density_kg_m3']==65. and e['continuous_temperature_C'][1]==80.
    assert e['maximum_processing_temperature_C']==145.


def test_hybrid_takeoff_counts_potting_fasteners_isolation_and_unknowns():
    p=c.attachment_plan('bond-plus-bolts',[[0.,0.,0.],[1.,0.,0.]])
    rows={r['id']:r for r in p['stock']}
    assert rows['positive-bolt']['quantity']==4 and rows['washers']['quantity']==8
    assert rows['insulating-bushings']['quantity']==4
    expected=4*pi/4*(.030**2-.012**2)*.02*650
    assert rows['ec3500-potting']['mass_kg']==pytest.approx(expected)
    assert p['known_stock_mass_subtotal_kg']>0
    assert p['complete_installed_joint_mass_kg'] is None and p['removed_core_mass_kg'] is None
    assert rows['dp490-bond']['mass_kg'] is None
    assert p['acceptance_load_N'] is None and p['validation_tasks']


@pytest.mark.parametrize('strategy',['potted-insert','clip-plus-positive-retention','welded-node','bonded-flange'])
def test_every_option_preserves_unknown_hardware_and_no_qualification(strategy):
    p=c.attachment_plan(strategy,[[0.,0.,0.]])
    assert p['unknown_mass_stock_ids'] and p['net_installed_mass_delta_kg'] is None
    assert not p['physical_accepted'] and p['qualification_status']=='unknown'
    with pytest.raises(ValueError):c.attachment_plan(strategy,[[float('nan'),0,0]])


def test_glazing_takeoff_does_not_disguise_sheet_as_complete_window():
    p=c.glazing_plan(1.,.8,.004)
    assert p['sheet_mass_kg']==pytest.approx(3.84)
    assert p['free_expansion_width_m']==pytest.approx(.00224)
    assert p['complete_window_mass_kg'] is None and p['retention_mass_kg'] is None
    assert c.glazing_plan(1.,.8,.004,temperature_C=(23.,80.))['free_expansion_width_m'] is None
    ex=c.glazing_plan(1.,.8,.004,product='fire-retardant-flat-window')
    assert ex['free_expansion_width_m']==pytest.approx(65e-6*32)
