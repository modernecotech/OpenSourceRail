# Eldoret Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`eldoret-line1.aln.toml`](eldoret-line1.aln.toml) | `line-1` | 20,318.2 m | 14 |
| [`eldoret-line10.aln.toml`](eldoret-line10.aln.toml) | `line-10` | 3,387.4 m | 3 |
| [`eldoret-line11.aln.toml`](eldoret-line11.aln.toml) | `line-11` | 2,725.3 m | 2 |
| [`eldoret-line12.aln.toml`](eldoret-line12.aln.toml) | `line-12` | 6,197.5 m | 3 |
| [`eldoret-line13.aln.toml`](eldoret-line13.aln.toml) | `line-13` | 8,673.7 m | 5 |
| [`eldoret-line14.aln.toml`](eldoret-line14.aln.toml) | `line-14` | 6,517.2 m | 4 |
| [`eldoret-line15.aln.toml`](eldoret-line15.aln.toml) | `line-15` | 3,106.8 m | 3 |
| [`eldoret-line16.aln.toml`](eldoret-line16.aln.toml) | `line-16` | 2,047.9 m | 2 |
| [`eldoret-line2.aln.toml`](eldoret-line2.aln.toml) | `line-2` | 13,797.9 m | 11 |
| [`eldoret-line3.aln.toml`](eldoret-line3.aln.toml) | `line-3` | 21,029.9 m | 14 |
| [`eldoret-line4.aln.toml`](eldoret-line4.aln.toml) | `line-4` | 4,947.4 m | 4 |
| [`eldoret-line5.aln.toml`](eldoret-line5.aln.toml) | `line-5` | 2,177.1 m | 3 |
| [`eldoret-line6.aln.toml`](eldoret-line6.aln.toml) | `line-6` | 4,828.4 m | 4 |
| [`eldoret-line7.aln.toml`](eldoret-line7.aln.toml) | `line-7` | 2,138.2 m | 2 |
| [`eldoret-line8.aln.toml`](eldoret-line8.aln.toml) | `line-8` | 4,894.9 m | 3 |
| [`eldoret-line9.aln.toml`](eldoret-line9.aln.toml) | `line-9` | 2,534.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
