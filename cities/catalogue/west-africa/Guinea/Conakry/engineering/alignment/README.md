# Conakry Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`conakry-line1.aln.toml`](conakry-line1.aln.toml) | `line-1` | 26,836.5 m | 24 |
| [`conakry-line10.aln.toml`](conakry-line10.aln.toml) | `line-10` | 6,679.8 m | 5 |
| [`conakry-line11.aln.toml`](conakry-line11.aln.toml) | `line-11` | 3,631.3 m | 4 |
| [`conakry-line12.aln.toml`](conakry-line12.aln.toml) | `line-12` | 6,747.0 m | 4 |
| [`conakry-line13.aln.toml`](conakry-line13.aln.toml) | `line-13` | 2,888.5 m | 2 |
| [`conakry-line14.aln.toml`](conakry-line14.aln.toml) | `line-14` | 5,882.3 m | 5 |
| [`conakry-line2.aln.toml`](conakry-line2.aln.toml) | `line-2` | 18,001.6 m | 11 |
| [`conakry-line3.aln.toml`](conakry-line3.aln.toml) | `line-3` | 37,424.4 m | 28 |
| [`conakry-line4.aln.toml`](conakry-line4.aln.toml) | `line-4` | 6,477.2 m | 5 |
| [`conakry-line5.aln.toml`](conakry-line5.aln.toml) | `line-5` | 3,520.1 m | 4 |
| [`conakry-line6.aln.toml`](conakry-line6.aln.toml) | `line-6` | 3,284.4 m | 3 |
| [`conakry-line7.aln.toml`](conakry-line7.aln.toml) | `line-7` | 8,394.3 m | 6 |
| [`conakry-line8.aln.toml`](conakry-line8.aln.toml) | `line-8` | 2,792.4 m | 2 |
| [`conakry-line9.aln.toml`](conakry-line9.aln.toml) | `line-9` | 2,406.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
