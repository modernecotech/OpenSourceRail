# Vientiane civil soil screening

1,686 route/station sample locations; 1,685 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1685 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1685 |
| granular-density-and-groundwater-tests | 1522 |
| silt-moisture-frost-and-erosion-review | 343 |

- No bearing capacity, CBR, friction angle, cohesion, groundwater, contamination, sulfate/chloride or deep stratigraphy is inferred from these maps.
- Desert, water, urban fill and other nodata remain unknown; no nearest-pixel or climate-based substitution.
- Texture fractions are independent predictions; they are not renormalised or converted to a geotechnical soil class.
- Prioritisation thresholds are editable OSR screening rules, not statutory limits or evidence of a hazard.
- No excavation depths, foundation dimensions, treatment quantities or civil costs are changed from pedological predictions.

Source: [OpenLandMap soilDB](https://github.com/openlandmap/soildb), Hengl et al., DOI 10.5194/essd-2025-336, CC BY 4.0. Exact source revision, URLs and raster metadata are retained in the receipt.

## Sampled property ranges

Ranges below span the sampled locations; they are not a city-wide characteristic soil value. The uncertainty envelope spans the lowest p16 to highest p84.

| Depth | Property | Unit | Mean range | Uncertainty envelope | Available locations |
|---|---|---|---:|---:|---:|
| 0..30cm | clay | % | 20–31 | 2–45 | 1685 |
| 0..30cm | sand | % | 32–55 | 6–86 | 1685 |
| 0..30cm | silt | % | 25–37 | 6–54 | 1685 |
| 0..30cm | bd.core | kg/m3 | 1080–1410 | 860–1620 | 1685 |
| 0..30cm | soc | g/kg | 5.5–13.7 | 2.5–36.8 | 1685 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.6–7.6 | 1685 |
| 30..60cm | clay | % | 22–32 | 3–44 | 1685 |
| 30..60cm | sand | % | 32–54 | 5–87 | 1685 |
| 30..60cm | silt | % | 25–37 | 5–55 | 1685 |
| 30..60cm | bd.core | kg/m3 | 1150–1460 | 870–1700 | 1685 |
| 30..60cm | soc | g/kg | 3.5–8.4 | 1.4–21.9 | 1685 |
| 30..60cm | ph.h2o | pH | 5.9–6.3 | 4.7–7.9 | 1685 |
| 60..100cm | clay | % | 22–32 | 4–45 | 1685 |
| 60..100cm | sand | % | 31–52 | 5–86 | 1685 |
| 60..100cm | silt | % | 26–37 | 5–56 | 1685 |
| 60..100cm | bd.core | kg/m3 | 1160–1460 | 740–1690 | 1685 |
| 60..100cm | soc | g/kg | 2.6–8 | 0.7–26.3 | 1685 |
| 60..100cm | ph.h2o | pH | 6.1–6.5 | 4.8–8.1 | 1685 |
