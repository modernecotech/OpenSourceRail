# Mukalla Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mukalla-line1.aln.toml`](mukalla-line1.aln.toml) | `line-1` | 15,724.8 m | 20 |
| [`mukalla-line2.aln.toml`](mukalla-line2.aln.toml) | `line-2` | 19,038.4 m | 17 |
| [`mukalla-line3.aln.toml`](mukalla-line3.aln.toml) | `line-3` | 25,814.6 m | 19 |
| [`mukalla-line4.aln.toml`](mukalla-line4.aln.toml) | `line-4` | 4,742.4 m | 4 |
| [`mukalla-line5.aln.toml`](mukalla-line5.aln.toml) | `line-5` | 3,707.1 m | 3 |
| [`mukalla-line6.aln.toml`](mukalla-line6.aln.toml) | `line-6` | 2,808.5 m | 4 |
| [`mukalla-line7.aln.toml`](mukalla-line7.aln.toml) | `line-7` | 3,286.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
