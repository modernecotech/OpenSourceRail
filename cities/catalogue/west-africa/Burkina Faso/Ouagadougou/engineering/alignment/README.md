# Ouagadougou Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ouagadougou-line1.aln.toml`](ouagadougou-line1.aln.toml) | `line-1` | 33,799.0 m | 11 |
| [`ouagadougou-line2.aln.toml`](ouagadougou-line2.aln.toml) | `line-2` | 20,008.2 m | 8 |
| [`ouagadougou-line3.aln.toml`](ouagadougou-line3.aln.toml) | `line-3` | 25,365.8 m | 10 |
| [`ouagadougou-line4.aln.toml`](ouagadougou-line4.aln.toml) | `line-4` | 27,503.2 m | 10 |
| [`ouagadougou-line5.aln.toml`](ouagadougou-line5.aln.toml) | `line-5` | 26,794.4 m | 8 |
| [`ouagadougou-line6.aln.toml`](ouagadougou-line6.aln.toml) | `line-6` | 60,577.6 m | 20 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
