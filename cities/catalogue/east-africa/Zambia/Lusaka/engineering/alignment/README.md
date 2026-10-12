# Lusaka Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lusaka-line1.aln.toml`](lusaka-line1.aln.toml) | `line-1` | 33,608.0 m | 11 |
| [`lusaka-line10.aln.toml`](lusaka-line10.aln.toml) | `line-10` | 5,651.4 m | 2 |
| [`lusaka-line11.aln.toml`](lusaka-line11.aln.toml) | `line-11` | 5,738.5 m | 2 |
| [`lusaka-line12.aln.toml`](lusaka-line12.aln.toml) | `line-12` | 7,550.1 m | 3 |
| [`lusaka-line2.aln.toml`](lusaka-line2.aln.toml) | `line-2` | 29,188.9 m | 11 |
| [`lusaka-line3.aln.toml`](lusaka-line3.aln.toml) | `line-3` | 25,478.2 m | 11 |
| [`lusaka-line4.aln.toml`](lusaka-line4.aln.toml) | `line-4` | 18,541.3 m | 13 |
| [`lusaka-line5.aln.toml`](lusaka-line5.aln.toml) | `line-5` | 29,095.2 m | 10 |
| [`lusaka-line6.aln.toml`](lusaka-line6.aln.toml) | `line-6` | 27,657.3 m | 11 |
| [`lusaka-line7.aln.toml`](lusaka-line7.aln.toml) | `line-7` | 28,898.6 m | 8 |
| [`lusaka-line8.aln.toml`](lusaka-line8.aln.toml) | `line-8` | 74,945.1 m | 28 |
| [`lusaka-line9.aln.toml`](lusaka-line9.aln.toml) | `line-9` | 6,933.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
