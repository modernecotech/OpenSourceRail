# Yaounde Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`yaounde-line1.aln.toml`](yaounde-line1.aln.toml) | `line-1` | 48,210.0 m | 23 |
| [`yaounde-line2.aln.toml`](yaounde-line2.aln.toml) | `line-2` | 50,900.3 m | 27 |
| [`yaounde-line3.aln.toml`](yaounde-line3.aln.toml) | `line-3` | 35,496.7 m | 30 |
| [`yaounde-line4.aln.toml`](yaounde-line4.aln.toml) | `line-4` | 20,999.6 m | 9 |
| [`yaounde-line5.aln.toml`](yaounde-line5.aln.toml) | `line-5` | 73,903.4 m | 34 |
| [`yaounde-line6.aln.toml`](yaounde-line6.aln.toml) | `line-6` | 7,377.5 m | 4 |
| [`yaounde-line7.aln.toml`](yaounde-line7.aln.toml) | `line-7` | 5,593.9 m | 3 |
| [`yaounde-line8.aln.toml`](yaounde-line8.aln.toml) | `line-8` | 5,551.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
