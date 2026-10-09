# Kirkuk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kirkuk-line1.aln.toml`](kirkuk-line1.aln.toml) | `line-1` | 17,500.3 m | 13 |
| [`kirkuk-line10.aln.toml`](kirkuk-line10.aln.toml) | `line-10` | 8,009.8 m | 6 |
| [`kirkuk-line11.aln.toml`](kirkuk-line11.aln.toml) | `line-11` | 14,879.9 m | 10 |
| [`kirkuk-line12.aln.toml`](kirkuk-line12.aln.toml) | `line-12` | 8,580.0 m | 5 |
| [`kirkuk-line13.aln.toml`](kirkuk-line13.aln.toml) | `line-13` | 8,942.7 m | 6 |
| [`kirkuk-line14.aln.toml`](kirkuk-line14.aln.toml) | `line-14` | 7,346.6 m | 5 |
| [`kirkuk-line15.aln.toml`](kirkuk-line15.aln.toml) | `line-15` | 9,941.8 m | 6 |
| [`kirkuk-line16.aln.toml`](kirkuk-line16.aln.toml) | `line-16` | 4,737.5 m | 3 |
| [`kirkuk-line17.aln.toml`](kirkuk-line17.aln.toml) | `line-17` | 4,260.0 m | 3 |
| [`kirkuk-line18.aln.toml`](kirkuk-line18.aln.toml) | `line-18` | 5,395.0 m | 4 |
| [`kirkuk-line2.aln.toml`](kirkuk-line2.aln.toml) | `line-2` | 17,328.6 m | 13 |
| [`kirkuk-line3.aln.toml`](kirkuk-line3.aln.toml) | `line-3` | 16,243.5 m | 10 |
| [`kirkuk-line4.aln.toml`](kirkuk-line4.aln.toml) | `line-4` | 22,647.9 m | 14 |
| [`kirkuk-line5.aln.toml`](kirkuk-line5.aln.toml) | `line-5` | 52,399.8 m | 35 |
| [`kirkuk-line6.aln.toml`](kirkuk-line6.aln.toml) | `line-6` | 3,508.2 m | 3 |
| [`kirkuk-line7.aln.toml`](kirkuk-line7.aln.toml) | `line-7` | 8,591.3 m | 7 |
| [`kirkuk-line8.aln.toml`](kirkuk-line8.aln.toml) | `line-8` | 2,928.2 m | 2 |
| [`kirkuk-line9.aln.toml`](kirkuk-line9.aln.toml) | `line-9` | 6,126.9 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
