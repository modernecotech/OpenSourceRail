# Aba-Ng Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`aba-ng-line1.aln.toml`](aba-ng-line1.aln.toml) | `line-1` | 9,881.6 m | 8 |
| [`aba-ng-line2.aln.toml`](aba-ng-line2.aln.toml) | `line-2` | 5,357.9 m | 6 |
| [`aba-ng-line3.aln.toml`](aba-ng-line3.aln.toml) | `line-3` | 10,192.2 m | 8 |
| [`aba-ng-line4.aln.toml`](aba-ng-line4.aln.toml) | `line-4` | 2,518.2 m | 3 |
| [`aba-ng-line5.aln.toml`](aba-ng-line5.aln.toml) | `line-5` | 2,848.8 m | 2 |
| [`aba-ng-line6.aln.toml`](aba-ng-line6.aln.toml) | `line-6` | 3,081.1 m | 3 |
| [`aba-ng-line7.aln.toml`](aba-ng-line7.aln.toml) | `line-7` | 8,303.3 m | 6 |
| [`aba-ng-line8.aln.toml`](aba-ng-line8.aln.toml) | `line-8` | 5,108.3 m | 4 |
| [`aba-ng-line9.aln.toml`](aba-ng-line9.aln.toml) | `line-9` | 3,160.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
