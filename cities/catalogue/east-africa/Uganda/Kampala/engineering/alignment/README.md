# Kampala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kampala-line1.aln.toml`](kampala-line1.aln.toml) | `line-1` | 37,158.1 m | 18 |
| [`kampala-line2.aln.toml`](kampala-line2.aln.toml) | `line-2` | 22,286.5 m | 13 |
| [`kampala-line3.aln.toml`](kampala-line3.aln.toml) | `line-3` | 25,001.5 m | 9 |
| [`kampala-line4.aln.toml`](kampala-line4.aln.toml) | `line-4` | 32,628.5 m | 17 |
| [`kampala-line5.aln.toml`](kampala-line5.aln.toml) | `line-5` | 30,795.6 m | 12 |
| [`kampala-line6.aln.toml`](kampala-line6.aln.toml) | `line-6` | 60,382.1 m | 21 |
| [`kampala-line7.aln.toml`](kampala-line7.aln.toml) | `line-7` | 4,615.0 m | 2 |
| [`kampala-line8.aln.toml`](kampala-line8.aln.toml) | `line-8` | 11,696.8 m | 11 |
| [`kampala-line9.aln.toml`](kampala-line9.aln.toml) | `line-9` | 12,479.1 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
