# Mosul Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mosul-line1.aln.toml`](mosul-line1.aln.toml) | `line-1` | 31,117.0 m | 19 |
| [`mosul-line10.aln.toml`](mosul-line10.aln.toml) | `line-10` | 4,135.5 m | 3 |
| [`mosul-line11.aln.toml`](mosul-line11.aln.toml) | `line-11` | 6,391.4 m | 4 |
| [`mosul-line12.aln.toml`](mosul-line12.aln.toml) | `line-12` | 4,645.6 m | 5 |
| [`mosul-line13.aln.toml`](mosul-line13.aln.toml) | `line-13` | 4,434.8 m | 3 |
| [`mosul-line14.aln.toml`](mosul-line14.aln.toml) | `line-14` | 3,832.8 m | 3 |
| [`mosul-line15.aln.toml`](mosul-line15.aln.toml) | `line-15` | 17,163.1 m | 10 |
| [`mosul-line16.aln.toml`](mosul-line16.aln.toml) | `line-16` | 4,877.5 m | 3 |
| [`mosul-line17.aln.toml`](mosul-line17.aln.toml) | `line-17` | 7,362.1 m | 5 |
| [`mosul-line18.aln.toml`](mosul-line18.aln.toml) | `line-18` | 7,456.1 m | 5 |
| [`mosul-line19.aln.toml`](mosul-line19.aln.toml) | `line-19` | 3,862.3 m | 5 |
| [`mosul-line2.aln.toml`](mosul-line2.aln.toml) | `line-2` | 28,856.3 m | 17 |
| [`mosul-line3.aln.toml`](mosul-line3.aln.toml) | `line-3` | 28,684.3 m | 17 |
| [`mosul-line4.aln.toml`](mosul-line4.aln.toml) | `line-4` | 26,323.0 m | 16 |
| [`mosul-line5.aln.toml`](mosul-line5.aln.toml) | `line-5` | 20,025.8 m | 13 |
| [`mosul-line6.aln.toml`](mosul-line6.aln.toml) | `line-6` | 56,009.7 m | 31 |
| [`mosul-line7.aln.toml`](mosul-line7.aln.toml) | `line-7` | 6,850.3 m | 7 |
| [`mosul-line8.aln.toml`](mosul-line8.aln.toml) | `line-8` | 4,457.9 m | 3 |
| [`mosul-line9.aln.toml`](mosul-line9.aln.toml) | `line-9` | 6,190.9 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
