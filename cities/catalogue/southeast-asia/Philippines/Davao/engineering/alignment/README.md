# Davao Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`davao-line1.aln.toml`](davao-line1.aln.toml) | `line-1` | 44,110.5 m | 24 |
| [`davao-line10.aln.toml`](davao-line10.aln.toml) | `line-10` | 7,194.9 m | 6 |
| [`davao-line11.aln.toml`](davao-line11.aln.toml) | `line-11` | 5,946.8 m | 4 |
| [`davao-line12.aln.toml`](davao-line12.aln.toml) | `line-12` | 6,582.0 m | 5 |
| [`davao-line13.aln.toml`](davao-line13.aln.toml) | `line-13` | 6,682.2 m | 5 |
| [`davao-line14.aln.toml`](davao-line14.aln.toml) | `line-14` | 5,571.4 m | 4 |
| [`davao-line15.aln.toml`](davao-line15.aln.toml) | `line-15` | 12,147.1 m | 8 |
| [`davao-line2.aln.toml`](davao-line2.aln.toml) | `line-2` | 37,737.9 m | 26 |
| [`davao-line3.aln.toml`](davao-line3.aln.toml) | `line-3` | 39,940.1 m | 22 |
| [`davao-line4.aln.toml`](davao-line4.aln.toml) | `line-4` | 33,494.9 m | 22 |
| [`davao-line5.aln.toml`](davao-line5.aln.toml) | `line-5` | 29,226.8 m | 18 |
| [`davao-line6.aln.toml`](davao-line6.aln.toml) | `line-6` | 85,732.3 m | 53 |
| [`davao-line7.aln.toml`](davao-line7.aln.toml) | `line-7` | 5,468.7 m | 4 |
| [`davao-line8.aln.toml`](davao-line8.aln.toml) | `line-8` | 5,912.7 m | 4 |
| [`davao-line9.aln.toml`](davao-line9.aln.toml) | `line-9` | 6,112.1 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
