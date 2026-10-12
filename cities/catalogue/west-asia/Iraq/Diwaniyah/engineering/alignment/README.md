# Diwaniyah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`diwaniyah-line1.aln.toml`](diwaniyah-line1.aln.toml) | `line-1` | 18,018.1 m | 6 |
| [`diwaniyah-line2.aln.toml`](diwaniyah-line2.aln.toml) | `line-2` | 8,473.3 m | 4 |
| [`diwaniyah-line3.aln.toml`](diwaniyah-line3.aln.toml) | `line-3` | 16,381.7 m | 5 |
| [`diwaniyah-line4.aln.toml`](diwaniyah-line4.aln.toml) | `line-4` | 4,670.2 m | 2 |
| [`diwaniyah-line5.aln.toml`](diwaniyah-line5.aln.toml) | `line-5` | 5,989.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
