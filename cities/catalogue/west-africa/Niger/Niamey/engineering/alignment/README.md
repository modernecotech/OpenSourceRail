# Niamey Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`niamey-line1.aln.toml`](niamey-line1.aln.toml) | `line-1` | 27,251.8 m | 10 |
| [`niamey-line2.aln.toml`](niamey-line2.aln.toml) | `line-2` | 18,911.0 m | 7 |
| [`niamey-line3.aln.toml`](niamey-line3.aln.toml) | `line-3` | 16,772.4 m | 7 |
| [`niamey-line4.aln.toml`](niamey-line4.aln.toml) | `line-4` | 21,666.3 m | 7 |
| [`niamey-line5.aln.toml`](niamey-line5.aln.toml) | `line-5` | 19,493.4 m | 7 |
| [`niamey-line6.aln.toml`](niamey-line6.aln.toml) | `line-6` | 53,526.3 m | 16 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
