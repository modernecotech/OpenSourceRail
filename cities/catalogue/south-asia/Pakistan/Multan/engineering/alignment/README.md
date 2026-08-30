# Multan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`multan-line1.aln.toml`](multan-line1.aln.toml) | `line-1` | 18,153.9 m | 9 |
| [`multan-line2.aln.toml`](multan-line2.aln.toml) | `line-2` | 19,956.8 m | 9 |
| [`multan-line3.aln.toml`](multan-line3.aln.toml) | `line-3` | 18,820.9 m | 7 |
| [`multan-line4.aln.toml`](multan-line4.aln.toml) | `line-4` | 19,693.6 m | 7 |
| [`multan-line5.aln.toml`](multan-line5.aln.toml) | `line-5` | 41,925.7 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
