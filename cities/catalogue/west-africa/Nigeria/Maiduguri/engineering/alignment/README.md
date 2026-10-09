# Maiduguri Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maiduguri-line1.aln.toml`](maiduguri-line1.aln.toml) | `line-1` | 24,636.3 m | 17 |
| [`maiduguri-line10.aln.toml`](maiduguri-line10.aln.toml) | `line-10` | 6,133.9 m | 4 |
| [`maiduguri-line11.aln.toml`](maiduguri-line11.aln.toml) | `line-11` | 7,035.5 m | 7 |
| [`maiduguri-line12.aln.toml`](maiduguri-line12.aln.toml) | `line-12` | 3,854.5 m | 4 |
| [`maiduguri-line13.aln.toml`](maiduguri-line13.aln.toml) | `line-13` | 5,649.0 m | 6 |
| [`maiduguri-line14.aln.toml`](maiduguri-line14.aln.toml) | `line-14` | 3,453.6 m | 3 |
| [`maiduguri-line15.aln.toml`](maiduguri-line15.aln.toml) | `line-15` | 5,955.4 m | 4 |
| [`maiduguri-line16.aln.toml`](maiduguri-line16.aln.toml) | `line-16` | 4,761.6 m | 4 |
| [`maiduguri-line17.aln.toml`](maiduguri-line17.aln.toml) | `line-17` | 3,231.6 m | 3 |
| [`maiduguri-line18.aln.toml`](maiduguri-line18.aln.toml) | `line-18` | 8,260.2 m | 6 |
| [`maiduguri-line19.aln.toml`](maiduguri-line19.aln.toml) | `line-19` | 6,574.0 m | 4 |
| [`maiduguri-line2.aln.toml`](maiduguri-line2.aln.toml) | `line-2` | 21,598.4 m | 17 |
| [`maiduguri-line20.aln.toml`](maiduguri-line20.aln.toml) | `line-20` | 8,984.7 m | 6 |
| [`maiduguri-line21.aln.toml`](maiduguri-line21.aln.toml) | `line-21` | 3,823.3 m | 3 |
| [`maiduguri-line22.aln.toml`](maiduguri-line22.aln.toml) | `line-22` | 3,274.5 m | 3 |
| [`maiduguri-line23.aln.toml`](maiduguri-line23.aln.toml) | `line-23` | 10,092.2 m | 7 |
| [`maiduguri-line3.aln.toml`](maiduguri-line3.aln.toml) | `line-3` | 26,319.0 m | 17 |
| [`maiduguri-line4.aln.toml`](maiduguri-line4.aln.toml) | `line-4` | 25,261.3 m | 15 |
| [`maiduguri-line5.aln.toml`](maiduguri-line5.aln.toml) | `line-5` | 59,776.4 m | 40 |
| [`maiduguri-line6.aln.toml`](maiduguri-line6.aln.toml) | `line-6` | 3,168.5 m | 3 |
| [`maiduguri-line7.aln.toml`](maiduguri-line7.aln.toml) | `line-7` | 5,723.8 m | 6 |
| [`maiduguri-line8.aln.toml`](maiduguri-line8.aln.toml) | `line-8` | 5,321.1 m | 4 |
| [`maiduguri-line9.aln.toml`](maiduguri-line9.aln.toml) | `line-9` | 5,175.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
