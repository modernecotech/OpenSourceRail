# Zagazig Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`zagazig-line1.aln.toml`](zagazig-line1.aln.toml) | `line-1` | 15,772.5 m | 10 |
| [`zagazig-line2.aln.toml`](zagazig-line2.aln.toml) | `line-2` | 8,552.4 m | 7 |
| [`zagazig-line3.aln.toml`](zagazig-line3.aln.toml) | `line-3` | 12,159.0 m | 8 |
| [`zagazig-line4.aln.toml`](zagazig-line4.aln.toml) | `line-4` | 3,728.5 m | 3 |
| [`zagazig-line5.aln.toml`](zagazig-line5.aln.toml) | `line-5` | 7,603.8 m | 5 |
| [`zagazig-line6.aln.toml`](zagazig-line6.aln.toml) | `line-6` | 11,327.1 m | 7 |
| [`zagazig-line7.aln.toml`](zagazig-line7.aln.toml) | `line-7` | 2,867.9 m | 2 |
| [`zagazig-line8.aln.toml`](zagazig-line8.aln.toml) | `line-8` | 4,403.0 m | 3 |
| [`zagazig-line9.aln.toml`](zagazig-line9.aln.toml) | `line-9` | 6,055.9 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
