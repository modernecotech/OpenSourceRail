# Rangpur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rangpur-line1.aln.toml`](rangpur-line1.aln.toml) | `line-1` | 12,992.0 m | 5 |
| [`rangpur-line2.aln.toml`](rangpur-line2.aln.toml) | `line-2` | 17,696.4 m | 6 |
| [`rangpur-line3.aln.toml`](rangpur-line3.aln.toml) | `line-3` | 10,590.8 m | 4 |
| [`rangpur-line4.aln.toml`](rangpur-line4.aln.toml) | `line-4` | 4,495.6 m | 2 |
| [`rangpur-line5.aln.toml`](rangpur-line5.aln.toml) | `line-5` | 5,511.4 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
