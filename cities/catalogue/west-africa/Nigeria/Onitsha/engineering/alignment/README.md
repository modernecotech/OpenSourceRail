# Onitsha Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`onitsha-line1.aln.toml`](onitsha-line1.aln.toml) | `line-1` | 25,218.0 m | 9 |
| [`onitsha-line2.aln.toml`](onitsha-line2.aln.toml) | `line-2` | 39,990.4 m | 11 |
| [`onitsha-line3.aln.toml`](onitsha-line3.aln.toml) | `line-3` | 42,558.6 m | 15 |
| [`onitsha-line4.aln.toml`](onitsha-line4.aln.toml) | `line-4` | 15,015.6 m | 9 |
| [`onitsha-line5.aln.toml`](onitsha-line5.aln.toml) | `line-5` | 91,497.1 m | 27 |
| [`onitsha-line6.aln.toml`](onitsha-line6.aln.toml) | `line-6` | 5,633.9 m | 4 |
| [`onitsha-line7.aln.toml`](onitsha-line7.aln.toml) | `line-7` | 5,333.6 m | 2 |
| [`onitsha-line8.aln.toml`](onitsha-line8.aln.toml) | `line-8` | 5,529.8 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
