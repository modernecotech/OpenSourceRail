# Kano Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kano-line1.aln.toml`](kano-line1.aln.toml) | `line-1` | 37,977.5 m | 16 |
| [`kano-line2.aln.toml`](kano-line2.aln.toml) | `line-2` | 43,236.4 m | 20 |
| [`kano-line3.aln.toml`](kano-line3.aln.toml) | `line-3` | 39,836.4 m | 17 |
| [`kano-line4.aln.toml`](kano-line4.aln.toml) | `line-4` | 35,430.4 m | 17 |
| [`kano-line5.aln.toml`](kano-line5.aln.toml) | `line-5` | 36,189.3 m | 15 |
| [`kano-line6.aln.toml`](kano-line6.aln.toml) | `line-6` | 30,259.9 m | 15 |
| [`kano-line7.aln.toml`](kano-line7.aln.toml) | `line-7` | 48,830.0 m | 20 |
| [`kano-line8.aln.toml`](kano-line8.aln.toml) | `line-8` | 44,056.1 m | 17 |
| [`kano-line9.aln.toml`](kano-line9.aln.toml) | `line-9` | 83,165.4 m | 29 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
