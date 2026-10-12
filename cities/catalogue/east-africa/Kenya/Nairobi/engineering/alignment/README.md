# Nairobi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nairobi-line1.aln.toml`](nairobi-line1.aln.toml) | `line-1` | 63,176.8 m | 20 |
| [`nairobi-line10.aln.toml`](nairobi-line10.aln.toml) | `line-10` | 17,913.3 m | 6 |
| [`nairobi-line11.aln.toml`](nairobi-line11.aln.toml) | `line-11` | 10,464.3 m | 5 |
| [`nairobi-line12.aln.toml`](nairobi-line12.aln.toml) | `line-12` | 8,688.9 m | 3 |
| [`nairobi-line13.aln.toml`](nairobi-line13.aln.toml) | `line-13` | 7,566.7 m | 3 |
| [`nairobi-line14.aln.toml`](nairobi-line14.aln.toml) | `line-14` | 9,733.8 m | 4 |
| [`nairobi-line2.aln.toml`](nairobi-line2.aln.toml) | `line-2` | 57,578.8 m | 54 |
| [`nairobi-line3.aln.toml`](nairobi-line3.aln.toml) | `line-3` | 55,733.5 m | 37 |
| [`nairobi-line4.aln.toml`](nairobi-line4.aln.toml) | `line-4` | 28,060.4 m | 13 |
| [`nairobi-line5.aln.toml`](nairobi-line5.aln.toml) | `line-5` | 51,266.8 m | 23 |
| [`nairobi-line6.aln.toml`](nairobi-line6.aln.toml) | `line-6` | 65,557.6 m | 23 |
| [`nairobi-line7.aln.toml`](nairobi-line7.aln.toml) | `line-7` | 58,141.2 m | 39 |
| [`nairobi-line8.aln.toml`](nairobi-line8.aln.toml) | `line-8` | 47,157.7 m | 15 |
| [`nairobi-line9.aln.toml`](nairobi-line9.aln.toml) | `line-9` | 108,457.8 m | 59 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
