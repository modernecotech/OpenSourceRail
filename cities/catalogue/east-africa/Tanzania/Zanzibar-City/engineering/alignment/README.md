# Zanzibar-City Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`zanzibar-city-line1.aln.toml`](zanzibar-city-line1.aln.toml) | `line-1` | 19,849.8 m | 7 |
| [`zanzibar-city-line2.aln.toml`](zanzibar-city-line2.aln.toml) | `line-2` | 11,297.4 m | 7 |
| [`zanzibar-city-line3.aln.toml`](zanzibar-city-line3.aln.toml) | `line-3` | 15,687.2 m | 6 |
| [`zanzibar-city-line4.aln.toml`](zanzibar-city-line4.aln.toml) | `line-4` | 7,523.0 m | 3 |
| [`zanzibar-city-line5.aln.toml`](zanzibar-city-line5.aln.toml) | `line-5` | 4,083.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
