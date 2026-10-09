# Kathmandu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kathmandu-line1.aln.toml`](kathmandu-line1.aln.toml) | `line-1` | 31,867.9 m | 21 |
| [`kathmandu-line10.aln.toml`](kathmandu-line10.aln.toml) | `line-10` | 3,436.8 m | 3 |
| [`kathmandu-line11.aln.toml`](kathmandu-line11.aln.toml) | `line-11` | 4,612.2 m | 4 |
| [`kathmandu-line12.aln.toml`](kathmandu-line12.aln.toml) | `line-12` | 4,251.6 m | 3 |
| [`kathmandu-line13.aln.toml`](kathmandu-line13.aln.toml) | `line-13` | 4,140.7 m | 3 |
| [`kathmandu-line2.aln.toml`](kathmandu-line2.aln.toml) | `line-2` | 24,861.9 m | 16 |
| [`kathmandu-line3.aln.toml`](kathmandu-line3.aln.toml) | `line-3` | 15,405.9 m | 11 |
| [`kathmandu-line4.aln.toml`](kathmandu-line4.aln.toml) | `line-4` | 20,483.7 m | 13 |
| [`kathmandu-line5.aln.toml`](kathmandu-line5.aln.toml) | `line-5` | 25,941.2 m | 17 |
| [`kathmandu-line6.aln.toml`](kathmandu-line6.aln.toml) | `line-6` | 50,911.4 m | 27 |
| [`kathmandu-line7.aln.toml`](kathmandu-line7.aln.toml) | `line-7` | 8,559.2 m | 6 |
| [`kathmandu-line8.aln.toml`](kathmandu-line8.aln.toml) | `line-8` | 3,676.2 m | 3 |
| [`kathmandu-line9.aln.toml`](kathmandu-line9.aln.toml) | `line-9` | 7,571.3 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
