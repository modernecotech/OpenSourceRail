# Hofuf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hofuf-line1.aln.toml`](hofuf-line1.aln.toml) | `line-1` | 23,534.5 m | 8 |
| [`hofuf-line2.aln.toml`](hofuf-line2.aln.toml) | `line-2` | 29,157.0 m | 9 |
| [`hofuf-line3.aln.toml`](hofuf-line3.aln.toml) | `line-3` | 23,957.3 m | 6 |
| [`hofuf-line4.aln.toml`](hofuf-line4.aln.toml) | `line-4` | 5,730.4 m | 3 |
| [`hofuf-line5.aln.toml`](hofuf-line5.aln.toml) | `line-5` | 6,112.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
