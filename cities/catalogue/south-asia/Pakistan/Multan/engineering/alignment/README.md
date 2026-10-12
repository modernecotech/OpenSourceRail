# Multan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`multan-line1.aln.toml`](multan-line1.aln.toml) | `line-1` | 19,801.0 m | 10 |
| [`multan-line2.aln.toml`](multan-line2.aln.toml) | `line-2` | 16,859.8 m | 8 |
| [`multan-line3.aln.toml`](multan-line3.aln.toml) | `line-3` | 20,270.8 m | 7 |
| [`multan-line4.aln.toml`](multan-line4.aln.toml) | `line-4` | 21,938.1 m | 12 |
| [`multan-line5.aln.toml`](multan-line5.aln.toml) | `line-5` | 44,919.3 m | 19 |
| [`multan-line6.aln.toml`](multan-line6.aln.toml) | `line-6` | 4,873.3 m | 2 |
| [`multan-line7.aln.toml`](multan-line7.aln.toml) | `line-7` | 4,322.7 m | 2 |
| [`multan-line8.aln.toml`](multan-line8.aln.toml) | `line-8` | 6,440.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
