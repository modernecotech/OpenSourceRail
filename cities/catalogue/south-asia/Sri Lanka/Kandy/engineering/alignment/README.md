# Kandy Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kandy-line1.aln.toml`](kandy-line1.aln.toml) | `line-1` | 22,168.3 m | 21 |
| [`kandy-line10.aln.toml`](kandy-line10.aln.toml) | `line-10` | 4,456.8 m | 4 |
| [`kandy-line11.aln.toml`](kandy-line11.aln.toml) | `line-11` | 6,487.2 m | 5 |
| [`kandy-line12.aln.toml`](kandy-line12.aln.toml) | `line-12` | 5,655.2 m | 3 |
| [`kandy-line13.aln.toml`](kandy-line13.aln.toml) | `line-13` | 5,153.5 m | 6 |
| [`kandy-line14.aln.toml`](kandy-line14.aln.toml) | `line-14` | 8,195.0 m | 5 |
| [`kandy-line15.aln.toml`](kandy-line15.aln.toml) | `line-15` | 2,154.8 m | 3 |
| [`kandy-line16.aln.toml`](kandy-line16.aln.toml) | `line-16` | 4,780.6 m | 3 |
| [`kandy-line17.aln.toml`](kandy-line17.aln.toml) | `line-17` | 3,796.2 m | 3 |
| [`kandy-line18.aln.toml`](kandy-line18.aln.toml) | `line-18` | 3,708.8 m | 3 |
| [`kandy-line2.aln.toml`](kandy-line2.aln.toml) | `line-2` | 21,340.0 m | 15 |
| [`kandy-line3.aln.toml`](kandy-line3.aln.toml) | `line-3` | 19,373.2 m | 11 |
| [`kandy-line4.aln.toml`](kandy-line4.aln.toml) | `line-4` | 2,512.2 m | 2 |
| [`kandy-line5.aln.toml`](kandy-line5.aln.toml) | `line-5` | 2,123.1 m | 2 |
| [`kandy-line6.aln.toml`](kandy-line6.aln.toml) | `line-6` | 2,323.3 m | 2 |
| [`kandy-line7.aln.toml`](kandy-line7.aln.toml) | `line-7` | 2,435.4 m | 2 |
| [`kandy-line8.aln.toml`](kandy-line8.aln.toml) | `line-8` | 3,299.9 m | 3 |
| [`kandy-line9.aln.toml`](kandy-line9.aln.toml) | `line-9` | 5,585.8 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
