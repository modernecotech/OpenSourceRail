# Jeddah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jeddah-line1.aln.toml`](jeddah-line1.aln.toml) | `line-1` | 47,300.1 m | 17 |
| [`jeddah-line10.aln.toml`](jeddah-line10.aln.toml) | `line-10` | 7,359.6 m | 10 |
| [`jeddah-line11.aln.toml`](jeddah-line11.aln.toml) | `line-11` | 6,171.9 m | 2 |
| [`jeddah-line12.aln.toml`](jeddah-line12.aln.toml) | `line-12` | 14,220.4 m | 5 |
| [`jeddah-line13.aln.toml`](jeddah-line13.aln.toml) | `line-13` | 6,314.7 m | 3 |
| [`jeddah-line14.aln.toml`](jeddah-line14.aln.toml) | `line-14` | 6,376.8 m | 2 |
| [`jeddah-line2.aln.toml`](jeddah-line2.aln.toml) | `line-2` | 26,901.2 m | 9 |
| [`jeddah-line3.aln.toml`](jeddah-line3.aln.toml) | `line-3` | 49,241.5 m | 22 |
| [`jeddah-line4.aln.toml`](jeddah-line4.aln.toml) | `line-4` | 44,451.6 m | 14 |
| [`jeddah-line5.aln.toml`](jeddah-line5.aln.toml) | `line-5` | 33,183.6 m | 13 |
| [`jeddah-line6.aln.toml`](jeddah-line6.aln.toml) | `line-6` | 33,882.7 m | 11 |
| [`jeddah-line7.aln.toml`](jeddah-line7.aln.toml) | `line-7` | 29,659.3 m | 11 |
| [`jeddah-line8.aln.toml`](jeddah-line8.aln.toml) | `line-8` | 29,164.1 m | 13 |
| [`jeddah-line9.aln.toml`](jeddah-line9.aln.toml) | `line-9` | 74,186.0 m | 27 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
