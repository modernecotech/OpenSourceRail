# Benin-City Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`benin-city-line1.aln.toml`](benin-city-line1.aln.toml) | `line-1` | 13,587.9 m | 8 |
| [`benin-city-line2.aln.toml`](benin-city-line2.aln.toml) | `line-2` | 22,090.6 m | 10 |
| [`benin-city-line3.aln.toml`](benin-city-line3.aln.toml) | `line-3` | 23,706.8 m | 9 |
| [`benin-city-line4.aln.toml`](benin-city-line4.aln.toml) | `line-4` | 22,586.6 m | 8 |
| [`benin-city-line5.aln.toml`](benin-city-line5.aln.toml) | `line-5` | 23,966.6 m | 12 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
