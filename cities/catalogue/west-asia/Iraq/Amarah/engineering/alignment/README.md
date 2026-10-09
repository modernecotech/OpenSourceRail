# Amarah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`amarah-line1.aln.toml`](amarah-line1.aln.toml) | `line-1` | 21,680.1 m | 14 |
| [`amarah-line2.aln.toml`](amarah-line2.aln.toml) | `line-2` | 9,847.1 m | 8 |
| [`amarah-line3.aln.toml`](amarah-line3.aln.toml) | `line-3` | 10,547.2 m | 9 |
| [`amarah-line4.aln.toml`](amarah-line4.aln.toml) | `line-4` | 7,692.6 m | 7 |
| [`amarah-line5.aln.toml`](amarah-line5.aln.toml) | `line-5` | 3,799.7 m | 4 |
| [`amarah-line6.aln.toml`](amarah-line6.aln.toml) | `line-6` | 8,443.1 m | 5 |
| [`amarah-line7.aln.toml`](amarah-line7.aln.toml) | `line-7` | 2,078.2 m | 2 |
| [`amarah-line8.aln.toml`](amarah-line8.aln.toml) | `line-8` | 5,645.2 m | 6 |
| [`amarah-line9.aln.toml`](amarah-line9.aln.toml) | `line-9` | 9,942.3 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
