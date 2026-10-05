# Maputo civil soil screening

1,296 route/station sample locations; 1,296 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1284 |
| fine-soil-plasticity-and-shrink-swell-tests | 1216 |
| granular-density-and-groundwater-tests | 1296 |
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
| 0..30cm | clay | % | 17–26 | 3–42 | 1296 |
| 0..30cm | sand | % | 53–73 | 17–97 | 1296 |
| 0..30cm | silt | % | 10–21 | 0–38 | 1296 |
| 0..30cm | bd.core | kg/m3 | 1070–1430 | 810–1570 | 1296 |
| 0..30cm | soc | g/kg | 5.2–24.1 | 1.5–48.9 | 1296 |
| 0..30cm | ph.h2o | pH | 6–6.9 | 5–8.3 | 1296 |
| 30..60cm | clay | % | 18–29 | 2–46 | 1296 |
| 30..60cm | sand | % | 52–72 | 18–97 | 1296 |
| 30..60cm | silt | % | 8–20 | 0–38 | 1296 |
| 30..60cm | bd.core | kg/m3 | 1080–1530 | 810–1680 | 1296 |
| 30..60cm | soc | g/kg | 3.1–17.1 | 0.8–37.5 | 1296 |
| 30..60cm | ph.h2o | pH | 6–6.9 | 5–8.3 | 1296 |
| 60..100cm | clay | % | 19–29 | 2–49 | 1296 |
| 60..100cm | sand | % | 52–72 | 17–97 | 1296 |
| 60..100cm | silt | % | 7–19 | 0–41 | 1296 |
| 60..100cm | bd.core | kg/m3 | 1050–1570 | 740–1750 | 1296 |
| 60..100cm | soc | g/kg | 2.3–14.7 | 0.2–50.1 | 1296 |
| 60..100cm | ph.h2o | pH | 6.1–7 | 4.6–8.4 | 1296 |
