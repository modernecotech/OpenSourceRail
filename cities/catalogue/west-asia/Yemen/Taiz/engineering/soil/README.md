# Taiz civil soil screening

110 route/station sample locations; 110 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 110 |
| granular-density-and-groundwater-tests | 74 |

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
| 0..30cm | clay | % | 22–32 | 8–46 | 110 |
| 0..30cm | sand | % | 36–58 | 14–81 | 110 |
| 0..30cm | silt | % | 20–32 | 6–46 | 110 |
| 0..30cm | bd.core | kg/m3 | 1270–1480 | 1100–1670 | 110 |
| 0..30cm | soc | g/kg | 4.7–19 | 2.6–35.7 | 110 |
| 0..30cm | ph.h2o | pH | 7.2–8.2 | 5.9–8.8 | 110 |
| 30..60cm | clay | % | 24–34 | 8–48 | 110 |
| 30..60cm | sand | % | 35–57 | 9–88 | 110 |
| 30..60cm | silt | % | 20–31 | 4–45 | 110 |
| 30..60cm | bd.core | kg/m3 | 1310–1480 | 1090–1690 | 110 |
| 30..60cm | soc | g/kg | 3.3–8.2 | 1.3–17.5 | 110 |
| 30..60cm | ph.h2o | pH | 7.4–8.4 | 6.4–9.1 | 110 |
| 60..100cm | clay | % | 24–35 | 7–48 | 110 |
| 60..100cm | sand | % | 35–56 | 6–88 | 110 |
| 60..100cm | silt | % | 20–32 | 3–46 | 110 |
| 60..100cm | bd.core | kg/m3 | 1300–1480 | 1000–1730 | 110 |
| 60..100cm | soc | g/kg | 2.4–5.6 | 0.8–12.8 | 110 |
| 60..100cm | ph.h2o | pH | 7.4–8.5 | 6.1–9.3 | 110 |
