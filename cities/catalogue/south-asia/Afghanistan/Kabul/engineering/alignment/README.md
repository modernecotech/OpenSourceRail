# Kabul Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kabul-line1.aln.toml`](kabul-line1.aln.toml) | `line-1` | 23,436.7 m | 9 |
| [`kabul-line2.aln.toml`](kabul-line2.aln.toml) | `line-2` | 26,494.5 m | 9 |
| [`kabul-line3.aln.toml`](kabul-line3.aln.toml) | `line-3` | 18,389.0 m | 9 |
| [`kabul-line4.aln.toml`](kabul-line4.aln.toml) | `line-4` | 25,910.2 m | 9 |
| [`kabul-line5.aln.toml`](kabul-line5.aln.toml) | `line-5` | 28,644.7 m | 10 |
| [`kabul-line6.aln.toml`](kabul-line6.aln.toml) | `line-6` | 18,059.3 m | 7 |
| [`kabul-line7.aln.toml`](kabul-line7.aln.toml) | `line-7` | 52,818.5 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
