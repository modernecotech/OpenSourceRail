# Huye Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`huye-line1.aln.toml`](huye-line1.aln.toml) | `line-1` | 14,480.7 m | 10 |
| [`huye-line10.aln.toml`](huye-line10.aln.toml) | `line-10` | 3,930.2 m | 4 |
| [`huye-line11.aln.toml`](huye-line11.aln.toml) | `line-11` | 5,845.2 m | 4 |
| [`huye-line12.aln.toml`](huye-line12.aln.toml) | `line-12` | 4,299.1 m | 3 |
| [`huye-line2.aln.toml`](huye-line2.aln.toml) | `line-2` | 12,457.3 m | 10 |
| [`huye-line3.aln.toml`](huye-line3.aln.toml) | `line-3` | 11,985.4 m | 8 |
| [`huye-line4.aln.toml`](huye-line4.aln.toml) | `line-4` | 2,422.5 m | 2 |
| [`huye-line5.aln.toml`](huye-line5.aln.toml) | `line-5` | 4,732.7 m | 3 |
| [`huye-line6.aln.toml`](huye-line6.aln.toml) | `line-6` | 5,472.2 m | 4 |
| [`huye-line7.aln.toml`](huye-line7.aln.toml) | `line-7` | 4,909.0 m | 4 |
| [`huye-line8.aln.toml`](huye-line8.aln.toml) | `line-8` | 3,405.8 m | 3 |
| [`huye-line9.aln.toml`](huye-line9.aln.toml) | `line-9` | 2,461.3 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
