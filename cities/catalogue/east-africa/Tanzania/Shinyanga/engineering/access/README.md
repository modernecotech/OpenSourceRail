# Shinyanga — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 33.3% |
| Reachable line pairs, including intermediate lines | 33.3% |
| Reachable with at most two transfers | 33.3% |
| Connected line components | 2 |
| Maximum transfers within a connected component | 1 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 145,645**. Catalogue planning population: 250,000. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 19,714 | 13.5% |
| 800 m | 43,821 | 30.1% |
| 1000 m | 56,611 | 38.9% |
| 1500 m | 81,836 | 56.2% |
| 2000 m | 102,856 | 70.6% |

Excluded nodata pixels: 0; valid pixels: 26,244.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (69.6%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
