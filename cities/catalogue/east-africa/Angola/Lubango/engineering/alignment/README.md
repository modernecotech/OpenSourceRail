# Lubango Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lubango-line1.aln.toml`](lubango-line1.aln.toml) | `line-1` | 15,808.0 m | 10 |
| [`lubango-line2.aln.toml`](lubango-line2.aln.toml) | `line-2` | 20,058.5 m | 8 |
| [`lubango-line3.aln.toml`](lubango-line3.aln.toml) | `line-3` | 13,975.9 m | 10 |
| [`lubango-line4.aln.toml`](lubango-line4.aln.toml) | `line-4` | 8,413.5 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
