# Chittagong Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`chittagong-line1.aln.toml`](chittagong-line1.aln.toml) | `line-1` | 40,888.4 m | 30 |
| [`chittagong-line10.aln.toml`](chittagong-line10.aln.toml) | `line-10` | 7,053.2 m | 9 |
| [`chittagong-line11.aln.toml`](chittagong-line11.aln.toml) | `line-11` | 6,607.6 m | 7 |
| [`chittagong-line12.aln.toml`](chittagong-line12.aln.toml) | `line-12` | 7,158.4 m | 9 |
| [`chittagong-line13.aln.toml`](chittagong-line13.aln.toml) | `line-13` | 7,512.7 m | 5 |
| [`chittagong-line14.aln.toml`](chittagong-line14.aln.toml) | `line-14` | 9,449.3 m | 8 |
| [`chittagong-line15.aln.toml`](chittagong-line15.aln.toml) | `line-15` | 7,679.6 m | 6 |
| [`chittagong-line16.aln.toml`](chittagong-line16.aln.toml) | `line-16` | 9,716.0 m | 6 |
| [`chittagong-line17.aln.toml`](chittagong-line17.aln.toml) | `line-17` | 7,003.1 m | 9 |
| [`chittagong-line18.aln.toml`](chittagong-line18.aln.toml) | `line-18` | 13,796.7 m | 9 |
| [`chittagong-line19.aln.toml`](chittagong-line19.aln.toml) | `line-19` | 9,300.4 m | 6 |
| [`chittagong-line2.aln.toml`](chittagong-line2.aln.toml) | `line-2` | 22,012.7 m | 18 |
| [`chittagong-line20.aln.toml`](chittagong-line20.aln.toml) | `line-20` | 7,239.2 m | 8 |
| [`chittagong-line21.aln.toml`](chittagong-line21.aln.toml) | `line-21` | 14,511.1 m | 9 |
| [`chittagong-line22.aln.toml`](chittagong-line22.aln.toml) | `line-22` | 9,391.4 m | 7 |
| [`chittagong-line23.aln.toml`](chittagong-line23.aln.toml) | `line-23` | 6,973.0 m | 4 |
| [`chittagong-line24.aln.toml`](chittagong-line24.aln.toml) | `line-24` | 14,012.0 m | 9 |
| [`chittagong-line25.aln.toml`](chittagong-line25.aln.toml) | `line-25` | 6,464.3 m | 4 |
| [`chittagong-line26.aln.toml`](chittagong-line26.aln.toml) | `line-26` | 8,072.0 m | 6 |
| [`chittagong-line27.aln.toml`](chittagong-line27.aln.toml) | `line-27` | 12,581.7 m | 8 |
| [`chittagong-line28.aln.toml`](chittagong-line28.aln.toml) | `line-28` | 7,212.2 m | 5 |
| [`chittagong-line29.aln.toml`](chittagong-line29.aln.toml) | `line-29` | 6,893.4 m | 6 |
| [`chittagong-line3.aln.toml`](chittagong-line3.aln.toml) | `line-3` | 61,223.0 m | 41 |
| [`chittagong-line30.aln.toml`](chittagong-line30.aln.toml) | `line-30` | 6,566.7 m | 8 |
| [`chittagong-line31.aln.toml`](chittagong-line31.aln.toml) | `line-31` | 8,018.7 m | 5 |
| [`chittagong-line32.aln.toml`](chittagong-line32.aln.toml) | `line-32` | 8,222.8 m | 11 |
| [`chittagong-line33.aln.toml`](chittagong-line33.aln.toml) | `line-33` | 13,937.5 m | 8 |
| [`chittagong-line34.aln.toml`](chittagong-line34.aln.toml) | `line-34` | 12,140.8 m | 9 |
| [`chittagong-line35.aln.toml`](chittagong-line35.aln.toml) | `line-35` | 15,741.3 m | 11 |
| [`chittagong-line36.aln.toml`](chittagong-line36.aln.toml) | `line-36` | 6,240.2 m | 4 |
| [`chittagong-line37.aln.toml`](chittagong-line37.aln.toml) | `line-37` | 7,277.1 m | 8 |
| [`chittagong-line4.aln.toml`](chittagong-line4.aln.toml) | `line-4` | 28,615.4 m | 20 |
| [`chittagong-line5.aln.toml`](chittagong-line5.aln.toml) | `line-5` | 31,768.3 m | 21 |
| [`chittagong-line6.aln.toml`](chittagong-line6.aln.toml) | `line-6` | 26,473.7 m | 21 |
| [`chittagong-line7.aln.toml`](chittagong-line7.aln.toml) | `line-7` | 34,409.3 m | 24 |
| [`chittagong-line8.aln.toml`](chittagong-line8.aln.toml) | `line-8` | 74,509.2 m | 55 |
| [`chittagong-line9.aln.toml`](chittagong-line9.aln.toml) | `line-9` | 6,325.5 m | 9 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
