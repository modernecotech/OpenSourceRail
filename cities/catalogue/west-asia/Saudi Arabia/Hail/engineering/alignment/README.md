# Hail Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hail-line1.aln.toml`](hail-line1.aln.toml) | `line-1` | 21,506.2 m | 11 |
| [`hail-line10.aln.toml`](hail-line10.aln.toml) | `line-10` | 5,333.6 m | 4 |
| [`hail-line11.aln.toml`](hail-line11.aln.toml) | `line-11` | 9,956.2 m | 6 |
| [`hail-line12.aln.toml`](hail-line12.aln.toml) | `line-12` | 5,627.1 m | 4 |
| [`hail-line13.aln.toml`](hail-line13.aln.toml) | `line-13` | 3,974.2 m | 4 |
| [`hail-line14.aln.toml`](hail-line14.aln.toml) | `line-14` | 2,870.2 m | 2 |
| [`hail-line2.aln.toml`](hail-line2.aln.toml) | `line-2` | 19,601.2 m | 17 |
| [`hail-line3.aln.toml`](hail-line3.aln.toml) | `line-3` | 14,504.8 m | 8 |
| [`hail-line4.aln.toml`](hail-line4.aln.toml) | `line-4` | 5,615.6 m | 4 |
| [`hail-line5.aln.toml`](hail-line5.aln.toml) | `line-5` | 2,279.7 m | 2 |
| [`hail-line6.aln.toml`](hail-line6.aln.toml) | `line-6` | 8,193.4 m | 5 |
| [`hail-line7.aln.toml`](hail-line7.aln.toml) | `line-7` | 3,873.6 m | 3 |
| [`hail-line8.aln.toml`](hail-line8.aln.toml) | `line-8` | 4,127.4 m | 3 |
| [`hail-line9.aln.toml`](hail-line9.aln.toml) | `line-9` | 3,391.6 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
