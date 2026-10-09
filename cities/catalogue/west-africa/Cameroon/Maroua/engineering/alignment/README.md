# Maroua Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`maroua-line1.aln.toml`](maroua-line1.aln.toml) | `line-1` | 23,818.2 m | 16 |
| [`maroua-line10.aln.toml`](maroua-line10.aln.toml) | `line-10` | 5,778.1 m | 4 |
| [`maroua-line11.aln.toml`](maroua-line11.aln.toml) | `line-11` | 3,357.1 m | 3 |
| [`maroua-line12.aln.toml`](maroua-line12.aln.toml) | `line-12` | 6,300.6 m | 4 |
| [`maroua-line13.aln.toml`](maroua-line13.aln.toml) | `line-13` | 3,201.3 m | 3 |
| [`maroua-line2.aln.toml`](maroua-line2.aln.toml) | `line-2` | 14,541.0 m | 9 |
| [`maroua-line3.aln.toml`](maroua-line3.aln.toml) | `line-3` | 7,445.1 m | 8 |
| [`maroua-line4.aln.toml`](maroua-line4.aln.toml) | `line-4` | 6,353.3 m | 4 |
| [`maroua-line5.aln.toml`](maroua-line5.aln.toml) | `line-5` | 2,915.9 m | 2 |
| [`maroua-line6.aln.toml`](maroua-line6.aln.toml) | `line-6` | 2,624.2 m | 2 |
| [`maroua-line7.aln.toml`](maroua-line7.aln.toml) | `line-7` | 3,177.1 m | 3 |
| [`maroua-line8.aln.toml`](maroua-line8.aln.toml) | `line-8` | 5,556.1 m | 4 |
| [`maroua-line9.aln.toml`](maroua-line9.aln.toml) | `line-9` | 5,835.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
