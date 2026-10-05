# Peshawar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`peshawar-line1.aln.toml`](peshawar-line1.aln.toml) | `line-1` | 28,748.9 m | 10 |
| [`peshawar-line2.aln.toml`](peshawar-line2.aln.toml) | `line-2` | 27,891.2 m | 9 |
| [`peshawar-line3.aln.toml`](peshawar-line3.aln.toml) | `line-3` | 30,775.0 m | 10 |
| [`peshawar-line4.aln.toml`](peshawar-line4.aln.toml) | `line-4` | 22,218.9 m | 8 |
| [`peshawar-line5.aln.toml`](peshawar-line5.aln.toml) | `line-5` | 61,679.6 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
