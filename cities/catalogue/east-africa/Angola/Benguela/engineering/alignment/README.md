# Benguela Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`benguela-line1.aln.toml`](benguela-line1.aln.toml) | `line-1` | 20,498.6 m | 10 |
| [`benguela-line10.aln.toml`](benguela-line10.aln.toml) | `line-10` | 6,586.5 m | 4 |
| [`benguela-line11.aln.toml`](benguela-line11.aln.toml) | `line-11` | 2,278.5 m | 2 |
| [`benguela-line12.aln.toml`](benguela-line12.aln.toml) | `line-12` | 7,362.1 m | 5 |
| [`benguela-line13.aln.toml`](benguela-line13.aln.toml) | `line-13` | 5,480.4 m | 4 |
| [`benguela-line14.aln.toml`](benguela-line14.aln.toml) | `line-14` | 2,230.2 m | 2 |
| [`benguela-line2.aln.toml`](benguela-line2.aln.toml) | `line-2` | 16,590.1 m | 9 |
| [`benguela-line3.aln.toml`](benguela-line3.aln.toml) | `line-3` | 10,842.5 m | 8 |
| [`benguela-line4.aln.toml`](benguela-line4.aln.toml) | `line-4` | 4,982.2 m | 4 |
| [`benguela-line5.aln.toml`](benguela-line5.aln.toml) | `line-5` | 3,341.7 m | 3 |
| [`benguela-line6.aln.toml`](benguela-line6.aln.toml) | `line-6` | 2,621.1 m | 2 |
| [`benguela-line7.aln.toml`](benguela-line7.aln.toml) | `line-7` | 3,382.7 m | 3 |
| [`benguela-line8.aln.toml`](benguela-line8.aln.toml) | `line-8` | 2,923.3 m | 3 |
| [`benguela-line9.aln.toml`](benguela-line9.aln.toml) | `line-9` | 5,664.4 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
