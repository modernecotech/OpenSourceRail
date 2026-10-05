# Najaf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najaf-line1.aln.toml`](najaf-line1.aln.toml) | `line-1` | 19,268.3 m | 9 |
| [`najaf-line2.aln.toml`](najaf-line2.aln.toml) | `line-2` | 32,421.6 m | 18 |
| [`najaf-line3.aln.toml`](najaf-line3.aln.toml) | `line-3` | 16,041.7 m | 9 |
| [`najaf-line4.aln.toml`](najaf-line4.aln.toml) | `line-4` | 23,651.0 m | 10 |
| [`najaf-line5.aln.toml`](najaf-line5.aln.toml) | `line-5` | 27,384.6 m | 11 |
| [`najaf-line6.aln.toml`](najaf-line6.aln.toml) | `line-6` | 28,429.2 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
