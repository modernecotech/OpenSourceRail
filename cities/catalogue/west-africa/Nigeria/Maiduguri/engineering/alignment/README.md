# Maiduguri Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maiduguri-line1.aln.toml`](maiduguri-line1.aln.toml) | `line-1` | 24,636.3 m | 8 |
| [`maiduguri-line2.aln.toml`](maiduguri-line2.aln.toml) | `line-2` | 21,550.1 m | 10 |
| [`maiduguri-line3.aln.toml`](maiduguri-line3.aln.toml) | `line-3` | 30,367.1 m | 13 |
| [`maiduguri-line4.aln.toml`](maiduguri-line4.aln.toml) | `line-4` | 28,704.8 m | 10 |
| [`maiduguri-line5.aln.toml`](maiduguri-line5.aln.toml) | `line-5` | 64,563.4 m | 17 |
| [`maiduguri-line6.aln.toml`](maiduguri-line6.aln.toml) | `line-6` | 5,607.0 m | 2 |
| [`maiduguri-line7.aln.toml`](maiduguri-line7.aln.toml) | `line-7` | 14,286.1 m | 6 |
| [`maiduguri-line8.aln.toml`](maiduguri-line8.aln.toml) | `line-8` | 4,829.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
