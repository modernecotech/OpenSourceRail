# Ouagadougou Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ouagadougou-line1.aln.toml`](ouagadougou-line1.aln.toml) | `line-1` | 38,354.2 m | 12 |
| [`ouagadougou-line2.aln.toml`](ouagadougou-line2.aln.toml) | `line-2` | 24,219.0 m | 10 |
| [`ouagadougou-line3.aln.toml`](ouagadougou-line3.aln.toml) | `line-3` | 28,451.8 m | 11 |
| [`ouagadougou-line4.aln.toml`](ouagadougou-line4.aln.toml) | `line-4` | 32,682.0 m | 12 |
| [`ouagadougou-line5.aln.toml`](ouagadougou-line5.aln.toml) | `line-5` | 32,412.1 m | 10 |
| [`ouagadougou-line6.aln.toml`](ouagadougou-line6.aln.toml) | `line-6` | 65,447.6 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
