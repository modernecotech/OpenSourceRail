# Arusha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`arusha-line1.aln.toml`](arusha-line1.aln.toml) | `line-1` | 14,281.4 m | 8 |
| [`arusha-line10.aln.toml`](arusha-line10.aln.toml) | `line-10` | 2,334.5 m | 2 |
| [`arusha-line11.aln.toml`](arusha-line11.aln.toml) | `line-11` | 2,308.5 m | 3 |
| [`arusha-line12.aln.toml`](arusha-line12.aln.toml) | `line-12` | 4,832.4 m | 4 |
| [`arusha-line13.aln.toml`](arusha-line13.aln.toml) | `line-13` | 3,147.7 m | 2 |
| [`arusha-line14.aln.toml`](arusha-line14.aln.toml) | `line-14` | 3,307.4 m | 3 |
| [`arusha-line15.aln.toml`](arusha-line15.aln.toml) | `line-15` | 4,038.5 m | 3 |
| [`arusha-line16.aln.toml`](arusha-line16.aln.toml) | `line-16` | 2,009.9 m | 2 |
| [`arusha-line17.aln.toml`](arusha-line17.aln.toml) | `line-17` | 7,925.5 m | 5 |
| [`arusha-line18.aln.toml`](arusha-line18.aln.toml) | `line-18` | 4,791.9 m | 4 |
| [`arusha-line2.aln.toml`](arusha-line2.aln.toml) | `line-2` | 17,090.5 m | 13 |
| [`arusha-line3.aln.toml`](arusha-line3.aln.toml) | `line-3` | 22,907.6 m | 15 |
| [`arusha-line4.aln.toml`](arusha-line4.aln.toml) | `line-4` | 2,699.9 m | 2 |
| [`arusha-line5.aln.toml`](arusha-line5.aln.toml) | `line-5` | 3,738.5 m | 3 |
| [`arusha-line6.aln.toml`](arusha-line6.aln.toml) | `line-6` | 2,331.4 m | 2 |
| [`arusha-line7.aln.toml`](arusha-line7.aln.toml) | `line-7` | 3,192.2 m | 3 |
| [`arusha-line8.aln.toml`](arusha-line8.aln.toml) | `line-8` | 2,739.7 m | 2 |
| [`arusha-line9.aln.toml`](arusha-line9.aln.toml) | `line-9` | 3,118.2 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
