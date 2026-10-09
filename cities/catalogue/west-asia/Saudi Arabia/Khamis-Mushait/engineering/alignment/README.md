# Khamis-Mushait Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khamis-mushait-line1.aln.toml`](khamis-mushait-line1.aln.toml) | `line-1` | 26,361.5 m | 13 |
| [`khamis-mushait-line10.aln.toml`](khamis-mushait-line10.aln.toml) | `line-10` | 5,317.5 m | 4 |
| [`khamis-mushait-line11.aln.toml`](khamis-mushait-line11.aln.toml) | `line-11` | 2,359.9 m | 2 |
| [`khamis-mushait-line12.aln.toml`](khamis-mushait-line12.aln.toml) | `line-12` | 12,433.4 m | 8 |
| [`khamis-mushait-line13.aln.toml`](khamis-mushait-line13.aln.toml) | `line-13` | 2,652.4 m | 2 |
| [`khamis-mushait-line14.aln.toml`](khamis-mushait-line14.aln.toml) | `line-14` | 2,001.9 m | 2 |
| [`khamis-mushait-line15.aln.toml`](khamis-mushait-line15.aln.toml) | `line-15` | 11,835.5 m | 7 |
| [`khamis-mushait-line16.aln.toml`](khamis-mushait-line16.aln.toml) | `line-16` | 4,159.6 m | 3 |
| [`khamis-mushait-line17.aln.toml`](khamis-mushait-line17.aln.toml) | `line-17` | 2,193.6 m | 2 |
| [`khamis-mushait-line2.aln.toml`](khamis-mushait-line2.aln.toml) | `line-2` | 23,419.5 m | 15 |
| [`khamis-mushait-line3.aln.toml`](khamis-mushait-line3.aln.toml) | `line-3` | 23,890.5 m | 14 |
| [`khamis-mushait-line4.aln.toml`](khamis-mushait-line4.aln.toml) | `line-4` | 3,637.5 m | 3 |
| [`khamis-mushait-line5.aln.toml`](khamis-mushait-line5.aln.toml) | `line-5` | 5,980.1 m | 4 |
| [`khamis-mushait-line6.aln.toml`](khamis-mushait-line6.aln.toml) | `line-6` | 4,326.2 m | 3 |
| [`khamis-mushait-line7.aln.toml`](khamis-mushait-line7.aln.toml) | `line-7` | 5,646.4 m | 5 |
| [`khamis-mushait-line8.aln.toml`](khamis-mushait-line8.aln.toml) | `line-8` | 5,774.1 m | 5 |
| [`khamis-mushait-line9.aln.toml`](khamis-mushait-line9.aln.toml) | `line-9` | 5,161.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
