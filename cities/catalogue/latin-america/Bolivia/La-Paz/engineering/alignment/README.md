# La-Paz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`la-paz-line1.aln.toml`](la-paz-line1.aln.toml) | `line-1` | 30,141.1 m | 11 |
| [`la-paz-line2.aln.toml`](la-paz-line2.aln.toml) | `line-2` | 29,651.6 m | 9 |
| [`la-paz-line3.aln.toml`](la-paz-line3.aln.toml) | `line-3` | 26,594.9 m | 8 |
| [`la-paz-line4.aln.toml`](la-paz-line4.aln.toml) | `line-4` | 30,137.3 m | 11 |
| [`la-paz-line5.aln.toml`](la-paz-line5.aln.toml) | `line-5` | 22,731.7 m | 8 |
| [`la-paz-line6.aln.toml`](la-paz-line6.aln.toml) | `line-6` | 53,148.4 m | 15 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
