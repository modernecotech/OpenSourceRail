# osr-aln-convert — civil-tool bridge for OSR-ALN

**RFC 0009 v3 deliverable.** Reads the alignment file every civil-
engineering firm already produces and emits the
[OSR-ALN](../../docs/civil/osr-aln-format.md) TOML that the OSR
pipeline ingests.

## What converters ship today

| Source tool | Export format | Converter | Status |
|---|---|---|---|
| Autodesk Civil 3D | LandXML | `landxml-to-osr-aln` | ✅ v1 |
| Bentley OpenRail | LandXML | `landxml-to-osr-aln` | ✅ v1 (same converter — OpenRail emits a compatible LandXML subset) |
| Trimble Business Center | LandXML | `landxml-to-osr-aln` | ✅ v1 |
| Trimble Business Center | CSV | `tcl-to-osr-aln` | pending v1.1 |
| QGIS + rail-path plugins | LandXML via plugin | `landxml-to-osr-aln` | ✅ v1 |
| OSR generated city design | `design.toml` + corridor GeoJSON | `current-network-to-osr-aln` | ✅ planning export |

One converter covers the three LandXML-emitting tools; they share
the `<Alignments>` + `<Profiles>` schema that Civil 3D defined and
Bentley + Trimble adopted.

## Usage

```bash
# One-time install (stdlib-only converter; no wheels to build).
pip install -e .

# Convert a LandXML dump from Civil 3D / OpenRail / Trimble.
landxml-to-osr-aln \
    --input  ./exports/samawah-line1.xml \
    --output ./cities/catalogue/west-asia/Iraq/Samawah/engineering/alignment/samawah-line1.aln.toml \
    --line-id samawah-line1 \
    --preset standard-urban \
    --consist light-metro-3car \
    --crs EPSG:32638 \
    --surveyor "Samawah Civil Associates"
```

The `--line-id`, `--preset`, `--consist`, `--crs`, `--surveyor`
flags populate the `[meta]` block in the output TOML; the rest of
the document is derived from the LandXML geometry. Station
placeholder platform lengths default from the selected `--consist`
per RFC 0008/0010; use `--platform-length-default` when a civil
package deliberately safeguards a longer local platform.

To regenerate a current OSR planning network directly from checked-in city
artifacts:

```bash
current-network-to-osr-aln \
    --design ../../cities/catalogue/west-asia/Iraq/Samawah/design.toml \
    --geojson ../../cities/catalogue/west-asia/Iraq/Samawah/samawah.corridor.geojson \
    --output-dir ../../cities/catalogue/west-asia/Iraq/Samawah/engineering/alignment \
    --design-date 2026-08-12
```

This path emits one file per current line, verifies line/station IDs and civil
coverage against `design.toml`, and embeds input hashes for drift review. It is
explicitly planning-only: the generated GIS trace has no fitted curves,
surveyed vertical profile, or designed cant. See the
[`Samawah package notice`](../../cities/catalogue/west-asia/Iraq/Samawah/engineering/alignment/README.md)
for the replacement gates.

## Explicit station, civil and cant companion data

Use `--sidecar line.mapping.toml --design design.toml` with the LandXML
command above to import reviewed station IDs, civil spans and cant. The
companion is TOML, so one file holds the three mappings and their provenance.
It selects a named alignment, including from a multi-alignment XML file.

```toml
schema_version = 1
# Use cant = [] here only when the supplied design explicitly has no cant.

[source]
landxml_sha256 = "<SHA-256 of the exact XML bytes>"
design_sha256 = "<SHA-256 of the exact design.toml bytes>"
alignment_name = "Survey A"
line_id = "line-1"
crs = "EPSG:32638"
vertical_datum = "<datum of the supplied elevation data>"

[[station]]
id = "<station ID on line-1 in design.toml>"
source_name = "<matching LandXML Station name>"
station_m = 100.0
platform_length_m = 61.0

[[civil]]
from_station_m = 0.0
to_station_m = 1000.0
class = "at-grade"

[[cant]]
from_station_m = 400.0
to_station_m = 600.0
max_cant_mm = 30
transition_in_m = 50.0
transition_out_m = 50.0
```

This is a schema illustration, not deployment data. Replace the placeholders,
include every station on the selected design line, and cover the complete
alignment with contiguous civil spans. Every XML station name must map once,
at its original chainage. Additional stations may supply chainages without
`source_name` when the XML has no corresponding station object. Civil and cant
spans cannot overlap; cant limits follow the selected preset, with nonzero
ramps fitting inside each nonzero-cant span.

The importer checks the two source hashes, line/consist/preset/ring identity,
CRS agreement, finite values, metric metre units and zero-origin chainage.
It rejects station equations, nonzero chainage origins, incomplete mappings
and unknown fields. The existing OSR-ALN hard gates also run before output is
written. CRS and vertical datum are declarations of the supplied coordinates;
the converter does not transform or independently verify them. Output retains
all three input hashes and `deployment_release_ready = false`. Passing these
checks does not replace engineering review or authority approval.

Without `--sidecar`, the existing placeholder workflow and golden fixture
remain unchanged.

## What the converter reads

From the input LandXML:

- **`<Alignments>/<Alignment>`** — one alignment per output file.
- **`<Alignment>/<CoordGeom>/<Line>`** + **`<Curve>`** +
  **`<Spiral>`** — horizontal alignment elements, emitted as
  `[[horizontal]]` rows.
- **`<Alignment>/<Profile>/<ProfAlign>/<PVI>`** — vertical profile
  points, emitted as `[[vertical]]` rows. Sag/crest curves (`<CircCurve>`)
  carry `vc_radius_m`.
- The companion-file path rejects **`<Alignment>/<StaEquations>`**;
  station-equation transforms are not implemented. The legacy path does not
  interpret them and must not be used for those exports.

## Remaining format limits

- **Station pin-pointing.** LandXML has `<Station>` on an
  alignment but most civil tools write stations as offsets on a
  separate `Survey` object. In v1 the converter emits a
  placeholder `[[station]]` for each input `<Station>`; the
  deployment engineer can use the companion file above to map names to
  design.toml station IDs or supply externally derived station chainages.
  Direct Survey-object interpretation and CSV mapping are not implemented.
- **Civil classes (at-grade / elevated / bridge).** LandXML has no
  civil-class annotation. The converter emits a placeholder
  `[[civil]]` covering the full length as `at-grade`; the
  companion file replaces this placeholder with explicit RFC 0011 spans.
- **Cant (superelevation).** Bentley OpenRail writes cant into a
  non-standard `<Cant>` extension; Civil 3D writes it as a
  separate file. The companion file imports explicit `[[cant]]` rows;
  direct interpretation of vendor cant extensions remains unimplemented.

The companion file closes the explicit station/civil/cant mapping task while
keeping vendor-specific parsing and survey acceptance separate.

## Synthetic round-trip fixture (not deployment data)

The converter ships with a deliberately abbreviated golden fixture at
[`samples/samawah-line1.xml`](samples/samawah-line1.xml) and the
corresponding golden output at
[`samples/samawah-line1.aln.toml`](samples/samawah-line1.aln.toml).
The historical name is retained to avoid disguising fixture provenance, but
the 3 km illustrative geometry is not a surveyed or current Samawah alignment;
see the [`samples/` fixture notice](samples/README.md).
The test suite
([`tests/test_round_trip.py`](tests/test_round_trip.py)) runs the
converter against the sample and asserts byte-identical output.
Run with `pytest`.

## Coding-standard compliance

Per the `reference-ma` precedent: stdlib only, no numpy, no
pydantic. Every byte of behaviour should be readable by a civil-
engineering reviewer without chasing into a framework. The one
imported module outside the stdlib is `pytest`, dev-only.
