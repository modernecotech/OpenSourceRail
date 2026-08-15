# Antananarivo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`antananarivo-line1.aln.toml`](antananarivo-line1.aln.toml) | `line-1` | 35,411.1 m | 21 |
| [`antananarivo-line2.aln.toml`](antananarivo-line2.aln.toml) | `line-2` | 29,354.0 m | 16 |
| [`antananarivo-line3.aln.toml`](antananarivo-line3.aln.toml) | `line-3` | 34,181.4 m | 20 |
| [`antananarivo-line4.aln.toml`](antananarivo-line4.aln.toml) | `line-4` | 25,700.6 m | 13 |
| [`antananarivo-line5.aln.toml`](antananarivo-line5.aln.toml) | `line-5` | 29,229.9 m | 17 |
| [`antananarivo-line6.aln.toml`](antananarivo-line6.aln.toml) | `line-6` | 35,453.9 m | 20 |
| [`antananarivo-line7.aln.toml`](antananarivo-line7.aln.toml) | `line-7` | 32,342.8 m | 16 |
| [`antananarivo-line8.aln.toml`](antananarivo-line8.aln.toml) | `line-8` | 29,503.4 m | 16 |
| [`antananarivo-line9.aln.toml`](antananarivo-line9.aln.toml) | `line-9` | 73,356.1 m | 39 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
