# Egypt National OpenSourceRail Strategy

This page contains only Egypt-specific aggregation. Shared network, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this national programme avoids **$42.82 B (88.4%) of external capital** and **$52.64 B of external interest**. Capital plus saved interest totals **$95.46 B**.

## National Programme

| Local measure | Planning value |
|---|---:|
| Catalogue cities | 19 |
| Represented population | 10,600,000 |
| Trainsets / vehicle modules | 4,936 / 14,532 |
| City infrastructure and fleet CAPEX | $25.97 B |
| Shared national factory | $863.1 M |
| Factory sizing basis | 1,470 modules for Tanta, then reused nationally |
| **Total national programme** | **$26.89 B** |

## Capital And Funding

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $5.59 B (20.8%) |
| Domestic / local capital | $21.30 B (79.2%) |
| Annual external capital draw | $1.12 B / yr |
| Annual local capital draw | $4.26 B / yr |
| Annual public construction commitment | $2.89 B / yr for 5 years |
| Annual post-grace debt service | $2.17 B / yr |
| Default foreign-turnkey external capital | $48.41 B |
| External capital saved | $42.82 B |
| Capital + lifetime external interest saved | $95.46 B |

### Procurement-Origin Composition

| CAPEX bucket | Total | Imported | Local value |
|---|---:|---:|---:|
| Civil works | $12.34 B | $1.85 B | $10.49 B |
| Stations | $4.43 B | $886.3 M | $3.55 B |
| Depots | $2.63 B | $658.3 M | $1.98 B |
| Rolling stock | $4.35 B | $1.52 B | $2.83 B |
| Dedicated solar plants | $362.2 M | $163.0 M | $199.2 M |
| Residual train control | $70.9 M | $35.5 M | $35.5 M |
| Charging microgrids | $107.6 M | $43.0 M | $64.6 M |
| EPC / project services | $1.74 B | $260.4 M | $1.48 B |
| Shared national trainset factory | $863.1 M | $172.6 M | $690.5 M |
| **Total** | **$26.89 B** | **$5.59 B** | **$21.30 B** |

## City Programme

| City | Population | Fleet | City CAPEX | External capital | Local capital |
|---|---:|---:|---:|---:|---:|
| [Mansoura Eg](Mansoura-Eg/README.md) | 1,000,000 | 316 | $1.63 B | $341.2 M | $1.29 B |
| [Port Said](Port-Said/README.md) | 800,000 | 78 | $481.4 M | $97.1 M | $384.3 M |
| [Suez](Suez/README.md) | 800,000 | 241 | $1.23 B | $257.5 M | $969.7 M |
| [Tanta](Tanta/README.md) | 750,000 | 490 | $2.34 B | $505.5 M | $1.84 B |
| [Ismailia](Ismailia/README.md) | 700,000 | 270 | $1.42 B | $297.5 M | $1.12 B |
| [Zagazig](Zagazig/README.md) | 700,000 | 255 | $1.33 B | $278.1 M | $1.05 B |
| [Asyut](Asyut/README.md) | 600,000 | 321 | $1.59 B | $336.4 M | $1.25 B |
| [Mahalla](Mahalla/README.md) | 600,000 | 241 | $1.28 B | $266.7 M | $1.01 B |
| [Minya](Minya/README.md) | 600,000 | 282 | $1.47 B | $305.9 M | $1.17 B |
| [Sohag](Sohag/README.md) | 550,000 | 247 | $1.23 B | $258.5 M | $975.8 M |
| [Damanhur](Damanhur/README.md) | 500,000 | 304 | $1.53 B | $323.4 M | $1.21 B |
| [Fayoum](Fayoum/README.md) | 500,000 | 433 | $2.01 B | $434.9 M | $1.58 B |
| [Luxor](Luxor/README.md) | 500,000 | 312 | $1.77 B | $362.6 M | $1.40 B |
| [Damietta](Damietta/README.md) | 400,000 | 421 | $2.22 B | $468.3 M | $1.75 B |
| [Beni Suef](Beni-Suef/README.md) | 350,000 | 202 | $1.07 B | $223.0 M | $850.6 M |
| [Qena](Qena/README.md) | 350,000 | 247 | $1.61 B | $321.0 M | $1.29 B |
| [Arish](Arish/README.md) | 300,000 | 53 | $330.4 M | $64.3 M | $266.0 M |
| [Hurghada](Hurghada/README.md) | 300,000 | 91 | $590.6 M | $111.8 M | $478.9 M |
| [Kafr El Sheikh](Kafr-El-Sheikh/README.md) | 300,000 | 132 | $811.3 M | $156.9 M | $654.4 M |

## Local Basis And Regeneration

Country finance parameters use `EG` in `lib/templates/country-finance.toml`. The factory is counted once nationally and excluded from city CAPEX. City values come from each local `design.toml` and expanded scenario; common limitations and interpretation are not repeated here.

```bash
python3 tools/automation/generate-national-briefs.py
```


## Population-led route regeneration (2026-10-09)

The city inventories include additional lines selected from retained unserved residential areas, continuous corridor junctions and bounded station spacing. Fleet, depots, construction, energy, staffing and country finance use those revised inventories. The working target is 80% within 1 km circles of emitted stations; remaining gaps and missing data stay explicit.

| City | Current lines | Added residential lines | Original station circles | Current station circles |
| --- | ---: | ---: | ---: | ---: |
| [Arish](Arish/README.md) | 4 | 2 | 28.5% | 61.2% |
| [Asyut](Asyut/README.md) | 10 | 7 | 29.9% | 71.1% |
| [Beni Suef](Beni-Suef/README.md) | 7 | 4 | 28.3% | 54.4% |
| [Damanhur](Damanhur/README.md) | 11 | 8 | 39.5% | 65.3% |
| [Damietta](Damietta/README.md) | 11 | 8 | 37.3% | 84.8% |
| [Fayoum](Fayoum/README.md) | 13 | 10 | 31.7% | 71.8% |
| [Hurghada](Hurghada/README.md) | 4 | 1 | 65.1% | 74.4% |
| [Ismailia](Ismailia/README.md) | 9 | 6 | 48.0% | 81.4% |
| [Kafr El Sheikh](Kafr-El-Sheikh/README.md) | 8 | 5 | 45.7% | 77.3% |
| [Luxor](Luxor/README.md) | 12 | 9 | 32.5% | 79.8% |
| [Mahalla](Mahalla/README.md) | 8 | 5 | 26.9% | 60.2% |
| [Mansoura Eg](Mansoura-Eg/README.md) | 11 | 8 | 25.7% | 62.1% |
| [Minya](Minya/README.md) | 9 | 6 | 14.1% | 61.9% |
| [Port Said](Port-Said/README.md) | 4 | 1 | 53.9% | 75.5% |
| [Qena](Qena/README.md) | 10 | 7 | 32.5% | 81.6% |
| [Sohag](Sohag/README.md) | 8 | 5 | 23.7% | 52.6% |
| [Suez](Suez/README.md) | 6 | 3 | 47.5% | 79.5% |
| [Tanta](Tanta/README.md) | 12 | 9 | 36.6% | 73.0% |
| [Zagazig](Zagazig/README.md) | 9 | 6 | 36.2% | 62.1% |

Coverage uses retained 2020 city-bbox population counts. Overlapping city populations are not added to claim national coverage. These circles are not current census, surveyed walking catchments, observed fare demand or construction approval. The [catalogue comparison](../../../../engineering/network-planning/catalogue/README.md) records targets and evidence limits.
