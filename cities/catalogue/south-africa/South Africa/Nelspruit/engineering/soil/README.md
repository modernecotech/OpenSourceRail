# Nelspruit civil soil screening

76 route/station sample locations; 76 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 71 |
| fine-soil-plasticity-and-shrink-swell-tests | 76 |
| granular-density-and-groundwater-tests | 75 |

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
| 0..30cm | clay | % | 27–36 | 14–50 | 76 |
| 0..30cm | sand | % | 40–58 | 10–80 | 76 |
| 0..30cm | silt | % | 15–24 | 2–40 | 76 |
| 0..30cm | bd.core | kg/m3 | 1170–1350 | 950–1600 | 76 |
| 0..30cm | soc | g/kg | 6.9–18 | 3.1–33.5 | 76 |
| 0..30cm | ph.h2o | pH | 5.7–7.4 | 5–8.2 | 76 |
| 30..60cm | clay | % | 29–38 | 13–51 | 76 |
| 30..60cm | sand | % | 39–57 | 12–81 | 76 |
| 30..60cm | silt | % | 14–23 | 0–39 | 76 |
| 30..60cm | bd.core | kg/m3 | 1240–1450 | 990–1600 | 76 |
| 30..60cm | soc | g/kg | 4.3–7.7 | 2.1–13.3 | 76 |
| 30..60cm | ph.h2o | pH | 5.8–7.5 | 5.1–8.4 | 76 |
| 60..100cm | clay | % | 29–39 | 11–53 | 76 |
| 60..100cm | sand | % | 39–56 | 12–81 | 76 |
| 60..100cm | silt | % | 14–23 | 0–40 | 76 |
| 60..100cm | bd.core | kg/m3 | 1260–1510 | 890–1700 | 76 |
| 60..100cm | soc | g/kg | 3.5–5.7 | 1.2–11.9 | 76 |
| 60..100cm | ph.h2o | pH | 6–7.5 | 5.1–8.7 | 76 |
