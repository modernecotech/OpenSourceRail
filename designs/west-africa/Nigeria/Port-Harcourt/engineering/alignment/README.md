# Port-Harcourt Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`port-harcourt-line1.aln.toml`](port-harcourt-line1.aln.toml) | `line-1` | 38,661.2 m | 22 |
| [`port-harcourt-line2.aln.toml`](port-harcourt-line2.aln.toml) | `line-2` | 28,686.6 m | 18 |
| [`port-harcourt-line3.aln.toml`](port-harcourt-line3.aln.toml) | `line-3` | 29,896.5 m | 19 |
| [`port-harcourt-line4.aln.toml`](port-harcourt-line4.aln.toml) | `line-4` | 30,612.5 m | 18 |
| [`port-harcourt-line5.aln.toml`](port-harcourt-line5.aln.toml) | `line-5` | 65,959.4 m | 42 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
