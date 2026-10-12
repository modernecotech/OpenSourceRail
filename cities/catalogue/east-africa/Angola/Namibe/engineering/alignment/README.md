# Namibe Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`namibe-line1.aln.toml`](namibe-line1.aln.toml) | `line-1` | 12,752.3 m | 5 |
| [`namibe-line2.aln.toml`](namibe-line2.aln.toml) | `line-2` | 12,021.6 m | 6 |
| [`namibe-line3.aln.toml`](namibe-line3.aln.toml) | `line-3` | 13,484.8 m | 7 |
| [`namibe-line4.aln.toml`](namibe-line4.aln.toml) | `line-4` | 4,726.8 m | 3 |
| [`namibe-line5.aln.toml`](namibe-line5.aln.toml) | `line-5` | 4,802.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
