# Phnom-Penh civil soil screening

484 route/station sample locations; 405 complete profiles; 79 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 11 |
| coverage-gap | 79 |
| fine-soil-plasticity-and-shrink-swell-tests | 405 |
| granular-density-and-groundwater-tests | 344 |
| silt-moisture-frost-and-erosion-review | 19 |

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
| 0..30cm | clay | % | 23–36 | 4–48 | 405 |
| 0..30cm | sand | % | 26–55 | 5–89 | 405 |
| 0..30cm | silt | % | 21–37 | 5–52 | 405 |
| 0..30cm | bd.core | kg/m3 | 1140–1460 | 840–1700 | 405 |
| 0..30cm | soc | g/kg | 3.7–12.2 | 1.3–32.8 | 405 |
| 0..30cm | ph.h2o | pH | 6.2–7 | 5.4–8.3 | 405 |
| 30..60cm | clay | % | 25–38 | 3–50 | 405 |
| 30..60cm | sand | % | 26–53 | 5–92 | 405 |
| 30..60cm | silt | % | 22–36 | 1–52 | 405 |
| 30..60cm | bd.core | kg/m3 | 1180–1500 | 800–1710 | 405 |
| 30..60cm | soc | g/kg | 2.8–10.3 | 0.8–21 | 405 |
| 30..60cm | ph.h2o | pH | 6.5–7.3 | 5.5–8.3 | 405 |
| 60..100cm | clay | % | 26–37 | 3–50 | 405 |
| 60..100cm | sand | % | 28–52 | 6–92 | 405 |
| 60..100cm | silt | % | 22–35 | 1–50 | 405 |
| 60..100cm | bd.core | kg/m3 | 1120–1530 | 540–1780 | 405 |
| 60..100cm | soc | g/kg | 2.1–9.1 | 0.6–29.9 | 405 |
| 60..100cm | ph.h2o | pH | 6.8–7.5 | 5.4–9 | 405 |
