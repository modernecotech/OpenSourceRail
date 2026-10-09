# Dhamar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dhamar-line1.aln.toml`](dhamar-line1.aln.toml) | `line-1` | 7,294.5 m | 5 |
| [`dhamar-line2.aln.toml`](dhamar-line2.aln.toml) | `line-2` | 9,444.5 m | 6 |
| [`dhamar-line3.aln.toml`](dhamar-line3.aln.toml) | `line-3` | 3,894.8 m | 4 |
| [`dhamar-line4.aln.toml`](dhamar-line4.aln.toml) | `line-4` | 2,309.9 m | 3 |
| [`dhamar-line5.aln.toml`](dhamar-line5.aln.toml) | `line-5` | 2,382.5 m | 2 |
| [`dhamar-line6.aln.toml`](dhamar-line6.aln.toml) | `line-6` | 4,191.5 m | 3 |
| [`dhamar-line7.aln.toml`](dhamar-line7.aln.toml) | `line-7` | 6,229.9 m | 4 |
| [`dhamar-line8.aln.toml`](dhamar-line8.aln.toml) | `line-8` | 4,467.4 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
