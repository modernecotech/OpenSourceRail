# Fallujah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`fallujah-line1.aln.toml`](fallujah-line1.aln.toml) | `line-1` | 17,953.2 m | 12 |
| [`fallujah-line10.aln.toml`](fallujah-line10.aln.toml) | `line-10` | 7,080.0 m | 5 |
| [`fallujah-line11.aln.toml`](fallujah-line11.aln.toml) | `line-11` | 2,190.8 m | 2 |
| [`fallujah-line12.aln.toml`](fallujah-line12.aln.toml) | `line-12` | 2,119.9 m | 2 |
| [`fallujah-line2.aln.toml`](fallujah-line2.aln.toml) | `line-2` | 11,307.7 m | 8 |
| [`fallujah-line3.aln.toml`](fallujah-line3.aln.toml) | `line-3` | 14,935.7 m | 10 |
| [`fallujah-line4.aln.toml`](fallujah-line4.aln.toml) | `line-4` | 2,820.0 m | 2 |
| [`fallujah-line5.aln.toml`](fallujah-line5.aln.toml) | `line-5` | 5,160.1 m | 5 |
| [`fallujah-line6.aln.toml`](fallujah-line6.aln.toml) | `line-6` | 2,601.7 m | 2 |
| [`fallujah-line7.aln.toml`](fallujah-line7.aln.toml) | `line-7` | 6,290.1 m | 4 |
| [`fallujah-line8.aln.toml`](fallujah-line8.aln.toml) | `line-8` | 6,958.0 m | 5 |
| [`fallujah-line9.aln.toml`](fallujah-line9.aln.toml) | `line-9` | 8,702.9 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
