# Dakar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dakar-line1.aln.toml`](dakar-line1.aln.toml) | `line-1` | 34,940.9 m | 19 |
| [`dakar-line10.aln.toml`](dakar-line10.aln.toml) | `line-10` | 4,636.5 m | 4 |
| [`dakar-line11.aln.toml`](dakar-line11.aln.toml) | `line-11` | 6,530.8 m | 5 |
| [`dakar-line12.aln.toml`](dakar-line12.aln.toml) | `line-12` | 9,668.5 m | 6 |
| [`dakar-line13.aln.toml`](dakar-line13.aln.toml) | `line-13` | 8,522.2 m | 7 |
| [`dakar-line14.aln.toml`](dakar-line14.aln.toml) | `line-14` | 7,356.1 m | 4 |
| [`dakar-line2.aln.toml`](dakar-line2.aln.toml) | `line-2` | 28,560.4 m | 27 |
| [`dakar-line3.aln.toml`](dakar-line3.aln.toml) | `line-3` | 27,167.2 m | 17 |
| [`dakar-line4.aln.toml`](dakar-line4.aln.toml) | `line-4` | 22,412.5 m | 16 |
| [`dakar-line5.aln.toml`](dakar-line5.aln.toml) | `line-5` | 35,934.0 m | 28 |
| [`dakar-line6.aln.toml`](dakar-line6.aln.toml) | `line-6` | 61,838.6 m | 42 |
| [`dakar-line7.aln.toml`](dakar-line7.aln.toml) | `line-7` | 7,753.9 m | 6 |
| [`dakar-line8.aln.toml`](dakar-line8.aln.toml) | `line-8` | 4,523.9 m | 3 |
| [`dakar-line9.aln.toml`](dakar-line9.aln.toml) | `line-9` | 6,461.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
