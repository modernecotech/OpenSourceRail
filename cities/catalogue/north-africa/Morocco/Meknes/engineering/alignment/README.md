# Meknes Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`meknes-line1.aln.toml`](meknes-line1.aln.toml) | `line-1` | 12,651.9 m | 9 |
| [`meknes-line2.aln.toml`](meknes-line2.aln.toml) | `line-2` | 9,034.2 m | 6 |
| [`meknes-line3.aln.toml`](meknes-line3.aln.toml) | `line-3` | 7,198.5 m | 5 |
| [`meknes-line4.aln.toml`](meknes-line4.aln.toml) | `line-4` | 5,651.0 m | 5 |
| [`meknes-line5.aln.toml`](meknes-line5.aln.toml) | `line-5` | 2,633.4 m | 2 |
| [`meknes-line6.aln.toml`](meknes-line6.aln.toml) | `line-6` | 3,483.9 m | 3 |
| [`meknes-line7.aln.toml`](meknes-line7.aln.toml) | `line-7` | 3,565.0 m | 3 |
| [`meknes-line8.aln.toml`](meknes-line8.aln.toml) | `line-8` | 3,401.3 m | 3 |
| [`meknes-line9.aln.toml`](meknes-line9.aln.toml) | `line-9` | 2,874.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
