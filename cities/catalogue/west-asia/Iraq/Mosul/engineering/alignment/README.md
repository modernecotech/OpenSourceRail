# Mosul Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mosul-line1.aln.toml`](mosul-line1.aln.toml) | `line-1` | 34,548.4 m | 11 |
| [`mosul-line2.aln.toml`](mosul-line2.aln.toml) | `line-2` | 31,090.4 m | 11 |
| [`mosul-line3.aln.toml`](mosul-line3.aln.toml) | `line-3` | 29,350.0 m | 10 |
| [`mosul-line4.aln.toml`](mosul-line4.aln.toml) | `line-4` | 25,429.9 m | 10 |
| [`mosul-line5.aln.toml`](mosul-line5.aln.toml) | `line-5` | 23,877.9 m | 10 |
| [`mosul-line6.aln.toml`](mosul-line6.aln.toml) | `line-6` | 63,045.9 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
