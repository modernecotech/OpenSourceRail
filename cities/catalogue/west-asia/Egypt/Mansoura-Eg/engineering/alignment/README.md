# Mansoura-Eg Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mansoura-eg-line1.aln.toml`](mansoura-eg-line1.aln.toml) | `line-1` | 10,085.1 m | 8 |
| [`mansoura-eg-line10.aln.toml`](mansoura-eg-line10.aln.toml) | `line-10` | 2,724.5 m | 2 |
| [`mansoura-eg-line11.aln.toml`](mansoura-eg-line11.aln.toml) | `line-11` | 2,535.9 m | 2 |
| [`mansoura-eg-line2.aln.toml`](mansoura-eg-line2.aln.toml) | `line-2` | 9,168.7 m | 6 |
| [`mansoura-eg-line3.aln.toml`](mansoura-eg-line3.aln.toml) | `line-3` | 24,857.9 m | 15 |
| [`mansoura-eg-line4.aln.toml`](mansoura-eg-line4.aln.toml) | `line-4` | 3,941.7 m | 3 |
| [`mansoura-eg-line5.aln.toml`](mansoura-eg-line5.aln.toml) | `line-5` | 7,711.5 m | 5 |
| [`mansoura-eg-line6.aln.toml`](mansoura-eg-line6.aln.toml) | `line-6` | 10,888.0 m | 7 |
| [`mansoura-eg-line7.aln.toml`](mansoura-eg-line7.aln.toml) | `line-7` | 8,177.8 m | 5 |
| [`mansoura-eg-line8.aln.toml`](mansoura-eg-line8.aln.toml) | `line-8` | 3,045.9 m | 2 |
| [`mansoura-eg-line9.aln.toml`](mansoura-eg-line9.aln.toml) | `line-9` | 4,528.8 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
