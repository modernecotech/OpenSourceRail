# Mahalla Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mahalla-line1.aln.toml`](mahalla-line1.aln.toml) | `line-1` | 10,038.1 m | 7 |
| [`mahalla-line2.aln.toml`](mahalla-line2.aln.toml) | `line-2` | 18,088.3 m | 11 |
| [`mahalla-line3.aln.toml`](mahalla-line3.aln.toml) | `line-3` | 5,501.0 m | 7 |
| [`mahalla-line4.aln.toml`](mahalla-line4.aln.toml) | `line-4` | 3,086.2 m | 3 |
| [`mahalla-line5.aln.toml`](mahalla-line5.aln.toml) | `line-5` | 3,921.9 m | 3 |
| [`mahalla-line6.aln.toml`](mahalla-line6.aln.toml) | `line-6` | 7,118.4 m | 5 |
| [`mahalla-line7.aln.toml`](mahalla-line7.aln.toml) | `line-7` | 11,369.1 m | 7 |
| [`mahalla-line8.aln.toml`](mahalla-line8.aln.toml) | `line-8` | 7,632.5 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
