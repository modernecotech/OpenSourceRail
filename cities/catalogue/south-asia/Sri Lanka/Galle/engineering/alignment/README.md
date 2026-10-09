# Galle Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`galle-line1.aln.toml`](galle-line1.aln.toml) | `line-1` | 23,316.2 m | 15 |
| [`galle-line10.aln.toml`](galle-line10.aln.toml) | `line-10` | 8,680.0 m | 5 |
| [`galle-line11.aln.toml`](galle-line11.aln.toml) | `line-11` | 8,566.5 m | 6 |
| [`galle-line12.aln.toml`](galle-line12.aln.toml) | `line-12` | 4,297.3 m | 3 |
| [`galle-line13.aln.toml`](galle-line13.aln.toml) | `line-13` | 2,479.1 m | 2 |
| [`galle-line14.aln.toml`](galle-line14.aln.toml) | `line-14` | 7,502.4 m | 5 |
| [`galle-line15.aln.toml`](galle-line15.aln.toml) | `line-15` | 2,315.6 m | 2 |
| [`galle-line2.aln.toml`](galle-line2.aln.toml) | `line-2` | 19,007.4 m | 11 |
| [`galle-line3.aln.toml`](galle-line3.aln.toml) | `line-3` | 16,238.2 m | 11 |
| [`galle-line4.aln.toml`](galle-line4.aln.toml) | `line-4` | 4,584.2 m | 3 |
| [`galle-line5.aln.toml`](galle-line5.aln.toml) | `line-5` | 2,523.7 m | 2 |
| [`galle-line6.aln.toml`](galle-line6.aln.toml) | `line-6` | 4,155.3 m | 3 |
| [`galle-line7.aln.toml`](galle-line7.aln.toml) | `line-7` | 2,635.6 m | 2 |
| [`galle-line8.aln.toml`](galle-line8.aln.toml) | `line-8` | 6,725.8 m | 5 |
| [`galle-line9.aln.toml`](galle-line9.aln.toml) | `line-9` | 3,877.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
