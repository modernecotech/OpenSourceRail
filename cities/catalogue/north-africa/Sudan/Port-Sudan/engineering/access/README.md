# Port-Sudan — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 23.8% |
| Reachable line pairs, including intermediate lines | 52.4% |
| Reachable with at most two transfers | 52.4% |
| Connected line components | 2 |
| Maximum transfers within a connected component | 2 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 480,842**. Catalogue planning population: 500,000. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 63,870 | 13.3% |
| 800 m | 150,268 | 31.3% |
| 1000 m | 208,678 | 43.4% |
| 1500 m | 287,213 | 59.7% |
| 2000 m | 328,797 | 68.4% |

Excluded nodata pixels: 20,918; valid pixels: 38,806.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (42.6%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
