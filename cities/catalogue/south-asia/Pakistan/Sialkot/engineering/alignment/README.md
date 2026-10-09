# Sialkot Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sialkot-line1.aln.toml`](sialkot-line1.aln.toml) | `line-1` | 17,547.3 m | 10 |
| [`sialkot-line10.aln.toml`](sialkot-line10.aln.toml) | `line-10` | 5,160.1 m | 4 |
| [`sialkot-line11.aln.toml`](sialkot-line11.aln.toml) | `line-11` | 2,094.8 m | 2 |
| [`sialkot-line12.aln.toml`](sialkot-line12.aln.toml) | `line-12` | 5,024.5 m | 4 |
| [`sialkot-line13.aln.toml`](sialkot-line13.aln.toml) | `line-13` | 6,202.6 m | 4 |
| [`sialkot-line14.aln.toml`](sialkot-line14.aln.toml) | `line-14` | 4,871.6 m | 3 |
| [`sialkot-line15.aln.toml`](sialkot-line15.aln.toml) | `line-15` | 4,293.4 m | 3 |
| [`sialkot-line16.aln.toml`](sialkot-line16.aln.toml) | `line-16` | 2,373.0 m | 2 |
| [`sialkot-line17.aln.toml`](sialkot-line17.aln.toml) | `line-17` | 4,284.8 m | 3 |
| [`sialkot-line2.aln.toml`](sialkot-line2.aln.toml) | `line-2` | 22,687.3 m | 14 |
| [`sialkot-line3.aln.toml`](sialkot-line3.aln.toml) | `line-3` | 13,462.5 m | 9 |
| [`sialkot-line4.aln.toml`](sialkot-line4.aln.toml) | `line-4` | 3,089.4 m | 3 |
| [`sialkot-line5.aln.toml`](sialkot-line5.aln.toml) | `line-5` | 3,112.8 m | 3 |
| [`sialkot-line6.aln.toml`](sialkot-line6.aln.toml) | `line-6` | 3,190.8 m | 2 |
| [`sialkot-line7.aln.toml`](sialkot-line7.aln.toml) | `line-7` | 2,856.5 m | 2 |
| [`sialkot-line8.aln.toml`](sialkot-line8.aln.toml) | `line-8` | 2,120.8 m | 2 |
| [`sialkot-line9.aln.toml`](sialkot-line9.aln.toml) | `line-9` | 4,762.4 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
