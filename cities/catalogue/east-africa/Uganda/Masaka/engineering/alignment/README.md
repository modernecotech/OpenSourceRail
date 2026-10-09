# Masaka Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`masaka-line1.aln.toml`](masaka-line1.aln.toml) | `line-1` | 9,336.1 m | 6 |
| [`masaka-line10.aln.toml`](masaka-line10.aln.toml) | `line-10` | 2,937.9 m | 2 |
| [`masaka-line2.aln.toml`](masaka-line2.aln.toml) | `line-2` | 6,739.8 m | 5 |
| [`masaka-line3.aln.toml`](masaka-line3.aln.toml) | `line-3` | 11,594.7 m | 7 |
| [`masaka-line4.aln.toml`](masaka-line4.aln.toml) | `line-4` | 5,986.4 m | 4 |
| [`masaka-line5.aln.toml`](masaka-line5.aln.toml) | `line-5` | 3,472.0 m | 3 |
| [`masaka-line6.aln.toml`](masaka-line6.aln.toml) | `line-6` | 3,282.3 m | 3 |
| [`masaka-line7.aln.toml`](masaka-line7.aln.toml) | `line-7` | 5,574.4 m | 4 |
| [`masaka-line8.aln.toml`](masaka-line8.aln.toml) | `line-8` | 3,035.0 m | 3 |
| [`masaka-line9.aln.toml`](masaka-line9.aln.toml) | `line-9` | 3,088.8 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
