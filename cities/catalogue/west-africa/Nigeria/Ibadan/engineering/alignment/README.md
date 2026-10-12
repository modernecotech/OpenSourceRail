# Ibadan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ibadan-line1.aln.toml`](ibadan-line1.aln.toml) | `line-1` | 21,493.6 m | 10 |
| [`ibadan-line2.aln.toml`](ibadan-line2.aln.toml) | `line-2` | 17,180.3 m | 10 |
| [`ibadan-line3.aln.toml`](ibadan-line3.aln.toml) | `line-3` | 15,772.7 m | 6 |
| [`ibadan-line4.aln.toml`](ibadan-line4.aln.toml) | `line-4` | 30,330.4 m | 44 |
| [`ibadan-line5.aln.toml`](ibadan-line5.aln.toml) | `line-5` | 34,817.3 m | 43 |
| [`ibadan-line6.aln.toml`](ibadan-line6.aln.toml) | `line-6` | 5,227.0 m | 7 |
| [`ibadan-line7.aln.toml`](ibadan-line7.aln.toml) | `line-7` | 10,324.3 m | 5 |
| [`ibadan-line8.aln.toml`](ibadan-line8.aln.toml) | `line-8` | 4,384.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
