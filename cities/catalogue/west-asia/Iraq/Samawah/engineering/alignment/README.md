# Samawah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`samawah-line1.aln.toml`](samawah-line1.aln.toml) | `line-1` | 22,737.2 m | 15 |
| [`samawah-line2.aln.toml`](samawah-line2.aln.toml) | `line-2` | 10,480.9 m | 8 |
| [`samawah-line3.aln.toml`](samawah-line3.aln.toml) | `line-3` | 8,798.8 m | 6 |
| [`samawah-line4.aln.toml`](samawah-line4.aln.toml) | `line-4` | 9,346.9 m | 6 |
| [`samawah-line5.aln.toml`](samawah-line5.aln.toml) | `line-5` | 3,933.9 m | 4 |
| [`samawah-line6.aln.toml`](samawah-line6.aln.toml) | `line-6` | 6,705.5 m | 4 |
| [`samawah-line7.aln.toml`](samawah-line7.aln.toml) | `line-7` | 4,459.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
