# Dammam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dammam-line1.aln.toml`](dammam-line1.aln.toml) | `line-1` | 45,162.3 m | 20 |
| [`dammam-line2.aln.toml`](dammam-line2.aln.toml) | `line-2` | 34,501.9 m | 14 |
| [`dammam-line3.aln.toml`](dammam-line3.aln.toml) | `line-3` | 25,732.5 m | 11 |
| [`dammam-line4.aln.toml`](dammam-line4.aln.toml) | `line-4` | 28,288.5 m | 13 |
| [`dammam-line5.aln.toml`](dammam-line5.aln.toml) | `line-5` | 43,696.0 m | 18 |
| [`dammam-line6.aln.toml`](dammam-line6.aln.toml) | `line-6` | 90,418.1 m | 31 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
