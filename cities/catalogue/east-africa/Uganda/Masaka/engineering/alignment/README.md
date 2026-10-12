# Masaka Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`masaka-line1.aln.toml`](masaka-line1.aln.toml) | `line-1` | 9,336.1 m | 6 |
| [`masaka-line2.aln.toml`](masaka-line2.aln.toml) | `line-2` | 9,286.1 m | 4 |
| [`masaka-line3.aln.toml`](masaka-line3.aln.toml) | `line-3` | 12,133.8 m | 8 |
| [`masaka-line4.aln.toml`](masaka-line4.aln.toml) | `line-4` | 4,495.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
