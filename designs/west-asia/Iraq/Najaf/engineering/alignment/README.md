# Najaf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najaf-line1.aln.toml`](najaf-line1.aln.toml) | `line-1` | 26,023.8 m | 16 |
| [`najaf-line2.aln.toml`](najaf-line2.aln.toml) | `line-2` | 36,699.9 m | 21 |
| [`najaf-line3.aln.toml`](najaf-line3.aln.toml) | `line-3` | 18,491.0 m | 12 |
| [`najaf-line4.aln.toml`](najaf-line4.aln.toml) | `line-4` | 28,015.1 m | 16 |
| [`najaf-line5.aln.toml`](najaf-line5.aln.toml) | `line-5` | 24,441.0 m | 13 |
| [`najaf-line6.aln.toml`](najaf-line6.aln.toml) | `line-6` | 31,450.4 m | 23 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
