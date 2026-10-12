# La-Paz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`la-paz-line1.aln.toml`](la-paz-line1.aln.toml) | `line-1` | 30,531.4 m | 10 |
| [`la-paz-line2.aln.toml`](la-paz-line2.aln.toml) | `line-2` | 37,305.7 m | 12 |
| [`la-paz-line3.aln.toml`](la-paz-line3.aln.toml) | `line-3` | 31,304.7 m | 9 |
| [`la-paz-line4.aln.toml`](la-paz-line4.aln.toml) | `line-4` | 30,317.1 m | 10 |
| [`la-paz-line5.aln.toml`](la-paz-line5.aln.toml) | `line-5` | 30,149.1 m | 9 |
| [`la-paz-line6.aln.toml`](la-paz-line6.aln.toml) | `line-6` | 53,148.4 m | 13 |
| [`la-paz-line7.aln.toml`](la-paz-line7.aln.toml) | `line-7` | 5,041.6 m | 2 |
| [`la-paz-line8.aln.toml`](la-paz-line8.aln.toml) | `line-8` | 5,265.3 m | 2 |
| [`la-paz-line9.aln.toml`](la-paz-line9.aln.toml) | `line-9` | 12,333.4 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
