# Tartus Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tartus-line1.aln.toml`](tartus-line1.aln.toml) | `line-1` | 10,568.6 m | 6 |
| [`tartus-line2.aln.toml`](tartus-line2.aln.toml) | `line-2` | 6,732.9 m | 5 |
| [`tartus-line3.aln.toml`](tartus-line3.aln.toml) | `line-3` | 4,244.2 m | 4 |
| [`tartus-line4.aln.toml`](tartus-line4.aln.toml) | `line-4` | 4,810.1 m | 3 |
| [`tartus-line5.aln.toml`](tartus-line5.aln.toml) | `line-5` | 6,229.3 m | 4 |
| [`tartus-line6.aln.toml`](tartus-line6.aln.toml) | `line-6` | 4,806.8 m | 3 |
| [`tartus-line7.aln.toml`](tartus-line7.aln.toml) | `line-7` | 5,320.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
