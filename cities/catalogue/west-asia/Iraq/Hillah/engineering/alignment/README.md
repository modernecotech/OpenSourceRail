# Hillah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hillah-line1.aln.toml`](hillah-line1.aln.toml) | `line-1` | 21,398.5 m | 7 |
| [`hillah-line2.aln.toml`](hillah-line2.aln.toml) | `line-2` | 17,823.9 m | 6 |
| [`hillah-line3.aln.toml`](hillah-line3.aln.toml) | `line-3` | 21,216.0 m | 7 |
| [`hillah-line4.aln.toml`](hillah-line4.aln.toml) | `line-4` | 10,095.5 m | 4 |
| [`hillah-line5.aln.toml`](hillah-line5.aln.toml) | `line-5` | 4,119.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
