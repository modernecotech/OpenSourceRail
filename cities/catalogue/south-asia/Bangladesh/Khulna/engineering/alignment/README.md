# Khulna Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khulna-line1.aln.toml`](khulna-line1.aln.toml) | `line-1` | 28,254.7 m | 13 |
| [`khulna-line2.aln.toml`](khulna-line2.aln.toml) | `line-2` | 27,806.4 m | 8 |
| [`khulna-line3.aln.toml`](khulna-line3.aln.toml) | `line-3` | 24,096.7 m | 11 |
| [`khulna-line4.aln.toml`](khulna-line4.aln.toml) | `line-4` | 16,350.5 m | 6 |
| [`khulna-line5.aln.toml`](khulna-line5.aln.toml) | `line-5` | 24,051.4 m | 8 |
| [`khulna-line6.aln.toml`](khulna-line6.aln.toml) | `line-6` | 51,975.4 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
