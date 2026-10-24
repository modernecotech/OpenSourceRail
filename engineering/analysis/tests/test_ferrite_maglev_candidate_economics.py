"""Equal-service comparison cannot declare failed physics bankable."""
import pytest
from engineering.ferrite_maglev import candidate_economics as e


def test_hotel_power_equal_and_support_loss_positive_in_both_comparisons():
    candidate=e.magnetics.definition();low=e.equal_service_energy(candidate,30.);high=e.equal_service_energy(candidate,60.)
    for value in (low,high):
        mag,rail=value['rows'];assert mag['hotel_kwh']==rail['hotel_kwh']
        assert rail['support_kwh']==0
        if mag['support_kwh'] is None:assert mag['total_kwh'] is None
        else:assert mag['support_kwh']>0
        assert mag['regeneration_credit_kwh']==rail['regeneration_credit_kwh']==0
        assert all(r['total_kwh']==pytest.approx(r['traction_kwh']+r['hotel_kwh']+r['support_kwh']) for r in value['rows'] if r['support_kwh'] is not None)
    assert high['rows'][0]['hotel_kwh']>low['rows'][0]['hotel_kwh']
    assert low['rows'][0]['mass_kg']==pytest.approx(6*candidate['controlled_aw3_kg'])
