# Qena Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`qena-line1.aln.toml`](qena-line1.aln.toml) | `line-1` | 10,279.1 m | 7 |
| [`qena-line10.aln.toml`](qena-line10.aln.toml) | `line-10` | 5,095.9 m | 4 |
| [`qena-line2.aln.toml`](qena-line2.aln.toml) | `line-2` | 18,371.0 m | 13 |
| [`qena-line3.aln.toml`](qena-line3.aln.toml) | `line-3` | 13,176.5 m | 8 |
| [`qena-line4.aln.toml`](qena-line4.aln.toml) | `line-4` | 2,915.6 m | 3 |
| [`qena-line5.aln.toml`](qena-line5.aln.toml) | `line-5` | 2,369.4 m | 2 |
| [`qena-line6.aln.toml`](qena-line6.aln.toml) | `line-6` | 6,997.2 m | 5 |
| [`qena-line7.aln.toml`](qena-line7.aln.toml) | `line-7` | 5,317.3 m | 4 |
| [`qena-line8.aln.toml`](qena-line8.aln.toml) | `line-8` | 2,085.1 m | 2 |
| [`qena-line9.aln.toml`](qena-line9.aln.toml) | `line-9` | 3,937.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
