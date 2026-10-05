# Gujranwala civil soil screening

281 route/station sample locations; 281 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 281 |
| granular-density-and-groundwater-tests | 219 |
| silt-moisture-frost-and-erosion-review | 12 |

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
| 0..30cm | clay | % | 22–29 | 6–44 | 281 |
| 0..30cm | sand | % | 42–52 | 14–80 | 281 |
| 0..30cm | silt | % | 25–32 | 8–46 | 281 |
| 0..30cm | bd.core | kg/m3 | 1280–1480 | 1040–1650 | 281 |
| 0..30cm | soc | g/kg | 3.3–6.8 | 0.7–17.1 | 281 |
| 0..30cm | ph.h2o | pH | 7.1–7.5 | 6–8.3 | 281 |
| 30..60cm | clay | % | 22–30 | 7–43 | 281 |
| 30..60cm | sand | % | 41–51 | 12–79 | 281 |
| 30..60cm | silt | % | 25–33 | 6–49 | 281 |
| 30..60cm | bd.core | kg/m3 | 1440–1610 | 1220–1770 | 281 |
| 30..60cm | soc | g/kg | 1.8–3.9 | 0.3–9.9 | 281 |
| 30..60cm | ph.h2o | pH | 7.2–7.6 | 6.2–8.3 | 281 |
| 60..100cm | clay | % | 23–31 | 6–45 | 281 |
| 60..100cm | sand | % | 39–50 | 10–79 | 281 |
| 60..100cm | silt | % | 26–34 | 7–52 | 281 |
| 60..100cm | bd.core | kg/m3 | 1530–1670 | 1270–1880 | 281 |
| 60..100cm | soc | g/kg | 1.3–3.3 | 0.2–7.8 | 281 |
| 60..100cm | ph.h2o | pH | 7.2–7.6 | 6.4–8.4 | 281 |
