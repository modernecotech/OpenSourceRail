# Vadodara Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`vadodara-line1.aln.toml`](vadodara-line1.aln.toml) | `line-1` | 25,755.7 m | 9 |
| [`vadodara-line2.aln.toml`](vadodara-line2.aln.toml) | `line-2` | 18,782.4 m | 9 |
| [`vadodara-line3.aln.toml`](vadodara-line3.aln.toml) | `line-3` | 16,682.7 m | 8 |
| [`vadodara-line4.aln.toml`](vadodara-line4.aln.toml) | `line-4` | 22,945.2 m | 10 |
| [`vadodara-line5.aln.toml`](vadodara-line5.aln.toml) | `line-5` | 23,164.7 m | 9 |
| [`vadodara-line6.aln.toml`](vadodara-line6.aln.toml) | `line-6` | 42,901.8 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
