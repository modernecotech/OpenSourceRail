# Pemba-Mz Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`pemba-mz-line1.aln.toml`](pemba-mz-line1.aln.toml) | `line-1` | 14,019.9 m | 6 |
| [`pemba-mz-line2.aln.toml`](pemba-mz-line2.aln.toml) | `line-2` | 7,780.6 m | 4 |
| [`pemba-mz-line3.aln.toml`](pemba-mz-line3.aln.toml) | `line-3` | 10,613.9 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
