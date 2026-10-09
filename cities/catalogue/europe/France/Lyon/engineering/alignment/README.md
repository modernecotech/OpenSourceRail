# Lyon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lyon-line1.aln.toml`](lyon-line1.aln.toml) | `line-1` | 42,913.0 m | 26 |
| [`lyon-line10.aln.toml`](lyon-line10.aln.toml) | `line-10` | 13,548.1 m | 16 |
| [`lyon-line11.aln.toml`](lyon-line11.aln.toml) | `line-11` | 5,941.0 m | 5 |
| [`lyon-line12.aln.toml`](lyon-line12.aln.toml) | `line-12` | 5,679.7 m | 10 |
| [`lyon-line13.aln.toml`](lyon-line13.aln.toml) | `line-13` | 4,964.2 m | 5 |
| [`lyon-line14.aln.toml`](lyon-line14.aln.toml) | `line-14` | 7,309.3 m | 8 |
| [`lyon-line15.aln.toml`](lyon-line15.aln.toml) | `line-15` | 8,045.6 m | 5 |
| [`lyon-line16.aln.toml`](lyon-line16.aln.toml) | `line-16` | 5,030.4 m | 4 |
| [`lyon-line17.aln.toml`](lyon-line17.aln.toml) | `line-17` | 12,752.2 m | 10 |
| [`lyon-line18.aln.toml`](lyon-line18.aln.toml) | `line-18` | 5,427.4 m | 7 |
| [`lyon-line19.aln.toml`](lyon-line19.aln.toml) | `line-19` | 6,944.9 m | 7 |
| [`lyon-line2.aln.toml`](lyon-line2.aln.toml) | `line-2` | 36,909.0 m | 25 |
| [`lyon-line20.aln.toml`](lyon-line20.aln.toml) | `line-20` | 6,967.9 m | 5 |
| [`lyon-line21.aln.toml`](lyon-line21.aln.toml) | `line-21` | 5,496.7 m | 4 |
| [`lyon-line22.aln.toml`](lyon-line22.aln.toml) | `line-22` | 5,610.7 m | 6 |
| [`lyon-line23.aln.toml`](lyon-line23.aln.toml) | `line-23` | 4,633.6 m | 4 |
| [`lyon-line24.aln.toml`](lyon-line24.aln.toml) | `line-24` | 7,566.4 m | 6 |
| [`lyon-line25.aln.toml`](lyon-line25.aln.toml) | `line-25` | 5,450.2 m | 4 |
| [`lyon-line26.aln.toml`](lyon-line26.aln.toml) | `line-26` | 8,677.3 m | 7 |
| [`lyon-line27.aln.toml`](lyon-line27.aln.toml) | `line-27` | 6,140.3 m | 4 |
| [`lyon-line28.aln.toml`](lyon-line28.aln.toml) | `line-28` | 6,682.9 m | 10 |
| [`lyon-line29.aln.toml`](lyon-line29.aln.toml) | `line-29` | 8,668.4 m | 8 |
| [`lyon-line3.aln.toml`](lyon-line3.aln.toml) | `line-3` | 20,504.2 m | 18 |
| [`lyon-line30.aln.toml`](lyon-line30.aln.toml) | `line-30` | 7,798.8 m | 7 |
| [`lyon-line31.aln.toml`](lyon-line31.aln.toml) | `line-31` | 5,973.8 m | 4 |
| [`lyon-line32.aln.toml`](lyon-line32.aln.toml) | `line-32` | 5,229.6 m | 4 |
| [`lyon-line33.aln.toml`](lyon-line33.aln.toml) | `line-33` | 7,552.2 m | 7 |
| [`lyon-line4.aln.toml`](lyon-line4.aln.toml) | `line-4` | 39,830.6 m | 28 |
| [`lyon-line5.aln.toml`](lyon-line5.aln.toml) | `line-5` | 26,016.7 m | 16 |
| [`lyon-line6.aln.toml`](lyon-line6.aln.toml) | `line-6` | 62,176.2 m | 44 |
| [`lyon-line7.aln.toml`](lyon-line7.aln.toml) | `line-7` | 6,074.7 m | 6 |
| [`lyon-line8.aln.toml`](lyon-line8.aln.toml) | `line-8` | 5,997.5 m | 3 |
| [`lyon-line9.aln.toml`](lyon-line9.aln.toml) | `line-9` | 5,438.5 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
