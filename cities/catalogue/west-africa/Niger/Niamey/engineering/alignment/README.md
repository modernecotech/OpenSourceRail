# Niamey Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`niamey-line1.aln.toml`](niamey-line1.aln.toml) | `line-1` | 22,676.3 m | 19 |
| [`niamey-line10.aln.toml`](niamey-line10.aln.toml) | `line-10` | 8,879.5 m | 6 |
| [`niamey-line11.aln.toml`](niamey-line11.aln.toml) | `line-11` | 5,022.2 m | 6 |
| [`niamey-line12.aln.toml`](niamey-line12.aln.toml) | `line-12` | 5,568.4 m | 4 |
| [`niamey-line13.aln.toml`](niamey-line13.aln.toml) | `line-13` | 3,391.1 m | 3 |
| [`niamey-line14.aln.toml`](niamey-line14.aln.toml) | `line-14` | 3,379.1 m | 3 |
| [`niamey-line15.aln.toml`](niamey-line15.aln.toml) | `line-15` | 4,063.6 m | 6 |
| [`niamey-line16.aln.toml`](niamey-line16.aln.toml) | `line-16` | 8,867.8 m | 5 |
| [`niamey-line17.aln.toml`](niamey-line17.aln.toml) | `line-17` | 2,833.9 m | 2 |
| [`niamey-line18.aln.toml`](niamey-line18.aln.toml) | `line-18` | 3,961.6 m | 5 |
| [`niamey-line19.aln.toml`](niamey-line19.aln.toml) | `line-19` | 4,438.7 m | 4 |
| [`niamey-line2.aln.toml`](niamey-line2.aln.toml) | `line-2` | 15,805.5 m | 11 |
| [`niamey-line20.aln.toml`](niamey-line20.aln.toml) | `line-20` | 6,489.4 m | 6 |
| [`niamey-line21.aln.toml`](niamey-line21.aln.toml) | `line-21` | 3,697.1 m | 3 |
| [`niamey-line22.aln.toml`](niamey-line22.aln.toml) | `line-22` | 3,852.0 m | 3 |
| [`niamey-line23.aln.toml`](niamey-line23.aln.toml) | `line-23` | 5,115.3 m | 3 |
| [`niamey-line24.aln.toml`](niamey-line24.aln.toml) | `line-24` | 3,496.7 m | 3 |
| [`niamey-line25.aln.toml`](niamey-line25.aln.toml) | `line-25` | 8,007.6 m | 5 |
| [`niamey-line26.aln.toml`](niamey-line26.aln.toml) | `line-26` | 8,483.7 m | 6 |
| [`niamey-line27.aln.toml`](niamey-line27.aln.toml) | `line-27` | 6,298.7 m | 5 |
| [`niamey-line28.aln.toml`](niamey-line28.aln.toml) | `line-28` | 7,427.6 m | 5 |
| [`niamey-line29.aln.toml`](niamey-line29.aln.toml) | `line-29` | 6,560.0 m | 5 |
| [`niamey-line3.aln.toml`](niamey-line3.aln.toml) | `line-3` | 14,193.0 m | 15 |
| [`niamey-line30.aln.toml`](niamey-line30.aln.toml) | `line-30` | 3,740.1 m | 4 |
| [`niamey-line31.aln.toml`](niamey-line31.aln.toml) | `line-31` | 3,990.1 m | 3 |
| [`niamey-line32.aln.toml`](niamey-line32.aln.toml) | `line-32` | 10,172.7 m | 7 |
| [`niamey-line33.aln.toml`](niamey-line33.aln.toml) | `line-33` | 3,207.4 m | 3 |
| [`niamey-line4.aln.toml`](niamey-line4.aln.toml) | `line-4` | 19,280.3 m | 11 |
| [`niamey-line5.aln.toml`](niamey-line5.aln.toml) | `line-5` | 18,737.6 m | 13 |
| [`niamey-line6.aln.toml`](niamey-line6.aln.toml) | `line-6` | 51,063.4 m | 42 |
| [`niamey-line7.aln.toml`](niamey-line7.aln.toml) | `line-7` | 3,925.1 m | 4 |
| [`niamey-line8.aln.toml`](niamey-line8.aln.toml) | `line-8` | 5,047.0 m | 4 |
| [`niamey-line9.aln.toml`](niamey-line9.aln.toml) | `line-9` | 4,949.6 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
