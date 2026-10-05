# Khartoum Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khartoum-line1.aln.toml`](khartoum-line1.aln.toml) | `line-1` | 33,120.2 m | 11 |
| [`khartoum-line2.aln.toml`](khartoum-line2.aln.toml) | `line-2` | 29,825.1 m | 9 |
| [`khartoum-line3.aln.toml`](khartoum-line3.aln.toml) | `line-3` | 49,026.7 m | 16 |
| [`khartoum-line4.aln.toml`](khartoum-line4.aln.toml) | `line-4` | 25,916.9 m | 11 |
| [`khartoum-line5.aln.toml`](khartoum-line5.aln.toml) | `line-5` | 34,059.9 m | 11 |
| [`khartoum-line6.aln.toml`](khartoum-line6.aln.toml) | `line-6` | 28,600.9 m | 11 |
| [`khartoum-line7.aln.toml`](khartoum-line7.aln.toml) | `line-7` | 35,788.3 m | 11 |
| [`khartoum-line8.aln.toml`](khartoum-line8.aln.toml) | `line-8` | 30,041.3 m | 10 |
| [`khartoum-line9.aln.toml`](khartoum-line9.aln.toml) | `line-9` | 90,867.5 m | 26 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
