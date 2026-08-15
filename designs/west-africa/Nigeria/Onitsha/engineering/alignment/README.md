# Onitsha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`onitsha-line1.aln.toml`](onitsha-line1.aln.toml) | `line-1` | 20,348.7 m | 8 |
| [`onitsha-line2.aln.toml`](onitsha-line2.aln.toml) | `line-2` | 32,415.0 m | 10 |
| [`onitsha-line3.aln.toml`](onitsha-line3.aln.toml) | `line-3` | 32,783.3 m | 10 |
| [`onitsha-line4.aln.toml`](onitsha-line4.aln.toml) | `line-4` | 16,881.6 m | 7 |
| [`onitsha-line5.aln.toml`](onitsha-line5.aln.toml) | `line-5` | 86,174.5 m | 28 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
