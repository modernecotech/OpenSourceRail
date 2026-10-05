# Kathmandu Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kathmandu-line1.aln.toml`](kathmandu-line1.aln.toml) | `line-1` | 31,867.9 m | 11 |
| [`kathmandu-line2.aln.toml`](kathmandu-line2.aln.toml) | `line-2` | 24,861.9 m | 12 |
| [`kathmandu-line3.aln.toml`](kathmandu-line3.aln.toml) | `line-3` | 15,445.9 m | 8 |
| [`kathmandu-line4.aln.toml`](kathmandu-line4.aln.toml) | `line-4` | 20,483.7 m | 11 |
| [`kathmandu-line5.aln.toml`](kathmandu-line5.aln.toml) | `line-5` | 25,941.2 m | 10 |
| [`kathmandu-line6.aln.toml`](kathmandu-line6.aln.toml) | `line-6` | 50,951.4 m | 19 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
