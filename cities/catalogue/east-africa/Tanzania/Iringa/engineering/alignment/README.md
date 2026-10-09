# Iringa Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`iringa-line1.aln.toml`](iringa-line1.aln.toml) | `line-1` | 7,864.9 m | 7 |
| [`iringa-line2.aln.toml`](iringa-line2.aln.toml) | `line-2` | 7,571.8 m | 6 |
| [`iringa-line3.aln.toml`](iringa-line3.aln.toml) | `line-3` | 4,717.3 m | 4 |
| [`iringa-line4.aln.toml`](iringa-line4.aln.toml) | `line-4` | 2,346.5 m | 3 |
| [`iringa-line5.aln.toml`](iringa-line5.aln.toml) | `line-5` | 4,169.6 m | 3 |
| [`iringa-line6.aln.toml`](iringa-line6.aln.toml) | `line-6` | 7,085.9 m | 6 |
| [`iringa-line7.aln.toml`](iringa-line7.aln.toml) | `line-7` | 5,137.1 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
