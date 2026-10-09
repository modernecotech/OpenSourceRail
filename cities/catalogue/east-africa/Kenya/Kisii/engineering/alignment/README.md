# Kisii Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kisii-line1.aln.toml`](kisii-line1.aln.toml) | `line-1` | 6,738.4 m | 4 |
| [`kisii-line2.aln.toml`](kisii-line2.aln.toml) | `line-2` | 2,951.1 m | 3 |
| [`kisii-line3.aln.toml`](kisii-line3.aln.toml) | `line-3` | 8,508.1 m | 6 |
| [`kisii-line4.aln.toml`](kisii-line4.aln.toml) | `line-4` | 2,797.6 m | 2 |
| [`kisii-line5.aln.toml`](kisii-line5.aln.toml) | `line-5` | 5,487.8 m | 4 |
| [`kisii-line6.aln.toml`](kisii-line6.aln.toml) | `line-6` | 5,840.1 m | 4 |
| [`kisii-line7.aln.toml`](kisii-line7.aln.toml) | `line-7` | 3,686.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
