# Sidon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sidon-line1.aln.toml`](sidon-line1.aln.toml) | `line-1` | 12,781.8 m | 8 |
| [`sidon-line2.aln.toml`](sidon-line2.aln.toml) | `line-2` | 3,588.2 m | 4 |
| [`sidon-line3.aln.toml`](sidon-line3.aln.toml) | `line-3` | 9,071.8 m | 6 |
| [`sidon-line4.aln.toml`](sidon-line4.aln.toml) | `line-4` | 2,848.5 m | 2 |
| [`sidon-line5.aln.toml`](sidon-line5.aln.toml) | `line-5` | 4,513.3 m | 3 |
| [`sidon-line6.aln.toml`](sidon-line6.aln.toml) | `line-6` | 3,616.7 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
