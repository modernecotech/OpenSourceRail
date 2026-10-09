# Hillah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`hillah-line1.aln.toml`](hillah-line1.aln.toml) | `line-1` | 17,902.1 m | 10 |
| [`hillah-line10.aln.toml`](hillah-line10.aln.toml) | `line-10` | 4,251.0 m | 3 |
| [`hillah-line11.aln.toml`](hillah-line11.aln.toml) | `line-11` | 9,567.5 m | 6 |
| [`hillah-line2.aln.toml`](hillah-line2.aln.toml) | `line-2` | 17,823.9 m | 11 |
| [`hillah-line3.aln.toml`](hillah-line3.aln.toml) | `line-3` | 18,119.9 m | 12 |
| [`hillah-line4.aln.toml`](hillah-line4.aln.toml) | `line-4` | 9,951.9 m | 6 |
| [`hillah-line5.aln.toml`](hillah-line5.aln.toml) | `line-5` | 8,012.3 m | 5 |
| [`hillah-line6.aln.toml`](hillah-line6.aln.toml) | `line-6` | 9,968.4 m | 6 |
| [`hillah-line7.aln.toml`](hillah-line7.aln.toml) | `line-7` | 3,999.1 m | 3 |
| [`hillah-line8.aln.toml`](hillah-line8.aln.toml) | `line-8` | 2,861.9 m | 2 |
| [`hillah-line9.aln.toml`](hillah-line9.aln.toml) | `line-9` | 4,532.5 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
