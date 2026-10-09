# Ramadi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ramadi-line1.aln.toml`](ramadi-line1.aln.toml) | `line-1` | 12,599.7 m | 9 |
| [`ramadi-line10.aln.toml`](ramadi-line10.aln.toml) | `line-10` | 2,759.9 m | 2 |
| [`ramadi-line11.aln.toml`](ramadi-line11.aln.toml) | `line-11` | 5,045.9 m | 6 |
| [`ramadi-line12.aln.toml`](ramadi-line12.aln.toml) | `line-12` | 3,660.0 m | 3 |
| [`ramadi-line2.aln.toml`](ramadi-line2.aln.toml) | `line-2` | 11,926.2 m | 8 |
| [`ramadi-line3.aln.toml`](ramadi-line3.aln.toml) | `line-3` | 13,223.8 m | 8 |
| [`ramadi-line4.aln.toml`](ramadi-line4.aln.toml) | `line-4` | 4,009.9 m | 4 |
| [`ramadi-line5.aln.toml`](ramadi-line5.aln.toml) | `line-5` | 3,420.2 m | 4 |
| [`ramadi-line6.aln.toml`](ramadi-line6.aln.toml) | `line-6` | 2,331.4 m | 2 |
| [`ramadi-line7.aln.toml`](ramadi-line7.aln.toml) | `line-7` | 7,229.6 m | 6 |
| [`ramadi-line8.aln.toml`](ramadi-line8.aln.toml) | `line-8` | 4,867.1 m | 3 |
| [`ramadi-line9.aln.toml`](ramadi-line9.aln.toml) | `line-9` | 3,136.8 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
