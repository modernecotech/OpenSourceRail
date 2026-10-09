# Kitale Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kitale-line1.aln.toml`](kitale-line1.aln.toml) | `line-1` | 12,609.1 m | 8 |
| [`kitale-line10.aln.toml`](kitale-line10.aln.toml) | `line-10` | 2,547.9 m | 2 |
| [`kitale-line11.aln.toml`](kitale-line11.aln.toml) | `line-11` | 5,936.8 m | 4 |
| [`kitale-line12.aln.toml`](kitale-line12.aln.toml) | `line-12` | 2,143.1 m | 2 |
| [`kitale-line13.aln.toml`](kitale-line13.aln.toml) | `line-13` | 5,615.8 m | 4 |
| [`kitale-line2.aln.toml`](kitale-line2.aln.toml) | `line-2` | 13,430.7 m | 9 |
| [`kitale-line3.aln.toml`](kitale-line3.aln.toml) | `line-3` | 10,410.7 m | 8 |
| [`kitale-line4.aln.toml`](kitale-line4.aln.toml) | `line-4` | 2,571.4 m | 2 |
| [`kitale-line5.aln.toml`](kitale-line5.aln.toml) | `line-5` | 4,917.9 m | 3 |
| [`kitale-line6.aln.toml`](kitale-line6.aln.toml) | `line-6` | 2,340.2 m | 2 |
| [`kitale-line7.aln.toml`](kitale-line7.aln.toml) | `line-7` | 4,931.1 m | 4 |
| [`kitale-line8.aln.toml`](kitale-line8.aln.toml) | `line-8` | 2,129.7 m | 2 |
| [`kitale-line9.aln.toml`](kitale-line9.aln.toml) | `line-9` | 2,858.8 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
