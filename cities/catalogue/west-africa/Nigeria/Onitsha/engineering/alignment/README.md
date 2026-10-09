# Onitsha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`onitsha-line1.aln.toml`](onitsha-line1.aln.toml) | `line-1` | 25,557.7 m | 15 |
| [`onitsha-line10.aln.toml`](onitsha-line10.aln.toml) | `line-10` | 4,538.7 m | 3 |
| [`onitsha-line11.aln.toml`](onitsha-line11.aln.toml) | `line-11` | 6,665.8 m | 4 |
| [`onitsha-line12.aln.toml`](onitsha-line12.aln.toml) | `line-12` | 7,892.9 m | 5 |
| [`onitsha-line13.aln.toml`](onitsha-line13.aln.toml) | `line-13` | 7,453.6 m | 5 |
| [`onitsha-line14.aln.toml`](onitsha-line14.aln.toml) | `line-14` | 6,479.8 m | 4 |
| [`onitsha-line15.aln.toml`](onitsha-line15.aln.toml) | `line-15` | 6,963.8 m | 5 |
| [`onitsha-line16.aln.toml`](onitsha-line16.aln.toml) | `line-16` | 6,479.1 m | 4 |
| [`onitsha-line17.aln.toml`](onitsha-line17.aln.toml) | `line-17` | 5,439.3 m | 5 |
| [`onitsha-line18.aln.toml`](onitsha-line18.aln.toml) | `line-18` | 4,103.3 m | 3 |
| [`onitsha-line19.aln.toml`](onitsha-line19.aln.toml) | `line-19` | 5,140.4 m | 4 |
| [`onitsha-line2.aln.toml`](onitsha-line2.aln.toml) | `line-2` | 34,873.5 m | 25 |
| [`onitsha-line20.aln.toml`](onitsha-line20.aln.toml) | `line-20` | 5,572.1 m | 4 |
| [`onitsha-line21.aln.toml`](onitsha-line21.aln.toml) | `line-21` | 10,167.2 m | 7 |
| [`onitsha-line22.aln.toml`](onitsha-line22.aln.toml) | `line-22` | 6,879.3 m | 6 |
| [`onitsha-line23.aln.toml`](onitsha-line23.aln.toml) | `line-23` | 8,358.8 m | 6 |
| [`onitsha-line24.aln.toml`](onitsha-line24.aln.toml) | `line-24` | 8,174.3 m | 7 |
| [`onitsha-line25.aln.toml`](onitsha-line25.aln.toml) | `line-25` | 11,650.8 m | 8 |
| [`onitsha-line26.aln.toml`](onitsha-line26.aln.toml) | `line-26` | 6,448.2 m | 5 |
| [`onitsha-line27.aln.toml`](onitsha-line27.aln.toml) | `line-27` | 6,640.3 m | 4 |
| [`onitsha-line28.aln.toml`](onitsha-line28.aln.toml) | `line-28` | 10,991.6 m | 8 |
| [`onitsha-line29.aln.toml`](onitsha-line29.aln.toml) | `line-29` | 6,618.5 m | 5 |
| [`onitsha-line3.aln.toml`](onitsha-line3.aln.toml) | `line-3` | 29,239.7 m | 22 |
| [`onitsha-line30.aln.toml`](onitsha-line30.aln.toml) | `line-30` | 14,535.0 m | 10 |
| [`onitsha-line31.aln.toml`](onitsha-line31.aln.toml) | `line-31` | 5,733.8 m | 4 |
| [`onitsha-line32.aln.toml`](onitsha-line32.aln.toml) | `line-32` | 4,965.0 m | 4 |
| [`onitsha-line33.aln.toml`](onitsha-line33.aln.toml) | `line-33` | 5,881.8 m | 4 |
| [`onitsha-line4.aln.toml`](onitsha-line4.aln.toml) | `line-4` | 15,015.6 m | 13 |
| [`onitsha-line5.aln.toml`](onitsha-line5.aln.toml) | `line-5` | 90,747.3 m | 54 |
| [`onitsha-line6.aln.toml`](onitsha-line6.aln.toml) | `line-6` | 4,455.9 m | 3 |
| [`onitsha-line7.aln.toml`](onitsha-line7.aln.toml) | `line-7` | 4,100.1 m | 3 |
| [`onitsha-line8.aln.toml`](onitsha-line8.aln.toml) | `line-8` | 5,610.4 m | 4 |
| [`onitsha-line9.aln.toml`](onitsha-line9.aln.toml) | `line-9` | 6,803.5 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
