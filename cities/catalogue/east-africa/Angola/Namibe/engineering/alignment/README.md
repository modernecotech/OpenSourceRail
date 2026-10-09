# Namibe Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`namibe-line1.aln.toml`](namibe-line1.aln.toml) | `line-1` | 12,752.3 m | 8 |
| [`namibe-line10.aln.toml`](namibe-line10.aln.toml) | `line-10` | 3,636.2 m | 3 |
| [`namibe-line11.aln.toml`](namibe-line11.aln.toml) | `line-11` | 2,344.5 m | 2 |
| [`namibe-line2.aln.toml`](namibe-line2.aln.toml) | `line-2` | 10,005.6 m | 8 |
| [`namibe-line3.aln.toml`](namibe-line3.aln.toml) | `line-3` | 13,913.6 m | 10 |
| [`namibe-line4.aln.toml`](namibe-line4.aln.toml) | `line-4` | 2,748.8 m | 2 |
| [`namibe-line5.aln.toml`](namibe-line5.aln.toml) | `line-5` | 3,360.8 m | 3 |
| [`namibe-line6.aln.toml`](namibe-line6.aln.toml) | `line-6` | 2,462.5 m | 2 |
| [`namibe-line7.aln.toml`](namibe-line7.aln.toml) | `line-7` | 3,099.4 m | 3 |
| [`namibe-line8.aln.toml`](namibe-line8.aln.toml) | `line-8` | 6,251.0 m | 4 |
| [`namibe-line9.aln.toml`](namibe-line9.aln.toml) | `line-9` | 6,327.0 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
