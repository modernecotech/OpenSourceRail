# Pokhara Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`pokhara-line1.aln.toml`](pokhara-line1.aln.toml) | `line-1` | 26,730.1 m | 18 |
| [`pokhara-line2.aln.toml`](pokhara-line2.aln.toml) | `line-2` | 20,937.7 m | 15 |
| [`pokhara-line3.aln.toml`](pokhara-line3.aln.toml) | `line-3` | 26,528.4 m | 16 |
| [`pokhara-line4.aln.toml`](pokhara-line4.aln.toml) | `line-4` | 4,789.3 m | 3 |
| [`pokhara-line5.aln.toml`](pokhara-line5.aln.toml) | `line-5` | 6,087.4 m | 4 |
| [`pokhara-line6.aln.toml`](pokhara-line6.aln.toml) | `line-6` | 4,409.0 m | 3 |
| [`pokhara-line7.aln.toml`](pokhara-line7.aln.toml) | `line-7` | 2,730.2 m | 2 |
| [`pokhara-line8.aln.toml`](pokhara-line8.aln.toml) | `line-8` | 2,555.6 m | 3 |
| [`pokhara-line9.aln.toml`](pokhara-line9.aln.toml) | `line-9` | 7,730.0 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
