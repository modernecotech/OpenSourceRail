# Fayoum Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`fayoum-line1.aln.toml`](fayoum-line1.aln.toml) | `line-1` | 26,247.0 m | 18 |
| [`fayoum-line10.aln.toml`](fayoum-line10.aln.toml) | `line-10` | 2,957.3 m | 2 |
| [`fayoum-line11.aln.toml`](fayoum-line11.aln.toml) | `line-11` | 8,993.0 m | 6 |
| [`fayoum-line12.aln.toml`](fayoum-line12.aln.toml) | `line-12` | 6,115.3 m | 4 |
| [`fayoum-line13.aln.toml`](fayoum-line13.aln.toml) | `line-13` | 5,348.9 m | 4 |
| [`fayoum-line2.aln.toml`](fayoum-line2.aln.toml) | `line-2` | 15,242.2 m | 9 |
| [`fayoum-line3.aln.toml`](fayoum-line3.aln.toml) | `line-3` | 18,851.1 m | 11 |
| [`fayoum-line4.aln.toml`](fayoum-line4.aln.toml) | `line-4` | 2,787.4 m | 2 |
| [`fayoum-line5.aln.toml`](fayoum-line5.aln.toml) | `line-5` | 8,448.1 m | 6 |
| [`fayoum-line6.aln.toml`](fayoum-line6.aln.toml) | `line-6` | 5,725.0 m | 5 |
| [`fayoum-line7.aln.toml`](fayoum-line7.aln.toml) | `line-7` | 6,541.8 m | 6 |
| [`fayoum-line8.aln.toml`](fayoum-line8.aln.toml) | `line-8` | 2,458.5 m | 3 |
| [`fayoum-line9.aln.toml`](fayoum-line9.aln.toml) | `line-9` | 10,603.2 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
