# Jaffna civil soil screening

118 route/station sample locations; 113 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 113 |
| granular-density-and-groundwater-tests | 113 |
| organic-content-and-compressibility-tests | 5 |

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
| 0..30cm | clay | % | 21–30 | 5–49 | 113 |
| 0..30cm | sand | % | 50–65 | 17–93 | 113 |
| 0..30cm | silt | % | 14–21 | 0–43 | 113 |
| 0..30cm | bd.core | kg/m3 | 1050–1310 | 710–1650 | 113 |
| 0..30cm | soc | g/kg | 6.8–20.8 | 3.1–49.6 | 113 |
| 0..30cm | ph.h2o | pH | 6.5–7.2 | 5.4–8.2 | 113 |
| 30..60cm | clay | % | 22–30 | 3–51 | 113 |
| 30..60cm | sand | % | 49–66 | 13–93 | 113 |
| 30..60cm | silt | % | 13–22 | 0–46 | 113 |
| 30..60cm | bd.core | kg/m3 | 1060–1280 | 670–1650 | 113 |
| 30..60cm | soc | g/kg | 5.7–19.3 | 1.1–48.3 | 113 |
| 30..60cm | ph.h2o | pH | 6.7–7.3 | 5.5–8.4 | 113 |
| 60..100cm | clay | % | 22–30 | 3–51 | 113 |
| 60..100cm | sand | % | 50–65 | 13–93 | 113 |
| 60..100cm | silt | % | 12–21 | 0–45 | 113 |
| 60..100cm | bd.core | kg/m3 | 1010–1240 | 440–1710 | 113 |
| 60..100cm | soc | g/kg | 4.6–19.1 | 1.3–55 | 113 |
| 60..100cm | ph.h2o | pH | 6.9–7.5 | 5.5–8.6 | 113 |
