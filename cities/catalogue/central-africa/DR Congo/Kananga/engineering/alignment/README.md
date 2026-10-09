# Kananga Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kananga-line1.aln.toml`](kananga-line1.aln.toml) | `line-1` | 12,557.3 m | 8 |
| [`kananga-line10.aln.toml`](kananga-line10.aln.toml) | `line-10` | 3,574.2 m | 3 |
| [`kananga-line2.aln.toml`](kananga-line2.aln.toml) | `line-2` | 24,058.0 m | 13 |
| [`kananga-line3.aln.toml`](kananga-line3.aln.toml) | `line-3` | 2,294.6 m | 3 |
| [`kananga-line4.aln.toml`](kananga-line4.aln.toml) | `line-4` | 5,416.8 m | 4 |
| [`kananga-line5.aln.toml`](kananga-line5.aln.toml) | `line-5` | 4,309.9 m | 3 |
| [`kananga-line6.aln.toml`](kananga-line6.aln.toml) | `line-6` | 4,588.8 m | 4 |
| [`kananga-line7.aln.toml`](kananga-line7.aln.toml) | `line-7` | 6,501.0 m | 6 |
| [`kananga-line8.aln.toml`](kananga-line8.aln.toml) | `line-8` | 4,466.8 m | 3 |
| [`kananga-line9.aln.toml`](kananga-line9.aln.toml) | `line-9` | 6,317.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
