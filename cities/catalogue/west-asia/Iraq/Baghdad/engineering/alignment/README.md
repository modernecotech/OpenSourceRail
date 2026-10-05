# Baghdad Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`baghdad-line1.aln.toml`](baghdad-line1.aln.toml) | `line-1` | 49,067.5 m | 20 |
| [`baghdad-line2.aln.toml`](baghdad-line2.aln.toml) | `line-2` | 52,850.6 m | 20 |
| [`baghdad-line3.aln.toml`](baghdad-line3.aln.toml) | `line-3` | 49,496.5 m | 20 |
| [`baghdad-line4.aln.toml`](baghdad-line4.aln.toml) | `line-4` | 41,931.8 m | 16 |
| [`baghdad-line5.aln.toml`](baghdad-line5.aln.toml) | `line-5` | 47,344.8 m | 20 |
| [`baghdad-line6.aln.toml`](baghdad-line6.aln.toml) | `line-6` | 52,503.4 m | 21 |
| [`baghdad-line7.aln.toml`](baghdad-line7.aln.toml) | `line-7` | 39,957.0 m | 16 |
| [`baghdad-line8.aln.toml`](baghdad-line8.aln.toml) | `line-8` | 48,136.6 m | 18 |
| [`baghdad-line9.aln.toml`](baghdad-line9.aln.toml) | `line-9` | 97,724.2 m | 35 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
