# Lichinga — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 0.0% |
| Reachable line pairs, including intermediate lines | 0.0% |
| Reachable with at most two transfers | 0.0% |
| Connected line components | 2 |
| Maximum transfers within a connected component | 0 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 242,389**. Catalogue planning population: 250,000. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 12,804 | 5.3% |
| 800 m | 30,103 | 12.4% |
| 1000 m | 43,355 | 17.9% |
| 1500 m | 75,413 | 31.1% |
| 2000 m | 100,416 | 41.4% |

Excluded nodata pixels: 21; valid pixels: 27,033.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (47.0%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
