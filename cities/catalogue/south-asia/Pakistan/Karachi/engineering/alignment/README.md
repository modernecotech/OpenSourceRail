# Karachi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`karachi-line1.aln.toml`](karachi-line1.aln.toml) | `line-1` | 43,586.3 m | 31 |
| [`karachi-line10.aln.toml`](karachi-line10.aln.toml) | `line-10` | 6,745.2 m | 5 |
| [`karachi-line11.aln.toml`](karachi-line11.aln.toml) | `line-11` | 7,667.8 m | 6 |
| [`karachi-line12.aln.toml`](karachi-line12.aln.toml) | `line-12` | 8,610.1 m | 8 |
| [`karachi-line13.aln.toml`](karachi-line13.aln.toml) | `line-13` | 6,435.2 m | 8 |
| [`karachi-line14.aln.toml`](karachi-line14.aln.toml) | `line-14` | 8,079.9 m | 6 |
| [`karachi-line15.aln.toml`](karachi-line15.aln.toml) | `line-15` | 14,805.7 m | 12 |
| [`karachi-line16.aln.toml`](karachi-line16.aln.toml) | `line-16` | 9,530.7 m | 7 |
| [`karachi-line17.aln.toml`](karachi-line17.aln.toml) | `line-17` | 7,818.1 m | 6 |
| [`karachi-line18.aln.toml`](karachi-line18.aln.toml) | `line-18` | 9,147.4 m | 7 |
| [`karachi-line19.aln.toml`](karachi-line19.aln.toml) | `line-19` | 7,440.4 m | 8 |
| [`karachi-line2.aln.toml`](karachi-line2.aln.toml) | `line-2` | 34,179.0 m | 24 |
| [`karachi-line20.aln.toml`](karachi-line20.aln.toml) | `line-20` | 6,188.7 m | 4 |
| [`karachi-line21.aln.toml`](karachi-line21.aln.toml) | `line-21` | 12,508.9 m | 9 |
| [`karachi-line22.aln.toml`](karachi-line22.aln.toml) | `line-22` | 11,676.3 m | 8 |
| [`karachi-line23.aln.toml`](karachi-line23.aln.toml) | `line-23` | 7,062.5 m | 5 |
| [`karachi-line24.aln.toml`](karachi-line24.aln.toml) | `line-24` | 8,789.5 m | 5 |
| [`karachi-line25.aln.toml`](karachi-line25.aln.toml) | `line-25` | 9,150.2 m | 9 |
| [`karachi-line26.aln.toml`](karachi-line26.aln.toml) | `line-26` | 8,028.1 m | 6 |
| [`karachi-line27.aln.toml`](karachi-line27.aln.toml) | `line-27` | 12,258.5 m | 10 |
| [`karachi-line28.aln.toml`](karachi-line28.aln.toml) | `line-28` | 11,508.6 m | 9 |
| [`karachi-line29.aln.toml`](karachi-line29.aln.toml) | `line-29` | 6,584.9 m | 5 |
| [`karachi-line3.aln.toml`](karachi-line3.aln.toml) | `line-3` | 46,503.2 m | 33 |
| [`karachi-line30.aln.toml`](karachi-line30.aln.toml) | `line-30` | 6,315.6 m | 6 |
| [`karachi-line31.aln.toml`](karachi-line31.aln.toml) | `line-31` | 12,174.9 m | 7 |
| [`karachi-line32.aln.toml`](karachi-line32.aln.toml) | `line-32` | 10,194.7 m | 7 |
| [`karachi-line33.aln.toml`](karachi-line33.aln.toml) | `line-33` | 7,961.2 m | 7 |
| [`karachi-line4.aln.toml`](karachi-line4.aln.toml) | `line-4` | 27,803.6 m | 22 |
| [`karachi-line5.aln.toml`](karachi-line5.aln.toml) | `line-5` | 38,953.3 m | 23 |
| [`karachi-line6.aln.toml`](karachi-line6.aln.toml) | `line-6` | 39,978.1 m | 30 |
| [`karachi-line7.aln.toml`](karachi-line7.aln.toml) | `line-7` | 40,868.5 m | 31 |
| [`karachi-line8.aln.toml`](karachi-line8.aln.toml) | `line-8` | 47,253.2 m | 29 |
| [`karachi-line9.aln.toml`](karachi-line9.aln.toml) | `line-9` | 143,091.9 m | 97 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
