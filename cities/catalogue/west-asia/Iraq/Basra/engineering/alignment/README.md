# Basra Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`basra-line1.aln.toml`](basra-line1.aln.toml) | `line-1` | 39,725.4 m | 16 |
| [`basra-line2.aln.toml`](basra-line2.aln.toml) | `line-2` | 17,314.0 m | 8 |
| [`basra-line3.aln.toml`](basra-line3.aln.toml) | `line-3` | 42,556.3 m | 17 |
| [`basra-line4.aln.toml`](basra-line4.aln.toml) | `line-4` | 34,970.7 m | 12 |
| [`basra-line5.aln.toml`](basra-line5.aln.toml) | `line-5` | 35,665.2 m | 14 |
| [`basra-line6.aln.toml`](basra-line6.aln.toml) | `line-6` | 26,389.0 m | 10 |
| [`basra-line7.aln.toml`](basra-line7.aln.toml) | `line-7` | 90,803.3 m | 28 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
