# Lyon Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`lyon-line1.aln.toml`](lyon-line1.aln.toml) | `line-1` | 42,913.0 m | 15 |
| [`lyon-line2.aln.toml`](lyon-line2.aln.toml) | `line-2` | 36,909.0 m | 13 |
| [`lyon-line3.aln.toml`](lyon-line3.aln.toml) | `line-3` | 20,504.2 m | 9 |
| [`lyon-line4.aln.toml`](lyon-line4.aln.toml) | `line-4` | 39,830.6 m | 12 |
| [`lyon-line5.aln.toml`](lyon-line5.aln.toml) | `line-5` | 26,016.7 m | 10 |
| [`lyon-line6.aln.toml`](lyon-line6.aln.toml) | `line-6` | 62,176.2 m | 18 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
