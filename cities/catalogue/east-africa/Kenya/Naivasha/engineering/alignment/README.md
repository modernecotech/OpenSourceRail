# Naivasha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`naivasha-line1.aln.toml`](naivasha-line1.aln.toml) | `line-1` | 13,699.6 m | 9 |
| [`naivasha-line10.aln.toml`](naivasha-line10.aln.toml) | `line-10` | 6,371.8 m | 6 |
| [`naivasha-line2.aln.toml`](naivasha-line2.aln.toml) | `line-2` | 8,280.5 m | 6 |
| [`naivasha-line3.aln.toml`](naivasha-line3.aln.toml) | `line-3` | 14,893.8 m | 11 |
| [`naivasha-line4.aln.toml`](naivasha-line4.aln.toml) | `line-4` | 2,955.9 m | 2 |
| [`naivasha-line5.aln.toml`](naivasha-line5.aln.toml) | `line-5` | 2,242.3 m | 2 |
| [`naivasha-line6.aln.toml`](naivasha-line6.aln.toml) | `line-6` | 2,432.8 m | 4 |
| [`naivasha-line7.aln.toml`](naivasha-line7.aln.toml) | `line-7` | 7,539.5 m | 5 |
| [`naivasha-line8.aln.toml`](naivasha-line8.aln.toml) | `line-8` | 7,936.3 m | 5 |
| [`naivasha-line9.aln.toml`](naivasha-line9.aln.toml) | `line-9` | 5,951.4 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
