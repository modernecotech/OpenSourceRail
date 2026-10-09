# Beira Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`beira-line1.aln.toml`](beira-line1.aln.toml) | `line-1` | 13,900.4 m | 10 |
| [`beira-line10.aln.toml`](beira-line10.aln.toml) | `line-10` | 3,412.2 m | 3 |
| [`beira-line11.aln.toml`](beira-line11.aln.toml) | `line-11` | 5,550.7 m | 4 |
| [`beira-line12.aln.toml`](beira-line12.aln.toml) | `line-12` | 3,525.6 m | 3 |
| [`beira-line13.aln.toml`](beira-line13.aln.toml) | `line-13` | 2,536.8 m | 2 |
| [`beira-line2.aln.toml`](beira-line2.aln.toml) | `line-2` | 9,812.3 m | 7 |
| [`beira-line3.aln.toml`](beira-line3.aln.toml) | `line-3` | 14,973.0 m | 9 |
| [`beira-line4.aln.toml`](beira-line4.aln.toml) | `line-4` | 3,672.8 m | 3 |
| [`beira-line5.aln.toml`](beira-line5.aln.toml) | `line-5` | 2,625.1 m | 2 |
| [`beira-line6.aln.toml`](beira-line6.aln.toml) | `line-6` | 3,365.3 m | 3 |
| [`beira-line7.aln.toml`](beira-line7.aln.toml) | `line-7` | 4,406.8 m | 3 |
| [`beira-line8.aln.toml`](beira-line8.aln.toml) | `line-8` | 4,277.9 m | 3 |
| [`beira-line9.aln.toml`](beira-line9.aln.toml) | `line-9` | 3,745.0 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
