# Kabul Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kabul-line1.aln.toml`](kabul-line1.aln.toml) | `line-1` | 29,996.9 m | 16 |
| [`kabul-line10.aln.toml`](kabul-line10.aln.toml) | `line-10` | 4,852.4 m | 2 |
| [`kabul-line11.aln.toml`](kabul-line11.aln.toml) | `line-11` | 13,417.6 m | 5 |
| [`kabul-line2.aln.toml`](kabul-line2.aln.toml) | `line-2` | 34,380.3 m | 40 |
| [`kabul-line3.aln.toml`](kabul-line3.aln.toml) | `line-3` | 24,912.2 m | 23 |
| [`kabul-line4.aln.toml`](kabul-line4.aln.toml) | `line-4` | 30,235.0 m | 19 |
| [`kabul-line5.aln.toml`](kabul-line5.aln.toml) | `line-5` | 31,672.4 m | 34 |
| [`kabul-line6.aln.toml`](kabul-line6.aln.toml) | `line-6` | 22,676.1 m | 11 |
| [`kabul-line7.aln.toml`](kabul-line7.aln.toml) | `line-7` | 56,942.3 m | 50 |
| [`kabul-line8.aln.toml`](kabul-line8.aln.toml) | `line-8` | 5,627.6 m | 3 |
| [`kabul-line9.aln.toml`](kabul-line9.aln.toml) | `line-9` | 5,416.7 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
