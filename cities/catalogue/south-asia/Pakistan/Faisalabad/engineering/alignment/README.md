# Faisalabad Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`faisalabad-line1.aln.toml`](faisalabad-line1.aln.toml) | `line-1` | 26,922.5 m | 10 |
| [`faisalabad-line2.aln.toml`](faisalabad-line2.aln.toml) | `line-2` | 18,850.7 m | 10 |
| [`faisalabad-line3.aln.toml`](faisalabad-line3.aln.toml) | `line-3` | 19,586.0 m | 10 |
| [`faisalabad-line4.aln.toml`](faisalabad-line4.aln.toml) | `line-4` | 20,927.4 m | 10 |
| [`faisalabad-line5.aln.toml`](faisalabad-line5.aln.toml) | `line-5` | 23,045.8 m | 9 |
| [`faisalabad-line6.aln.toml`](faisalabad-line6.aln.toml) | `line-6` | 39,189.3 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
