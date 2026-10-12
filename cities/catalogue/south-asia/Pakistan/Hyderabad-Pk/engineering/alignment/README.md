# Hyderabad-Pk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hyderabad-pk-line1.aln.toml`](hyderabad-pk-line1.aln.toml) | `line-1` | 17,855.5 m | 13 |
| [`hyderabad-pk-line2.aln.toml`](hyderabad-pk-line2.aln.toml) | `line-2` | 22,268.2 m | 21 |
| [`hyderabad-pk-line3.aln.toml`](hyderabad-pk-line3.aln.toml) | `line-3` | 20,996.4 m | 9 |
| [`hyderabad-pk-line4.aln.toml`](hyderabad-pk-line4.aln.toml) | `line-4` | 27,859.0 m | 12 |
| [`hyderabad-pk-line5.aln.toml`](hyderabad-pk-line5.aln.toml) | `line-5` | 32,242.3 m | 24 |
| [`hyderabad-pk-line6.aln.toml`](hyderabad-pk-line6.aln.toml) | `line-6` | 64,111.4 m | 20 |
| [`hyderabad-pk-line7.aln.toml`](hyderabad-pk-line7.aln.toml) | `line-7` | 4,362.5 m | 4 |
| [`hyderabad-pk-line8.aln.toml`](hyderabad-pk-line8.aln.toml) | `line-8` | 13,339.7 m | 7 |
| [`hyderabad-pk-line9.aln.toml`](hyderabad-pk-line9.aln.toml) | `line-9` | 12,926.3 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
