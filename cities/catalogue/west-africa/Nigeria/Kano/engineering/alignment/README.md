# Kano Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kano-line1.aln.toml`](kano-line1.aln.toml) | `line-1` | 47,483.2 m | 17 |
| [`kano-line10.aln.toml`](kano-line10.aln.toml) | `line-10` | 10,226.8 m | 4 |
| [`kano-line11.aln.toml`](kano-line11.aln.toml) | `line-11` | 6,842.4 m | 3 |
| [`kano-line12.aln.toml`](kano-line12.aln.toml) | `line-12` | 9,942.2 m | 4 |
| [`kano-line13.aln.toml`](kano-line13.aln.toml) | `line-13` | 9,597.1 m | 4 |
| [`kano-line14.aln.toml`](kano-line14.aln.toml) | `line-14` | 11,262.1 m | 4 |
| [`kano-line2.aln.toml`](kano-line2.aln.toml) | `line-2` | 49,525.0 m | 18 |
| [`kano-line3.aln.toml`](kano-line3.aln.toml) | `line-3` | 48,454.7 m | 19 |
| [`kano-line4.aln.toml`](kano-line4.aln.toml) | `line-4` | 35,468.6 m | 13 |
| [`kano-line5.aln.toml`](kano-line5.aln.toml) | `line-5` | 36,720.1 m | 13 |
| [`kano-line6.aln.toml`](kano-line6.aln.toml) | `line-6` | 30,314.6 m | 12 |
| [`kano-line7.aln.toml`](kano-line7.aln.toml) | `line-7` | 50,092.9 m | 17 |
| [`kano-line8.aln.toml`](kano-line8.aln.toml) | `line-8` | 44,653.6 m | 17 |
| [`kano-line9.aln.toml`](kano-line9.aln.toml) | `line-9` | 83,165.4 m | 23 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
