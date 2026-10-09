# Kigoma civil soil screening

347 route/station sample locations; 347 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 347 |
| fine-soil-plasticity-and-shrink-swell-tests | 347 |
| granular-density-and-groundwater-tests | 328 |

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
| 0..30cm | clay | % | 21–32 | 8–46 | 347 |
| 0..30cm | sand | % | 42–63 | 16–87 | 347 |
| 0..30cm | silt | % | 16–27 | 3–40 | 347 |
| 0..30cm | bd.core | kg/m3 | 1290–1400 | 1070–1580 | 347 |
| 0..30cm | soc | g/kg | 7.1–12.9 | 3.4–21.4 | 347 |
| 0..30cm | ph.h2o | pH | 5.5–6 | 4.6–7.1 | 347 |
| 30..60cm | clay | % | 25–34 | 8–47 | 347 |
| 30..60cm | sand | % | 37–57 | 13–88 | 347 |
| 30..60cm | silt | % | 17–30 | 0–46 | 347 |
| 30..60cm | bd.core | kg/m3 | 1370–1510 | 1200–1720 | 347 |
| 30..60cm | soc | g/kg | 4.4–6.7 | 2.3–11.9 | 347 |
| 30..60cm | ph.h2o | pH | 5.6–6.1 | 4.5–7.2 | 347 |
| 60..100cm | clay | % | 25–35 | 8–50 | 347 |
| 60..100cm | sand | % | 35–55 | 12–88 | 347 |
| 60..100cm | silt | % | 19–30 | 0–48 | 347 |
| 60..100cm | bd.core | kg/m3 | 1390–1530 | 1130–1790 | 347 |
| 60..100cm | soc | g/kg | 4–6.5 | 2–17.8 | 347 |
| 60..100cm | ph.h2o | pH | 5.6–6.2 | 4.4–8 | 347 |
