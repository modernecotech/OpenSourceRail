# Coimbatore Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`coimbatore-line1.aln.toml`](coimbatore-line1.aln.toml) | `line-1` | 42,909.8 m | 16 |
| [`coimbatore-line2.aln.toml`](coimbatore-line2.aln.toml) | `line-2` | 23,232.3 m | 10 |
| [`coimbatore-line3.aln.toml`](coimbatore-line3.aln.toml) | `line-3` | 26,509.3 m | 12 |
| [`coimbatore-line4.aln.toml`](coimbatore-line4.aln.toml) | `line-4` | 29,530.6 m | 12 |
| [`coimbatore-line5.aln.toml`](coimbatore-line5.aln.toml) | `line-5` | 26,328.6 m | 11 |
| [`coimbatore-line6.aln.toml`](coimbatore-line6.aln.toml) | `line-6` | 32,363.4 m | 14 |
| [`coimbatore-line7.aln.toml`](coimbatore-line7.aln.toml) | `line-7` | 20,759.8 m | 12 |
| [`coimbatore-line8.aln.toml`](coimbatore-line8.aln.toml) | `line-8` | 26,531.8 m | 17 |
| [`coimbatore-line9.aln.toml`](coimbatore-line9.aln.toml) | `line-9` | 72,320.6 m | 30 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
