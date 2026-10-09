# Dodoma Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`dodoma-line1.aln.toml`](dodoma-line1.aln.toml) | `line-1` | 12,960.7 m | 9 |
| [`dodoma-line10.aln.toml`](dodoma-line10.aln.toml) | `line-10` | 4,203.9 m | 3 |
| [`dodoma-line11.aln.toml`](dodoma-line11.aln.toml) | `line-11` | 6,375.9 m | 4 |
| [`dodoma-line12.aln.toml`](dodoma-line12.aln.toml) | `line-12` | 3,419.9 m | 3 |
| [`dodoma-line13.aln.toml`](dodoma-line13.aln.toml) | `line-13` | 3,506.8 m | 3 |
| [`dodoma-line14.aln.toml`](dodoma-line14.aln.toml) | `line-14` | 2,252.8 m | 2 |
| [`dodoma-line2.aln.toml`](dodoma-line2.aln.toml) | `line-2` | 14,602.4 m | 8 |
| [`dodoma-line3.aln.toml`](dodoma-line3.aln.toml) | `line-3` | 16,547.2 m | 12 |
| [`dodoma-line4.aln.toml`](dodoma-line4.aln.toml) | `line-4` | 4,723.9 m | 4 |
| [`dodoma-line5.aln.toml`](dodoma-line5.aln.toml) | `line-5` | 2,527.9 m | 2 |
| [`dodoma-line6.aln.toml`](dodoma-line6.aln.toml) | `line-6` | 4,219.3 m | 3 |
| [`dodoma-line7.aln.toml`](dodoma-line7.aln.toml) | `line-7` | 2,991.6 m | 2 |
| [`dodoma-line8.aln.toml`](dodoma-line8.aln.toml) | `line-8` | 3,446.4 m | 3 |
| [`dodoma-line9.aln.toml`](dodoma-line9.aln.toml) | `line-9` | 6,374.1 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
