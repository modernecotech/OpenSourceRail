# Sayun Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sayun-line1.aln.toml`](sayun-line1.aln.toml) | `line-1` | 13,053.4 m | 8 |
| [`sayun-line2.aln.toml`](sayun-line2.aln.toml) | `line-2` | 3,676.6 m | 3 |
| [`sayun-line3.aln.toml`](sayun-line3.aln.toml) | `line-3` | 4,168.5 m | 4 |
| [`sayun-line4.aln.toml`](sayun-line4.aln.toml) | `line-4` | 4,429.1 m | 4 |
| [`sayun-line5.aln.toml`](sayun-line5.aln.toml) | `line-5` | 6,613.9 m | 5 |
| [`sayun-line6.aln.toml`](sayun-line6.aln.toml) | `line-6` | 3,745.3 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
