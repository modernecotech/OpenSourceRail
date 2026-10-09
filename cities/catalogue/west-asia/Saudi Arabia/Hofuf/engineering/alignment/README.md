# Hofuf Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hofuf-line1.aln.toml`](hofuf-line1.aln.toml) | `line-1` | 23,534.5 m | 14 |
| [`hofuf-line10.aln.toml`](hofuf-line10.aln.toml) | `line-10` | 6,482.5 m | 5 |
| [`hofuf-line11.aln.toml`](hofuf-line11.aln.toml) | `line-11` | 2,200.2 m | 2 |
| [`hofuf-line12.aln.toml`](hofuf-line12.aln.toml) | `line-12` | 4,956.7 m | 4 |
| [`hofuf-line13.aln.toml`](hofuf-line13.aln.toml) | `line-13` | 8,728.7 m | 5 |
| [`hofuf-line14.aln.toml`](hofuf-line14.aln.toml) | `line-14` | 2,320.8 m | 3 |
| [`hofuf-line15.aln.toml`](hofuf-line15.aln.toml) | `line-15` | 3,140.1 m | 2 |
| [`hofuf-line16.aln.toml`](hofuf-line16.aln.toml) | `line-16` | 8,033.5 m | 7 |
| [`hofuf-line17.aln.toml`](hofuf-line17.aln.toml) | `line-17` | 2,076.8 m | 2 |
| [`hofuf-line18.aln.toml`](hofuf-line18.aln.toml) | `line-18` | 4,024.4 m | 3 |
| [`hofuf-line19.aln.toml`](hofuf-line19.aln.toml) | `line-19` | 2,076.5 m | 2 |
| [`hofuf-line2.aln.toml`](hofuf-line2.aln.toml) | `line-2` | 24,788.0 m | 14 |
| [`hofuf-line3.aln.toml`](hofuf-line3.aln.toml) | `line-3` | 23,957.3 m | 13 |
| [`hofuf-line4.aln.toml`](hofuf-line4.aln.toml) | `line-4` | 4,794.2 m | 4 |
| [`hofuf-line5.aln.toml`](hofuf-line5.aln.toml) | `line-5` | 4,754.2 m | 5 |
| [`hofuf-line6.aln.toml`](hofuf-line6.aln.toml) | `line-6` | 2,579.7 m | 2 |
| [`hofuf-line7.aln.toml`](hofuf-line7.aln.toml) | `line-7` | 3,171.6 m | 3 |
| [`hofuf-line8.aln.toml`](hofuf-line8.aln.toml) | `line-8` | 9,486.3 m | 6 |
| [`hofuf-line9.aln.toml`](hofuf-line9.aln.toml) | `line-9` | 2,011.4 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
