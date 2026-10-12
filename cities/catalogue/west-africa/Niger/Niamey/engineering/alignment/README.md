# Niamey Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`niamey-line1.aln.toml`](niamey-line1.aln.toml) | `line-1` | 29,671.3 m | 17 |
| [`niamey-line2.aln.toml`](niamey-line2.aln.toml) | `line-2` | 20,777.8 m | 10 |
| [`niamey-line3.aln.toml`](niamey-line3.aln.toml) | `line-3` | 16,812.4 m | 13 |
| [`niamey-line4.aln.toml`](niamey-line4.aln.toml) | `line-4` | 22,761.4 m | 10 |
| [`niamey-line5.aln.toml`](niamey-line5.aln.toml) | `line-5` | 18,552.8 m | 7 |
| [`niamey-line6.aln.toml`](niamey-line6.aln.toml) | `line-6` | 56,325.9 m | 19 |
| [`niamey-line7.aln.toml`](niamey-line7.aln.toml) | `line-7` | 5,115.3 m | 2 |
| [`niamey-line8.aln.toml`](niamey-line8.aln.toml) | `line-8` | 10,291.7 m | 3 |
| [`niamey-line9.aln.toml`](niamey-line9.aln.toml) | `line-9` | 8,044.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
