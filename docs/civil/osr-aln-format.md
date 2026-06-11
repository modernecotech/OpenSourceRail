# OSR-ALN — alignment interchange format (v1.0)

**Status:** v2 deliverable of [RFC 0009](../rfcs/0009-track-design-standard.md).
**Purpose:** a tool-agnostic text schema that civil-engineering
software (Civil 3D, Bentley OpenRail, Trimble, open-source
tools) can export *to* and the OSR simulator / emitter can
import *from*.

## Why OSR-ALN

Every civil-engineering firm uses a different authoring tool.
Every tool has a different native file format. LandXML covers
the generic case but is verbose and has many optional fields
that don't apply to urban rail.

**OSR-ALN is a minimal text format that round-trips a
rail-ready alignment to / from any tool.** It is a 100%-plain-
text TOML schema (no XML, no binary) with one row per
`HorizontalPoint` + one row per `VerticalPoint`. A civil firm
produces OSR-ALN from their native format as part of the
deployment deliverable; the OSR pipeline validates it against
RFC 0009's compatibility matrix and feeds `osr-sim` +
`osr-routing` without further adaptation.

## File layout

One alignment per line per file. Filename convention:
`<city>-<line>.aln.toml`. Example:
`sample-city-line-a.aln.toml`.

```toml
# OSR-ALN v1.0 — alignment interchange format per RFC 0009 v2.
[meta]
schema_version = "1.0"
line_id        = "sample-city-line-a"
design_date    = "2026-04-22"
surveyor       = "<firm name>"
preset         = "standard-urban"       # RFC 0009 §1 preset key
consist        = "light-metro-3car"     # RFC 0008 §1 family key
crs            = "EPSG:32638"           # Coordinate Reference System (UTM Zone 38N for Iraq)
units          = "metric"               # SI only — OSR is SI
is_ring        = false

# ----------------------------------------------------------------------
# Horizontal alignment points — tangent + circular + transition elements
# expressed as a sequence of PI (Point of Intersection) with before /
# after bearings. The standard alignment reconstructs the clothoid
# transition curves deterministically from adjacent PIs + the declared
# radii + transition lengths.
# ----------------------------------------------------------------------

[[horizontal]]
station_m          = 0.0
easting_m          = 477_500.00       # UTM
northing_m         = 3_467_100.00
bearing_in_deg     = 128.7
bearing_out_deg    = 128.7
curve_radius_m     = 0.0              # 0 = tangent
transition_length_m = 0.0

[[horizontal]]
station_m          = 1_000.0
easting_m          = 478_135.50
northing_m         = 3_466_522.00
bearing_in_deg     = 128.7
bearing_out_deg    = 123.7            # Curve begins here
curve_radius_m     = 26_300.0
transition_length_m = 2.0              # Clothoid transition length

# ... more rows one per PI or tangent endpoint ...

# ----------------------------------------------------------------------
# Vertical alignment points — elevation along station_m. Interpolation
# is linear between adjacent points with a circular vertical curve of
# radius `vc_radius_m` at each grade-change point.
# ----------------------------------------------------------------------

[[vertical]]
station_m     = 0.0
elevation_m   = 6.0                    # at top of rail
vc_radius_m   = 0.0                    # 0 = tangent (no vertical curve here)

[[vertical]]
station_m     = 1_000.0
elevation_m   = 6.0                    # still level
vc_radius_m   = 0.0

[[vertical]]
station_m     = 1_150.0
elevation_m   = 11.25                   # top of ramp into viaduct
vc_radius_m   = 300.0                   # sag curve

# ...

# ----------------------------------------------------------------------
# Civil-class spans — per-class segment between two station_m values.
# Must cover the full [0, total_length_m] range with no gaps and no
# overlaps.
# ----------------------------------------------------------------------

[[civil]]
from_station_m = 0.0
to_station_m   = 1_000.0
class          = "at-grade"

[[civil]]
from_station_m = 1_000.0
to_station_m   = 2_300.0
class          = "elevated"

[[civil]]
from_station_m = 4_100.0
to_station_m   = 5_300.0
class          = "bridge"

# ...

# ----------------------------------------------------------------------
# Stations on this alignment — references the station ids in the
# deployment's design.toml. station_m pinpoints the platform
# centreline stop mark on this alignment.
# ----------------------------------------------------------------------

[[station]]
id          = "samawah-rws"
station_m   = 0.0
platform_length_m = 61.0              # derived from consist per RFC 0010

[[station]]
id          = "north-gate"
station_m   = 1_000.0
platform_length_m = 61.0

# ...

# ----------------------------------------------------------------------
# Superelevation (cant) per curved span. One row per cant-change PI.
# ----------------------------------------------------------------------

[[cant]]
from_station_m  = 1_000.0
to_station_m    = 2_300.0
max_cant_mm     = 30
transition_in_m = 50.0                 # cant development length in
transition_out_m = 50.0                # cant runoff length out
```

## Required fields per section

### [meta]

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | Always `"1.0"` for this format |
| `line_id` | string | yes | Matches a `[[lines]] name` in design.toml |
| `design_date` | date | yes | ISO 8601 |
| `surveyor` | string | yes | Civil firm of record |
| `preset` | string | yes | Must be one of the RFC 0009 §1 presets |
| `consist` | string | yes | Must be one of the RFC 0008 §1 families |
| `crs` | string | yes | EPSG code or WKT; UTM zone typical |
| `units` | string | yes | Always `"metric"` |
| `is_ring` | bool | yes | Whether the line loops back |

### [[horizontal]]

Sequence of horizontal points along the alignment. `station_m`
values must be monotonic-ascending. Bearings are in compass
degrees (0° = north, 90° = east). Tangent segments have
`curve_radius_m = 0.0`. Transition curves (clothoids) are
declared on the entry/exit of each circular curve via
`transition_length_m`.

### [[vertical]]

Sequence of vertical points. `station_m` monotonic-ascending.
`elevation_m` is top-of-rail elevation above the local datum
(typically mean sea level, per `crs`). `vc_radius_m` declares
a circular vertical curve at grade-change points; 0 = sharp
grade break (discouraged above 2.5 ‰).

### [[civil]]

Civil-class spans covering the full length. No gaps, no
overlaps. `class` must be one of `at-grade`, `elevated`,
`bridge` per RFC 0011 — **no `tunnel`** (v2 validator rejects).

### [[station]]

Platform centrelines along the alignment. Every station id
must match a `[[stations]]` block in the deployment's
`design.toml`.

### [[cant]]

Optional superelevation ramp + full-cant section + runoff.
Absent cant rows mean `max_cant_mm = 0` for that span (tangent
track).

## Validator semantics

A validator ships at
[`tools/osr-aln-convert/src/osr_aln/validate.py`](../../tools/osr-aln-convert/src/osr_aln/validate.py)
(exposed as the `osr-aln-validate` CLI after `pip install -e .`).
It checks:

### Hard gates (reject on fail)

1. `meta.preset` is one of the four RFC 0009 presets.
2. `meta.consist` is in the preset's `compatible_consists`.
3. `[[civil]]` spans are contiguous and cover the full length.
4. No `[[civil]]` has `class = "tunnel"`.
5. Every station id has a matching entry in the deployment's
   design.toml.
6. Every curve's `curve_radius_m` ≥ preset's `min_curve_radius_m`.
7. Every vertical grade ≤ preset's `max_gradient_per_mille`.
8. Every `max_cant_mm` ≤ preset's `max_cant_mm`.

### Soft gates (warn, don't reject)

1. Elevated share > 30 % → RFC 0011 §8 soft gate.
2. Any curve radius ≤ 2× preset minimum → flag for speed
   restriction.
3. Any grade > 80 % of preset maximum → flag.

### Round-trip consistency

Round-tripping OSR-ALN → simulator → OSR-ALN must produce a
byte-identical file. The simulator may compute derived
quantities (stopping distance, power draw, etc.) but must not
modify the alignment.

## Tool support

Converter at [`tools/osr-aln-convert/`](../../tools/osr-aln-convert/)
— stdlib-only Python; installs with `pip install -e .` and
exposes one CLI per source format.

Firms using:

- **Autodesk Civil 3D** — export via LandXML, then transform
  with `landxml-to-osr-aln`. ✅ v1 (shipping).
- **Bentley OpenRail** — export via LandXML (OpenRail emits a
  compatible subset), transform with `landxml-to-osr-aln`. Cant
  data is written to a non-standard `<Cant>` extension that v1.1
  will read. ✅ v1.
- **Trimble Business Center** — export via LandXML, transform
  with `landxml-to-osr-aln`. A TCL CSV reader is v1.1. ✅ v1
  via LandXML.
- **Open-source (QGIS + rail-path plugins)** — LandXML export
  supported. ✅ v1.

## Validation Example

A deployment exports one `.aln.toml` file per surveyed line and
validates it against the current generated `design.toml` for that city:

```
$ osr-aln-validate exports/survey/samawah-line-1.aln.toml \
                   --design-toml designs/west-asia/Iraq/Samawah/design.toml
2 soft-gate warning(s):
  ⚠ S3: grade between [[vertical]] #1 and #2 is 35.00 ‰ — within 80 %
       of preset maximum 40.0 ‰, flag for review
  ⚠ S3: grade between [[vertical]] #5 and #6 is 35.00 ‰ — within 80 %
       of preset maximum 40.0 ‰, flag for review
```

Both warnings are expected (the two viaduct ramps at 35 ‰);
no hard gates fire.

## Version history

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-04-22 | Initial spec |

## What v2 does NOT include

- Reference validator implementation (v3).
- Per-tool converter scripts (v3).
- A "delta file" format for alignment updates during
  construction (v4, if ever needed).
- Drainage profiles — handled separately at civil-design
  time, not part of the alignment.
