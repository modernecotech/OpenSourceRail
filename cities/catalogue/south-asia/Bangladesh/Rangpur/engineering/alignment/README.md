# Rangpur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rangpur-line1.aln.toml`](rangpur-line1.aln.toml) | `line-1` | 11,635.2 m | 8 |
| [`rangpur-line10.aln.toml`](rangpur-line10.aln.toml) | `line-10` | 3,499.4 m | 3 |
| [`rangpur-line11.aln.toml`](rangpur-line11.aln.toml) | `line-11` | 2,739.9 m | 2 |
| [`rangpur-line2.aln.toml`](rangpur-line2.aln.toml) | `line-2` | 15,221.6 m | 9 |
| [`rangpur-line3.aln.toml`](rangpur-line3.aln.toml) | `line-3` | 10,590.8 m | 8 |
| [`rangpur-line4.aln.toml`](rangpur-line4.aln.toml) | `line-4` | 2,414.8 m | 2 |
| [`rangpur-line5.aln.toml`](rangpur-line5.aln.toml) | `line-5` | 5,507.6 m | 4 |
| [`rangpur-line6.aln.toml`](rangpur-line6.aln.toml) | `line-6` | 5,024.5 m | 3 |
| [`rangpur-line7.aln.toml`](rangpur-line7.aln.toml) | `line-7` | 6,009.8 m | 4 |
| [`rangpur-line8.aln.toml`](rangpur-line8.aln.toml) | `line-8` | 5,753.9 m | 4 |
| [`rangpur-line9.aln.toml`](rangpur-line9.aln.toml) | `line-9` | 6,146.2 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
