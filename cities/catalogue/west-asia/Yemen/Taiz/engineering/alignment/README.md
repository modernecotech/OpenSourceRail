# Taiz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`taiz-line1.aln.toml`](taiz-line1.aln.toml) | `line-1` | 18,403.9 m | 7 |
| [`taiz-line2.aln.toml`](taiz-line2.aln.toml) | `line-2` | 8,652.3 m | 4 |
| [`taiz-line3.aln.toml`](taiz-line3.aln.toml) | `line-3` | 15,876.9 m | 11 |
| [`taiz-line4.aln.toml`](taiz-line4.aln.toml) | `line-4` | 5,412.4 m | 2 |
| [`taiz-line5.aln.toml`](taiz-line5.aln.toml) | `line-5` | 4,951.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
