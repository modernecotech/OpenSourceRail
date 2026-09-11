"""Synthetic deployment mappings must preserve identity and reject drift."""

import hashlib
import json
import tomllib

import pytest

from osr_aln.landxml_to_osr_aln import Meta, convert, main
from osr_aln.validate import validate


def write_sidecar(path, document):
    lines = ["schema_version = 1"]
    if not document["cant"]:
        lines.append("cant = []")
    lines.append("[source]")
    lines.extend(f"{k} = {json.dumps(v)}" for k, v in document["source"].items())
    for section in ("station", "civil", "cant"):
        for row in document[section]:
            lines.append(f"[[{section}]]")
            lines.extend(f"{k} = {json.dumps(v) if isinstance(v, str) else str(v).lower()}" for k, v in row.items())
    path.write_text("\n".join(lines) + "\n")


@pytest.fixture
def inputs(tmp_path):
    xml, design, sidecar = [tmp_path / n for n in ("line.xml", "design.toml", "sidecar.toml")]
    xml.write_text('''<LandXML xmlns="http://www.landxml.org/schema/LandXML-1.2">
<Units><Metric linearUnit="meter"/></Units><Alignments>
<Alignment name="other" length="1000"/>
<Alignment name="Survey A" length="1000" staStart="0">
<CoordGeom><Line staStart="0" length="1000"><Start>0 0</Start><End>1000 0</End></Line></CoordGeom>
<Profile><ProfAlign><PVI>0 10</PVI><PVI>1000 10</PVI></ProfAlign></Profile>
<Station name="South" station="100"/><Station name="North" station="900"/>
</Alignment></Alignments></LandXML>''')
    design.write_text('''[[lines]]
name = "L1"
rolling_stock = "light-metro-3car"
geometry = "standard-urban"
[[stations]]
id = "south-id"
line = "L1"
[[stations]]
id = "north-id"
line = "L1"
[[stations]]
id = "another-line-id"
line = "L2"
''')
    document = {
        "source": {"landxml_sha256": hashlib.sha256(xml.read_bytes()).hexdigest(),
                   "design_sha256": hashlib.sha256(design.read_bytes()).hexdigest(),
                   "alignment_name": "Survey A", "line_id": "L1", "crs": "EPSG:32638",
                   "vertical_datum": 'Synthetic "datum"'},
        "station": [{"id": "south-id", "source_name": "South", "station_m": 100.0, "platform_length_m": 61.0},
                    {"id": "north-id", "source_name": "North", "station_m": 900.0, "platform_length_m": 75.0}],
        "civil": [{"from_station_m": 0.0, "to_station_m": 600.0, "class": "at-grade"},
                  {"from_station_m": 600.0, "to_station_m": 1000.0, "class": "bridge"}],
        "cant": [{"from_station_m": 400.0, "to_station_m": 600.0, "max_cant_mm": 30,
                  "transition_in_m": 50.0, "transition_out_m": 50.0}],
    }
    write_sidecar(sidecar, document)
    meta = Meta("L1", "standard-urban", "light-metro-3car", "EPSG:32638", 'Synthetic "reviewer"', "2026-09-10")
    return xml, design, sidecar, document, meta


def converted(inputs):
    xml, design, sidecar, _, meta = inputs
    return convert(xml, meta, sidecar_path=sidecar, design_path=design)


def test_named_alignment_and_complete_mapping_are_deterministic(inputs):
    text = converted(inputs)
    assert converted(inputs) == text
    doc = tomllib.loads(text)
    source = inputs[3]
    assert doc["station"] == [{k: v for k, v in s.items() if k != "source_name"} for s in source["station"]]
    assert doc["civil"] == source["civil"]
    assert doc["cant"] == source["cant"]
    assert doc["meta"]["vertical_datum"] == 'Synthetic "datum"'
    assert doc["meta"]["surveyor"] == 'Synthetic "reviewer"'
    assert doc["provenance"]["sidecar_sha256"] == hashlib.sha256(inputs[2].read_bytes()).hexdigest()
    assert doc["provenance"]["landxml_sha256"] == source["source"]["landxml_sha256"]
    assert doc["provenance"]["deployment_release_ready"] is False
    assert "REVIEW REQUIRED: classify" not in text
    assert validate(doc, {"south-id", "north-id"}, {"L1"}).ok


@pytest.mark.parametrize("index", [0, 1])
def test_changed_source_revision_is_rejected(inputs, index):
    path = inputs[index]
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="input revision"):
        converted(inputs)


@pytest.mark.parametrize("section,index,key,value,error", [
    ("station", 0, "id", "another-line-id", "another line"),
    ("station", 1, "id", "south-id", "duplicated"),
    ("station", 0, "source_name", "Missing", "source_name"),
    ("station", 0, "station_m", 101.0, "disagrees"),
    ("station", 0, "station_m", float("nan"), "finite"),
    ("station", 0, "platform_length_m", -1.0, "range"),
    ("civil", 1, "from_station_m", 601.0, "gap"),
    ("civil", 1, "from_station_m", 599.0, "overlap"),
    ("civil", 1, "to_station_m", 999.0, "full alignment"),
    ("civil", 0, "class", "tunnel", "civil class"),
    ("cant", 0, "max_cant_mm", 151, "preset"),
    ("cant", 0, "max_cant_mm", -1, "preset"),
    ("cant", 0, "transition_in_m", 160, "transitions"),
    ("cant", 0, "transition_out_m", 0, "transitions"),
    ("cant", 0, "to_station_m", 1001, "outside"),
])
def test_invalid_mappings_fail_closed(inputs, section, index, key, value, error):
    inputs[3][section][index][key] = value
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(ValueError, match=error):
        converted(inputs)


def test_missing_station_and_overlapping_cant_are_rejected(inputs):
    station = inputs[3]["station"].pop()
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(ValueError, match="every station"):
        converted(inputs)
    inputs[3]["station"].append(station)
    inputs[3]["cant"].append(dict(inputs[3]["cant"][0]))
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(ValueError, match="overlap"):
        converted(inputs)


@pytest.mark.parametrize("key,value", [("line_id", "L2"), ("crs", "EPSG:4326"), ("alignment_name", "absent")])
def test_wrong_line_crs_or_alignment_are_rejected(inputs, key, value):
    inputs[3]["source"][key] = value
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(ValueError):
        converted(inputs)


def test_external_station_chainages_and_explicit_zero_cant(inputs):
    xml = inputs[0]
    xml.write_text(xml.read_text().replace('<Station name="South" station="100"/><Station name="North" station="900"/>', ''))
    inputs[3]["source"]["landxml_sha256"] = hashlib.sha256(xml.read_bytes()).hexdigest()
    for row in inputs[3]["station"]:
        del row["source_name"]
    inputs[3]["cant"] = []
    write_sidecar(inputs[2], inputs[3])
    doc = tomllib.loads(converted(inputs))
    assert len(doc["station"]) == 2
    assert doc.get("cant", []) == []


@pytest.mark.parametrize("old,new,error", [
    ('linearUnit="meter"', 'linearUnit="foot"', "metre"),
    ('staStart="0"', 'staStart="100"', "chainage origins"),
    ('<CoordGeom>', '<StaEquations/><CoordGeom>', "station equations"),
    ('<CoordGeom>', '<StaEquation staBack="500" staAhead="550"/><CoordGeom>', "station equations"),
])
def test_unsupported_units_and_chainage_transforms_are_not_silently_imported(inputs, old, new, error):
    xml = inputs[0]
    xml.write_text(xml.read_text().replace(old, new))
    inputs[3]["source"]["landxml_sha256"] = hashlib.sha256(xml.read_bytes()).hexdigest()
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(ValueError, match=error):
        converted(inputs)


def test_cli_failure_preserves_existing_output(inputs, tmp_path):
    output = tmp_path / "retained.aln.toml"
    output.write_text("existing reviewed alignment\n")
    inputs[3]["source"]["crs"] = "EPSG:4326"
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(SystemExit) as error:
        main(["--input", str(inputs[0]), "--sidecar", str(inputs[2]), "--design", str(inputs[1]),
              "--output", str(output), "--line-id", "L1", "--preset", "standard-urban",
              "--consist", "light-metro-3car", "--crs", "EPSG:32638"])
    assert error.value.code == 2
    assert output.read_text() == "existing reviewed alignment\n"


def test_cli_writes_a_validated_mapping(inputs, tmp_path):
    output = tmp_path / "mapped.aln.toml"
    assert main(["--input", str(inputs[0]), "--sidecar", str(inputs[2]), "--design", str(inputs[1]),
                 "--output", str(output), "--line-id", "L1", "--preset", "standard-urban",
                 "--consist", "light-metro-3car", "--crs", "EPSG:32638",
                 "--surveyor", inputs[4].surveyor, "--design-date", inputs[4].design_date]) == 0
    assert output.read_text() == converted(inputs)


@pytest.mark.parametrize("field,value", [("consist", "metro-6car"), ("preset", "standard-metro"), ("is_ring", True)])
def test_conversion_metadata_must_match_the_declared_design(inputs, field, value):
    setattr(inputs[4], field, value)
    with pytest.raises(ValueError, match="disagrees with design"):
        converted(inputs)


def test_geometry_hard_gates_still_apply_with_valid_mapping(inputs):
    xml = inputs[0]
    xml.write_text(xml.read_text().replace("1000 10</PVI>", "1000 500</PVI>"))
    inputs[3]["source"]["landxml_sha256"] = hashlib.sha256(xml.read_bytes()).hexdigest()
    write_sidecar(inputs[2], inputs[3])
    with pytest.raises(ValueError, match="H7"):
        converted(inputs)
