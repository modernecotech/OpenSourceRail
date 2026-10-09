# Najaf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najaf-line1.aln.toml`](najaf-line1.aln.toml) | `line-1` | 20,314.0 m | 15 |
| [`najaf-line10.aln.toml`](najaf-line10.aln.toml) | `line-10` | 2,987.9 m | 3 |
| [`najaf-line11.aln.toml`](najaf-line11.aln.toml) | `line-11` | 9,559.9 m | 5 |
| [`najaf-line12.aln.toml`](najaf-line12.aln.toml) | `line-12` | 5,916.4 m | 4 |
| [`najaf-line13.aln.toml`](najaf-line13.aln.toml) | `line-13` | 4,638.8 m | 6 |
| [`najaf-line14.aln.toml`](najaf-line14.aln.toml) | `line-14` | 4,279.9 m | 3 |
| [`najaf-line15.aln.toml`](najaf-line15.aln.toml) | `line-15` | 3,512.4 m | 4 |
| [`najaf-line16.aln.toml`](najaf-line16.aln.toml) | `line-16` | 3,609.7 m | 3 |
| [`najaf-line2.aln.toml`](najaf-line2.aln.toml) | `line-2` | 32,421.6 m | 26 |
| [`najaf-line3.aln.toml`](najaf-line3.aln.toml) | `line-3` | 16,041.7 m | 12 |
| [`najaf-line4.aln.toml`](najaf-line4.aln.toml) | `line-4` | 23,651.0 m | 16 |
| [`najaf-line5.aln.toml`](najaf-line5.aln.toml) | `line-5` | 27,384.6 m | 16 |
| [`najaf-line6.aln.toml`](najaf-line6.aln.toml) | `line-6` | 28,429.2 m | 26 |
| [`najaf-line7.aln.toml`](najaf-line7.aln.toml) | `line-7` | 4,775.9 m | 3 |
| [`najaf-line8.aln.toml`](najaf-line8.aln.toml) | `line-8` | 4,567.6 m | 3 |
| [`najaf-line9.aln.toml`](najaf-line9.aln.toml) | `line-9` | 5,741.7 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
