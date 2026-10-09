# Tripoli-Lb Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`tripoli-lb-line1.aln.toml`](tripoli-lb-line1.aln.toml) | `line-1` | 11,762.2 m | 7 |
| [`tripoli-lb-line2.aln.toml`](tripoli-lb-line2.aln.toml) | `line-2` | 16,994.3 m | 10 |
| [`tripoli-lb-line3.aln.toml`](tripoli-lb-line3.aln.toml) | `line-3` | 12,231.1 m | 8 |
| [`tripoli-lb-line4.aln.toml`](tripoli-lb-line4.aln.toml) | `line-4` | 3,231.3 m | 3 |
| [`tripoli-lb-line5.aln.toml`](tripoli-lb-line5.aln.toml) | `line-5` | 2,096.8 m | 2 |
| [`tripoli-lb-line6.aln.toml`](tripoli-lb-line6.aln.toml) | `line-6` | 3,995.3 m | 3 |
| [`tripoli-lb-line7.aln.toml`](tripoli-lb-line7.aln.toml) | `line-7` | 11,488.4 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
