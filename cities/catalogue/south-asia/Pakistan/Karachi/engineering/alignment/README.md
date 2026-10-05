# Karachi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karachi-line1.aln.toml`](karachi-line1.aln.toml) | `line-1` | 43,586.3 m | 16 |
| [`karachi-line2.aln.toml`](karachi-line2.aln.toml) | `line-2` | 34,156.2 m | 17 |
| [`karachi-line3.aln.toml`](karachi-line3.aln.toml) | `line-3` | 46,503.2 m | 20 |
| [`karachi-line4.aln.toml`](karachi-line4.aln.toml) | `line-4` | 27,767.0 m | 11 |
| [`karachi-line5.aln.toml`](karachi-line5.aln.toml) | `line-5` | 38,986.4 m | 15 |
| [`karachi-line6.aln.toml`](karachi-line6.aln.toml) | `line-6` | 39,978.1 m | 16 |
| [`karachi-line7.aln.toml`](karachi-line7.aln.toml) | `line-7` | 41,082.5 m | 20 |
| [`karachi-line8.aln.toml`](karachi-line8.aln.toml) | `line-8` | 47,253.2 m | 24 |
| [`karachi-line9.aln.toml`](karachi-line9.aln.toml) | `line-9` | 143,091.9 m | 54 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
