# Luanda Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`luanda-line1.aln.toml`](luanda-line1.aln.toml) | `line-1` | 52,373.1 m | 18 |
| [`luanda-line10.aln.toml`](luanda-line10.aln.toml) | `line-10` | 8,953.4 m | 4 |
| [`luanda-line11.aln.toml`](luanda-line11.aln.toml) | `line-11` | 7,995.8 m | 4 |
| [`luanda-line12.aln.toml`](luanda-line12.aln.toml) | `line-12` | 6,108.7 m | 2 |
| [`luanda-line13.aln.toml`](luanda-line13.aln.toml) | `line-13` | 15,224.3 m | 6 |
| [`luanda-line14.aln.toml`](luanda-line14.aln.toml) | `line-14` | 6,599.2 m | 2 |
| [`luanda-line2.aln.toml`](luanda-line2.aln.toml) | `line-2` | 31,214.1 m | 10 |
| [`luanda-line3.aln.toml`](luanda-line3.aln.toml) | `line-3` | 46,482.6 m | 18 |
| [`luanda-line4.aln.toml`](luanda-line4.aln.toml) | `line-4` | 46,980.9 m | 16 |
| [`luanda-line5.aln.toml`](luanda-line5.aln.toml) | `line-5` | 45,165.2 m | 16 |
| [`luanda-line6.aln.toml`](luanda-line6.aln.toml) | `line-6` | 27,065.5 m | 16 |
| [`luanda-line7.aln.toml`](luanda-line7.aln.toml) | `line-7` | 31,723.9 m | 13 |
| [`luanda-line8.aln.toml`](luanda-line8.aln.toml) | `line-8` | 33,175.5 m | 14 |
| [`luanda-line9.aln.toml`](luanda-line9.aln.toml) | `line-9` | 65,807.8 m | 21 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
