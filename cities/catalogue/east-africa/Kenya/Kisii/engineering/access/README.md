# Kisii — population access and transfers

Controlled planning screen; population counts, passenger transfers and routing demand are separate measures.

| Transfer measure | Value |
|---|---:|
| Direct transfer line pairs | 28.6% |
| Reachable line pairs, including intermediate lines | 100.0% |
| Reachable with at most two transfers | 61.9% |
| Connected line components | 1 |
| Maximum transfers within a connected component | 4 |

A crossing creates no transfer unless passenger interchange membership is recorded. Physical access, waiting time, timetable and fares remain unverified.

## Population access

Native **2020 bbox population: 354,836**. Catalogue planning population: 300,000. Different dates and boundaries; no multiplication or rebasing of a demand score.

| Radius | Residents in union of station circles (2020) | Share of raster bbox population |
|---|---:|---:|
| 500 m | 47,902 | 13.5% |
| 800 m | 107,167 | 30.2% |
| 1000 m | 145,727 | 41.1% |
| 1500 m | 192,255 | 54.2% |
| 2000 m | 215,817 | 60.8% |

Excluded nodata pixels: 0; valid pixels: 26,569.

[Retained source and attribution](population-source.json) · [Native count pixels](population-pixels.npz.gz).

Station circles use great-circle distances and count each native pixel once. They are potential radial access, **not validated walking coverage**: rivers, motorways, walls, hills and actual entrances can reduce access. Native pixel-centre assignment adds source-resolution uncertainty at catchment boundaries. The 1,500–2,000 m cases are extended access/feeder sensitivities; no feeder service or finance is assumed.

The legacy routing score (81.2%) measures high-demand cells close to tracks. It can be lower or higher than population access. Its former multiplication by city population is retired. Coverage alone never increases modeled paid trips or financial viability.

[Machine-readable accounting and source hashes](summary.json).
