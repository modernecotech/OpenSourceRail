# Soyo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`soyo-line1.aln.toml`](soyo-line1.aln.toml) | `line-1` | 6,915.8 m | 7 |
| [`soyo-line2.aln.toml`](soyo-line2.aln.toml) | `line-2` | 3,905.6 m | 4 |
| [`soyo-line3.aln.toml`](soyo-line3.aln.toml) | `line-3` | 10,159.2 m | 8 |
| [`soyo-line4.aln.toml`](soyo-line4.aln.toml) | `line-4` | 9,003.7 m | 8 |
| [`soyo-line5.aln.toml`](soyo-line5.aln.toml) | `line-5` | 8,279.7 m | 6 |
| [`soyo-line6.aln.toml`](soyo-line6.aln.toml) | `line-6` | 3,503.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
