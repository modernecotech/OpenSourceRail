# Lahij Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lahij-line1.aln.toml`](lahij-line1.aln.toml) | `line-1` | 8,179.4 m | 6 |
| [`lahij-line2.aln.toml`](lahij-line2.aln.toml) | `line-2` | 6,222.3 m | 5 |
| [`lahij-line3.aln.toml`](lahij-line3.aln.toml) | `line-3` | 9,190.3 m | 8 |
| [`lahij-line4.aln.toml`](lahij-line4.aln.toml) | `line-4` | 6,669.4 m | 4 |
| [`lahij-line5.aln.toml`](lahij-line5.aln.toml) | `line-5` | 7,545.5 m | 5 |
| [`lahij-line6.aln.toml`](lahij-line6.aln.toml) | `line-6` | 2,796.2 m | 2 |
| [`lahij-line7.aln.toml`](lahij-line7.aln.toml) | `line-7` | 5,815.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
