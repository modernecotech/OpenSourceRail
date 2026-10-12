# Aleppo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`aleppo-line1.aln.toml`](aleppo-line1.aln.toml) | `line-1` | 28,667.5 m | 40 |
| [`aleppo-line2.aln.toml`](aleppo-line2.aln.toml) | `line-2` | 27,941.2 m | 17 |
| [`aleppo-line3.aln.toml`](aleppo-line3.aln.toml) | `line-3` | 15,709.5 m | 18 |
| [`aleppo-line4.aln.toml`](aleppo-line4.aln.toml) | `line-4` | 27,367.6 m | 31 |
| [`aleppo-line5.aln.toml`](aleppo-line5.aln.toml) | `line-5` | 29,202.1 m | 30 |
| [`aleppo-line6.aln.toml`](aleppo-line6.aln.toml) | `line-6` | 59,463.1 m | 21 |
| [`aleppo-line7.aln.toml`](aleppo-line7.aln.toml) | `line-7` | 4,406.8 m | 2 |
| [`aleppo-line8.aln.toml`](aleppo-line8.aln.toml) | `line-8` | 6,981.8 m | 2 |
| [`aleppo-line9.aln.toml`](aleppo-line9.aln.toml) | `line-9` | 5,502.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
