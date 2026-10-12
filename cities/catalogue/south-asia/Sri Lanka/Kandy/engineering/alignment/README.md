# Kandy Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kandy-line1.aln.toml`](kandy-line1.aln.toml) | `line-1` | 22,168.3 m | 6 |
| [`kandy-line2.aln.toml`](kandy-line2.aln.toml) | `line-2` | 28,177.7 m | 9 |
| [`kandy-line3.aln.toml`](kandy-line3.aln.toml) | `line-3` | 19,373.2 m | 7 |
| [`kandy-line4.aln.toml`](kandy-line4.aln.toml) | `line-4` | 12,591.4 m | 4 |
| [`kandy-line5.aln.toml`](kandy-line5.aln.toml) | `line-5` | 4,259.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
