# Goma civil soil screening

731 route/station sample locations; 731 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 446 |
| fine-soil-plasticity-and-shrink-swell-tests | 731 |
| granular-density-and-groundwater-tests | 97 |
| organic-content-and-compressibility-tests | 64 |

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
| 0..30cm | clay | % | 28–39 | 14–50 | 731 |
| 0..30cm | sand | % | 32–54 | 13–76 | 731 |
| 0..30cm | silt | % | 18–30 | 5–46 | 731 |
| 0..30cm | bd.core | kg/m3 | 970–1200 | 750–1450 | 731 |
| 0..30cm | soc | g/kg | 10–39.5 | 3.9–88.3 | 731 |
| 0..30cm | ph.h2o | pH | 5.6–6.7 | 5–7.5 | 731 |
| 30..60cm | clay | % | 30–43 | 13–56 | 731 |
| 30..60cm | sand | % | 29–50 | 8–77 | 731 |
| 30..60cm | silt | % | 18–31 | 1–47 | 731 |
| 30..60cm | bd.core | kg/m3 | 1040–1250 | 790–1430 | 731 |
| 30..60cm | soc | g/kg | 7.1–18.5 | 1.9–33.1 | 731 |
| 30..60cm | ph.h2o | pH | 5.7–6.7 | 5–7.7 | 731 |
| 60..100cm | clay | % | 31–44 | 14–58 | 731 |
| 60..100cm | sand | % | 27–48 | 8–77 | 731 |
| 60..100cm | silt | % | 19–31 | 0–47 | 731 |
| 60..100cm | bd.core | kg/m3 | 1050–1280 | 610–1530 | 731 |
| 60..100cm | soc | g/kg | 4.6–14.1 | 1.5–33.8 | 731 |
| 60..100cm | ph.h2o | pH | 5.7–6.8 | 5–7.7 | 731 |
