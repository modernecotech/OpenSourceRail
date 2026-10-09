# Kumba Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kumba-line1.aln.toml`](kumba-line1.aln.toml) | `line-1` | 16,646.3 m | 10 |
| [`kumba-line10.aln.toml`](kumba-line10.aln.toml) | `line-10` | 2,504.8 m | 2 |
| [`kumba-line11.aln.toml`](kumba-line11.aln.toml) | `line-11` | 3,696.2 m | 3 |
| [`kumba-line2.aln.toml`](kumba-line2.aln.toml) | `line-2` | 11,017.8 m | 8 |
| [`kumba-line3.aln.toml`](kumba-line3.aln.toml) | `line-3` | 8,138.0 m | 7 |
| [`kumba-line4.aln.toml`](kumba-line4.aln.toml) | `line-4` | 3,066.8 m | 3 |
| [`kumba-line5.aln.toml`](kumba-line5.aln.toml) | `line-5` | 3,371.6 m | 3 |
| [`kumba-line6.aln.toml`](kumba-line6.aln.toml) | `line-6` | 7,334.4 m | 5 |
| [`kumba-line7.aln.toml`](kumba-line7.aln.toml) | `line-7` | 6,097.1 m | 4 |
| [`kumba-line8.aln.toml`](kumba-line8.aln.toml) | `line-8` | 3,140.8 m | 3 |
| [`kumba-line9.aln.toml`](kumba-line9.aln.toml) | `line-9` | 6,210.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
