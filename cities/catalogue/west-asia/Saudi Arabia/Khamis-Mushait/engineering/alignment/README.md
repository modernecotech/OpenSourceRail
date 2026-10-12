# Khamis-Mushait Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khamis-mushait-line1.aln.toml`](khamis-mushait-line1.aln.toml) | `line-1` | 29,976.8 m | 16 |
| [`khamis-mushait-line2.aln.toml`](khamis-mushait-line2.aln.toml) | `line-2` | 27,852.4 m | 8 |
| [`khamis-mushait-line3.aln.toml`](khamis-mushait-line3.aln.toml) | `line-3` | 28,727.5 m | 15 |
| [`khamis-mushait-line4.aln.toml`](khamis-mushait-line4.aln.toml) | `line-4` | 8,370.3 m | 4 |
| [`khamis-mushait-line5.aln.toml`](khamis-mushait-line5.aln.toml) | `line-5` | 4,375.0 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
