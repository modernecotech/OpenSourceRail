# Amman Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`amman-line1.aln.toml`](amman-line1.aln.toml) | `line-1` | 48,175.3 m | 13 |
| [`amman-line10.aln.toml`](amman-line10.aln.toml) | `line-10` | 11,099.5 m | 4 |
| [`amman-line11.aln.toml`](amman-line11.aln.toml) | `line-11` | 8,384.9 m | 3 |
| [`amman-line12.aln.toml`](amman-line12.aln.toml) | `line-12` | 13,342.5 m | 4 |
| [`amman-line13.aln.toml`](amman-line13.aln.toml) | `line-13` | 8,313.5 m | 3 |
| [`amman-line14.aln.toml`](amman-line14.aln.toml) | `line-14` | 7,591.5 m | 3 |
| [`amman-line2.aln.toml`](amman-line2.aln.toml) | `line-2` | 52,596.7 m | 14 |
| [`amman-line3.aln.toml`](amman-line3.aln.toml) | `line-3` | 30,283.2 m | 9 |
| [`amman-line4.aln.toml`](amman-line4.aln.toml) | `line-4` | 18,210.8 m | 8 |
| [`amman-line5.aln.toml`](amman-line5.aln.toml) | `line-5` | 33,008.8 m | 10 |
| [`amman-line6.aln.toml`](amman-line6.aln.toml) | `line-6` | 35,829.4 m | 14 |
| [`amman-line7.aln.toml`](amman-line7.aln.toml) | `line-7` | 28,823.7 m | 12 |
| [`amman-line8.aln.toml`](amman-line8.aln.toml) | `line-8` | 34,889.0 m | 12 |
| [`amman-line9.aln.toml`](amman-line9.aln.toml) | `line-9` | 82,351.2 m | 23 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
