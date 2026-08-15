# Maiduguri Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maiduguri-line1.aln.toml`](maiduguri-line1.aln.toml) | `line-1` | 26,679.7 m | 10 |
| [`maiduguri-line2.aln.toml`](maiduguri-line2.aln.toml) | `line-2` | 25,387.4 m | 10 |
| [`maiduguri-line3.aln.toml`](maiduguri-line3.aln.toml) | `line-3` | 27,924.6 m | 11 |
| [`maiduguri-line4.aln.toml`](maiduguri-line4.aln.toml) | `line-4` | 26,322.5 m | 9 |
| [`maiduguri-line5.aln.toml`](maiduguri-line5.aln.toml) | `line-5` | 62,047.5 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
