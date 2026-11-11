"""A changed coupled packet remains verifiable only in its pinned source epoch."""
import pytest

from engineering.design_search import railway_publication
from engineering.station_rail import retired_station_reference


def test_coupled_packet_is_historical_and_strict_current_verification_holds():
    result = retired_station_reference.verify_coupled_packet()

    assert result["manifest_id"] == retired_station_reference.COUPLED_PACKET_MANIFEST_ID
    assert result["source_epoch"] == "historical"
    assert result["analytical_replay"] is False
    assert result["numerical_reexecuted"] is False
    assert result["current_evaluator_admission"] is False
    assert all(
        result[name] is False
        for name in (
            "physical_accepted",
            "engineering_accepted",
            "manufacturing_release",
            "operating_release",
        )
    )

    with pytest.raises(ValueError, match="Coordinated source epoch changed"):
        railway_publication.verify()
