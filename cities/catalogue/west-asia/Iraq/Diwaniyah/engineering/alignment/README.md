# Diwaniyah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`diwaniyah-line1.aln.toml`](diwaniyah-line1.aln.toml) | `line-1` | 18,018.1 m | 12 |
| [`diwaniyah-line2.aln.toml`](diwaniyah-line2.aln.toml) | `line-2` | 8,473.3 m | 8 |
| [`diwaniyah-line3.aln.toml`](diwaniyah-line3.aln.toml) | `line-3` | 13,083.0 m | 8 |
| [`diwaniyah-line4.aln.toml`](diwaniyah-line4.aln.toml) | `line-4` | 4,689.0 m | 4 |
| [`diwaniyah-line5.aln.toml`](diwaniyah-line5.aln.toml) | `line-5` | 4,670.2 m | 3 |
| [`diwaniyah-line6.aln.toml`](diwaniyah-line6.aln.toml) | `line-6` | 5,989.8 m | 4 |
| [`diwaniyah-line7.aln.toml`](diwaniyah-line7.aln.toml) | `line-7` | 5,472.1 m | 4 |
| [`diwaniyah-line8.aln.toml`](diwaniyah-line8.aln.toml) | `line-8` | 8,938.0 m | 6 |
| [`diwaniyah-line9.aln.toml`](diwaniyah-line9.aln.toml) | `line-9` | 6,397.6 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
