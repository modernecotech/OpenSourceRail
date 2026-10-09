# East-London-Za Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`east-london-za-line1.aln.toml`](east-london-za-line1.aln.toml) | `line-1` | 17,460.7 m | 10 |
| [`east-london-za-line10.aln.toml`](east-london-za-line10.aln.toml) | `line-10` | 4,141.7 m | 3 |
| [`east-london-za-line2.aln.toml`](east-london-za-line2.aln.toml) | `line-2` | 20,744.6 m | 12 |
| [`east-london-za-line3.aln.toml`](east-london-za-line3.aln.toml) | `line-3` | 20,966.3 m | 13 |
| [`east-london-za-line4.aln.toml`](east-london-za-line4.aln.toml) | `line-4` | 4,857.0 m | 4 |
| [`east-london-za-line5.aln.toml`](east-london-za-line5.aln.toml) | `line-5` | 3,602.8 m | 3 |
| [`east-london-za-line6.aln.toml`](east-london-za-line6.aln.toml) | `line-6` | 8,065.1 m | 6 |
| [`east-london-za-line7.aln.toml`](east-london-za-line7.aln.toml) | `line-7` | 5,055.9 m | 4 |
| [`east-london-za-line8.aln.toml`](east-london-za-line8.aln.toml) | `line-8` | 5,325.2 m | 4 |
| [`east-london-za-line9.aln.toml`](east-london-za-line9.aln.toml) | `line-9` | 3,664.4 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
