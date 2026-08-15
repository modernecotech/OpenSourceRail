# Aleppo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`aleppo-line1.aln.toml`](aleppo-line1.aln.toml) | `line-1` | 29,122.0 m | 18 |
| [`aleppo-line2.aln.toml`](aleppo-line2.aln.toml) | `line-2` | 28,140.5 m | 19 |
| [`aleppo-line3.aln.toml`](aleppo-line3.aln.toml) | `line-3` | 15,215.0 m | 12 |
| [`aleppo-line4.aln.toml`](aleppo-line4.aln.toml) | `line-4` | 24,988.1 m | 15 |
| [`aleppo-line5.aln.toml`](aleppo-line5.aln.toml) | `line-5` | 26,586.3 m | 17 |
| [`aleppo-line6.aln.toml`](aleppo-line6.aln.toml) | `line-6` | 59,884.1 m | 38 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
