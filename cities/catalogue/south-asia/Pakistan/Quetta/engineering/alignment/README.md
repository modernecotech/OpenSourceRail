# Quetta Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`quetta-line1.aln.toml`](quetta-line1.aln.toml) | `line-1` | 20,556.7 m | 7 |
| [`quetta-line2.aln.toml`](quetta-line2.aln.toml) | `line-2` | 27,221.5 m | 8 |
| [`quetta-line3.aln.toml`](quetta-line3.aln.toml) | `line-3` | 14,366.7 m | 5 |
| [`quetta-line4.aln.toml`](quetta-line4.aln.toml) | `line-4` | 54,924.4 m | 17 |
| [`quetta-line5.aln.toml`](quetta-line5.aln.toml) | `line-5` | 4,777.6 m | 2 |
| [`quetta-line6.aln.toml`](quetta-line6.aln.toml) | `line-6` | 6,962.4 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
