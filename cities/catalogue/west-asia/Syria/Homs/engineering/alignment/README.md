# Homs Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`homs-line1.aln.toml`](homs-line1.aln.toml) | `line-1` | 10,103.1 m | 7 |
| [`homs-line10.aln.toml`](homs-line10.aln.toml) | `line-10` | 6,124.2 m | 4 |
| [`homs-line2.aln.toml`](homs-line2.aln.toml) | `line-2` | 10,669.4 m | 8 |
| [`homs-line3.aln.toml`](homs-line3.aln.toml) | `line-3` | 12,511.3 m | 8 |
| [`homs-line4.aln.toml`](homs-line4.aln.toml) | `line-4` | 3,004.2 m | 2 |
| [`homs-line5.aln.toml`](homs-line5.aln.toml) | `line-5` | 2,160.5 m | 2 |
| [`homs-line6.aln.toml`](homs-line6.aln.toml) | `line-6` | 2,928.8 m | 3 |
| [`homs-line7.aln.toml`](homs-line7.aln.toml) | `line-7` | 6,996.0 m | 4 |
| [`homs-line8.aln.toml`](homs-line8.aln.toml) | `line-8` | 6,182.7 m | 4 |
| [`homs-line9.aln.toml`](homs-line9.aln.toml) | `line-9` | 5,575.3 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
