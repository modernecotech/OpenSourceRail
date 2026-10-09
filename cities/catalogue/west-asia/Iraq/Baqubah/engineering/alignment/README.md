# Baqubah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`baqubah-line1.aln.toml`](baqubah-line1.aln.toml) | `line-1` | 11,135.7 m | 8 |
| [`baqubah-line10.aln.toml`](baqubah-line10.aln.toml) | `line-10` | 10,426.5 m | 7 |
| [`baqubah-line11.aln.toml`](baqubah-line11.aln.toml) | `line-11` | 5,663.2 m | 4 |
| [`baqubah-line12.aln.toml`](baqubah-line12.aln.toml) | `line-12` | 4,928.4 m | 4 |
| [`baqubah-line2.aln.toml`](baqubah-line2.aln.toml) | `line-2` | 21,987.8 m | 16 |
| [`baqubah-line3.aln.toml`](baqubah-line3.aln.toml) | `line-3` | 21,222.3 m | 14 |
| [`baqubah-line4.aln.toml`](baqubah-line4.aln.toml) | `line-4` | 4,674.5 m | 4 |
| [`baqubah-line5.aln.toml`](baqubah-line5.aln.toml) | `line-5` | 8,097.0 m | 5 |
| [`baqubah-line6.aln.toml`](baqubah-line6.aln.toml) | `line-6` | 4,319.7 m | 3 |
| [`baqubah-line7.aln.toml`](baqubah-line7.aln.toml) | `line-7` | 4,762.2 m | 3 |
| [`baqubah-line8.aln.toml`](baqubah-line8.aln.toml) | `line-8` | 7,668.7 m | 5 |
| [`baqubah-line9.aln.toml`](baqubah-line9.aln.toml) | `line-9` | 3,189.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
