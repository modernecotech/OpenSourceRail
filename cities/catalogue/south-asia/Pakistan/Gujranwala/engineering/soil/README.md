# Gujranwala civil soil screening

294 route/station sample locations; 294 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 294 |
| granular-density-and-groundwater-tests | 229 |
| silt-moisture-frost-and-erosion-review | 10 |

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
| 0..30cm | clay | % | 22–29 | 6–43 | 294 |
| 0..30cm | sand | % | 43–52 | 13–81 | 294 |
| 0..30cm | silt | % | 25–31 | 8–46 | 294 |
| 0..30cm | bd.core | kg/m3 | 1280–1460 | 1040–1650 | 294 |
| 0..30cm | soc | g/kg | 3.9–6.8 | 0.8–19 | 294 |
| 0..30cm | ph.h2o | pH | 7.1–7.5 | 6–8.3 | 294 |
| 30..60cm | clay | % | 22–29 | 5–43 | 294 |
| 30..60cm | sand | % | 41–52 | 12–84 | 294 |
| 30..60cm | silt | % | 24–31 | 6–49 | 294 |
| 30..60cm | bd.core | kg/m3 | 1430–1610 | 1170–1780 | 294 |
| 30..60cm | soc | g/kg | 1.9–3.7 | 0.3–9.6 | 294 |
| 30..60cm | ph.h2o | pH | 7.2–7.6 | 6.2–8.3 | 294 |
| 60..100cm | clay | % | 23–30 | 6–45 | 294 |
| 60..100cm | sand | % | 39–51 | 10–81 | 294 |
| 60..100cm | silt | % | 24–32 | 6–52 | 294 |
| 60..100cm | bd.core | kg/m3 | 1500–1670 | 1240–1870 | 294 |
| 60..100cm | soc | g/kg | 1.3–3.2 | 0.3–7.7 | 294 |
| 60..100cm | ph.h2o | pH | 7.2–7.6 | 6.4–8.4 | 294 |
