# Hyderabad-Pk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hyderabad-pk-line1.aln.toml`](hyderabad-pk-line1.aln.toml) | `line-1` | 14,532.7 m | 6 |
| [`hyderabad-pk-line2.aln.toml`](hyderabad-pk-line2.aln.toml) | `line-2` | 17,630.7 m | 7 |
| [`hyderabad-pk-line3.aln.toml`](hyderabad-pk-line3.aln.toml) | `line-3` | 15,918.4 m | 7 |
| [`hyderabad-pk-line4.aln.toml`](hyderabad-pk-line4.aln.toml) | `line-4` | 27,801.5 m | 9 |
| [`hyderabad-pk-line5.aln.toml`](hyderabad-pk-line5.aln.toml) | `line-5` | 28,550.2 m | 9 |
| [`hyderabad-pk-line6.aln.toml`](hyderabad-pk-line6.aln.toml) | `line-6` | 54,628.4 m | 15 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
