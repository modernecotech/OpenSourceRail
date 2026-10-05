# Kampala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kampala-line1.aln.toml`](kampala-line1.aln.toml) | `line-1` | 31,606.0 m | 13 |
| [`kampala-line2.aln.toml`](kampala-line2.aln.toml) | `line-2` | 21,736.4 m | 8 |
| [`kampala-line3.aln.toml`](kampala-line3.aln.toml) | `line-3` | 24,771.8 m | 10 |
| [`kampala-line4.aln.toml`](kampala-line4.aln.toml) | `line-4` | 26,384.8 m | 11 |
| [`kampala-line5.aln.toml`](kampala-line5.aln.toml) | `line-5` | 22,122.5 m | 9 |
| [`kampala-line6.aln.toml`](kampala-line6.aln.toml) | `line-6` | 57,736.6 m | 15 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
