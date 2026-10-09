# Aden Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`aden-line1.aln.toml`](aden-line1.aln.toml) | `line-1` | 20,196.1 m | 13 |
| [`aden-line2.aln.toml`](aden-line2.aln.toml) | `line-2` | 13,690.2 m | 9 |
| [`aden-line3.aln.toml`](aden-line3.aln.toml) | `line-3` | 13,799.1 m | 10 |
| [`aden-line4.aln.toml`](aden-line4.aln.toml) | `line-4` | 2,450.2 m | 2 |
| [`aden-line5.aln.toml`](aden-line5.aln.toml) | `line-5` | 2,516.8 m | 2 |
| [`aden-line6.aln.toml`](aden-line6.aln.toml) | `line-6` | 2,241.9 m | 2 |
| [`aden-line7.aln.toml`](aden-line7.aln.toml) | `line-7` | 2,574.6 m | 2 |
| [`aden-line8.aln.toml`](aden-line8.aln.toml) | `line-8` | 3,010.2 m | 3 |
| [`aden-line9.aln.toml`](aden-line9.aln.toml) | `line-9` | 9,577.4 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
