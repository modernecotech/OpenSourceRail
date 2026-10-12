# Bandung Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bandung-line1.aln.toml`](bandung-line1.aln.toml) | `line-1` | 41,633.9 m | 20 |
| [`bandung-line2.aln.toml`](bandung-line2.aln.toml) | `line-2` | 48,604.3 m | 36 |
| [`bandung-line3.aln.toml`](bandung-line3.aln.toml) | `line-3` | 24,590.0 m | 35 |
| [`bandung-line4.aln.toml`](bandung-line4.aln.toml) | `line-4` | 34,820.6 m | 33 |
| [`bandung-line5.aln.toml`](bandung-line5.aln.toml) | `line-5` | 32,276.6 m | 23 |
| [`bandung-line6.aln.toml`](bandung-line6.aln.toml) | `line-6` | 72,809.0 m | 42 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
