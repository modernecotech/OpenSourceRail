# Marrakech Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`marrakech-line1.aln.toml`](marrakech-line1.aln.toml) | `line-1` | 27,750.9 m | 20 |
| [`marrakech-line10.aln.toml`](marrakech-line10.aln.toml) | `line-10` | 6,083.2 m | 5 |
| [`marrakech-line11.aln.toml`](marrakech-line11.aln.toml) | `line-11` | 5,633.9 m | 4 |
| [`marrakech-line12.aln.toml`](marrakech-line12.aln.toml) | `line-12` | 5,281.8 m | 4 |
| [`marrakech-line13.aln.toml`](marrakech-line13.aln.toml) | `line-13` | 4,926.2 m | 3 |
| [`marrakech-line14.aln.toml`](marrakech-line14.aln.toml) | `line-14` | 6,400.4 m | 4 |
| [`marrakech-line15.aln.toml`](marrakech-line15.aln.toml) | `line-15` | 4,694.9 m | 5 |
| [`marrakech-line2.aln.toml`](marrakech-line2.aln.toml) | `line-2` | 24,838.7 m | 17 |
| [`marrakech-line3.aln.toml`](marrakech-line3.aln.toml) | `line-3` | 21,134.7 m | 14 |
| [`marrakech-line4.aln.toml`](marrakech-line4.aln.toml) | `line-4` | 25,369.2 m | 18 |
| [`marrakech-line5.aln.toml`](marrakech-line5.aln.toml) | `line-5` | 30,577.6 m | 19 |
| [`marrakech-line6.aln.toml`](marrakech-line6.aln.toml) | `line-6` | 52,965.6 m | 32 |
| [`marrakech-line7.aln.toml`](marrakech-line7.aln.toml) | `line-7` | 4,395.3 m | 3 |
| [`marrakech-line8.aln.toml`](marrakech-line8.aln.toml) | `line-8` | 5,108.4 m | 4 |
| [`marrakech-line9.aln.toml`](marrakech-line9.aln.toml) | `line-9` | 4,222.5 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
