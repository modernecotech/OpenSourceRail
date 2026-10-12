# Meknes Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`meknes-line1.aln.toml`](meknes-line1.aln.toml) | `line-1` | 15,766.2 m | 10 |
| [`meknes-line2.aln.toml`](meknes-line2.aln.toml) | `line-2` | 12,219.1 m | 7 |
| [`meknes-line3.aln.toml`](meknes-line3.aln.toml) | `line-3` | 11,396.3 m | 6 |
| [`meknes-line4.aln.toml`](meknes-line4.aln.toml) | `line-4` | 4,246.4 m | 2 |
| [`meknes-line5.aln.toml`](meknes-line5.aln.toml) | `line-5` | 4,036.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
