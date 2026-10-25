"""Exercise actual compiler station records, rather than renderer-only fixtures."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from engineering.ferrite_maglev import cities


def test_real_city_compilation_retains_terminal_ownership_and_context(tmp_path):
    city=cities.ROOT/'cities/catalogue/central-africa/Angola/Benguela'
    report=cities.generate(city,output_dir=tmp_path)
    svg=ET.parse(tmp_path/'network.svg');ns={'s':'http://www.w3.org/2000/svg'}
    definition=json.loads((city/'city.json').read_bytes())
    expected=2*sum(line['shape']=='radial' for line in definition['lines'])
    assert len(svg.findall('.//s:g[@id="current-proposal"]/s:rect',ns))==expected
    assert svg.find('.//s:g[@id="basemap-roads"]/s:path',ns) is not None
    assert svg.find('.//s:g[@id="basemap-labels"]/s:text',ns) is not None
    relative=(city/'map-context.json.gz').relative_to(cities.ROOT).as_posix()
    assert report['source_sha256'][relative]==cities.digest(city/'map-context.json.gz')
    assert report['map_context']['projection']=='EPSG:3857'
