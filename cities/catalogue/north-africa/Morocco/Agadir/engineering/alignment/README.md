# Agadir Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`agadir-line1.aln.toml`](agadir-line1.aln.toml) | `line-1` | 24,393.6 m | 13 |
| [`agadir-line10.aln.toml`](agadir-line10.aln.toml) | `line-10` | 2,359.7 m | 2 |
| [`agadir-line2.aln.toml`](agadir-line2.aln.toml) | `line-2` | 24,469.3 m | 17 |
| [`agadir-line3.aln.toml`](agadir-line3.aln.toml) | `line-3` | 24,337.2 m | 14 |
| [`agadir-line4.aln.toml`](agadir-line4.aln.toml) | `line-4` | 7,237.5 m | 5 |
| [`agadir-line5.aln.toml`](agadir-line5.aln.toml) | `line-5` | 2,287.4 m | 2 |
| [`agadir-line6.aln.toml`](agadir-line6.aln.toml) | `line-6` | 2,926.8 m | 3 |
| [`agadir-line7.aln.toml`](agadir-line7.aln.toml) | `line-7` | 3,081.9 m | 3 |
| [`agadir-line8.aln.toml`](agadir-line8.aln.toml) | `line-8` | 2,392.2 m | 2 |
| [`agadir-line9.aln.toml`](agadir-line9.aln.toml) | `line-9` | 2,941.1 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
