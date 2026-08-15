# Khulna Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khulna-line1.aln.toml`](khulna-line1.aln.toml) | `line-1` | 34,467.3 m | 22 |
| [`khulna-line2.aln.toml`](khulna-line2.aln.toml) | `line-2` | 32,116.0 m | 19 |
| [`khulna-line3.aln.toml`](khulna-line3.aln.toml) | `line-3` | 26,342.2 m | 16 |
| [`khulna-line4.aln.toml`](khulna-line4.aln.toml) | `line-4` | 19,360.1 m | 11 |
| [`khulna-line5.aln.toml`](khulna-line5.aln.toml) | `line-5` | 27,044.1 m | 16 |
| [`khulna-line6.aln.toml`](khulna-line6.aln.toml) | `line-6` | 57,050.3 m | 36 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
