# Khartoum Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khartoum-line1.aln.toml`](khartoum-line1.aln.toml) | `line-1` | 39,579.9 m | 17 |
| [`khartoum-line2.aln.toml`](khartoum-line2.aln.toml) | `line-2` | 29,386.2 m | 17 |
| [`khartoum-line3.aln.toml`](khartoum-line3.aln.toml) | `line-3` | 50,324.9 m | 16 |
| [`khartoum-line4.aln.toml`](khartoum-line4.aln.toml) | `line-4` | 25,554.1 m | 17 |
| [`khartoum-line5.aln.toml`](khartoum-line5.aln.toml) | `line-5` | 34,039.9 m | 14 |
| [`khartoum-line6.aln.toml`](khartoum-line6.aln.toml) | `line-6` | 28,788.0 m | 12 |
| [`khartoum-line7.aln.toml`](khartoum-line7.aln.toml) | `line-7` | 35,968.2 m | 14 |
| [`khartoum-line8.aln.toml`](khartoum-line8.aln.toml) | `line-8` | 30,243.2 m | 13 |
| [`khartoum-line9.aln.toml`](khartoum-line9.aln.toml) | `line-9` | 108,715.6 m | 40 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
