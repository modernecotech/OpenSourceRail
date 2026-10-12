# Basra Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`basra-line1.aln.toml`](basra-line1.aln.toml) | `line-1` | 48,286.2 m | 18 |
| [`basra-line10.aln.toml`](basra-line10.aln.toml) | `line-10` | 9,935.2 m | 3 |
| [`basra-line11.aln.toml`](basra-line11.aln.toml) | `line-11` | 6,585.5 m | 2 |
| [`basra-line2.aln.toml`](basra-line2.aln.toml) | `line-2` | 21,872.1 m | 17 |
| [`basra-line3.aln.toml`](basra-line3.aln.toml) | `line-3` | 41,543.8 m | 11 |
| [`basra-line4.aln.toml`](basra-line4.aln.toml) | `line-4` | 34,970.7 m | 12 |
| [`basra-line5.aln.toml`](basra-line5.aln.toml) | `line-5` | 41,191.3 m | 16 |
| [`basra-line6.aln.toml`](basra-line6.aln.toml) | `line-6` | 26,389.0 m | 10 |
| [`basra-line7.aln.toml`](basra-line7.aln.toml) | `line-7` | 95,210.4 m | 38 |
| [`basra-line8.aln.toml`](basra-line8.aln.toml) | `line-8` | 10,670.5 m | 4 |
| [`basra-line9.aln.toml`](basra-line9.aln.toml) | `line-9` | 11,353.7 m | 6 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
