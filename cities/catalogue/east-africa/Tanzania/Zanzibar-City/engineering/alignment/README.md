# Zanzibar-City Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`zanzibar-city-line1.aln.toml`](zanzibar-city-line1.aln.toml) | `line-1` | 14,010.2 m | 10 |
| [`zanzibar-city-line2.aln.toml`](zanzibar-city-line2.aln.toml) | `line-2` | 11,297.4 m | 8 |
| [`zanzibar-city-line3.aln.toml`](zanzibar-city-line3.aln.toml) | `line-3` | 15,727.2 m | 11 |
| [`zanzibar-city-line4.aln.toml`](zanzibar-city-line4.aln.toml) | `line-4` | 2,042.5 m | 3 |
| [`zanzibar-city-line5.aln.toml`](zanzibar-city-line5.aln.toml) | `line-5` | 4,029.4 m | 3 |
| [`zanzibar-city-line6.aln.toml`](zanzibar-city-line6.aln.toml) | `line-6` | 2,732.2 m | 2 |
| [`zanzibar-city-line7.aln.toml`](zanzibar-city-line7.aln.toml) | `line-7` | 3,789.4 m | 3 |
| [`zanzibar-city-line8.aln.toml`](zanzibar-city-line8.aln.toml) | `line-8` | 3,483.1 m | 3 |
| [`zanzibar-city-line9.aln.toml`](zanzibar-city-line9.aln.toml) | `line-9` | 4,999.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
