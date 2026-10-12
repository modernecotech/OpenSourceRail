# Raipur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`raipur-line1.aln.toml`](raipur-line1.aln.toml) | `line-1` | 29,010.8 m | 11 |
| [`raipur-line2.aln.toml`](raipur-line2.aln.toml) | `line-2` | 25,842.9 m | 7 |
| [`raipur-line3.aln.toml`](raipur-line3.aln.toml) | `line-3` | 12,692.4 m | 4 |
| [`raipur-line4.aln.toml`](raipur-line4.aln.toml) | `line-4` | 22,908.2 m | 8 |
| [`raipur-line5.aln.toml`](raipur-line5.aln.toml) | `line-5` | 21,528.8 m | 8 |
| [`raipur-line6.aln.toml`](raipur-line6.aln.toml) | `line-6` | 31,122.5 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
