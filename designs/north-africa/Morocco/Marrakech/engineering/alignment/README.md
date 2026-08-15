# Marrakech Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`marrakech-line1.aln.toml`](marrakech-line1.aln.toml) | `line-1` | 29,159.9 m | 10 |
| [`marrakech-line2.aln.toml`](marrakech-line2.aln.toml) | `line-2` | 27,204.5 m | 9 |
| [`marrakech-line3.aln.toml`](marrakech-line3.aln.toml) | `line-3` | 26,428.7 m | 7 |
| [`marrakech-line4.aln.toml`](marrakech-line4.aln.toml) | `line-4` | 27,223.2 m | 8 |
| [`marrakech-line5.aln.toml`](marrakech-line5.aln.toml) | `line-5` | 34,036.5 m | 9 |
| [`marrakech-line6.aln.toml`](marrakech-line6.aln.toml) | `line-6` | 50,054.2 m | 14 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
