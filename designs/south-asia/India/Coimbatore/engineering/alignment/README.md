# Coimbatore Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`coimbatore-line1.aln.toml`](coimbatore-line1.aln.toml) | `line-1` | 48,163.5 m | 17 |
| [`coimbatore-line2.aln.toml`](coimbatore-line2.aln.toml) | `line-2` | 28,411.4 m | 10 |
| [`coimbatore-line3.aln.toml`](coimbatore-line3.aln.toml) | `line-3` | 32,783.2 m | 12 |
| [`coimbatore-line4.aln.toml`](coimbatore-line4.aln.toml) | `line-4` | 32,210.9 m | 8 |
| [`coimbatore-line5.aln.toml`](coimbatore-line5.aln.toml) | `line-5` | 31,070.5 m | 10 |
| [`coimbatore-line6.aln.toml`](coimbatore-line6.aln.toml) | `line-6` | 37,770.9 m | 14 |
| [`coimbatore-line7.aln.toml`](coimbatore-line7.aln.toml) | `line-7` | 23,408.6 m | 9 |
| [`coimbatore-line8.aln.toml`](coimbatore-line8.aln.toml) | `line-8` | 32,053.3 m | 10 |
| [`coimbatore-line9.aln.toml`](coimbatore-line9.aln.toml) | `line-9` | 76,086.9 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
