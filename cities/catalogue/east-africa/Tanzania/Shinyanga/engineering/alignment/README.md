# Shinyanga Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`shinyanga-line1.aln.toml`](shinyanga-line1.aln.toml) | `line-1` | 13,755.3 m | 11 |
| [`shinyanga-line2.aln.toml`](shinyanga-line2.aln.toml) | `line-2` | 7,835.8 m | 6 |
| [`shinyanga-line3.aln.toml`](shinyanga-line3.aln.toml) | `line-3` | 6,714.7 m | 5 |
| [`shinyanga-line4.aln.toml`](shinyanga-line4.aln.toml) | `line-4` | 2,492.8 m | 2 |
| [`shinyanga-line5.aln.toml`](shinyanga-line5.aln.toml) | `line-5` | 4,748.2 m | 3 |
| [`shinyanga-line6.aln.toml`](shinyanga-line6.aln.toml) | `line-6` | 3,095.0 m | 3 |
| [`shinyanga-line7.aln.toml`](shinyanga-line7.aln.toml) | `line-7` | 2,883.9 m | 2 |
| [`shinyanga-line8.aln.toml`](shinyanga-line8.aln.toml) | `line-8` | 6,277.0 m | 4 |
| [`shinyanga-line9.aln.toml`](shinyanga-line9.aln.toml) | `line-9` | 8,413.1 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
