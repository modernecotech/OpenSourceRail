# Dammam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dammam-line1.aln.toml`](dammam-line1.aln.toml) | `line-1` | 45,162.3 m | 31 |
| [`dammam-line10.aln.toml`](dammam-line10.aln.toml) | `line-10` | 10,132.5 m | 7 |
| [`dammam-line11.aln.toml`](dammam-line11.aln.toml) | `line-11` | 6,872.2 m | 5 |
| [`dammam-line12.aln.toml`](dammam-line12.aln.toml) | `line-12` | 6,072.0 m | 5 |
| [`dammam-line13.aln.toml`](dammam-line13.aln.toml) | `line-13` | 5,481.9 m | 6 |
| [`dammam-line14.aln.toml`](dammam-line14.aln.toml) | `line-14` | 5,590.4 m | 4 |
| [`dammam-line15.aln.toml`](dammam-line15.aln.toml) | `line-15` | 6,138.7 m | 4 |
| [`dammam-line16.aln.toml`](dammam-line16.aln.toml) | `line-16` | 6,740.5 m | 4 |
| [`dammam-line17.aln.toml`](dammam-line17.aln.toml) | `line-17` | 7,752.9 m | 6 |
| [`dammam-line18.aln.toml`](dammam-line18.aln.toml) | `line-18` | 10,865.0 m | 6 |
| [`dammam-line19.aln.toml`](dammam-line19.aln.toml) | `line-19` | 10,040.6 m | 7 |
| [`dammam-line2.aln.toml`](dammam-line2.aln.toml) | `line-2` | 34,501.9 m | 20 |
| [`dammam-line20.aln.toml`](dammam-line20.aln.toml) | `line-20` | 6,737.3 m | 5 |
| [`dammam-line21.aln.toml`](dammam-line21.aln.toml) | `line-21` | 9,650.3 m | 6 |
| [`dammam-line22.aln.toml`](dammam-line22.aln.toml) | `line-22` | 13,722.5 m | 9 |
| [`dammam-line23.aln.toml`](dammam-line23.aln.toml) | `line-23` | 7,175.4 m | 7 |
| [`dammam-line24.aln.toml`](dammam-line24.aln.toml) | `line-24` | 8,279.6 m | 6 |
| [`dammam-line25.aln.toml`](dammam-line25.aln.toml) | `line-25` | 6,241.2 m | 6 |
| [`dammam-line26.aln.toml`](dammam-line26.aln.toml) | `line-26` | 9,673.8 m | 5 |
| [`dammam-line27.aln.toml`](dammam-line27.aln.toml) | `line-27` | 6,603.7 m | 4 |
| [`dammam-line28.aln.toml`](dammam-line28.aln.toml) | `line-28` | 6,625.5 m | 6 |
| [`dammam-line29.aln.toml`](dammam-line29.aln.toml) | `line-29` | 5,376.5 m | 4 |
| [`dammam-line3.aln.toml`](dammam-line3.aln.toml) | `line-3` | 25,732.5 m | 18 |
| [`dammam-line30.aln.toml`](dammam-line30.aln.toml) | `line-30` | 5,363.5 m | 4 |
| [`dammam-line31.aln.toml`](dammam-line31.aln.toml) | `line-31` | 6,069.3 m | 5 |
| [`dammam-line4.aln.toml`](dammam-line4.aln.toml) | `line-4` | 28,288.5 m | 17 |
| [`dammam-line5.aln.toml`](dammam-line5.aln.toml) | `line-5` | 43,696.0 m | 28 |
| [`dammam-line6.aln.toml`](dammam-line6.aln.toml) | `line-6` | 90,418.1 m | 51 |
| [`dammam-line7.aln.toml`](dammam-line7.aln.toml) | `line-7` | 5,895.9 m | 4 |
| [`dammam-line8.aln.toml`](dammam-line8.aln.toml) | `line-8` | 8,031.2 m | 6 |
| [`dammam-line9.aln.toml`](dammam-line9.aln.toml) | `line-9` | 5,864.8 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
