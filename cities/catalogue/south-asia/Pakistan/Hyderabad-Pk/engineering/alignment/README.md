# Hyderabad-Pk Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hyderabad-pk-line1.aln.toml`](hyderabad-pk-line1.aln.toml) | `line-1` | 14,532.7 m | 11 |
| [`hyderabad-pk-line10.aln.toml`](hyderabad-pk-line10.aln.toml) | `line-10` | 6,844.9 m | 5 |
| [`hyderabad-pk-line11.aln.toml`](hyderabad-pk-line11.aln.toml) | `line-11` | 5,109.9 m | 3 |
| [`hyderabad-pk-line12.aln.toml`](hyderabad-pk-line12.aln.toml) | `line-12` | 3,627.4 m | 3 |
| [`hyderabad-pk-line13.aln.toml`](hyderabad-pk-line13.aln.toml) | `line-13` | 5,716.2 m | 4 |
| [`hyderabad-pk-line14.aln.toml`](hyderabad-pk-line14.aln.toml) | `line-14` | 4,656.1 m | 3 |
| [`hyderabad-pk-line15.aln.toml`](hyderabad-pk-line15.aln.toml) | `line-15` | 4,962.5 m | 3 |
| [`hyderabad-pk-line2.aln.toml`](hyderabad-pk-line2.aln.toml) | `line-2` | 16,178.2 m | 11 |
| [`hyderabad-pk-line3.aln.toml`](hyderabad-pk-line3.aln.toml) | `line-3` | 15,563.2 m | 12 |
| [`hyderabad-pk-line4.aln.toml`](hyderabad-pk-line4.aln.toml) | `line-4` | 27,859.0 m | 18 |
| [`hyderabad-pk-line5.aln.toml`](hyderabad-pk-line5.aln.toml) | `line-5` | 28,124.1 m | 17 |
| [`hyderabad-pk-line6.aln.toml`](hyderabad-pk-line6.aln.toml) | `line-6` | 55,017.5 m | 35 |
| [`hyderabad-pk-line7.aln.toml`](hyderabad-pk-line7.aln.toml) | `line-7` | 6,094.2 m | 5 |
| [`hyderabad-pk-line8.aln.toml`](hyderabad-pk-line8.aln.toml) | `line-8` | 4,469.9 m | 3 |
| [`hyderabad-pk-line9.aln.toml`](hyderabad-pk-line9.aln.toml) | `line-9` | 3,589.6 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
