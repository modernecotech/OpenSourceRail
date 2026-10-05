# Gazipur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gazipur-line1.aln.toml`](gazipur-line1.aln.toml) | `line-1` | 31,495.6 m | 12 |
| [`gazipur-line2.aln.toml`](gazipur-line2.aln.toml) | `line-2` | 33,767.1 m | 13 |
| [`gazipur-line3.aln.toml`](gazipur-line3.aln.toml) | `line-3` | 45,036.0 m | 16 |
| [`gazipur-line4.aln.toml`](gazipur-line4.aln.toml) | `line-4` | 42,864.6 m | 13 |
| [`gazipur-line5.aln.toml`](gazipur-line5.aln.toml) | `line-5` | 27,730.0 m | 9 |
| [`gazipur-line6.aln.toml`](gazipur-line6.aln.toml) | `line-6` | 63,880.7 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
