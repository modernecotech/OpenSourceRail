# Najaf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najaf-line1.aln.toml`](najaf-line1.aln.toml) | `line-1` | 18,947.4 m | 6 |
| [`najaf-line2.aln.toml`](najaf-line2.aln.toml) | `line-2` | 32,209.5 m | 10 |
| [`najaf-line3.aln.toml`](najaf-line3.aln.toml) | `line-3` | 16,826.0 m | 7 |
| [`najaf-line4.aln.toml`](najaf-line4.aln.toml) | `line-4` | 22,771.5 m | 7 |
| [`najaf-line5.aln.toml`](najaf-line5.aln.toml) | `line-5` | 21,448.2 m | 7 |
| [`najaf-line6.aln.toml`](najaf-line6.aln.toml) | `line-6` | 28,020.5 m | 10 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
