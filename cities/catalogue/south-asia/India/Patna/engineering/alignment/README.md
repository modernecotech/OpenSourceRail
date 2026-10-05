# Patna Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`patna-line1.aln.toml`](patna-line1.aln.toml) | `line-1` | 27,504.6 m | 8 |
| [`patna-line2.aln.toml`](patna-line2.aln.toml) | `line-2` | 17,979.4 m | 7 |
| [`patna-line3.aln.toml`](patna-line3.aln.toml) | `line-3` | 15,802.8 m | 5 |
| [`patna-line4.aln.toml`](patna-line4.aln.toml) | `line-4` | 21,491.4 m | 9 |
| [`patna-line5.aln.toml`](patna-line5.aln.toml) | `line-5` | 24,684.3 m | 8 |
| [`patna-line6.aln.toml`](patna-line6.aln.toml) | `line-6` | 52,051.3 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
