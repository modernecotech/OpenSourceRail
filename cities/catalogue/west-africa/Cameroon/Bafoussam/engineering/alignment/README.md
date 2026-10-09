# Bafoussam Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`bafoussam-line1.aln.toml`](bafoussam-line1.aln.toml) | `line-1` | 17,015.3 m | 10 |
| [`bafoussam-line10.aln.toml`](bafoussam-line10.aln.toml) | `line-10` | 11,000.4 m | 7 |
| [`bafoussam-line11.aln.toml`](bafoussam-line11.aln.toml) | `line-11` | 2,071.4 m | 2 |
| [`bafoussam-line12.aln.toml`](bafoussam-line12.aln.toml) | `line-12` | 11,047.4 m | 7 |
| [`bafoussam-line13.aln.toml`](bafoussam-line13.aln.toml) | `line-13` | 4,372.7 m | 3 |
| [`bafoussam-line14.aln.toml`](bafoussam-line14.aln.toml) | `line-14` | 2,271.4 m | 2 |
| [`bafoussam-line15.aln.toml`](bafoussam-line15.aln.toml) | `line-15` | 4,186.2 m | 3 |
| [`bafoussam-line2.aln.toml`](bafoussam-line2.aln.toml) | `line-2` | 19,623.9 m | 14 |
| [`bafoussam-line3.aln.toml`](bafoussam-line3.aln.toml) | `line-3` | 22,665.4 m | 14 |
| [`bafoussam-line4.aln.toml`](bafoussam-line4.aln.toml) | `line-4` | 3,074.0 m | 2 |
| [`bafoussam-line5.aln.toml`](bafoussam-line5.aln.toml) | `line-5` | 2,592.8 m | 2 |
| [`bafoussam-line6.aln.toml`](bafoussam-line6.aln.toml) | `line-6` | 4,906.5 m | 4 |
| [`bafoussam-line7.aln.toml`](bafoussam-line7.aln.toml) | `line-7` | 5,221.0 m | 4 |
| [`bafoussam-line8.aln.toml`](bafoussam-line8.aln.toml) | `line-8` | 2,109.7 m | 2 |
| [`bafoussam-line9.aln.toml`](bafoussam-line9.aln.toml) | `line-9` | 5,558.4 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
