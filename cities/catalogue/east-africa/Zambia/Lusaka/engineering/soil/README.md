# Lusaka civil soil screening

616 route/station sample locations; 616 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 607 |
| fine-soil-plasticity-and-shrink-swell-tests | 616 |
| granular-density-and-groundwater-tests | 609 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 22–33 | 9–45 | 616 |
| 0..30cm | sand | % | 45–63 | 23–89 | 616 |
| 0..30cm | silt | % | 14–23 | 2–40 | 616 |
| 0..30cm | bd.core | kg/m3 | 1240–1450 | 1030–1600 | 616 |
| 0..30cm | soc | g/kg | 4.5–14.4 | 1.8–33.8 | 616 |
| 0..30cm | ph.h2o | pH | 5.8–6.5 | 4.9–7.5 | 616 |
| 30..60cm | clay | % | 26–36 | 10–50 | 616 |
| 30..60cm | sand | % | 41–56 | 15–88 | 616 |
| 30..60cm | silt | % | 17–27 | 0–48 | 616 |
| 30..60cm | bd.core | kg/m3 | 1280–1490 | 1100–1670 | 616 |
| 30..60cm | soc | g/kg | 3.2–5.9 | 1.3–9.5 | 616 |
| 30..60cm | ph.h2o | pH | 5.8–6.7 | 5.1–7.7 | 616 |
| 60..100cm | clay | % | 26–36 | 8–53 | 616 |
| 60..100cm | sand | % | 40–56 | 9–87 | 616 |
| 60..100cm | silt | % | 16–28 | 0–50 | 616 |
| 60..100cm | bd.core | kg/m3 | 1270–1510 | 740–1740 | 616 |
| 60..100cm | soc | g/kg | 3.1–4.8 | 0.8–11.3 | 616 |
| 60..100cm | ph.h2o | pH | 5.9–6.9 | 5.2–8.1 | 616 |
