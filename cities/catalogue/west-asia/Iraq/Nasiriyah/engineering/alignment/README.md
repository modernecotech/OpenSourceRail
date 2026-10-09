# Nasiriyah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nasiriyah-line1.aln.toml`](nasiriyah-line1.aln.toml) | `line-1` | 25,705.8 m | 14 |
| [`nasiriyah-line2.aln.toml`](nasiriyah-line2.aln.toml) | `line-2` | 9,530.0 m | 7 |
| [`nasiriyah-line3.aln.toml`](nasiriyah-line3.aln.toml) | `line-3` | 8,119.2 m | 7 |
| [`nasiriyah-line4.aln.toml`](nasiriyah-line4.aln.toml) | `line-4` | 5,390.3 m | 4 |
| [`nasiriyah-line5.aln.toml`](nasiriyah-line5.aln.toml) | `line-5` | 2,752.2 m | 2 |
| [`nasiriyah-line6.aln.toml`](nasiriyah-line6.aln.toml) | `line-6` | 3,473.3 m | 3 |
| [`nasiriyah-line7.aln.toml`](nasiriyah-line7.aln.toml) | `line-7` | 7,020.4 m | 5 |
| [`nasiriyah-line8.aln.toml`](nasiriyah-line8.aln.toml) | `line-8` | 10,805.9 m | 6 |
| [`nasiriyah-line9.aln.toml`](nasiriyah-line9.aln.toml) | `line-9` | 8,259.4 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
