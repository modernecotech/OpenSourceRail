# Jalalabad-Af Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jalalabad-af-line1.aln.toml`](jalalabad-af-line1.aln.toml) | `line-1` | 8,245.1 m | 6 |
| [`jalalabad-af-line10.aln.toml`](jalalabad-af-line10.aln.toml) | `line-10` | 7,829.7 m | 5 |
| [`jalalabad-af-line2.aln.toml`](jalalabad-af-line2.aln.toml) | `line-2` | 20,383.8 m | 14 |
| [`jalalabad-af-line3.aln.toml`](jalalabad-af-line3.aln.toml) | `line-3` | 11,942.8 m | 8 |
| [`jalalabad-af-line4.aln.toml`](jalalabad-af-line4.aln.toml) | `line-4` | 2,769.4 m | 3 |
| [`jalalabad-af-line5.aln.toml`](jalalabad-af-line5.aln.toml) | `line-5` | 3,504.2 m | 3 |
| [`jalalabad-af-line6.aln.toml`](jalalabad-af-line6.aln.toml) | `line-6` | 3,448.8 m | 3 |
| [`jalalabad-af-line7.aln.toml`](jalalabad-af-line7.aln.toml) | `line-7` | 7,902.5 m | 6 |
| [`jalalabad-af-line8.aln.toml`](jalalabad-af-line8.aln.toml) | `line-8` | 6,802.4 m | 5 |
| [`jalalabad-af-line9.aln.toml`](jalalabad-af-line9.aln.toml) | `line-9` | 6,114.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
