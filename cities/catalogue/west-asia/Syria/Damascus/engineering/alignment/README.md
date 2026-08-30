# Damascus Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`damascus-line1.aln.toml`](damascus-line1.aln.toml) | `line-1` | 25,312.2 m | 10 |
| [`damascus-line2.aln.toml`](damascus-line2.aln.toml) | `line-2` | 26,435.5 m | 9 |
| [`damascus-line3.aln.toml`](damascus-line3.aln.toml) | `line-3` | 29,102.2 m | 11 |
| [`damascus-line4.aln.toml`](damascus-line4.aln.toml) | `line-4` | 24,921.1 m | 9 |
| [`damascus-line5.aln.toml`](damascus-line5.aln.toml) | `line-5` | 27,863.0 m | 8 |
| [`damascus-line6.aln.toml`](damascus-line6.aln.toml) | `line-6` | 64,309.5 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
