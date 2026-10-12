# Jos Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`jos-line1.aln.toml`](jos-line1.aln.toml) | `line-1` | 22,408.9 m | 6 |
| [`jos-line2.aln.toml`](jos-line2.aln.toml) | `line-2` | 13,305.5 m | 5 |
| [`jos-line3.aln.toml`](jos-line3.aln.toml) | `line-3` | 11,594.4 m | 5 |
| [`jos-line4.aln.toml`](jos-line4.aln.toml) | `line-4` | 6,244.4 m | 3 |
| [`jos-line5.aln.toml`](jos-line5.aln.toml) | `line-5` | 4,837.3 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
