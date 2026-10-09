# Mymensingh Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mymensingh-line1.aln.toml`](mymensingh-line1.aln.toml) | `line-1` | 9,186.6 m | 6 |
| [`mymensingh-line10.aln.toml`](mymensingh-line10.aln.toml) | `line-10` | 3,545.0 m | 3 |
| [`mymensingh-line2.aln.toml`](mymensingh-line2.aln.toml) | `line-2` | 8,661.0 m | 7 |
| [`mymensingh-line3.aln.toml`](mymensingh-line3.aln.toml) | `line-3` | 19,315.5 m | 13 |
| [`mymensingh-line4.aln.toml`](mymensingh-line4.aln.toml) | `line-4` | 2,389.9 m | 3 |
| [`mymensingh-line5.aln.toml`](mymensingh-line5.aln.toml) | `line-5` | 7,561.2 m | 5 |
| [`mymensingh-line6.aln.toml`](mymensingh-line6.aln.toml) | `line-6` | 5,411.9 m | 4 |
| [`mymensingh-line7.aln.toml`](mymensingh-line7.aln.toml) | `line-7` | 5,566.3 m | 4 |
| [`mymensingh-line8.aln.toml`](mymensingh-line8.aln.toml) | `line-8` | 8,730.4 m | 6 |
| [`mymensingh-line9.aln.toml`](mymensingh-line9.aln.toml) | `line-9` | 3,798.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
