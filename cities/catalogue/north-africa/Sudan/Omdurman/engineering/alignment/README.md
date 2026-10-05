# Omdurman Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`omdurman-line1.aln.toml`](omdurman-line1.aln.toml) | `line-1` | 32,231.7 m | 12 |
| [`omdurman-line2.aln.toml`](omdurman-line2.aln.toml) | `line-2` | 32,446.7 m | 11 |
| [`omdurman-line3.aln.toml`](omdurman-line3.aln.toml) | `line-3` | 32,504.8 m | 11 |
| [`omdurman-line4.aln.toml`](omdurman-line4.aln.toml) | `line-4` | 29,868.9 m | 10 |
| [`omdurman-line5.aln.toml`](omdurman-line5.aln.toml) | `line-5` | 23,159.3 m | 9 |
| [`omdurman-line6.aln.toml`](omdurman-line6.aln.toml) | `line-6` | 72,799.7 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
