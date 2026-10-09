# Nablus Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`nablus-line1.aln.toml`](nablus-line1.aln.toml) | `line-1` | 16,811.4 m | 12 |
| [`nablus-line10.aln.toml`](nablus-line10.aln.toml) | `line-10` | 2,205.3 m | 2 |
| [`nablus-line11.aln.toml`](nablus-line11.aln.toml) | `line-11` | 2,167.1 m | 2 |
| [`nablus-line12.aln.toml`](nablus-line12.aln.toml) | `line-12` | 4,354.5 m | 3 |
| [`nablus-line13.aln.toml`](nablus-line13.aln.toml) | `line-13` | 2,356.6 m | 2 |
| [`nablus-line14.aln.toml`](nablus-line14.aln.toml) | `line-14` | 6,309.9 m | 4 |
| [`nablus-line2.aln.toml`](nablus-line2.aln.toml) | `line-2` | 25,331.3 m | 15 |
| [`nablus-line3.aln.toml`](nablus-line3.aln.toml) | `line-3` | 20,201.2 m | 14 |
| [`nablus-line4.aln.toml`](nablus-line4.aln.toml) | `line-4` | 5,171.9 m | 5 |
| [`nablus-line5.aln.toml`](nablus-line5.aln.toml) | `line-5` | 4,565.8 m | 4 |
| [`nablus-line6.aln.toml`](nablus-line6.aln.toml) | `line-6` | 7,931.2 m | 6 |
| [`nablus-line7.aln.toml`](nablus-line7.aln.toml) | `line-7` | 2,792.5 m | 2 |
| [`nablus-line8.aln.toml`](nablus-line8.aln.toml) | `line-8` | 9,653.2 m | 5 |
| [`nablus-line9.aln.toml`](nablus-line9.aln.toml) | `line-9` | 9,495.8 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
