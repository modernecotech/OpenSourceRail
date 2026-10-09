# Multan Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`multan-line1.aln.toml`](multan-line1.aln.toml) | `line-1` | 15,641.5 m | 9 |
| [`multan-line10.aln.toml`](multan-line10.aln.toml) | `line-10` | 5,939.6 m | 5 |
| [`multan-line11.aln.toml`](multan-line11.aln.toml) | `line-11` | 3,637.5 m | 3 |
| [`multan-line12.aln.toml`](multan-line12.aln.toml) | `line-12` | 3,095.0 m | 3 |
| [`multan-line13.aln.toml`](multan-line13.aln.toml) | `line-13` | 6,472.9 m | 4 |
| [`multan-line14.aln.toml`](multan-line14.aln.toml) | `line-14` | 8,694.5 m | 7 |
| [`multan-line15.aln.toml`](multan-line15.aln.toml) | `line-15` | 2,805.7 m | 2 |
| [`multan-line16.aln.toml`](multan-line16.aln.toml) | `line-16` | 2,694.0 m | 2 |
| [`multan-line17.aln.toml`](multan-line17.aln.toml) | `line-17` | 2,614.8 m | 3 |
| [`multan-line18.aln.toml`](multan-line18.aln.toml) | `line-18` | 3,490.4 m | 3 |
| [`multan-line19.aln.toml`](multan-line19.aln.toml) | `line-19` | 3,999.6 m | 4 |
| [`multan-line2.aln.toml`](multan-line2.aln.toml) | `line-2` | 16,859.8 m | 11 |
| [`multan-line20.aln.toml`](multan-line20.aln.toml) | `line-20` | 2,867.9 m | 2 |
| [`multan-line21.aln.toml`](multan-line21.aln.toml) | `line-21` | 9,373.4 m | 6 |
| [`multan-line22.aln.toml`](multan-line22.aln.toml) | `line-22` | 4,369.3 m | 3 |
| [`multan-line23.aln.toml`](multan-line23.aln.toml) | `line-23` | 11,881.0 m | 7 |
| [`multan-line24.aln.toml`](multan-line24.aln.toml) | `line-24` | 3,162.5 m | 2 |
| [`multan-line25.aln.toml`](multan-line25.aln.toml) | `line-25` | 3,039.1 m | 3 |
| [`multan-line3.aln.toml`](multan-line3.aln.toml) | `line-3` | 14,628.5 m | 10 |
| [`multan-line4.aln.toml`](multan-line4.aln.toml) | `line-4` | 15,322.7 m | 10 |
| [`multan-line5.aln.toml`](multan-line5.aln.toml) | `line-5` | 38,950.7 m | 25 |
| [`multan-line6.aln.toml`](multan-line6.aln.toml) | `line-6` | 3,649.9 m | 3 |
| [`multan-line7.aln.toml`](multan-line7.aln.toml) | `line-7` | 4,880.7 m | 4 |
| [`multan-line8.aln.toml`](multan-line8.aln.toml) | `line-8` | 4,970.4 m | 4 |
| [`multan-line9.aln.toml`](multan-line9.aln.toml) | `line-9` | 6,865.0 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
