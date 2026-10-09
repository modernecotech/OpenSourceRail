# Herat Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`herat-line1.aln.toml`](herat-line1.aln.toml) | `line-1` | 9,206.6 m | 6 |
| [`herat-line10.aln.toml`](herat-line10.aln.toml) | `line-10` | 4,695.6 m | 3 |
| [`herat-line2.aln.toml`](herat-line2.aln.toml) | `line-2` | 10,284.0 m | 6 |
| [`herat-line3.aln.toml`](herat-line3.aln.toml) | `line-3` | 20,682.9 m | 13 |
| [`herat-line4.aln.toml`](herat-line4.aln.toml) | `line-4` | 2,321.1 m | 2 |
| [`herat-line5.aln.toml`](herat-line5.aln.toml) | `line-5` | 6,616.4 m | 4 |
| [`herat-line6.aln.toml`](herat-line6.aln.toml) | `line-6` | 3,301.9 m | 3 |
| [`herat-line7.aln.toml`](herat-line7.aln.toml) | `line-7` | 8,447.0 m | 5 |
| [`herat-line8.aln.toml`](herat-line8.aln.toml) | `line-8` | 7,126.7 m | 5 |
| [`herat-line9.aln.toml`](herat-line9.aln.toml) | `line-9` | 7,102.4 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
