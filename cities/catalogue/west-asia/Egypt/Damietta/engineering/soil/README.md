# Damietta civil soil screening

580 route/station sample locations; 576 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 44 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 575 |
| granular-density-and-groundwater-tests | 537 |
| organic-content-and-compressibility-tests | 234 |

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
| 0..30cm | clay | % | 20–29 | 6–41 | 576 |
| 0..30cm | sand | % | 40–58 | 12–85 | 576 |
| 0..30cm | silt | % | 23–32 | 9–49 | 576 |
| 0..30cm | bd.core | kg/m3 | 1000–1440 | 680–1660 | 576 |
| 0..30cm | soc | g/kg | 3.6–24.4 | 1.7–71.3 | 576 |
| 0..30cm | ph.h2o | pH | 7.5–8.4 | 6.3–9 | 576 |
| 30..60cm | clay | % | 21–30 | 6–44 | 576 |
| 30..60cm | sand | % | 40–57 | 12–87 | 576 |
| 30..60cm | silt | % | 22–30 | 4–48 | 576 |
| 30..60cm | bd.core | kg/m3 | 1050–1530 | 740–1820 | 576 |
| 30..60cm | soc | g/kg | 2.2–21.8 | 0.7–79.2 | 576 |
| 30..60cm | ph.h2o | pH | 7.1–8.6 | 4.4–9.6 | 576 |
| 60..100cm | clay | % | 21–30 | 6–44 | 576 |
| 60..100cm | sand | % | 39–58 | 12–88 | 576 |
| 60..100cm | silt | % | 21–30 | 3–48 | 576 |
| 60..100cm | bd.core | kg/m3 | 1060–1550 | 570–1890 | 576 |
| 60..100cm | soc | g/kg | 1.5–26.9 | 0.4–162 | 576 |
| 60..100cm | ph.h2o | pH | 6.8–8.7 | 3.3–9.9 | 576 |
