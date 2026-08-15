# Faisalabad Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`faisalabad-line1.aln.toml`](faisalabad-line1.aln.toml) | `line-1` | 32,259.4 m | 21 |
| [`faisalabad-line2.aln.toml`](faisalabad-line2.aln.toml) | `line-2` | 22,906.6 m | 14 |
| [`faisalabad-line3.aln.toml`](faisalabad-line3.aln.toml) | `line-3` | 23,068.2 m | 17 |
| [`faisalabad-line4.aln.toml`](faisalabad-line4.aln.toml) | `line-4` | 22,795.9 m | 15 |
| [`faisalabad-line5.aln.toml`](faisalabad-line5.aln.toml) | `line-5` | 24,748.2 m | 14 |
| [`faisalabad-line6.aln.toml`](faisalabad-line6.aln.toml) | `line-6` | 43,938.3 m | 36 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
