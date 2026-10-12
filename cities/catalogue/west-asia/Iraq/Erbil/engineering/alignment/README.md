# Erbil Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`erbil-line1.aln.toml`](erbil-line1.aln.toml) | `line-1` | 38,543.7 m | 13 |
| [`erbil-line2.aln.toml`](erbil-line2.aln.toml) | `line-2` | 30,768.8 m | 12 |
| [`erbil-line3.aln.toml`](erbil-line3.aln.toml) | `line-3` | 25,774.9 m | 7 |
| [`erbil-line4.aln.toml`](erbil-line4.aln.toml) | `line-4` | 25,002.3 m | 10 |
| [`erbil-line5.aln.toml`](erbil-line5.aln.toml) | `line-5` | 18,001.9 m | 8 |
| [`erbil-line6.aln.toml`](erbil-line6.aln.toml) | `line-6` | 4,369.4 m | 2 |
| [`erbil-line7.aln.toml`](erbil-line7.aln.toml) | `line-7` | 5,837.9 m | 2 |
| [`erbil-line8.aln.toml`](erbil-line8.aln.toml) | `line-8` | 4,000.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
