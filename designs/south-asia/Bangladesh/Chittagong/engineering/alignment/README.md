# Chittagong Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`chittagong-line1.aln.toml`](chittagong-line1.aln.toml) | `line-1` | 41,910.2 m | 19 |
| [`chittagong-line2.aln.toml`](chittagong-line2.aln.toml) | `line-2` | 28,984.4 m | 19 |
| [`chittagong-line3.aln.toml`](chittagong-line3.aln.toml) | `line-3` | 47,618.2 m | 25 |
| [`chittagong-line4.aln.toml`](chittagong-line4.aln.toml) | `line-4` | 33,319.8 m | 18 |
| [`chittagong-line5.aln.toml`](chittagong-line5.aln.toml) | `line-5` | 35,818.8 m | 20 |
| [`chittagong-line6.aln.toml`](chittagong-line6.aln.toml) | `line-6` | 29,926.3 m | 17 |
| [`chittagong-line7.aln.toml`](chittagong-line7.aln.toml) | `line-7` | 37,033.5 m | 19 |
| [`chittagong-line8.aln.toml`](chittagong-line8.aln.toml) | `line-8` | 69,161.9 m | 45 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
