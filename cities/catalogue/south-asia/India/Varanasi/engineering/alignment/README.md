# Varanasi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`varanasi-line1.aln.toml`](varanasi-line1.aln.toml) | `line-1` | 29,769.7 m | 12 |
| [`varanasi-line2.aln.toml`](varanasi-line2.aln.toml) | `line-2` | 47,197.6 m | 16 |
| [`varanasi-line3.aln.toml`](varanasi-line3.aln.toml) | `line-3` | 14,954.4 m | 6 |
| [`varanasi-line4.aln.toml`](varanasi-line4.aln.toml) | `line-4` | 21,975.4 m | 8 |
| [`varanasi-line5.aln.toml`](varanasi-line5.aln.toml) | `line-5` | 22,965.1 m | 8 |
| [`varanasi-line6.aln.toml`](varanasi-line6.aln.toml) | `line-6` | 60,609.0 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
