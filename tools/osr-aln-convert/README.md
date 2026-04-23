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
    --output ./designs/middle-east/iraq/samawah/samawah-line1.aln.toml \
    --line-id samawah-line1 \
    --preset standard-urban \
    --consist light-metro-3car \
    --crs EPSG:32638 \
    --surveyor "Samawah Civil Associates"
```

The `--line-id`, `--preset`, `--consist`, `--crs`, `--surveyor`
flags populate the `[meta]` block in the output TOML; the rest of
the document is derived from the LandXML geometry.

## What the v1 converter reads

From the input LandXML:

- **`<Alignments>/<Alignment>`** — one alignment per output file.
- **`<Alignment>/<CoordGeom>/<Line>`** + **`<Curve>`** +
  **`<Spiral>`** — horizontal alignment elements, emitted as
  `[[horizontal]]` rows.
- **`<Alignment>/<Profile>/<ProfAlign>/<PVI>`** — vertical profile
  points, emitted as `[[vertical]]` rows. Sag/crest curves (`<CircCurve>`)
  carry `vc_radius_m`.
- **`<Alignment>/<StaEquations>`** — station equations (not common
  in new builds; the converter emits them to a warning log rather
  than trying to unwrap them).

## What the v1 converter does NOT read

- **Station pin-pointing.** LandXML has `<Station>` on an
  alignment but most civil tools write stations as offsets on a
  separate `Survey` object. In v1 the converter emits a
  placeholder `[[station]]` for each input `<Station>`; the
  deployment engineer hand-edits to the design.toml station ids.
  v1.1 will accept a CSV sidecar mapping station-name → station
  id.
- **Civil classes (at-grade / elevated / bridge).** LandXML has no
  civil-class annotation. The converter emits a placeholder
  `[[civil]]` covering the full length as `at-grade`; the
  deployment engineer splits it per the RFC 0011 per-segment
  classification.
- **Cant (superelevation).** Bentley OpenRail writes cant into a
  non-standard `<Cant>` extension; Civil 3D writes it as a
  separate file. v1 leaves `[[cant]]` empty; v1.1 will read
  Bentley's extension.

These gaps are deliberate for v1 — the converter handles the
geometric bulk of the work (95 %+ of the line by volume of
decisions) and flags the rest for human review, matching the
RFC 0009 v3 scope.

## Round-trip validation

The converter ships with a sample LandXML at
[`samples/samawah-line1.xml`](samples/samawah-line1.xml) and the
corresponding golden output at
[`samples/samawah-line1.aln.toml`](samples/samawah-line1.aln.toml).
The test suite
([`tests/test_round_trip.py`](tests/test_round_trip.py)) runs the
converter against the sample and asserts byte-identical output.
Run with `pytest`.

## Coding-standard compliance

Per the `reference-ma` precedent: stdlib only, no numpy, no
pydantic. Every byte of behaviour should be readable by a civil-
engineering reviewer without chasing into a framework. The one
imported module outside the stdlib is `pytest`, dev-only.
