# Polokwane Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`polokwane-line1.aln.toml`](polokwane-line1.aln.toml) | `line-1` | 21,187.0 m | 8 |
| [`polokwane-line2.aln.toml`](polokwane-line2.aln.toml) | `line-2` | 13,622.2 m | 5 |
| [`polokwane-line3.aln.toml`](polokwane-line3.aln.toml) | `line-3` | 15,850.1 m | 5 |
| [`polokwane-line4.aln.toml`](polokwane-line4.aln.toml) | `line-4` | 6,964.1 m | 2 |
| [`polokwane-line5.aln.toml`](polokwane-line5.aln.toml) | `line-5` | 4,954.5 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
