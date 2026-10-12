# Latakia civil soil screening

717 route/station sample locations; 714 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 670 |
| granular-density-and-groundwater-tests | 587 |
| silt-moisture-frost-and-erosion-review | 10 |

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
| 0..30cm | clay | % | 13–27 | 0–41 | 714 |
| 0..30cm | sand | % | 40–69 | 13–97 | 714 |
| 0..30cm | silt | % | 17–33 | 1–50 | 714 |
| 0..30cm | bd.core | kg/m3 | 1220–1410 | 960–1600 | 714 |
| 0..30cm | soc | g/kg | 4.3–16.6 | 1.8–32.4 | 714 |
| 0..30cm | ph.h2o | pH | 7–7.7 | 5.7–8.3 | 714 |
| 30..60cm | clay | % | 13–29 | 0–44 | 714 |
| 30..60cm | sand | % | 41–70 | 14–96 | 714 |
| 30..60cm | silt | % | 15–32 | 0–48 | 714 |
| 30..60cm | bd.core | kg/m3 | 1280–1530 | 1060–1720 | 714 |
| 30..60cm | soc | g/kg | 3.1–7.6 | 1.2–16.6 | 714 |
| 30..60cm | ph.h2o | pH | 7–7.6 | 5.7–8.3 | 714 |
| 60..100cm | clay | % | 14–29 | 0–44 | 714 |
| 60..100cm | sand | % | 39–71 | 11–96 | 714 |
| 60..100cm | silt | % | 15–33 | 0–51 | 714 |
| 60..100cm | bd.core | kg/m3 | 1260–1550 | 880–1760 | 714 |
| 60..100cm | soc | g/kg | 1.7–7.7 | 0.4–20.9 | 714 |
| 60..100cm | ph.h2o | pH | 7–7.6 | 5.5–8.3 | 714 |
