# Nyala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nyala-line1.aln.toml`](nyala-line1.aln.toml) | `line-1` | 16,443.6 m | 5 |
| [`nyala-line2.aln.toml`](nyala-line2.aln.toml) | `line-2` | 15,312.3 m | 7 |
| [`nyala-line3.aln.toml`](nyala-line3.aln.toml) | `line-3` | 11,945.2 m | 5 |
| [`nyala-line4.aln.toml`](nyala-line4.aln.toml) | `line-4` | 4,153.6 m | 2 |
| [`nyala-line5.aln.toml`](nyala-line5.aln.toml) | `line-5` | 5,000.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
