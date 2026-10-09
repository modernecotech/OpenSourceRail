# Baghdad — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 12.6% |
| Reachable line pairs, including intermediate lines | 100.0% |
| Reachable with at most two transfers | 69.3% |
| Connected line components | 1 |
| Maximum transfers within a connected component | 4 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 5,985,974**. Catalogue planning population: 9,780,429. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 1,705,550 | 28.5% |
| 800 m | 3,694,552 | 61.7% |
| 1000 m | 4,713,907 | 78.7% |
| 1500 m | 5,641,849 | 94.3% |
| 2000 m | 5,762,967 | 96.3% |

Excluded nodata pixels: 248,597; valid pixels: 107,803.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (66.4%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
