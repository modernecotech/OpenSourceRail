# Sialkot Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sialkot-line1.aln.toml`](sialkot-line1.aln.toml) | `line-1` | 17,547.3 m | 6 |
| [`sialkot-line2.aln.toml`](sialkot-line2.aln.toml) | `line-2` | 22,687.3 m | 7 |
| [`sialkot-line3.aln.toml`](sialkot-line3.aln.toml) | `line-3` | 14,171.2 m | 5 |
| [`sialkot-line4.aln.toml`](sialkot-line4.aln.toml) | `line-4` | 4,955.0 m | 3 |
| [`sialkot-line5.aln.toml`](sialkot-line5.aln.toml) | `line-5` | 4,004.2 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
