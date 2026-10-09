# Colombo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`colombo-line1.aln.toml`](colombo-line1.aln.toml) | `line-1` | 29,410.3 m | 25 |
| [`colombo-line10.aln.toml`](colombo-line10.aln.toml) | `line-10` | 5,896.5 m | 3 |
| [`colombo-line11.aln.toml`](colombo-line11.aln.toml) | `line-11` | 9,217.9 m | 6 |
| [`colombo-line12.aln.toml`](colombo-line12.aln.toml) | `line-12` | 6,608.9 m | 5 |
| [`colombo-line13.aln.toml`](colombo-line13.aln.toml) | `line-13` | 6,000.7 m | 4 |
| [`colombo-line14.aln.toml`](colombo-line14.aln.toml) | `line-14` | 6,449.4 m | 4 |
| [`colombo-line15.aln.toml`](colombo-line15.aln.toml) | `line-15` | 9,902.2 m | 7 |
| [`colombo-line16.aln.toml`](colombo-line16.aln.toml) | `line-16` | 6,523.9 m | 4 |
| [`colombo-line17.aln.toml`](colombo-line17.aln.toml) | `line-17` | 8,546.1 m | 5 |
| [`colombo-line18.aln.toml`](colombo-line18.aln.toml) | `line-18` | 9,534.2 m | 7 |
| [`colombo-line19.aln.toml`](colombo-line19.aln.toml) | `line-19` | 10,094.4 m | 6 |
| [`colombo-line2.aln.toml`](colombo-line2.aln.toml) | `line-2` | 23,123.5 m | 13 |
| [`colombo-line20.aln.toml`](colombo-line20.aln.toml) | `line-20` | 12,075.0 m | 8 |
| [`colombo-line21.aln.toml`](colombo-line21.aln.toml) | `line-21` | 8,415.9 m | 8 |
| [`colombo-line22.aln.toml`](colombo-line22.aln.toml) | `line-22` | 7,559.6 m | 6 |
| [`colombo-line23.aln.toml`](colombo-line23.aln.toml) | `line-23` | 11,960.7 m | 9 |
| [`colombo-line24.aln.toml`](colombo-line24.aln.toml) | `line-24` | 8,045.7 m | 5 |
| [`colombo-line25.aln.toml`](colombo-line25.aln.toml) | `line-25` | 11,446.7 m | 11 |
| [`colombo-line26.aln.toml`](colombo-line26.aln.toml) | `line-26` | 6,235.9 m | 4 |
| [`colombo-line27.aln.toml`](colombo-line27.aln.toml) | `line-27` | 6,301.2 m | 4 |
| [`colombo-line28.aln.toml`](colombo-line28.aln.toml) | `line-28` | 8,866.7 m | 7 |
| [`colombo-line29.aln.toml`](colombo-line29.aln.toml) | `line-29` | 10,192.3 m | 8 |
| [`colombo-line3.aln.toml`](colombo-line3.aln.toml) | `line-3` | 37,524.0 m | 28 |
| [`colombo-line30.aln.toml`](colombo-line30.aln.toml) | `line-30` | 7,328.1 m | 6 |
| [`colombo-line31.aln.toml`](colombo-line31.aln.toml) | `line-31` | 5,804.7 m | 4 |
| [`colombo-line32.aln.toml`](colombo-line32.aln.toml) | `line-32` | 9,890.4 m | 7 |
| [`colombo-line33.aln.toml`](colombo-line33.aln.toml) | `line-33` | 9,419.9 m | 7 |
| [`colombo-line34.aln.toml`](colombo-line34.aln.toml) | `line-34` | 7,618.0 m | 5 |
| [`colombo-line35.aln.toml`](colombo-line35.aln.toml) | `line-35` | 6,294.2 m | 5 |
| [`colombo-line36.aln.toml`](colombo-line36.aln.toml) | `line-36` | 7,703.1 m | 7 |
| [`colombo-line37.aln.toml`](colombo-line37.aln.toml) | `line-37` | 6,857.7 m | 4 |
| [`colombo-line4.aln.toml`](colombo-line4.aln.toml) | `line-4` | 22,840.5 m | 17 |
| [`colombo-line5.aln.toml`](colombo-line5.aln.toml) | `line-5` | 29,185.1 m | 20 |
| [`colombo-line6.aln.toml`](colombo-line6.aln.toml) | `line-6` | 27,128.7 m | 19 |
| [`colombo-line7.aln.toml`](colombo-line7.aln.toml) | `line-7` | 25,100.9 m | 21 |
| [`colombo-line8.aln.toml`](colombo-line8.aln.toml) | `line-8` | 20,226.2 m | 19 |
| [`colombo-line9.aln.toml`](colombo-line9.aln.toml) | `line-9` | 70,985.2 m | 57 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
