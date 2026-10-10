# Colombo civil soil screening

7,706 route/station sample locations; 7,664 complete profiles; 42 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 7664 |
| coverage-gap | 42 |
| fine-soil-plasticity-and-shrink-swell-tests | 7664 |
| granular-density-and-groundwater-tests | 6239 |
| organic-content-and-compressibility-tests | 2637 |
| silt-moisture-frost-and-erosion-review | 32 |

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
| 0..30cm | clay | % | 19–38 | 2–49 | 7664 |
| 0..30cm | sand | % | 34–65 | 10–95 | 7664 |
| 0..30cm | silt | % | 16–31 | 0–48 | 7664 |
| 0..30cm | bd.core | kg/m3 | 340–1320 | 130–1590 | 7664 |
| 0..30cm | soc | g/kg | 7.6–89.4 | 1.7–279.8 | 7664 |
| 0..30cm | ph.h2o | pH | 5.1–5.9 | 4.1–7 | 7664 |
| 30..60cm | clay | % | 19–41 | 1–55 | 7664 |
| 30..60cm | sand | % | 34–66 | 7–95 | 7664 |
| 30..60cm | silt | % | 14–32 | 0–47 | 7664 |
| 30..60cm | bd.core | kg/m3 | 350–1440 | 150–1680 | 7664 |
| 30..60cm | soc | g/kg | 4.1–56.1 | 1.2–214.2 | 7664 |
| 30..60cm | ph.h2o | pH | 5.1–6.1 | 4.2–7.6 | 7664 |
| 60..100cm | clay | % | 19–41 | 1–55 | 7664 |
| 60..100cm | sand | % | 31–66 | 5–95 | 7664 |
| 60..100cm | silt | % | 15–34 | 0–53 | 7664 |
| 60..100cm | bd.core | kg/m3 | 360–1480 | 130–1740 | 7664 |
| 60..100cm | soc | g/kg | 3.1–37.8 | 1–408.1 | 7664 |
| 60..100cm | ph.h2o | pH | 5.2–6.2 | 4.3–8.1 | 7664 |
