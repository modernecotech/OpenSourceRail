# Tabuk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tabuk-line1.aln.toml`](tabuk-line1.aln.toml) | `line-1` | 18,998.8 m | 8 |
| [`tabuk-line2.aln.toml`](tabuk-line2.aln.toml) | `line-2` | 18,161.6 m | 7 |
| [`tabuk-line3.aln.toml`](tabuk-line3.aln.toml) | `line-3` | 25,216.8 m | 7 |
| [`tabuk-line4.aln.toml`](tabuk-line4.aln.toml) | `line-4` | 4,589.8 m | 2 |
| [`tabuk-line5.aln.toml`](tabuk-line5.aln.toml) | `line-5` | 7,208.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
