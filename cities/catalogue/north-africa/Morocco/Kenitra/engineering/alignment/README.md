# Kenitra Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kenitra-line1.aln.toml`](kenitra-line1.aln.toml) | `line-1` | 17,755.6 m | 13 |
| [`kenitra-line2.aln.toml`](kenitra-line2.aln.toml) | `line-2` | 16,692.8 m | 7 |
| [`kenitra-line3.aln.toml`](kenitra-line3.aln.toml) | `line-3` | 24,012.8 m | 10 |
| [`kenitra-line4.aln.toml`](kenitra-line4.aln.toml) | `line-4` | 12,232.8 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
