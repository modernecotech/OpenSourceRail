# Rajshahi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rajshahi-line1.aln.toml`](rajshahi-line1.aln.toml) | `line-1` | 17,034.5 m | 12 |
| [`rajshahi-line2.aln.toml`](rajshahi-line2.aln.toml) | `line-2` | 5,435.0 m | 5 |
| [`rajshahi-line3.aln.toml`](rajshahi-line3.aln.toml) | `line-3` | 10,073.2 m | 9 |
| [`rajshahi-line4.aln.toml`](rajshahi-line4.aln.toml) | `line-4` | 5,909.6 m | 4 |
| [`rajshahi-line5.aln.toml`](rajshahi-line5.aln.toml) | `line-5` | 2,015.4 m | 2 |
| [`rajshahi-line6.aln.toml`](rajshahi-line6.aln.toml) | `line-6` | 7,028.2 m | 5 |
| [`rajshahi-line7.aln.toml`](rajshahi-line7.aln.toml) | `line-7` | 5,503.6 m | 4 |
| [`rajshahi-line8.aln.toml`](rajshahi-line8.aln.toml) | `line-8` | 7,908.0 m | 6 |
| [`rajshahi-line9.aln.toml`](rajshahi-line9.aln.toml) | `line-9` | 3,502.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
