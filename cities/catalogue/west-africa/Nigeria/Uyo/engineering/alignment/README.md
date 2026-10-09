# Uyo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`uyo-line1.aln.toml`](uyo-line1.aln.toml) | `line-1` | 12,053.8 m | 7 |
| [`uyo-line2.aln.toml`](uyo-line2.aln.toml) | `line-2` | 6,932.3 m | 6 |
| [`uyo-line3.aln.toml`](uyo-line3.aln.toml) | `line-3` | 6,552.9 m | 5 |
| [`uyo-line4.aln.toml`](uyo-line4.aln.toml) | `line-4` | 2,786.5 m | 2 |
| [`uyo-line5.aln.toml`](uyo-line5.aln.toml) | `line-5` | 7,082.2 m | 5 |
| [`uyo-line6.aln.toml`](uyo-line6.aln.toml) | `line-6` | 2,332.0 m | 2 |
| [`uyo-line7.aln.toml`](uyo-line7.aln.toml) | `line-7` | 4,587.9 m | 3 |
| [`uyo-line8.aln.toml`](uyo-line8.aln.toml) | `line-8` | 2,089.4 m | 2 |
| [`uyo-line9.aln.toml`](uyo-line9.aln.toml) | `line-9` | 6,465.5 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
