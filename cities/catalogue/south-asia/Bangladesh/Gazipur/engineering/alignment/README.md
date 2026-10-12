# Gazipur Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`gazipur-line1.aln.toml`](gazipur-line1.aln.toml) | `line-1` | 39,709.2 m | 17 |
| [`gazipur-line2.aln.toml`](gazipur-line2.aln.toml) | `line-2` | 36,169.3 m | 11 |
| [`gazipur-line3.aln.toml`](gazipur-line3.aln.toml) | `line-3` | 46,869.6 m | 16 |
| [`gazipur-line4.aln.toml`](gazipur-line4.aln.toml) | `line-4` | 50,461.1 m | 15 |
| [`gazipur-line5.aln.toml`](gazipur-line5.aln.toml) | `line-5` | 30,420.5 m | 9 |
| [`gazipur-line6.aln.toml`](gazipur-line6.aln.toml) | `line-6` | 66,499.4 m | 20 |
| [`gazipur-line7.aln.toml`](gazipur-line7.aln.toml) | `line-7` | 7,467.8 m | 3 |
| [`gazipur-line8.aln.toml`](gazipur-line8.aln.toml) | `line-8` | 5,486.4 m | 3 |
| [`gazipur-line9.aln.toml`](gazipur-line9.aln.toml) | `line-9` | 6,615.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
