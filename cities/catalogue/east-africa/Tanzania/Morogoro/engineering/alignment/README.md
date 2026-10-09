# Morogoro Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`morogoro-line1.aln.toml`](morogoro-line1.aln.toml) | `line-1` | 15,331.4 m | 11 |
| [`morogoro-line10.aln.toml`](morogoro-line10.aln.toml) | `line-10` | 5,837.2 m | 4 |
| [`morogoro-line11.aln.toml`](morogoro-line11.aln.toml) | `line-11` | 7,621.5 m | 5 |
| [`morogoro-line12.aln.toml`](morogoro-line12.aln.toml) | `line-12` | 2,272.8 m | 2 |
| [`morogoro-line2.aln.toml`](morogoro-line2.aln.toml) | `line-2` | 15,140.7 m | 10 |
| [`morogoro-line3.aln.toml`](morogoro-line3.aln.toml) | `line-3` | 12,970.0 m | 8 |
| [`morogoro-line4.aln.toml`](morogoro-line4.aln.toml) | `line-4` | 2,050.8 m | 2 |
| [`morogoro-line5.aln.toml`](morogoro-line5.aln.toml) | `line-5` | 3,929.6 m | 4 |
| [`morogoro-line6.aln.toml`](morogoro-line6.aln.toml) | `line-6` | 4,213.0 m | 3 |
| [`morogoro-line7.aln.toml`](morogoro-line7.aln.toml) | `line-7` | 6,030.4 m | 5 |
| [`morogoro-line8.aln.toml`](morogoro-line8.aln.toml) | `line-8` | 7,197.2 m | 4 |
| [`morogoro-line9.aln.toml`](morogoro-line9.aln.toml) | `line-9` | 3,262.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
