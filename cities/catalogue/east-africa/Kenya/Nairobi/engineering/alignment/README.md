# Nairobi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nairobi-line1.aln.toml`](nairobi-line1.aln.toml) | `line-1` | 57,880.3 m | 18 |
| [`nairobi-line2.aln.toml`](nairobi-line2.aln.toml) | `line-2` | 54,500.6 m | 19 |
| [`nairobi-line3.aln.toml`](nairobi-line3.aln.toml) | `line-3` | 52,239.8 m | 15 |
| [`nairobi-line4.aln.toml`](nairobi-line4.aln.toml) | `line-4` | 32,541.6 m | 10 |
| [`nairobi-line5.aln.toml`](nairobi-line5.aln.toml) | `line-5` | 46,082.1 m | 13 |
| [`nairobi-line6.aln.toml`](nairobi-line6.aln.toml) | `line-6` | 59,932.5 m | 16 |
| [`nairobi-line7.aln.toml`](nairobi-line7.aln.toml) | `line-7` | 53,920.0 m | 18 |
| [`nairobi-line8.aln.toml`](nairobi-line8.aln.toml) | `line-8` | 43,584.1 m | 12 |
| [`nairobi-line9.aln.toml`](nairobi-line9.aln.toml) | `line-9` | 105,088.5 m | 30 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
