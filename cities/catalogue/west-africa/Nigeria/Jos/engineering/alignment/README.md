# Jos Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jos-line1.aln.toml`](jos-line1.aln.toml) | `line-1` | 17,084.1 m | 10 |
| [`jos-line10.aln.toml`](jos-line10.aln.toml) | `line-10` | 3,427.1 m | 3 |
| [`jos-line11.aln.toml`](jos-line11.aln.toml) | `line-11` | 3,323.7 m | 3 |
| [`jos-line12.aln.toml`](jos-line12.aln.toml) | `line-12` | 3,620.7 m | 3 |
| [`jos-line2.aln.toml`](jos-line2.aln.toml) | `line-2` | 11,399.4 m | 8 |
| [`jos-line3.aln.toml`](jos-line3.aln.toml) | `line-3` | 7,937.6 m | 6 |
| [`jos-line4.aln.toml`](jos-line4.aln.toml) | `line-4` | 5,608.8 m | 4 |
| [`jos-line5.aln.toml`](jos-line5.aln.toml) | `line-5` | 4,965.6 m | 4 |
| [`jos-line6.aln.toml`](jos-line6.aln.toml) | `line-6` | 5,454.2 m | 4 |
| [`jos-line7.aln.toml`](jos-line7.aln.toml) | `line-7` | 2,612.5 m | 2 |
| [`jos-line8.aln.toml`](jos-line8.aln.toml) | `line-8` | 3,708.5 m | 3 |
| [`jos-line9.aln.toml`](jos-line9.aln.toml) | `line-9` | 3,178.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
