# Hyderabad-Pk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hyderabad-pk-line1.aln.toml`](hyderabad-pk-line1.aln.toml) | `line-1` | 18,477.7 m | 7 |
| [`hyderabad-pk-line2.aln.toml`](hyderabad-pk-line2.aln.toml) | `line-2` | 20,778.3 m | 8 |
| [`hyderabad-pk-line3.aln.toml`](hyderabad-pk-line3.aln.toml) | `line-3` | 19,452.4 m | 7 |
| [`hyderabad-pk-line4.aln.toml`](hyderabad-pk-line4.aln.toml) | `line-4` | 29,366.6 m | 9 |
| [`hyderabad-pk-line5.aln.toml`](hyderabad-pk-line5.aln.toml) | `line-5` | 31,645.7 m | 10 |
| [`hyderabad-pk-line6.aln.toml`](hyderabad-pk-line6.aln.toml) | `line-6` | 60,241.7 m | 17 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
