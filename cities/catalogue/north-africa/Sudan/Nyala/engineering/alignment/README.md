# Nyala Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nyala-line1.aln.toml`](nyala-line1.aln.toml) | `line-1` | 16,443.6 m | 10 |
| [`nyala-line10.aln.toml`](nyala-line10.aln.toml) | `line-10` | 3,408.8 m | 3 |
| [`nyala-line11.aln.toml`](nyala-line11.aln.toml) | `line-11` | 3,425.3 m | 3 |
| [`nyala-line12.aln.toml`](nyala-line12.aln.toml) | `line-12` | 4,091.0 m | 3 |
| [`nyala-line2.aln.toml`](nyala-line2.aln.toml) | `line-2` | 11,557.9 m | 8 |
| [`nyala-line3.aln.toml`](nyala-line3.aln.toml) | `line-3` | 10,857.7 m | 7 |
| [`nyala-line4.aln.toml`](nyala-line4.aln.toml) | `line-4` | 5,008.7 m | 3 |
| [`nyala-line5.aln.toml`](nyala-line5.aln.toml) | `line-5` | 3,221.7 m | 3 |
| [`nyala-line6.aln.toml`](nyala-line6.aln.toml) | `line-6` | 3,558.8 m | 4 |
| [`nyala-line7.aln.toml`](nyala-line7.aln.toml) | `line-7` | 5,646.8 m | 4 |
| [`nyala-line8.aln.toml`](nyala-line8.aln.toml) | `line-8` | 5,016.2 m | 4 |
| [`nyala-line9.aln.toml`](nyala-line9.aln.toml) | `line-9` | 4,980.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
