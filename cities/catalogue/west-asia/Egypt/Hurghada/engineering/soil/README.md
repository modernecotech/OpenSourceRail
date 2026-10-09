# Hurghada civil soil screening

204 route/station sample locations; 203 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 35 |
| coverage-gap | 1 |
| granular-density-and-groundwater-tests | 203 |

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
| 0..30cm | clay | % | 10–17 | 0–29 | 203 |
| 0..30cm | sand | % | 60–73 | 39–94 | 203 |
| 0..30cm | silt | % | 16–23 | 4–36 | 203 |
| 0..30cm | bd.core | kg/m3 | 1370–1470 | 1050–1670 | 203 |
| 0..30cm | soc | g/kg | 2.9–8.1 | 0.7–24.7 | 203 |
| 0..30cm | ph.h2o | pH | 7.2–8.3 | 5.4–9.4 | 203 |
| 30..60cm | clay | % | 10–17 | 0–33 | 203 |
| 30..60cm | sand | % | 61–77 | 28–96 | 203 |
| 30..60cm | silt | % | 14–22 | 1–39 | 203 |
| 30..60cm | bd.core | kg/m3 | 1450–1520 | 1240–1670 | 203 |
| 30..60cm | soc | g/kg | 2.1–10 | 0–42 | 203 |
| 30..60cm | ph.h2o | pH | 7.3–8.5 | 4.8–9.8 | 203 |
| 60..100cm | clay | % | 9–18 | 0–33 | 203 |
| 60..100cm | sand | % | 60–77 | 28–96 | 203 |
| 60..100cm | silt | % | 14–22 | 1–39 | 203 |
| 60..100cm | bd.core | kg/m3 | 1480–1570 | 1250–1780 | 203 |
| 60..100cm | soc | g/kg | 1.9–7.8 | 0.1–34 | 203 |
| 60..100cm | ph.h2o | pH | 7.3–8.5 | 4.8–9.8 | 203 |
