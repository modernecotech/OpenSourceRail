# Tabuk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tabuk-line1.aln.toml`](tabuk-line1.aln.toml) | `line-1` | 15,818.4 m | 10 |
| [`tabuk-line10.aln.toml`](tabuk-line10.aln.toml) | `line-10` | 7,726.0 m | 5 |
| [`tabuk-line11.aln.toml`](tabuk-line11.aln.toml) | `line-11` | 13,593.5 m | 9 |
| [`tabuk-line12.aln.toml`](tabuk-line12.aln.toml) | `line-12` | 3,861.6 m | 3 |
| [`tabuk-line2.aln.toml`](tabuk-line2.aln.toml) | `line-2` | 18,161.6 m | 11 |
| [`tabuk-line3.aln.toml`](tabuk-line3.aln.toml) | `line-3` | 22,856.9 m | 15 |
| [`tabuk-line4.aln.toml`](tabuk-line4.aln.toml) | `line-4` | 5,173.3 m | 4 |
| [`tabuk-line5.aln.toml`](tabuk-line5.aln.toml) | `line-5` | 4,992.4 m | 4 |
| [`tabuk-line6.aln.toml`](tabuk-line6.aln.toml) | `line-6` | 9,606.8 m | 7 |
| [`tabuk-line7.aln.toml`](tabuk-line7.aln.toml) | `line-7` | 2,133.4 m | 2 |
| [`tabuk-line8.aln.toml`](tabuk-line8.aln.toml) | `line-8` | 4,220.0 m | 3 |
| [`tabuk-line9.aln.toml`](tabuk-line9.aln.toml) | `line-9` | 3,579.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
