# Sanaa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sanaa-line1.aln.toml`](sanaa-line1.aln.toml) | `line-1` | 44,565.5 m | 33 |
| [`sanaa-line10.aln.toml`](sanaa-line10.aln.toml) | `line-10` | 14,951.9 m | 9 |
| [`sanaa-line11.aln.toml`](sanaa-line11.aln.toml) | `line-11` | 20,946.3 m | 17 |
| [`sanaa-line2.aln.toml`](sanaa-line2.aln.toml) | `line-2` | 22,928.2 m | 19 |
| [`sanaa-line3.aln.toml`](sanaa-line3.aln.toml) | `line-3` | 32,602.5 m | 8 |
| [`sanaa-line4.aln.toml`](sanaa-line4.aln.toml) | `line-4` | 22,083.9 m | 8 |
| [`sanaa-line5.aln.toml`](sanaa-line5.aln.toml) | `line-5` | 34,648.6 m | 13 |
| [`sanaa-line6.aln.toml`](sanaa-line6.aln.toml) | `line-6` | 23,479.0 m | 14 |
| [`sanaa-line7.aln.toml`](sanaa-line7.aln.toml) | `line-7` | 62,936.6 m | 34 |
| [`sanaa-line8.aln.toml`](sanaa-line8.aln.toml) | `line-8` | 5,128.7 m | 2 |
| [`sanaa-line9.aln.toml`](sanaa-line9.aln.toml) | `line-9` | 4,999.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
