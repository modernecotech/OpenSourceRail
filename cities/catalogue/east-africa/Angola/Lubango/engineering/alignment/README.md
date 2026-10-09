# Lubango Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lubango-line1.aln.toml`](lubango-line1.aln.toml) | `line-1` | 13,415.2 m | 11 |
| [`lubango-line10.aln.toml`](lubango-line10.aln.toml) | `line-10` | 3,094.2 m | 3 |
| [`lubango-line2.aln.toml`](lubango-line2.aln.toml) | `line-2` | 20,058.5 m | 12 |
| [`lubango-line3.aln.toml`](lubango-line3.aln.toml) | `line-3` | 11,318.0 m | 8 |
| [`lubango-line4.aln.toml`](lubango-line4.aln.toml) | `line-4` | 6,569.0 m | 5 |
| [`lubango-line5.aln.toml`](lubango-line5.aln.toml) | `line-5` | 2,003.7 m | 2 |
| [`lubango-line6.aln.toml`](lubango-line6.aln.toml) | `line-6` | 6,971.4 m | 4 |
| [`lubango-line7.aln.toml`](lubango-line7.aln.toml) | `line-7` | 10,354.0 m | 7 |
| [`lubango-line8.aln.toml`](lubango-line8.aln.toml) | `line-8` | 5,772.7 m | 4 |
| [`lubango-line9.aln.toml`](lubango-line9.aln.toml) | `line-9` | 9,468.3 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
