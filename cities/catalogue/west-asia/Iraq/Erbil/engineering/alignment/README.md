# Erbil Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`erbil-line1.aln.toml`](erbil-line1.aln.toml) | `line-1` | 29,468.6 m | 19 |
| [`erbil-line10.aln.toml`](erbil-line10.aln.toml) | `line-10` | 2,882.3 m | 2 |
| [`erbil-line11.aln.toml`](erbil-line11.aln.toml) | `line-11` | 3,495.4 m | 3 |
| [`erbil-line12.aln.toml`](erbil-line12.aln.toml) | `line-12` | 6,254.5 m | 4 |
| [`erbil-line13.aln.toml`](erbil-line13.aln.toml) | `line-13` | 8,085.2 m | 6 |
| [`erbil-line14.aln.toml`](erbil-line14.aln.toml) | `line-14` | 3,983.7 m | 3 |
| [`erbil-line15.aln.toml`](erbil-line15.aln.toml) | `line-15` | 3,827.0 m | 3 |
| [`erbil-line16.aln.toml`](erbil-line16.aln.toml) | `line-16` | 2,701.3 m | 2 |
| [`erbil-line17.aln.toml`](erbil-line17.aln.toml) | `line-17` | 2,652.0 m | 2 |
| [`erbil-line18.aln.toml`](erbil-line18.aln.toml) | `line-18` | 3,579.3 m | 3 |
| [`erbil-line19.aln.toml`](erbil-line19.aln.toml) | `line-19` | 4,958.8 m | 5 |
| [`erbil-line2.aln.toml`](erbil-line2.aln.toml) | `line-2` | 30,768.8 m | 19 |
| [`erbil-line20.aln.toml`](erbil-line20.aln.toml) | `line-20` | 11,479.0 m | 7 |
| [`erbil-line21.aln.toml`](erbil-line21.aln.toml) | `line-21` | 2,617.6 m | 2 |
| [`erbil-line22.aln.toml`](erbil-line22.aln.toml) | `line-22` | 4,739.1 m | 4 |
| [`erbil-line23.aln.toml`](erbil-line23.aln.toml) | `line-23` | 4,303.3 m | 3 |
| [`erbil-line24.aln.toml`](erbil-line24.aln.toml) | `line-24` | 6,406.8 m | 6 |
| [`erbil-line25.aln.toml`](erbil-line25.aln.toml) | `line-25` | 3,319.1 m | 3 |
| [`erbil-line26.aln.toml`](erbil-line26.aln.toml) | `line-26` | 2,930.2 m | 2 |
| [`erbil-line27.aln.toml`](erbil-line27.aln.toml) | `line-27` | 3,266.2 m | 4 |
| [`erbil-line28.aln.toml`](erbil-line28.aln.toml) | `line-28` | 4,325.6 m | 3 |
| [`erbil-line29.aln.toml`](erbil-line29.aln.toml) | `line-29` | 10,485.8 m | 8 |
| [`erbil-line3.aln.toml`](erbil-line3.aln.toml) | `line-3` | 20,012.8 m | 14 |
| [`erbil-line30.aln.toml`](erbil-line30.aln.toml) | `line-30` | 7,038.5 m | 5 |
| [`erbil-line31.aln.toml`](erbil-line31.aln.toml) | `line-31` | 4,181.9 m | 4 |
| [`erbil-line4.aln.toml`](erbil-line4.aln.toml) | `line-4` | 25,002.3 m | 17 |
| [`erbil-line5.aln.toml`](erbil-line5.aln.toml) | `line-5` | 18,001.9 m | 13 |
| [`erbil-line6.aln.toml`](erbil-line6.aln.toml) | `line-6` | 4,285.1 m | 3 |
| [`erbil-line7.aln.toml`](erbil-line7.aln.toml) | `line-7` | 2,628.5 m | 2 |
| [`erbil-line8.aln.toml`](erbil-line8.aln.toml) | `line-8` | 2,945.3 m | 4 |
| [`erbil-line9.aln.toml`](erbil-line9.aln.toml) | `line-9` | 4,863.9 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
