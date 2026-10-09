# Buraidah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`buraidah-line1.aln.toml`](buraidah-line1.aln.toml) | `line-1` | 27,030.7 m | 17 |
| [`buraidah-line10.aln.toml`](buraidah-line10.aln.toml) | `line-10` | 8,269.2 m | 5 |
| [`buraidah-line11.aln.toml`](buraidah-line11.aln.toml) | `line-11` | 3,441.3 m | 3 |
| [`buraidah-line12.aln.toml`](buraidah-line12.aln.toml) | `line-12` | 9,565.9 m | 5 |
| [`buraidah-line13.aln.toml`](buraidah-line13.aln.toml) | `line-13` | 3,344.5 m | 3 |
| [`buraidah-line14.aln.toml`](buraidah-line14.aln.toml) | `line-14` | 2,359.3 m | 2 |
| [`buraidah-line2.aln.toml`](buraidah-line2.aln.toml) | `line-2` | 15,211.8 m | 9 |
| [`buraidah-line3.aln.toml`](buraidah-line3.aln.toml) | `line-3` | 15,512.0 m | 10 |
| [`buraidah-line4.aln.toml`](buraidah-line4.aln.toml) | `line-4` | 4,585.6 m | 3 |
| [`buraidah-line5.aln.toml`](buraidah-line5.aln.toml) | `line-5` | 2,990.8 m | 3 |
| [`buraidah-line6.aln.toml`](buraidah-line6.aln.toml) | `line-6` | 5,066.4 m | 4 |
| [`buraidah-line7.aln.toml`](buraidah-line7.aln.toml) | `line-7` | 3,245.7 m | 3 |
| [`buraidah-line8.aln.toml`](buraidah-line8.aln.toml) | `line-8` | 10,270.1 m | 6 |
| [`buraidah-line9.aln.toml`](buraidah-line9.aln.toml) | `line-9` | 4,455.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
