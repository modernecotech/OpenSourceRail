# Sylhet Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sylhet-line1.aln.toml`](sylhet-line1.aln.toml) | `line-1` | 10,195.9 m | 7 |
| [`sylhet-line10.aln.toml`](sylhet-line10.aln.toml) | `line-10` | 4,275.0 m | 3 |
| [`sylhet-line11.aln.toml`](sylhet-line11.aln.toml) | `line-11` | 3,570.8 m | 3 |
| [`sylhet-line12.aln.toml`](sylhet-line12.aln.toml) | `line-12` | 3,060.8 m | 3 |
| [`sylhet-line2.aln.toml`](sylhet-line2.aln.toml) | `line-2` | 21,181.3 m | 13 |
| [`sylhet-line3.aln.toml`](sylhet-line3.aln.toml) | `line-3` | 9,670.0 m | 6 |
| [`sylhet-line4.aln.toml`](sylhet-line4.aln.toml) | `line-4` | 4,633.0 m | 4 |
| [`sylhet-line5.aln.toml`](sylhet-line5.aln.toml) | `line-5` | 5,604.2 m | 4 |
| [`sylhet-line6.aln.toml`](sylhet-line6.aln.toml) | `line-6` | 6,254.7 m | 4 |
| [`sylhet-line7.aln.toml`](sylhet-line7.aln.toml) | `line-7` | 5,015.3 m | 4 |
| [`sylhet-line8.aln.toml`](sylhet-line8.aln.toml) | `line-8` | 2,078.8 m | 2 |
| [`sylhet-line9.aln.toml`](sylhet-line9.aln.toml) | `line-9` | 6,013.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
