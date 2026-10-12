# Benin-City Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`benin-city-line1.aln.toml`](benin-city-line1.aln.toml) | `line-1` | 17,854.6 m | 10 |
| [`benin-city-line2.aln.toml`](benin-city-line2.aln.toml) | `line-2` | 28,768.7 m | 26 |
| [`benin-city-line3.aln.toml`](benin-city-line3.aln.toml) | `line-3` | 27,117.4 m | 11 |
| [`benin-city-line4.aln.toml`](benin-city-line4.aln.toml) | `line-4` | 23,766.7 m | 8 |
| [`benin-city-line5.aln.toml`](benin-city-line5.aln.toml) | `line-5` | 23,966.6 m | 12 |
| [`benin-city-line6.aln.toml`](benin-city-line6.aln.toml) | `line-6` | 10,448.0 m | 13 |
| [`benin-city-line7.aln.toml`](benin-city-line7.aln.toml) | `line-7` | 6,159.2 m | 7 |
| [`benin-city-line8.aln.toml`](benin-city-line8.aln.toml) | `line-8` | 4,943.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
