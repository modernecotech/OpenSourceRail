import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('independent_water',ROOT/'tools/automation/refresh-city-water-evidence.py')
water = importlib.util.module_from_spec(spec)
spec.loader.exec_module(water)


def test_independent_lake_and_coast_coverage_survives_missing_osm_polygon():
    samples = np.array([[[80,80,80,80],[50,50,80,80],[50,50,50,50]]],dtype=np.uint8)
    assert water.combined_mask(samples,np.zeros((1,3),dtype=np.uint8)).tolist() == [[100,50,0]]


def test_unknown_coverage_cannot_be_interpreted_as_dry_land():
    samples = np.array([[[0,50,50,50],[80,80,80,0],[50,50,50,50]]],dtype=np.uint8)
    assert water.combined_mask(samples,np.array([[0,100,100]],dtype=np.uint8)).tolist() == [[255,255,100]]


def test_independent_samples_must_use_the_exact_grid():
    with pytest.raises(ValueError,match='grid differ'):
        water.combined_mask(np.zeros((2,2,4),dtype=np.uint8),np.zeros((1,2),dtype=np.uint8))


def test_southern_western_and_equatorial_tile_names():
    assert water.tile_name(-3,27)=='S03E027'
    assert water.tile_name(0,-3)=='N00W003'


def test_retained_bukavu_evidence_detects_lake_platforms():
    import json,gzip
    root = ROOT/'cities/catalogue/central-africa/DR Congo/Bukavu/engineering/alignment'
    receipt_path = root/'water-source-receipt.json'
    if not receipt_path.exists():pytest.skip('Independent publication has not yet been generated')
    grid=json.loads((root/'planning-grid.json').read_text())
    mask=gzip.decompress((root/'planning-water-mask.bin.gz').read_bytes())
    # Lake Kivu (-2.43, 28.84) was previously incorrectly marked dry.
    row=int((grid['bbox_north']+2.43)*grid['m_per_deg_lat']/grid['cell_m'])
    col=int((28.84-grid['bbox_west'])*grid['m_per_deg_lon']/grid['cell_m'])
    assert mask[row*grid['width']+col]>=50
    assert water.sha(mask)==json.loads(receipt_path.read_text())['mask_sha256']
