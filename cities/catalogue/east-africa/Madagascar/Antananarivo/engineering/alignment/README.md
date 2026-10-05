# Antananarivo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`antananarivo-line1.aln.toml`](antananarivo-line1.aln.toml) | `line-1` | 27,836.4 m | 14 |
| [`antananarivo-line2.aln.toml`](antananarivo-line2.aln.toml) | `line-2` | 24,361.6 m | 11 |
| [`antananarivo-line3.aln.toml`](antananarivo-line3.aln.toml) | `line-3` | 28,818.0 m | 13 |
| [`antananarivo-line4.aln.toml`](antananarivo-line4.aln.toml) | `line-4` | 22,581.7 m | 9 |
| [`antananarivo-line5.aln.toml`](antananarivo-line5.aln.toml) | `line-5` | 25,757.0 m | 12 |
| [`antananarivo-line6.aln.toml`](antananarivo-line6.aln.toml) | `line-6` | 32,096.6 m | 12 |
| [`antananarivo-line7.aln.toml`](antananarivo-line7.aln.toml) | `line-7` | 28,933.7 m | 11 |
| [`antananarivo-line8.aln.toml`](antananarivo-line8.aln.toml) | `line-8` | 29,018.8 m | 13 |
| [`antananarivo-line9.aln.toml`](antananarivo-line9.aln.toml) | `line-9` | 71,237.3 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
