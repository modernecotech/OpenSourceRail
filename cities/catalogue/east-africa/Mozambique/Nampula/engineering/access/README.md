# Nampula — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 15.0% |
| Reachable line pairs, including intermediate lines | 100.0% |
| Reachable with at most two transfers | 58.3% |
| Connected line components | 1 |
| Maximum transfers within a connected component | 3 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 874,738**. Catalogue planning population: 800,000. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 191,891 | 21.9% |
| 800 m | 430,662 | 49.2% |
| 1000 m | 556,359 | 63.6% |
| 1500 m | 669,713 | 76.6% |
| 2000 m | 722,633 | 82.6% |

Excluded nodata pixels: 104; valid pixels: 58,682.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (62.5%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
