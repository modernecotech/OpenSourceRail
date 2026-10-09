# Khouribga Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`khouribga-line1.aln.toml`](khouribga-line1.aln.toml) | `line-1` | 6,847.5 m | 4 |
| [`khouribga-line2.aln.toml`](khouribga-line2.aln.toml) | `line-2` | 5,028.4 m | 4 |
| [`khouribga-line3.aln.toml`](khouribga-line3.aln.toml) | `line-3` | 3,667.4 m | 4 |
| [`khouribga-line4.aln.toml`](khouribga-line4.aln.toml) | `line-4` | 2,915.6 m | 3 |
| [`khouribga-line5.aln.toml`](khouribga-line5.aln.toml) | `line-5` | 2,665.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
