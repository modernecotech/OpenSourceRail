# Sulaymaniyah Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`sulaymaniyah-line1.aln.toml`](sulaymaniyah-line1.aln.toml) | `line-1` | 17,287.0 m | 10 |
| [`sulaymaniyah-line2.aln.toml`](sulaymaniyah-line2.aln.toml) | `line-2` | 15,139.8 m | 10 |
| [`sulaymaniyah-line3.aln.toml`](sulaymaniyah-line3.aln.toml) | `line-3` | 28,298.2 m | 15 |
| [`sulaymaniyah-line4.aln.toml`](sulaymaniyah-line4.aln.toml) | `line-4` | 59,101.7 m | 34 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
