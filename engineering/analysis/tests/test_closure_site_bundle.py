"""Portable map/raw-data agreement, without the original GIS data paths."""
import pytest
from engineering.assembly_design import site_bundle
from engineering.twin_workflow import core


def test_actual_site_data_is_portable_and_its_map_cannot_diverge(tmp_path):
    value=site_bundle.snapshot()
    output=tmp_path/'site'
    site_bundle.export(value,output)
    assert site_bundle.verify(value,output)['verified']
    assert not any(value[k] for k in core.FLAGS)
    assert value['screening']['site_investigation_complete'] is False
    summary=core.read(output/'summary.json',maximum=20_000_000)
    summary['context']['groundwater_level_m']=2
    core.write(output/'summary.json',summary)
    with pytest.raises(ValueError,match='frozen baseline'):site_bundle.verify(value,output)
