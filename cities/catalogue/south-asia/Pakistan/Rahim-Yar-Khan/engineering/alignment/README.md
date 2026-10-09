# Rahim-Yar-Khan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`rahim-yar-khan-line1.aln.toml`](rahim-yar-khan-line1.aln.toml) | `line-1` | 7,713.2 m | 7 |
| [`rahim-yar-khan-line10.aln.toml`](rahim-yar-khan-line10.aln.toml) | `line-10` | 3,016.5 m | 4 |
| [`rahim-yar-khan-line2.aln.toml`](rahim-yar-khan-line2.aln.toml) | `line-2` | 17,996.0 m | 12 |
| [`rahim-yar-khan-line3.aln.toml`](rahim-yar-khan-line3.aln.toml) | `line-3` | 25,262.7 m | 18 |
| [`rahim-yar-khan-line4.aln.toml`](rahim-yar-khan-line4.aln.toml) | `line-4` | 5,109.3 m | 4 |
| [`rahim-yar-khan-line5.aln.toml`](rahim-yar-khan-line5.aln.toml) | `line-5` | 4,399.3 m | 3 |
| [`rahim-yar-khan-line6.aln.toml`](rahim-yar-khan-line6.aln.toml) | `line-6` | 9,044.8 m | 6 |
| [`rahim-yar-khan-line7.aln.toml`](rahim-yar-khan-line7.aln.toml) | `line-7` | 3,044.2 m | 2 |
| [`rahim-yar-khan-line8.aln.toml`](rahim-yar-khan-line8.aln.toml) | `line-8` | 6,484.9 m | 5 |
| [`rahim-yar-khan-line9.aln.toml`](rahim-yar-khan-line9.aln.toml) | `line-9` | 18,872.1 m | 12 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
