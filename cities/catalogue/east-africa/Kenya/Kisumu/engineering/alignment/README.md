# Kisumu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kisumu-line1.aln.toml`](kisumu-line1.aln.toml) | `line-1` | 16,909.8 m | 6 |
| [`kisumu-line2.aln.toml`](kisumu-line2.aln.toml) | `line-2` | 27,716.8 m | 9 |
| [`kisumu-line3.aln.toml`](kisumu-line3.aln.toml) | `line-3` | 7,929.1 m | 3 |
| [`kisumu-line4.aln.toml`](kisumu-line4.aln.toml) | `line-4` | 4,135.0 m | 2 |
| [`kisumu-line5.aln.toml`](kisumu-line5.aln.toml) | `line-5` | 4,062.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
