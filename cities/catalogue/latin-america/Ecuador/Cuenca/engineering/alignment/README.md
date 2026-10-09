# Cuenca Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`cuenca-line1.aln.toml`](cuenca-line1.aln.toml) | `line-1` | 21,088.8 m | 12 |
| [`cuenca-line10.aln.toml`](cuenca-line10.aln.toml) | `line-10` | 7,050.9 m | 5 |
| [`cuenca-line11.aln.toml`](cuenca-line11.aln.toml) | `line-11` | 8,655.0 m | 6 |
| [`cuenca-line2.aln.toml`](cuenca-line2.aln.toml) | `line-2` | 19,575.5 m | 12 |
| [`cuenca-line3.aln.toml`](cuenca-line3.aln.toml) | `line-3` | 19,168.9 m | 12 |
| [`cuenca-line4.aln.toml`](cuenca-line4.aln.toml) | `line-4` | 4,783.9 m | 3 |
| [`cuenca-line5.aln.toml`](cuenca-line5.aln.toml) | `line-5` | 5,441.8 m | 4 |
| [`cuenca-line6.aln.toml`](cuenca-line6.aln.toml) | `line-6` | 3,864.5 m | 3 |
| [`cuenca-line7.aln.toml`](cuenca-line7.aln.toml) | `line-7` | 5,257.6 m | 4 |
| [`cuenca-line8.aln.toml`](cuenca-line8.aln.toml) | `line-8` | 8,459.9 m | 6 |
| [`cuenca-line9.aln.toml`](cuenca-line9.aln.toml) | `line-9` | 2,871.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
