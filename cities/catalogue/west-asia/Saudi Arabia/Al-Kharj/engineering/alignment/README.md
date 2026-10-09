# Al-Kharj Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`al-kharj-line1.aln.toml`](al-kharj-line1.aln.toml) | `line-1` | 20,353.5 m | 12 |
| [`al-kharj-line10.aln.toml`](al-kharj-line10.aln.toml) | `line-10` | 9,015.3 m | 6 |
| [`al-kharj-line11.aln.toml`](al-kharj-line11.aln.toml) | `line-11` | 10,242.9 m | 7 |
| [`al-kharj-line12.aln.toml`](al-kharj-line12.aln.toml) | `line-12` | 9,022.3 m | 8 |
| [`al-kharj-line13.aln.toml`](al-kharj-line13.aln.toml) | `line-13` | 2,600.0 m | 2 |
| [`al-kharj-line2.aln.toml`](al-kharj-line2.aln.toml) | `line-2` | 20,776.9 m | 15 |
| [`al-kharj-line3.aln.toml`](al-kharj-line3.aln.toml) | `line-3` | 17,193.4 m | 12 |
| [`al-kharj-line4.aln.toml`](al-kharj-line4.aln.toml) | `line-4` | 5,033.9 m | 4 |
| [`al-kharj-line5.aln.toml`](al-kharj-line5.aln.toml) | `line-5` | 3,980.1 m | 3 |
| [`al-kharj-line6.aln.toml`](al-kharj-line6.aln.toml) | `line-6` | 2,588.5 m | 2 |
| [`al-kharj-line7.aln.toml`](al-kharj-line7.aln.toml) | `line-7` | 2,873.0 m | 2 |
| [`al-kharj-line8.aln.toml`](al-kharj-line8.aln.toml) | `line-8` | 4,248.3 m | 3 |
| [`al-kharj-line9.aln.toml`](al-kharj-line9.aln.toml) | `line-9` | 8,100.4 m | 5 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
