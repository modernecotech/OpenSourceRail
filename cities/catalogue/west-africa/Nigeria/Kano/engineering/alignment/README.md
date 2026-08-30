# Kano Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kano-line1.aln.toml`](kano-line1.aln.toml) | `line-1` | 43,384.5 m | 15 |
| [`kano-line2.aln.toml`](kano-line2.aln.toml) | `line-2` | 46,035.4 m | 17 |
| [`kano-line3.aln.toml`](kano-line3.aln.toml) | `line-3` | 45,096.8 m | 15 |
| [`kano-line4.aln.toml`](kano-line4.aln.toml) | `line-4` | 39,300.0 m | 14 |
| [`kano-line5.aln.toml`](kano-line5.aln.toml) | `line-5` | 38,252.3 m | 13 |
| [`kano-line6.aln.toml`](kano-line6.aln.toml) | `line-6` | 33,872.1 m | 10 |
| [`kano-line7.aln.toml`](kano-line7.aln.toml) | `line-7` | 52,622.0 m | 17 |
| [`kano-line8.aln.toml`](kano-line8.aln.toml) | `line-8` | 45,895.0 m | 15 |
| [`kano-line9.aln.toml`](kano-line9.aln.toml) | `line-9` | 89,951.9 m | 26 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
