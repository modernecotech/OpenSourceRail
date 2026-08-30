# Davao Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`davao-line1.aln.toml`](davao-line1.aln.toml) | `line-1` | 47,206.1 m | 17 |
| [`davao-line2.aln.toml`](davao-line2.aln.toml) | `line-2` | 40,380.6 m | 15 |
| [`davao-line3.aln.toml`](davao-line3.aln.toml) | `line-3` | 36,372.7 m | 12 |
| [`davao-line4.aln.toml`](davao-line4.aln.toml) | `line-4` | 36,887.8 m | 14 |
| [`davao-line5.aln.toml`](davao-line5.aln.toml) | `line-5` | 32,058.7 m | 11 |
| [`davao-line6.aln.toml`](davao-line6.aln.toml) | `line-6` | 87,295.7 m | 30 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
