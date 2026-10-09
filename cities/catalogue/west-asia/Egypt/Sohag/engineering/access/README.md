# Sohag — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 21.4% |
| Reachable line pairs, including intermediate lines | 57.1% |
| Reachable with at most two transfers | 46.4% |
| Connected line components | 2 |
| Maximum transfers within a connected component | 3 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 1,514,494**. Catalogue planning population: 550,000. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 261,832 | 17.3% |
| 800 m | 607,519 | 40.1% |
| 1000 m | 796,002 | 52.6% |
| 1500 m | 1,013,526 | 66.9% |
| 2000 m | 1,120,282 | 74.0% |

Excluded nodata pixels: 45,067; valid pixels: 18,241.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (65.3%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
