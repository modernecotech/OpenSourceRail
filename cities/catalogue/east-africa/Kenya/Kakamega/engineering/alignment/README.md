# Kakamega Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kakamega-line1.aln.toml`](kakamega-line1.aln.toml) | `line-1` | 11,581.5 m | 8 |
| [`kakamega-line10.aln.toml`](kakamega-line10.aln.toml) | `line-10` | 4,339.4 m | 3 |
| [`kakamega-line11.aln.toml`](kakamega-line11.aln.toml) | `line-11` | 3,148.3 m | 2 |
| [`kakamega-line2.aln.toml`](kakamega-line2.aln.toml) | `line-2` | 14,743.9 m | 10 |
| [`kakamega-line3.aln.toml`](kakamega-line3.aln.toml) | `line-3` | 11,723.8 m | 9 |
| [`kakamega-line4.aln.toml`](kakamega-line4.aln.toml) | `line-4` | 4,001.3 m | 4 |
| [`kakamega-line5.aln.toml`](kakamega-line5.aln.toml) | `line-5` | 9,279.1 m | 6 |
| [`kakamega-line6.aln.toml`](kakamega-line6.aln.toml) | `line-6` | 5,374.9 m | 4 |
| [`kakamega-line7.aln.toml`](kakamega-line7.aln.toml) | `line-7` | 5,627.1 m | 4 |
| [`kakamega-line8.aln.toml`](kakamega-line8.aln.toml) | `line-8` | 3,644.2 m | 3 |
| [`kakamega-line9.aln.toml`](kakamega-line9.aln.toml) | `line-9` | 2,123.9 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
