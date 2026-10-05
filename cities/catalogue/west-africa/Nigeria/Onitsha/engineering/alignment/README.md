# Onitsha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`onitsha-line1.aln.toml`](onitsha-line1.aln.toml) | `line-1` | 25,557.7 m | 8 |
| [`onitsha-line2.aln.toml`](onitsha-line2.aln.toml) | `line-2` | 34,873.5 m | 14 |
| [`onitsha-line3.aln.toml`](onitsha-line3.aln.toml) | `line-3` | 29,239.7 m | 12 |
| [`onitsha-line4.aln.toml`](onitsha-line4.aln.toml) | `line-4` | 15,015.6 m | 6 |
| [`onitsha-line5.aln.toml`](onitsha-line5.aln.toml) | `line-5` | 90,747.3 m | 25 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
