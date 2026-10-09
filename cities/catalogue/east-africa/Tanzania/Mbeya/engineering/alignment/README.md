# Mbeya Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`mbeya-line1.aln.toml`](mbeya-line1.aln.toml) | `line-1` | 15,469.1 m | 11 |
| [`mbeya-line10.aln.toml`](mbeya-line10.aln.toml) | `line-10` | 3,364.8 m | 3 |
| [`mbeya-line11.aln.toml`](mbeya-line11.aln.toml) | `line-11` | 3,149.1 m | 3 |
| [`mbeya-line12.aln.toml`](mbeya-line12.aln.toml) | `line-12` | 4,547.1 m | 4 |
| [`mbeya-line2.aln.toml`](mbeya-line2.aln.toml) | `line-2` | 19,459.6 m | 11 |
| [`mbeya-line3.aln.toml`](mbeya-line3.aln.toml) | `line-3` | 7,113.6 m | 6 |
| [`mbeya-line4.aln.toml`](mbeya-line4.aln.toml) | `line-4` | 3,306.5 m | 3 |
| [`mbeya-line5.aln.toml`](mbeya-line5.aln.toml) | `line-5` | 4,227.4 m | 3 |
| [`mbeya-line6.aln.toml`](mbeya-line6.aln.toml) | `line-6` | 8,406.7 m | 7 |
| [`mbeya-line7.aln.toml`](mbeya-line7.aln.toml) | `line-7` | 5,734.9 m | 4 |
| [`mbeya-line8.aln.toml`](mbeya-line8.aln.toml) | `line-8` | 3,777.1 m | 3 |
| [`mbeya-line9.aln.toml`](mbeya-line9.aln.toml) | `line-9` | 4,282.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
