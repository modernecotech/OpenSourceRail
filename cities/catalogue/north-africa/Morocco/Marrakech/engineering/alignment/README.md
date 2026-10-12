# Marrakech Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`marrakech-line1.aln.toml`](marrakech-line1.aln.toml) | `line-1` | 27,750.9 m | 12 |
| [`marrakech-line2.aln.toml`](marrakech-line2.aln.toml) | `line-2` | 30,083.8 m | 13 |
| [`marrakech-line3.aln.toml`](marrakech-line3.aln.toml) | `line-3` | 21,134.7 m | 9 |
| [`marrakech-line4.aln.toml`](marrakech-line4.aln.toml) | `line-4` | 29,247.2 m | 16 |
| [`marrakech-line5.aln.toml`](marrakech-line5.aln.toml) | `line-5` | 35,835.0 m | 33 |
| [`marrakech-line6.aln.toml`](marrakech-line6.aln.toml) | `line-6` | 52,965.6 m | 33 |
| [`marrakech-line7.aln.toml`](marrakech-line7.aln.toml) | `line-7` | 5,917.9 m | 3 |
| [`marrakech-line8.aln.toml`](marrakech-line8.aln.toml) | `line-8` | 4,931.0 m | 3 |
| [`marrakech-line9.aln.toml`](marrakech-line9.aln.toml) | `line-9` | 11,867.2 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
