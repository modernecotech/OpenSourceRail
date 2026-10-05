# Davao Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`davao-line1.aln.toml`](davao-line1.aln.toml) | `line-1` | 41,092.0 m | 17 |
| [`davao-line2.aln.toml`](davao-line2.aln.toml) | `line-2` | 35,820.3 m | 18 |
| [`davao-line3.aln.toml`](davao-line3.aln.toml) | `line-3` | 39,940.1 m | 15 |
| [`davao-line4.aln.toml`](davao-line4.aln.toml) | `line-4` | 33,494.9 m | 13 |
| [`davao-line5.aln.toml`](davao-line5.aln.toml) | `line-5` | 29,051.3 m | 12 |
| [`davao-line6.aln.toml`](davao-line6.aln.toml) | `line-6` | 85,732.3 m | 35 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
