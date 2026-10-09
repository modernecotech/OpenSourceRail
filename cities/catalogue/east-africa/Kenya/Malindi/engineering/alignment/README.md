# Malindi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`malindi-line1.aln.toml`](malindi-line1.aln.toml) | `line-1` | 8,690.6 m | 6 |
| [`malindi-line2.aln.toml`](malindi-line2.aln.toml) | `line-2` | 8,987.0 m | 6 |
| [`malindi-line3.aln.toml`](malindi-line3.aln.toml) | `line-3` | 6,709.1 m | 4 |
| [`malindi-line4.aln.toml`](malindi-line4.aln.toml) | `line-4` | 3,399.1 m | 3 |
| [`malindi-line5.aln.toml`](malindi-line5.aln.toml) | `line-5` | 4,992.4 m | 4 |
| [`malindi-line6.aln.toml`](malindi-line6.aln.toml) | `line-6` | 9,430.9 m | 5 |
| [`malindi-line7.aln.toml`](malindi-line7.aln.toml) | `line-7` | 2,723.1 m | 2 |
| [`malindi-line8.aln.toml`](malindi-line8.aln.toml) | `line-8` | 2,645.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
