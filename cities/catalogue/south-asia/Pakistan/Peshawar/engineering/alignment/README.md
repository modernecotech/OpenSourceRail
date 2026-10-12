# Peshawar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`peshawar-line1.aln.toml`](peshawar-line1.aln.toml) | `line-1` | 31,574.2 m | 9 |
| [`peshawar-line2.aln.toml`](peshawar-line2.aln.toml) | `line-2` | 28,971.3 m | 8 |
| [`peshawar-line3.aln.toml`](peshawar-line3.aln.toml) | `line-3` | 35,955.6 m | 11 |
| [`peshawar-line4.aln.toml`](peshawar-line4.aln.toml) | `line-4` | 25,471.6 m | 8 |
| [`peshawar-line5.aln.toml`](peshawar-line5.aln.toml) | `line-5` | 66,738.4 m | 18 |
| [`peshawar-line6.aln.toml`](peshawar-line6.aln.toml) | `line-6` | 5,594.9 m | 2 |
| [`peshawar-line7.aln.toml`](peshawar-line7.aln.toml) | `line-7` | 6,793.5 m | 2 |
| [`peshawar-line8.aln.toml`](peshawar-line8.aln.toml) | `line-8` | 5,054.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
