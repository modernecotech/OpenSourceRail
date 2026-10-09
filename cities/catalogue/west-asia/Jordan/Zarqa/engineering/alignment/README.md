# Zarqa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`zarqa-line1.aln.toml`](zarqa-line1.aln.toml) | `line-1` | 28,370.4 m | 18 |
| [`zarqa-line10.aln.toml`](zarqa-line10.aln.toml) | `line-10` | 2,755.0 m | 2 |
| [`zarqa-line11.aln.toml`](zarqa-line11.aln.toml) | `line-11` | 2,694.8 m | 2 |
| [`zarqa-line12.aln.toml`](zarqa-line12.aln.toml) | `line-12` | 4,567.2 m | 3 |
| [`zarqa-line13.aln.toml`](zarqa-line13.aln.toml) | `line-13` | 2,622.8 m | 3 |
| [`zarqa-line2.aln.toml`](zarqa-line2.aln.toml) | `line-2` | 26,550.4 m | 17 |
| [`zarqa-line3.aln.toml`](zarqa-line3.aln.toml) | `line-3` | 11,905.4 m | 7 |
| [`zarqa-line4.aln.toml`](zarqa-line4.aln.toml) | `line-4` | 4,979.3 m | 4 |
| [`zarqa-line5.aln.toml`](zarqa-line5.aln.toml) | `line-5` | 4,468.4 m | 4 |
| [`zarqa-line6.aln.toml`](zarqa-line6.aln.toml) | `line-6` | 3,686.2 m | 3 |
| [`zarqa-line7.aln.toml`](zarqa-line7.aln.toml) | `line-7` | 6,937.4 m | 4 |
| [`zarqa-line8.aln.toml`](zarqa-line8.aln.toml) | `line-8` | 6,053.9 m | 4 |
| [`zarqa-line9.aln.toml`](zarqa-line9.aln.toml) | `line-9` | 6,521.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
