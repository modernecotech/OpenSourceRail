# Gulu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gulu-line1.aln.toml`](gulu-line1.aln.toml) | `line-1` | 12,274.5 m | 9 |
| [`gulu-line10.aln.toml`](gulu-line10.aln.toml) | `line-10` | 6,563.6 m | 5 |
| [`gulu-line11.aln.toml`](gulu-line11.aln.toml) | `line-11` | 5,284.7 m | 4 |
| [`gulu-line12.aln.toml`](gulu-line12.aln.toml) | `line-12` | 5,965.5 m | 5 |
| [`gulu-line13.aln.toml`](gulu-line13.aln.toml) | `line-13` | 4,438.5 m | 3 |
| [`gulu-line14.aln.toml`](gulu-line14.aln.toml) | `line-14` | 2,045.3 m | 2 |
| [`gulu-line15.aln.toml`](gulu-line15.aln.toml) | `line-15` | 2,234.5 m | 2 |
| [`gulu-line2.aln.toml`](gulu-line2.aln.toml) | `line-2` | 26,270.1 m | 15 |
| [`gulu-line3.aln.toml`](gulu-line3.aln.toml) | `line-3` | 16,375.0 m | 10 |
| [`gulu-line4.aln.toml`](gulu-line4.aln.toml) | `line-4` | 2,650.8 m | 2 |
| [`gulu-line5.aln.toml`](gulu-line5.aln.toml) | `line-5` | 5,427.4 m | 4 |
| [`gulu-line6.aln.toml`](gulu-line6.aln.toml) | `line-6` | 5,897.9 m | 4 |
| [`gulu-line7.aln.toml`](gulu-line7.aln.toml) | `line-7` | 2,637.6 m | 2 |
| [`gulu-line8.aln.toml`](gulu-line8.aln.toml) | `line-8` | 3,599.3 m | 3 |
| [`gulu-line9.aln.toml`](gulu-line9.aln.toml) | `line-9` | 6,789.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
