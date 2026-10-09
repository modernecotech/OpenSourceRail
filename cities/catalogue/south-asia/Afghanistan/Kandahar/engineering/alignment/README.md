# Kandahar Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kandahar-line1.aln.toml`](kandahar-line1.aln.toml) | `line-1` | 17,728.2 m | 12 |
| [`kandahar-line10.aln.toml`](kandahar-line10.aln.toml) | `line-10` | 7,373.2 m | 5 |
| [`kandahar-line11.aln.toml`](kandahar-line11.aln.toml) | `line-11` | 4,113.6 m | 3 |
| [`kandahar-line12.aln.toml`](kandahar-line12.aln.toml) | `line-12` | 2,411.1 m | 3 |
| [`kandahar-line2.aln.toml`](kandahar-line2.aln.toml) | `line-2` | 14,053.6 m | 9 |
| [`kandahar-line3.aln.toml`](kandahar-line3.aln.toml) | `line-3` | 10,915.1 m | 8 |
| [`kandahar-line4.aln.toml`](kandahar-line4.aln.toml) | `line-4` | 5,067.6 m | 4 |
| [`kandahar-line5.aln.toml`](kandahar-line5.aln.toml) | `line-5` | 2,128.5 m | 3 |
| [`kandahar-line6.aln.toml`](kandahar-line6.aln.toml) | `line-6` | 6,026.1 m | 4 |
| [`kandahar-line7.aln.toml`](kandahar-line7.aln.toml) | `line-7` | 3,519.9 m | 3 |
| [`kandahar-line8.aln.toml`](kandahar-line8.aln.toml) | `line-8` | 5,193.6 m | 4 |
| [`kandahar-line9.aln.toml`](kandahar-line9.aln.toml) | `line-9` | 5,403.2 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
