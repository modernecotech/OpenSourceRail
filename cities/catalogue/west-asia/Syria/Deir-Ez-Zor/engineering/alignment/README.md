# Deir-Ez-Zor Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`deir-ez-zor-line1.aln.toml`](deir-ez-zor-line1.aln.toml) | `line-1` | 20,914.8 m | 23 |
| [`deir-ez-zor-line10.aln.toml`](deir-ez-zor-line10.aln.toml) | `line-10` | 8,318.5 m | 6 |
| [`deir-ez-zor-line11.aln.toml`](deir-ez-zor-line11.aln.toml) | `line-11` | 3,262.2 m | 3 |
| [`deir-ez-zor-line12.aln.toml`](deir-ez-zor-line12.aln.toml) | `line-12` | 4,907.8 m | 13 |
| [`deir-ez-zor-line2.aln.toml`](deir-ez-zor-line2.aln.toml) | `line-2` | 12,804.4 m | 9 |
| [`deir-ez-zor-line3.aln.toml`](deir-ez-zor-line3.aln.toml) | `line-3` | 15,888.4 m | 12 |
| [`deir-ez-zor-line4.aln.toml`](deir-ez-zor-line4.aln.toml) | `line-4` | 2,244.5 m | 2 |
| [`deir-ez-zor-line5.aln.toml`](deir-ez-zor-line5.aln.toml) | `line-5` | 5,612.3 m | 5 |
| [`deir-ez-zor-line6.aln.toml`](deir-ez-zor-line6.aln.toml) | `line-6` | 4,846.8 m | 3 |
| [`deir-ez-zor-line7.aln.toml`](deir-ez-zor-line7.aln.toml) | `line-7` | 3,705.9 m | 3 |
| [`deir-ez-zor-line8.aln.toml`](deir-ez-zor-line8.aln.toml) | `line-8` | 5,718.4 m | 4 |
| [`deir-ez-zor-line9.aln.toml`](deir-ez-zor-line9.aln.toml) | `line-9` | 10,543.6 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
