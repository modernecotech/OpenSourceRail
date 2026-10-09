# Amman Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`amman-line1.aln.toml`](amman-line1.aln.toml) | `line-1` | 39,410.8 m | 28 |
| [`amman-line10.aln.toml`](amman-line10.aln.toml) | `line-10` | 6,079.0 m | 5 |
| [`amman-line11.aln.toml`](amman-line11.aln.toml) | `line-11` | 7,151.0 m | 7 |
| [`amman-line12.aln.toml`](amman-line12.aln.toml) | `line-12` | 9,539.9 m | 7 |
| [`amman-line13.aln.toml`](amman-line13.aln.toml) | `line-13` | 11,146.2 m | 9 |
| [`amman-line14.aln.toml`](amman-line14.aln.toml) | `line-14` | 10,613.8 m | 9 |
| [`amman-line15.aln.toml`](amman-line15.aln.toml) | `line-15` | 6,392.7 m | 4 |
| [`amman-line16.aln.toml`](amman-line16.aln.toml) | `line-16` | 7,315.4 m | 6 |
| [`amman-line17.aln.toml`](amman-line17.aln.toml) | `line-17` | 9,154.4 m | 6 |
| [`amman-line18.aln.toml`](amman-line18.aln.toml) | `line-18` | 9,996.7 m | 8 |
| [`amman-line19.aln.toml`](amman-line19.aln.toml) | `line-19` | 6,913.9 m | 6 |
| [`amman-line2.aln.toml`](amman-line2.aln.toml) | `line-2` | 42,425.5 m | 26 |
| [`amman-line20.aln.toml`](amman-line20.aln.toml) | `line-20` | 7,389.6 m | 5 |
| [`amman-line21.aln.toml`](amman-line21.aln.toml) | `line-21` | 6,926.3 m | 5 |
| [`amman-line22.aln.toml`](amman-line22.aln.toml) | `line-22` | 15,035.7 m | 12 |
| [`amman-line23.aln.toml`](amman-line23.aln.toml) | `line-23` | 7,167.8 m | 7 |
| [`amman-line24.aln.toml`](amman-line24.aln.toml) | `line-24` | 9,614.8 m | 6 |
| [`amman-line25.aln.toml`](amman-line25.aln.toml) | `line-25` | 9,164.7 m | 6 |
| [`amman-line26.aln.toml`](amman-line26.aln.toml) | `line-26` | 10,373.9 m | 7 |
| [`amman-line27.aln.toml`](amman-line27.aln.toml) | `line-27` | 7,827.4 m | 5 |
| [`amman-line28.aln.toml`](amman-line28.aln.toml) | `line-28` | 8,249.2 m | 6 |
| [`amman-line29.aln.toml`](amman-line29.aln.toml) | `line-29` | 9,978.0 m | 10 |
| [`amman-line3.aln.toml`](amman-line3.aln.toml) | `line-3` | 22,957.1 m | 12 |
| [`amman-line30.aln.toml`](amman-line30.aln.toml) | `line-30` | 8,672.1 m | 5 |
| [`amman-line31.aln.toml`](amman-line31.aln.toml) | `line-31` | 6,910.4 m | 5 |
| [`amman-line4.aln.toml`](amman-line4.aln.toml) | `line-4` | 18,230.8 m | 13 |
| [`amman-line5.aln.toml`](amman-line5.aln.toml) | `line-5` | 29,336.6 m | 20 |
| [`amman-line6.aln.toml`](amman-line6.aln.toml) | `line-6` | 32,472.6 m | 22 |
| [`amman-line7.aln.toml`](amman-line7.aln.toml) | `line-7` | 24,910.0 m | 15 |
| [`amman-line8.aln.toml`](amman-line8.aln.toml) | `line-8` | 29,047.5 m | 20 |
| [`amman-line9.aln.toml`](amman-line9.aln.toml) | `line-9` | 77,720.7 m | 47 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
