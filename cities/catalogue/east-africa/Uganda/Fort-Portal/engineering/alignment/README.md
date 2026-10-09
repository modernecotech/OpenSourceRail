# Fort-Portal Planning OSR-ALN Package

Deterministic alignment exports for every line in the current generated network.

| File | Design line | Length | Stations |
|---|---:|---:|---:|
| [`fort-portal-line1.aln.toml`](fort-portal-line1.aln.toml) | `line-1` | 9,294.3 m | 6 |
| [`fort-portal-line10.aln.toml`](fort-portal-line10.aln.toml) | `line-10` | 2,842.5 m | 2 |
| [`fort-portal-line2.aln.toml`](fort-portal-line2.aln.toml) | `line-2` | 6,667.5 m | 6 |
| [`fort-portal-line3.aln.toml`](fort-portal-line3.aln.toml) | `line-3` | 12,784.4 m | 9 |
| [`fort-portal-line4.aln.toml`](fort-portal-line4.aln.toml) | `line-4` | 2,633.0 m | 3 |
| [`fort-portal-line5.aln.toml`](fort-portal-line5.aln.toml) | `line-5` | 6,643.3 m | 4 |
| [`fort-portal-line6.aln.toml`](fort-portal-line6.aln.toml) | `line-6` | 4,775.5 m | 3 |
| [`fort-portal-line7.aln.toml`](fort-portal-line7.aln.toml) | `line-7` | 2,189.1 m | 2 |
| [`fort-portal-line8.aln.toml`](fort-portal-line8.aln.toml) | `line-8` | 5,679.3 m | 4 |
| [`fort-portal-line9.aln.toml`](fort-portal-line9.aln.toml) | `line-9` | 2,291.1 m | 2 |

## Status

These files are **planning-only and not for construction**. Horizontal control
comes from the current WGS84 corridor and is projected to the local UTM zone.
Circular curves and transitions are not fitted, the vertical profile is a
zero-datum placeholder, and cant has not been designed. Survey, curve-fit,
vertical-profile, cant, geotechnical, utility, property, drainage, and
structural release gates therefore remain open.

Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the
city corridor GeoJSON used to generate it.
