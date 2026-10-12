# Antananarivo Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`antananarivo-line1.aln.toml`](antananarivo-line1.aln.toml) | `line-1` | 35,983.0 m | 45 |
| [`antananarivo-line10.aln.toml`](antananarivo-line10.aln.toml) | `line-10` | 6,806.9 m | 2 |
| [`antananarivo-line11.aln.toml`](antananarivo-line11.aln.toml) | `line-11` | 6,775.3 m | 3 |
| [`antananarivo-line12.aln.toml`](antananarivo-line12.aln.toml) | `line-12` | 6,603.8 m | 5 |
| [`antananarivo-line13.aln.toml`](antananarivo-line13.aln.toml) | `line-13` | 6,742.6 m | 4 |
| [`antananarivo-line14.aln.toml`](antananarivo-line14.aln.toml) | `line-14` | 8,324.4 m | 3 |
| [`antananarivo-line2.aln.toml`](antananarivo-line2.aln.toml) | `line-2` | 24,389.5 m | 10 |
| [`antananarivo-line3.aln.toml`](antananarivo-line3.aln.toml) | `line-3` | 29,591.7 m | 12 |
| [`antananarivo-line4.aln.toml`](antananarivo-line4.aln.toml) | `line-4` | 27,415.1 m | 8 |
| [`antananarivo-line5.aln.toml`](antananarivo-line5.aln.toml) | `line-5` | 30,050.4 m | 41 |
| [`antananarivo-line6.aln.toml`](antananarivo-line6.aln.toml) | `line-6` | 37,314.8 m | 22 |
| [`antananarivo-line7.aln.toml`](antananarivo-line7.aln.toml) | `line-7` | 33,298.1 m | 13 |
| [`antananarivo-line8.aln.toml`](antananarivo-line8.aln.toml) | `line-8` | 31,029.1 m | 10 |
| [`antananarivo-line9.aln.toml`](antananarivo-line9.aln.toml) | `line-9` | 71,737.1 m | 20 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
