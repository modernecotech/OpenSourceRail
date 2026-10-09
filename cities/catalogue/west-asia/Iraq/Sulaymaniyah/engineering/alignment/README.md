# Sulaymaniyah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sulaymaniyah-line1.aln.toml`](sulaymaniyah-line1.aln.toml) | `line-1` | 13,517.5 m | 9 |
| [`sulaymaniyah-line10.aln.toml`](sulaymaniyah-line10.aln.toml) | `line-10` | 5,972.3 m | 5 |
| [`sulaymaniyah-line11.aln.toml`](sulaymaniyah-line11.aln.toml) | `line-11` | 8,068.0 m | 5 |
| [`sulaymaniyah-line12.aln.toml`](sulaymaniyah-line12.aln.toml) | `line-12` | 2,215.0 m | 2 |
| [`sulaymaniyah-line13.aln.toml`](sulaymaniyah-line13.aln.toml) | `line-13` | 7,205.2 m | 5 |
| [`sulaymaniyah-line14.aln.toml`](sulaymaniyah-line14.aln.toml) | `line-14` | 2,817.9 m | 2 |
| [`sulaymaniyah-line15.aln.toml`](sulaymaniyah-line15.aln.toml) | `line-15` | 3,345.9 m | 3 |
| [`sulaymaniyah-line16.aln.toml`](sulaymaniyah-line16.aln.toml) | `line-16` | 10,401.7 m | 7 |
| [`sulaymaniyah-line17.aln.toml`](sulaymaniyah-line17.aln.toml) | `line-17` | 6,633.9 m | 5 |
| [`sulaymaniyah-line2.aln.toml`](sulaymaniyah-line2.aln.toml) | `line-2` | 12,294.4 m | 8 |
| [`sulaymaniyah-line3.aln.toml`](sulaymaniyah-line3.aln.toml) | `line-3` | 27,333.8 m | 17 |
| [`sulaymaniyah-line4.aln.toml`](sulaymaniyah-line4.aln.toml) | `line-4` | 53,403.5 m | 32 |
| [`sulaymaniyah-line5.aln.toml`](sulaymaniyah-line5.aln.toml) | `line-5` | 4,968.4 m | 4 |
| [`sulaymaniyah-line6.aln.toml`](sulaymaniyah-line6.aln.toml) | `line-6` | 4,985.3 m | 4 |
| [`sulaymaniyah-line7.aln.toml`](sulaymaniyah-line7.aln.toml) | `line-7` | 6,534.1 m | 4 |
| [`sulaymaniyah-line8.aln.toml`](sulaymaniyah-line8.aln.toml) | `line-8` | 7,357.3 m | 6 |
| [`sulaymaniyah-line9.aln.toml`](sulaymaniyah-line9.aln.toml) | `line-9` | 5,397.5 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
