# Kigali Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kigali-line1.aln.toml`](kigali-line1.aln.toml) | `line-1` | 32,505.5 m | 20 |
| [`kigali-line2.aln.toml`](kigali-line2.aln.toml) | `line-2` | 22,830.0 m | 16 |
| [`kigali-line3.aln.toml`](kigali-line3.aln.toml) | `line-3` | 18,536.9 m | 13 |
| [`kigali-line4.aln.toml`](kigali-line4.aln.toml) | `line-4` | 24,189.6 m | 16 |
| [`kigali-line5.aln.toml`](kigali-line5.aln.toml) | `line-5` | 24,923.6 m | 15 |
| [`kigali-line6.aln.toml`](kigali-line6.aln.toml) | `line-6` | 60,246.9 m | 40 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
