# Maputo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maputo-line1.aln.toml`](maputo-line1.aln.toml) | `line-1` | 25,961.4 m | 19 |
| [`maputo-line2.aln.toml`](maputo-line2.aln.toml) | `line-2` | 22,986.6 m | 12 |
| [`maputo-line3.aln.toml`](maputo-line3.aln.toml) | `line-3` | 22,735.2 m | 6 |
| [`maputo-line4.aln.toml`](maputo-line4.aln.toml) | `line-4` | 26,357.7 m | 9 |
| [`maputo-line5.aln.toml`](maputo-line5.aln.toml) | `line-5` | 22,949.6 m | 9 |
| [`maputo-line6.aln.toml`](maputo-line6.aln.toml) | `line-6` | 56,789.8 m | 26 |
| [`maputo-line7.aln.toml`](maputo-line7.aln.toml) | `line-7` | 6,927.2 m | 3 |
| [`maputo-line8.aln.toml`](maputo-line8.aln.toml) | `line-8` | 9,036.0 m | 5 |
| [`maputo-line9.aln.toml`](maputo-line9.aln.toml) | `line-9` | 10,921.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
