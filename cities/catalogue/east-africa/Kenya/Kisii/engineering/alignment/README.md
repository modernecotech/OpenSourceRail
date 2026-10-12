# Kisii Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`kisii-line1.aln.toml`](kisii-line1.aln.toml) | `line-1` | 7,109.3 m | 3 |
| [`kisii-line2.aln.toml`](kisii-line2.aln.toml) | `line-2` | 6,258.7 m | 4 |
| [`kisii-line3.aln.toml`](kisii-line3.aln.toml) | `line-3` | 10,882.3 m | 6 |
| [`kisii-line4.aln.toml`](kisii-line4.aln.toml) | `line-4` | 5,912.4 m | 3 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
