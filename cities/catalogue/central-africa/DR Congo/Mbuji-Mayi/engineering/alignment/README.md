# Mbuji-Mayi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mbuji-mayi-line1.aln.toml`](mbuji-mayi-line1.aln.toml) | `line-1` | 25,077.4 m | 14 |
| [`mbuji-mayi-line10.aln.toml`](mbuji-mayi-line10.aln.toml) | `line-10` | 12,548.5 m | 9 |
| [`mbuji-mayi-line11.aln.toml`](mbuji-mayi-line11.aln.toml) | `line-11` | 4,216.5 m | 4 |
| [`mbuji-mayi-line12.aln.toml`](mbuji-mayi-line12.aln.toml) | `line-12` | 3,685.9 m | 4 |
| [`mbuji-mayi-line2.aln.toml`](mbuji-mayi-line2.aln.toml) | `line-2` | 15,640.5 m | 9 |
| [`mbuji-mayi-line3.aln.toml`](mbuji-mayi-line3.aln.toml) | `line-3` | 29,303.0 m | 19 |
| [`mbuji-mayi-line4.aln.toml`](mbuji-mayi-line4.aln.toml) | `line-4` | 35,272.2 m | 23 |
| [`mbuji-mayi-line5.aln.toml`](mbuji-mayi-line5.aln.toml) | `line-5` | 5,155.5 m | 5 |
| [`mbuji-mayi-line6.aln.toml`](mbuji-mayi-line6.aln.toml) | `line-6` | 2,737.4 m | 3 |
| [`mbuji-mayi-line7.aln.toml`](mbuji-mayi-line7.aln.toml) | `line-7` | 3,304.3 m | 3 |
| [`mbuji-mayi-line8.aln.toml`](mbuji-mayi-line8.aln.toml) | `line-8` | 2,208.5 m | 2 |
| [`mbuji-mayi-line9.aln.toml`](mbuji-mayi-line9.aln.toml) | `line-9` | 4,661.8 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
