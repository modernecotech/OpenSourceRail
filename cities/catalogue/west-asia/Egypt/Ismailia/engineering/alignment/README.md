# Ismailia Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ismailia-line1.aln.toml`](ismailia-line1.aln.toml) | `line-1` | 11,564.9 m | 8 |
| [`ismailia-line2.aln.toml`](ismailia-line2.aln.toml) | `line-2` | 19,287.5 m | 15 |
| [`ismailia-line3.aln.toml`](ismailia-line3.aln.toml) | `line-3` | 11,678.6 m | 9 |
| [`ismailia-line4.aln.toml`](ismailia-line4.aln.toml) | `line-4` | 2,150.2 m | 3 |
| [`ismailia-line5.aln.toml`](ismailia-line5.aln.toml) | `line-5` | 8,807.0 m | 5 |
| [`ismailia-line6.aln.toml`](ismailia-line6.aln.toml) | `line-6` | 2,888.8 m | 2 |
| [`ismailia-line7.aln.toml`](ismailia-line7.aln.toml) | `line-7` | 2,330.8 m | 3 |
| [`ismailia-line8.aln.toml`](ismailia-line8.aln.toml) | `line-8` | 3,174.8 m | 2 |
| [`ismailia-line9.aln.toml`](ismailia-line9.aln.toml) | `line-9` | 12,500.1 m | 7 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
