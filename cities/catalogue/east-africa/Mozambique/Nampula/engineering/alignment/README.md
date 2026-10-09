# Nampula Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nampula-line1.aln.toml`](nampula-line1.aln.toml) | `line-1` | 12,619.0 m | 10 |
| [`nampula-line10.aln.toml`](nampula-line10.aln.toml) | `line-10` | 3,763.9 m | 3 |
| [`nampula-line11.aln.toml`](nampula-line11.aln.toml) | `line-11` | 3,635.6 m | 3 |
| [`nampula-line12.aln.toml`](nampula-line12.aln.toml) | `line-12` | 2,101.9 m | 2 |
| [`nampula-line13.aln.toml`](nampula-line13.aln.toml) | `line-13` | 4,586.8 m | 3 |
| [`nampula-line14.aln.toml`](nampula-line14.aln.toml) | `line-14` | 3,347.9 m | 3 |
| [`nampula-line15.aln.toml`](nampula-line15.aln.toml) | `line-15` | 3,239.7 m | 3 |
| [`nampula-line16.aln.toml`](nampula-line16.aln.toml) | `line-16` | 2,384.5 m | 2 |
| [`nampula-line2.aln.toml`](nampula-line2.aln.toml) | `line-2` | 18,943.2 m | 13 |
| [`nampula-line3.aln.toml`](nampula-line3.aln.toml) | `line-3` | 10,621.6 m | 8 |
| [`nampula-line4.aln.toml`](nampula-line4.aln.toml) | `line-4` | 4,213.0 m | 3 |
| [`nampula-line5.aln.toml`](nampula-line5.aln.toml) | `line-5` | 2,028.5 m | 2 |
| [`nampula-line6.aln.toml`](nampula-line6.aln.toml) | `line-6` | 2,354.6 m | 2 |
| [`nampula-line7.aln.toml`](nampula-line7.aln.toml) | `line-7` | 2,174.0 m | 2 |
| [`nampula-line8.aln.toml`](nampula-line8.aln.toml) | `line-8` | 5,408.8 m | 4 |
| [`nampula-line9.aln.toml`](nampula-line9.aln.toml) | `line-9` | 2,931.6 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
