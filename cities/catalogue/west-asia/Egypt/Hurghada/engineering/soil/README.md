# Hurghada civil soil screening

495 route/station sample locations; 476 complete profiles; 19 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 124 |
| coverage-gap | 19 |
| granular-density-and-groundwater-tests | 476 |

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
| 0..30cm | clay | % | 11–16 | 0–29 | 476 |
| 0..30cm | sand | % | 61–72 | 36–95 | 476 |
| 0..30cm | silt | % | 17–23 | 4–37 | 476 |
| 0..30cm | bd.core | kg/m3 | 1380–1480 | 1050–1670 | 476 |
| 0..30cm | soc | g/kg | 2.7–8 | 0.7–25.2 | 476 |
| 0..30cm | ph.h2o | pH | 7.3–8.2 | 5–9.3 | 476 |
| 30..60cm | clay | % | 10–18 | 0–32 | 476 |
| 30..60cm | sand | % | 60–77 | 33–98 | 476 |
| 30..60cm | silt | % | 13–22 | 1–37 | 476 |
| 30..60cm | bd.core | kg/m3 | 1460–1520 | 1270–1670 | 476 |
| 30..60cm | soc | g/kg | 1.6–9.6 | 0–42 | 476 |
| 30..60cm | ph.h2o | pH | 7.3–8.5 | 4.8–9.8 | 476 |
| 60..100cm | clay | % | 9–18 | 0–34 | 476 |
| 60..100cm | sand | % | 59–77 | 32–96 | 476 |
| 60..100cm | silt | % | 13–22 | 2–39 | 476 |
| 60..100cm | bd.core | kg/m3 | 1480–1560 | 1240–1780 | 476 |
| 60..100cm | soc | g/kg | 1.6–7.4 | 0–31.8 | 476 |
| 60..100cm | ph.h2o | pH | 7.3–8.5 | 4.8–9.8 | 476 |
