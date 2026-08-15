# Ranchi Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`ranchi-line1.aln.toml`](ranchi-line1.aln.toml) | `line-1` | 35,590.9 m | 14 |
| [`ranchi-line2.aln.toml`](ranchi-line2.aln.toml) | `line-2` | 26,562.3 m | 10 |
| [`ranchi-line3.aln.toml`](ranchi-line3.aln.toml) | `line-3` | 22,881.7 m | 9 |
| [`ranchi-line4.aln.toml`](ranchi-line4.aln.toml) | `line-4` | 30,202.0 m | 11 |
| [`ranchi-line5.aln.toml`](ranchi-line5.aln.toml) | `line-5` | 27,069.2 m | 11 |
| [`ranchi-line6.aln.toml`](ranchi-line6.aln.toml) | `line-6` | 79,190.6 m | 22 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
