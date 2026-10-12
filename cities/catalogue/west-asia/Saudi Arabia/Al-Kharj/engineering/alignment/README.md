# Al-Kharj Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`al-kharj-line1.aln.toml`](al-kharj-line1.aln.toml) | `line-1` | 20,353.5 m | 7 |
| [`al-kharj-line2.aln.toml`](al-kharj-line2.aln.toml) | `line-2` | 24,911.8 m | 8 |
| [`al-kharj-line3.aln.toml`](al-kharj-line3.aln.toml) | `line-3` | 17,193.4 m | 6 |
| [`al-kharj-line4.aln.toml`](al-kharj-line4.aln.toml) | `line-4` | 5,992.4 m | 3 |
| [`al-kharj-line5.aln.toml`](al-kharj-line5.aln.toml) | `line-5` | 6,900.7 m | 4 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
