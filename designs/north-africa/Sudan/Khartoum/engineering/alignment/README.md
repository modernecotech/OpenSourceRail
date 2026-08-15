# Khartoum Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khartoum-line1.aln.toml`](khartoum-line1.aln.toml) | `line-1` | 40,751.6 m | 24 |
| [`khartoum-line2.aln.toml`](khartoum-line2.aln.toml) | `line-2` | 35,581.3 m | 21 |
| [`khartoum-line3.aln.toml`](khartoum-line3.aln.toml) | `line-3` | 55,964.5 m | 26 |
| [`khartoum-line4.aln.toml`](khartoum-line4.aln.toml) | `line-4` | 31,720.9 m | 20 |
| [`khartoum-line5.aln.toml`](khartoum-line5.aln.toml) | `line-5` | 41,652.7 m | 24 |
| [`khartoum-line6.aln.toml`](khartoum-line6.aln.toml) | `line-6` | 34,186.4 m | 19 |
| [`khartoum-line7.aln.toml`](khartoum-line7.aln.toml) | `line-7` | 40,708.3 m | 22 |
| [`khartoum-line8.aln.toml`](khartoum-line8.aln.toml) | `line-8` | 36,614.0 m | 22 |
| [`khartoum-line9.aln.toml`](khartoum-line9.aln.toml) | `line-9` | 99,864.6 m | 62 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
