# Niamey Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`niamey-line1.aln.toml`](niamey-line1.aln.toml) | `line-1` | 22,676.3 m | 10 |
| [`niamey-line2.aln.toml`](niamey-line2.aln.toml) | `line-2` | 15,735.8 m | 8 |
| [`niamey-line3.aln.toml`](niamey-line3.aln.toml) | `line-3` | 14,193.0 m | 8 |
| [`niamey-line4.aln.toml`](niamey-line4.aln.toml) | `line-4` | 19,280.3 m | 10 |
| [`niamey-line5.aln.toml`](niamey-line5.aln.toml) | `line-5` | 18,810.8 m | 9 |
| [`niamey-line6.aln.toml`](niamey-line6.aln.toml) | `line-6` | 51,063.4 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
