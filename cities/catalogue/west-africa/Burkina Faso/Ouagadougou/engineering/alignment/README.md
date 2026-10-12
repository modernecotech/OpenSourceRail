# Ouagadougou Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ouagadougou-line1.aln.toml`](ouagadougou-line1.aln.toml) | `line-1` | 39,351.2 m | 26 |
| [`ouagadougou-line2.aln.toml`](ouagadougou-line2.aln.toml) | `line-2` | 19,345.3 m | 7 |
| [`ouagadougou-line3.aln.toml`](ouagadougou-line3.aln.toml) | `line-3` | 25,524.5 m | 8 |
| [`ouagadougou-line4.aln.toml`](ouagadougou-line4.aln.toml) | `line-4` | 27,702.1 m | 10 |
| [`ouagadougou-line5.aln.toml`](ouagadougou-line5.aln.toml) | `line-5` | 33,324.2 m | 26 |
| [`ouagadougou-line6.aln.toml`](ouagadougou-line6.aln.toml) | `line-6` | 67,297.7 m | 21 |
| [`ouagadougou-line7.aln.toml`](ouagadougou-line7.aln.toml) | `line-7` | 5,501.6 m | 2 |
| [`ouagadougou-line8.aln.toml`](ouagadougou-line8.aln.toml) | `line-8` | 8,065.8 m | 3 |
| [`ouagadougou-line9.aln.toml`](ouagadougou-line9.aln.toml) | `line-9` | 6,110.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
