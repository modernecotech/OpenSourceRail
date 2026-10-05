# Bhopal civil soil screening

779 route/station sample locations; 777 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 774 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 742 |
| granular-density-and-groundwater-tests | 777 |
| silt-moisture-frost-and-erosion-review | 5 |

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
| 0..30cm | clay | % | 19–28 | 3–42 | 777 |
| 0..30cm | sand | % | 43–60 | 17–88 | 777 |
| 0..30cm | silt | % | 20–29 | 1–47 | 777 |
| 0..30cm | bd.core | kg/m3 | 1120–1450 | 790–1660 | 777 |
| 0..30cm | soc | g/kg | 4.3–8.3 | 1.3–21.1 | 777 |
| 0..30cm | ph.h2o | pH | 6.1–6.7 | 5–8.1 | 777 |
| 30..60cm | clay | % | 20–30 | 4–45 | 777 |
| 30..60cm | sand | % | 44–59 | 15–89 | 777 |
| 30..60cm | silt | % | 19–27 | 0–52 | 777 |
| 30..60cm | bd.core | kg/m3 | 1250–1530 | 940–1740 | 777 |
| 30..60cm | soc | g/kg | 2.4–5.1 | 0.5–12.3 | 777 |
| 30..60cm | ph.h2o | pH | 6.2–6.9 | 5.2–8.2 | 777 |
| 60..100cm | clay | % | 21–31 | 4–46 | 777 |
| 60..100cm | sand | % | 44–60 | 12–90 | 777 |
| 60..100cm | silt | % | 18–26 | 0–52 | 777 |
| 60..100cm | bd.core | kg/m3 | 1390–1610 | 1030–1880 | 777 |
| 60..100cm | soc | g/kg | 1.8–3.8 | 0.3–10.3 | 777 |
| 60..100cm | ph.h2o | pH | 6.3–7 | 5–8.4 | 777 |
