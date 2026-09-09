# Moshi civil soil screening

93 route/station sample locations; 93 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 93 |
| granular-density-and-groundwater-tests | 19 |

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
| 0..30cm | clay | % | 29–46 | 15–56 | 93 |
| 0..30cm | sand | % | 22–49 | 4–84 | 93 |
| 0..30cm | silt | % | 21–34 | 4–46 | 93 |
| 0..30cm | bd.core | kg/m3 | 1120–1370 | 950–1530 | 93 |
| 0..30cm | soc | g/kg | 7.3–20.1 | 4.6–35.3 | 93 |
| 0..30cm | ph.h2o | pH | 6.2–7.2 | 5.2–8.1 | 93 |
| 30..60cm | clay | % | 31–48 | 15–60 | 93 |
| 30..60cm | sand | % | 21–46 | 4–83 | 93 |
| 30..60cm | silt | % | 22–34 | 4–47 | 93 |
| 30..60cm | bd.core | kg/m3 | 1260–1390 | 1090–1560 | 93 |
| 30..60cm | soc | g/kg | 5.3–9.2 | 2.7–16.6 | 93 |
| 30..60cm | ph.h2o | pH | 6.3–7.2 | 5.3–8.1 | 93 |
| 60..100cm | clay | % | 31–47 | 14–61 | 93 |
| 60..100cm | sand | % | 22–48 | 4–81 | 93 |
| 60..100cm | silt | % | 21–33 | 3–49 | 93 |
| 60..100cm | bd.core | kg/m3 | 1290–1380 | 1040–1610 | 93 |
| 60..100cm | soc | g/kg | 4.3–6.2 | 1.9–11.4 | 93 |
| 60..100cm | ph.h2o | pH | 6.4–7.3 | 5.4–8.1 | 93 |
