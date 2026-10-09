# Medina Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`medina-line1.aln.toml`](medina-line1.aln.toml) | `line-1` | 32,733.5 m | 23 |
| [`medina-line10.aln.toml`](medina-line10.aln.toml) | `line-10` | 4,058.1 m | 4 |
| [`medina-line11.aln.toml`](medina-line11.aln.toml) | `line-11` | 5,441.0 m | 4 |
| [`medina-line12.aln.toml`](medina-line12.aln.toml) | `line-12` | 5,156.2 m | 3 |
| [`medina-line13.aln.toml`](medina-line13.aln.toml) | `line-13` | 4,777.9 m | 3 |
| [`medina-line14.aln.toml`](medina-line14.aln.toml) | `line-14` | 4,456.7 m | 3 |
| [`medina-line15.aln.toml`](medina-line15.aln.toml) | `line-15` | 7,402.1 m | 6 |
| [`medina-line16.aln.toml`](medina-line16.aln.toml) | `line-16` | 5,071.0 m | 4 |
| [`medina-line17.aln.toml`](medina-line17.aln.toml) | `line-17` | 5,107.0 m | 5 |
| [`medina-line18.aln.toml`](medina-line18.aln.toml) | `line-18` | 4,285.6 m | 4 |
| [`medina-line19.aln.toml`](medina-line19.aln.toml) | `line-19` | 6,100.4 m | 4 |
| [`medina-line2.aln.toml`](medina-line2.aln.toml) | `line-2` | 19,119.4 m | 11 |
| [`medina-line20.aln.toml`](medina-line20.aln.toml) | `line-20` | 3,501.1 m | 3 |
| [`medina-line21.aln.toml`](medina-line21.aln.toml) | `line-21` | 5,121.8 m | 4 |
| [`medina-line22.aln.toml`](medina-line22.aln.toml) | `line-22` | 5,382.4 m | 5 |
| [`medina-line23.aln.toml`](medina-line23.aln.toml) | `line-23` | 5,010.9 m | 4 |
| [`medina-line24.aln.toml`](medina-line24.aln.toml) | `line-24` | 12,679.7 m | 8 |
| [`medina-line25.aln.toml`](medina-line25.aln.toml) | `line-25` | 10,872.7 m | 6 |
| [`medina-line26.aln.toml`](medina-line26.aln.toml) | `line-26` | 5,290.8 m | 4 |
| [`medina-line27.aln.toml`](medina-line27.aln.toml) | `line-27` | 13,941.1 m | 10 |
| [`medina-line28.aln.toml`](medina-line28.aln.toml) | `line-28` | 4,420.2 m | 4 |
| [`medina-line29.aln.toml`](medina-line29.aln.toml) | `line-29` | 5,107.4 m | 4 |
| [`medina-line3.aln.toml`](medina-line3.aln.toml) | `line-3` | 18,605.2 m | 12 |
| [`medina-line30.aln.toml`](medina-line30.aln.toml) | `line-30` | 6,402.6 m | 4 |
| [`medina-line31.aln.toml`](medina-line31.aln.toml) | `line-31` | 4,196.2 m | 3 |
| [`medina-line32.aln.toml`](medina-line32.aln.toml) | `line-32` | 6,762.7 m | 5 |
| [`medina-line33.aln.toml`](medina-line33.aln.toml) | `line-33` | 9,401.9 m | 8 |
| [`medina-line34.aln.toml`](medina-line34.aln.toml) | `line-34` | 5,167.2 m | 3 |
| [`medina-line35.aln.toml`](medina-line35.aln.toml) | `line-35` | 3,849.4 m | 3 |
| [`medina-line4.aln.toml`](medina-line4.aln.toml) | `line-4` | 23,806.8 m | 12 |
| [`medina-line5.aln.toml`](medina-line5.aln.toml) | `line-5` | 19,443.1 m | 12 |
| [`medina-line6.aln.toml`](medina-line6.aln.toml) | `line-6` | 58,528.0 m | 32 |
| [`medina-line7.aln.toml`](medina-line7.aln.toml) | `line-7` | 5,282.4 m | 3 |
| [`medina-line8.aln.toml`](medina-line8.aln.toml) | `line-8` | 4,778.7 m | 4 |
| [`medina-line9.aln.toml`](medina-line9.aln.toml) | `line-9` | 3,689.6 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
