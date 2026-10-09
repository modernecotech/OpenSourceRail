# Goma Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`goma-line1.aln.toml`](goma-line1.aln.toml) | `line-1` | 19,434.9 m | 10 |
| [`goma-line10.aln.toml`](goma-line10.aln.toml) | `line-10` | 6,863.0 m | 7 |
| [`goma-line11.aln.toml`](goma-line11.aln.toml) | `line-11` | 3,359.4 m | 3 |
| [`goma-line12.aln.toml`](goma-line12.aln.toml) | `line-12` | 2,691.0 m | 2 |
| [`goma-line13.aln.toml`](goma-line13.aln.toml) | `line-13` | 6,085.6 m | 5 |
| [`goma-line14.aln.toml`](goma-line14.aln.toml) | `line-14` | 2,124.9 m | 2 |
| [`goma-line2.aln.toml`](goma-line2.aln.toml) | `line-2` | 16,084.8 m | 12 |
| [`goma-line3.aln.toml`](goma-line3.aln.toml) | `line-3` | 11,394.8 m | 8 |
| [`goma-line4.aln.toml`](goma-line4.aln.toml) | `line-4` | 4,181.3 m | 3 |
| [`goma-line5.aln.toml`](goma-line5.aln.toml) | `line-5` | 3,043.7 m | 2 |
| [`goma-line6.aln.toml`](goma-line6.aln.toml) | `line-6` | 5,360.7 m | 6 |
| [`goma-line7.aln.toml`](goma-line7.aln.toml) | `line-7` | 4,601.3 m | 3 |
| [`goma-line8.aln.toml`](goma-line8.aln.toml) | `line-8` | 5,726.2 m | 4 |
| [`goma-line9.aln.toml`](goma-line9.aln.toml) | `line-9` | 2,020.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
