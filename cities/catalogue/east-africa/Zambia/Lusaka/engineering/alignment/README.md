# Lusaka Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lusaka-line1.aln.toml`](lusaka-line1.aln.toml) | `line-1` | 33,608.0 m | 20 |
| [`lusaka-line10.aln.toml`](lusaka-line10.aln.toml) | `line-10` | 6,913.0 m | 6 |
| [`lusaka-line11.aln.toml`](lusaka-line11.aln.toml) | `line-11` | 5,128.1 m | 5 |
| [`lusaka-line12.aln.toml`](lusaka-line12.aln.toml) | `line-12` | 5,736.5 m | 4 |
| [`lusaka-line13.aln.toml`](lusaka-line13.aln.toml) | `line-13` | 7,225.8 m | 6 |
| [`lusaka-line14.aln.toml`](lusaka-line14.aln.toml) | `line-14` | 4,996.8 m | 4 |
| [`lusaka-line15.aln.toml`](lusaka-line15.aln.toml) | `line-15` | 5,049.3 m | 3 |
| [`lusaka-line16.aln.toml`](lusaka-line16.aln.toml) | `line-16` | 5,584.8 m | 5 |
| [`lusaka-line17.aln.toml`](lusaka-line17.aln.toml) | `line-17` | 6,059.7 m | 4 |
| [`lusaka-line18.aln.toml`](lusaka-line18.aln.toml) | `line-18` | 6,005.8 m | 5 |
| [`lusaka-line19.aln.toml`](lusaka-line19.aln.toml) | `line-19` | 7,036.5 m | 5 |
| [`lusaka-line2.aln.toml`](lusaka-line2.aln.toml) | `line-2` | 21,349.7 m | 14 |
| [`lusaka-line20.aln.toml`](lusaka-line20.aln.toml) | `line-20` | 5,210.7 m | 3 |
| [`lusaka-line21.aln.toml`](lusaka-line21.aln.toml) | `line-21` | 6,267.8 m | 6 |
| [`lusaka-line22.aln.toml`](lusaka-line22.aln.toml) | `line-22` | 6,662.4 m | 4 |
| [`lusaka-line23.aln.toml`](lusaka-line23.aln.toml) | `line-23` | 6,367.7 m | 6 |
| [`lusaka-line24.aln.toml`](lusaka-line24.aln.toml) | `line-24` | 6,914.7 m | 5 |
| [`lusaka-line25.aln.toml`](lusaka-line25.aln.toml) | `line-25` | 16,174.8 m | 10 |
| [`lusaka-line26.aln.toml`](lusaka-line26.aln.toml) | `line-26` | 15,095.5 m | 11 |
| [`lusaka-line27.aln.toml`](lusaka-line27.aln.toml) | `line-27` | 8,847.2 m | 6 |
| [`lusaka-line28.aln.toml`](lusaka-line28.aln.toml) | `line-28` | 5,878.4 m | 4 |
| [`lusaka-line29.aln.toml`](lusaka-line29.aln.toml) | `line-29` | 5,766.1 m | 5 |
| [`lusaka-line3.aln.toml`](lusaka-line3.aln.toml) | `line-3` | 25,478.2 m | 18 |
| [`lusaka-line30.aln.toml`](lusaka-line30.aln.toml) | `line-30` | 5,247.2 m | 4 |
| [`lusaka-line31.aln.toml`](lusaka-line31.aln.toml) | `line-31` | 5,304.8 m | 5 |
| [`lusaka-line32.aln.toml`](lusaka-line32.aln.toml) | `line-32` | 5,676.1 m | 5 |
| [`lusaka-line4.aln.toml`](lusaka-line4.aln.toml) | `line-4` | 17,915.0 m | 13 |
| [`lusaka-line5.aln.toml`](lusaka-line5.aln.toml) | `line-5` | 20,410.4 m | 13 |
| [`lusaka-line6.aln.toml`](lusaka-line6.aln.toml) | `line-6` | 27,657.3 m | 20 |
| [`lusaka-line7.aln.toml`](lusaka-line7.aln.toml) | `line-7` | 25,123.9 m | 18 |
| [`lusaka-line8.aln.toml`](lusaka-line8.aln.toml) | `line-8` | 69,247.5 m | 50 |
| [`lusaka-line9.aln.toml`](lusaka-line9.aln.toml) | `line-9` | 5,865.2 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
