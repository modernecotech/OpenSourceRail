# Safi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`safi-line1.aln.toml`](safi-line1.aln.toml) | `line-1` | 18,709.2 m | 11 |
| [`safi-line2.aln.toml`](safi-line2.aln.toml) | `line-2` | 8,294.7 m | 6 |
| [`safi-line3.aln.toml`](safi-line3.aln.toml) | `line-3` | 7,626.1 m | 6 |
| [`safi-line4.aln.toml`](safi-line4.aln.toml) | `line-4` | 2,632.2 m | 4 |
| [`safi-line5.aln.toml`](safi-line5.aln.toml) | `line-5` | 3,173.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
