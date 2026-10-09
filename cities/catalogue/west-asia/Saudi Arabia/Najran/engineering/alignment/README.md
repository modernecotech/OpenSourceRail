# Najran Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`najran-line1.aln.toml`](najran-line1.aln.toml) | `line-1` | 19,018.4 m | 12 |
| [`najran-line10.aln.toml`](najran-line10.aln.toml) | `line-10` | 4,883.3 m | 3 |
| [`najran-line11.aln.toml`](najran-line11.aln.toml) | `line-11` | 7,457.6 m | 6 |
| [`najran-line12.aln.toml`](najran-line12.aln.toml) | `line-12` | 8,061.2 m | 7 |
| [`najran-line13.aln.toml`](najran-line13.aln.toml) | `line-13` | 2,889.9 m | 3 |
| [`najran-line2.aln.toml`](najran-line2.aln.toml) | `line-2` | 20,169.2 m | 11 |
| [`najran-line3.aln.toml`](najran-line3.aln.toml) | `line-3` | 12,666.8 m | 8 |
| [`najran-line4.aln.toml`](najran-line4.aln.toml) | `line-4` | 2,190.5 m | 3 |
| [`najran-line5.aln.toml`](najran-line5.aln.toml) | `line-5` | 2,692.0 m | 2 |
| [`najran-line6.aln.toml`](najran-line6.aln.toml) | `line-6` | 3,643.1 m | 3 |
| [`najran-line7.aln.toml`](najran-line7.aln.toml) | `line-7` | 7,399.3 m | 5 |
| [`najran-line8.aln.toml`](najran-line8.aln.toml) | `line-8` | 6,977.1 m | 5 |
| [`najran-line9.aln.toml`](najran-line9.aln.toml) | `line-9` | 5,066.2 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
