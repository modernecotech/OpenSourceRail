# Omdurman Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`omdurman-line1.aln.toml`](omdurman-line1.aln.toml) | `line-1` | 41,724.3 m | 29 |
| [`omdurman-line2.aln.toml`](omdurman-line2.aln.toml) | `line-2` | 48,964.1 m | 36 |
| [`omdurman-line3.aln.toml`](omdurman-line3.aln.toml) | `line-3` | 42,107.1 m | 14 |
| [`omdurman-line4.aln.toml`](omdurman-line4.aln.toml) | `line-4` | 43,973.5 m | 43 |
| [`omdurman-line5.aln.toml`](omdurman-line5.aln.toml) | `line-5` | 26,827.8 m | 13 |
| [`omdurman-line6.aln.toml`](omdurman-line6.aln.toml) | `line-6` | 89,229.9 m | 26 |
| [`omdurman-line7.aln.toml`](omdurman-line7.aln.toml) | `line-7` | 6,440.5 m | 2 |
| [`omdurman-line8.aln.toml`](omdurman-line8.aln.toml) | `line-8` | 6,745.3 m | 2 |
| [`omdurman-line9.aln.toml`](omdurman-line9.aln.toml) | `line-9` | 7,429.8 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
