# Irbid Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`irbid-line1.aln.toml`](irbid-line1.aln.toml) | `line-1` | 11,023.9 m | 8 |
| [`irbid-line10.aln.toml`](irbid-line10.aln.toml) | `line-10` | 3,558.7 m | 3 |
| [`irbid-line11.aln.toml`](irbid-line11.aln.toml) | `line-11` | 2,551.4 m | 2 |
| [`irbid-line12.aln.toml`](irbid-line12.aln.toml) | `line-12` | 7,982.2 m | 5 |
| [`irbid-line2.aln.toml`](irbid-line2.aln.toml) | `line-2` | 10,386.8 m | 7 |
| [`irbid-line3.aln.toml`](irbid-line3.aln.toml) | `line-3` | 16,698.8 m | 11 |
| [`irbid-line4.aln.toml`](irbid-line4.aln.toml) | `line-4` | 3,028.3 m | 3 |
| [`irbid-line5.aln.toml`](irbid-line5.aln.toml) | `line-5` | 2,972.2 m | 2 |
| [`irbid-line6.aln.toml`](irbid-line6.aln.toml) | `line-6` | 5,754.7 m | 4 |
| [`irbid-line7.aln.toml`](irbid-line7.aln.toml) | `line-7` | 2,616.5 m | 2 |
| [`irbid-line8.aln.toml`](irbid-line8.aln.toml) | `line-8` | 6,937.1 m | 5 |
| [`irbid-line9.aln.toml`](irbid-line9.aln.toml) | `line-9` | 2,069.9 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
