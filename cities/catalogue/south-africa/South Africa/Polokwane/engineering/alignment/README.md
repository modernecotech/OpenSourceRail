# Polokwane Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`polokwane-line1.aln.toml`](polokwane-line1.aln.toml) | `line-1` | 16,284.0 m | 12 |
| [`polokwane-line10.aln.toml`](polokwane-line10.aln.toml) | `line-10` | 2,874.2 m | 3 |
| [`polokwane-line11.aln.toml`](polokwane-line11.aln.toml) | `line-11` | 2,686.5 m | 2 |
| [`polokwane-line2.aln.toml`](polokwane-line2.aln.toml) | `line-2` | 9,205.7 m | 6 |
| [`polokwane-line3.aln.toml`](polokwane-line3.aln.toml) | `line-3` | 15,850.1 m | 10 |
| [`polokwane-line4.aln.toml`](polokwane-line4.aln.toml) | `line-4` | 6,186.1 m | 4 |
| [`polokwane-line5.aln.toml`](polokwane-line5.aln.toml) | `line-5` | 4,224.9 m | 3 |
| [`polokwane-line6.aln.toml`](polokwane-line6.aln.toml) | `line-6` | 4,921.7 m | 4 |
| [`polokwane-line7.aln.toml`](polokwane-line7.aln.toml) | `line-7` | 2,023.1 m | 2 |
| [`polokwane-line8.aln.toml`](polokwane-line8.aln.toml) | `line-8` | 6,950.3 m | 6 |
| [`polokwane-line9.aln.toml`](polokwane-line9.aln.toml) | `line-9` | 2,361.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
