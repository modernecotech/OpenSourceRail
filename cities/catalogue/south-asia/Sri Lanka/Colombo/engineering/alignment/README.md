# Colombo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`colombo-line1.aln.toml`](colombo-line1.aln.toml) | `line-1` | 29,410.3 m | 11 |
| [`colombo-line10.aln.toml`](colombo-line10.aln.toml) | `line-10` | 6,502.4 m | 2 |
| [`colombo-line11.aln.toml`](colombo-line11.aln.toml) | `line-11` | 6,612.4 m | 2 |
| [`colombo-line12.aln.toml`](colombo-line12.aln.toml) | `line-12` | 6,233.3 m | 3 |
| [`colombo-line13.aln.toml`](colombo-line13.aln.toml) | `line-13` | 9,508.3 m | 8 |
| [`colombo-line14.aln.toml`](colombo-line14.aln.toml) | `line-14` | 9,018.6 m | 9 |
| [`colombo-line2.aln.toml`](colombo-line2.aln.toml) | `line-2` | 29,895.7 m | 10 |
| [`colombo-line3.aln.toml`](colombo-line3.aln.toml) | `line-3` | 47,775.9 m | 22 |
| [`colombo-line4.aln.toml`](colombo-line4.aln.toml) | `line-4` | 29,853.1 m | 10 |
| [`colombo-line5.aln.toml`](colombo-line5.aln.toml) | `line-5` | 28,924.5 m | 16 |
| [`colombo-line6.aln.toml`](colombo-line6.aln.toml) | `line-6` | 30,473.1 m | 14 |
| [`colombo-line7.aln.toml`](colombo-line7.aln.toml) | `line-7` | 25,100.9 m | 14 |
| [`colombo-line8.aln.toml`](colombo-line8.aln.toml) | `line-8` | 25,388.9 m | 13 |
| [`colombo-line9.aln.toml`](colombo-line9.aln.toml) | `line-9` | 70,985.2 m | 38 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
