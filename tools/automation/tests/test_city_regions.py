"""Angola uses the UN Middle/Central Africa catalogue bucket consistently."""
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'design/city-generation/src'))
from osr_batch.geonames_import import COUNTRY_CONTINENT


def test_angola_region_matches_catalogue_and_future_city_imports():
    entries=[c for c in tomllib.loads((ROOT/'lib/city-batches/world-sample.toml').read_text())['cities'] if c['country']=='AO']
    assert len(entries)==9 and all(c['continent']=='central-africa' for c in entries)
    assert COUNTRY_CONTINENT['AO']=='central-africa'
    assert not (ROOT/'cities/catalogue/east-africa/Angola').exists()
    paths=list((ROOT/'cities/catalogue/central-africa/Angola').glob('*/design.toml'))
    assert {tomllib.loads(p.read_text())['city']['slug'] for p in paths}=={c['slug'] for c in entries}
