# Baghdad Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`baghdad-line1.aln.toml`](baghdad-line1.aln.toml) | `line-1` | 49,067.5 m | 17 |
| [`baghdad-line10.aln.toml`](baghdad-line10.aln.toml) | `line-10` | 6,803.6 m | 3 |
| [`baghdad-line11.aln.toml`](baghdad-line11.aln.toml) | `line-11` | 6,884.3 m | 2 |
| [`baghdad-line12.aln.toml`](baghdad-line12.aln.toml) | `line-12` | 6,586.4 m | 3 |
| [`baghdad-line13.aln.toml`](baghdad-line13.aln.toml) | `line-13` | 8,041.8 m | 4 |
| [`baghdad-line14.aln.toml`](baghdad-line14.aln.toml) | `line-14` | 6,047.0 m | 2 |
| [`baghdad-line2.aln.toml`](baghdad-line2.aln.toml) | `line-2` | 52,850.6 m | 14 |
| [`baghdad-line3.aln.toml`](baghdad-line3.aln.toml) | `line-3` | 49,496.5 m | 16 |
| [`baghdad-line4.aln.toml`](baghdad-line4.aln.toml) | `line-4` | 41,931.8 m | 12 |
| [`baghdad-line5.aln.toml`](baghdad-line5.aln.toml) | `line-5` | 47,344.8 m | 16 |
| [`baghdad-line6.aln.toml`](baghdad-line6.aln.toml) | `line-6` | 52,503.4 m | 16 |
| [`baghdad-line7.aln.toml`](baghdad-line7.aln.toml) | `line-7` | 39,957.0 m | 13 |
| [`baghdad-line8.aln.toml`](baghdad-line8.aln.toml) | `line-8` | 48,136.6 m | 15 |
| [`baghdad-line9.aln.toml`](baghdad-line9.aln.toml) | `line-9` | 97,684.2 m | 26 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
