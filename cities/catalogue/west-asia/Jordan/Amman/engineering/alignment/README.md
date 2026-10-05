# Amman Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`amman-line1.aln.toml`](amman-line1.aln.toml) | `line-1` | 38,448.8 m | 16 |
| [`amman-line2.aln.toml`](amman-line2.aln.toml) | `line-2` | 39,486.7 m | 16 |
| [`amman-line3.aln.toml`](amman-line3.aln.toml) | `line-3` | 22,801.7 m | 12 |
| [`amman-line4.aln.toml`](amman-line4.aln.toml) | `line-4` | 18,230.8 m | 11 |
| [`amman-line5.aln.toml`](amman-line5.aln.toml) | `line-5` | 29,085.4 m | 15 |
| [`amman-line6.aln.toml`](amman-line6.aln.toml) | `line-6` | 31,585.1 m | 12 |
| [`amman-line7.aln.toml`](amman-line7.aln.toml) | `line-7` | 24,749.9 m | 12 |
| [`amman-line8.aln.toml`](amman-line8.aln.toml) | `line-8` | 29,047.5 m | 13 |
| [`amman-line9.aln.toml`](amman-line9.aln.toml) | `line-9` | 75,958.4 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
