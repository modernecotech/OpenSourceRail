# Onitsha civil soil screening

333 route/station sample locations; 320 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 320 |
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 320 |
| granular-density-and-groundwater-tests | 225 |

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
| 0..30cm | clay | % | 24–36 | 7–50 | 320 |
| 0..30cm | sand | % | 41–62 | 15–91 | 320 |
| 0..30cm | silt | % | 12–25 | 0–38 | 320 |
| 0..30cm | bd.core | kg/m3 | 1050–1480 | 730–1620 | 320 |
| 0..30cm | soc | g/kg | 5.3–15.5 | 1.7–34 | 320 |
| 0..30cm | ph.h2o | pH | 5.1–6.1 | 4.6–6.9 | 320 |
| 30..60cm | clay | % | 26–39 | 7–51 | 320 |
| 30..60cm | sand | % | 40–62 | 17–93 | 320 |
| 30..60cm | silt | % | 10–23 | 0–38 | 320 |
| 30..60cm | bd.core | kg/m3 | 1120–1510 | 660–1680 | 320 |
| 30..60cm | soc | g/kg | 2.9–11.1 | 0.8–38.6 | 320 |
| 30..60cm | ph.h2o | pH | 5.2–6.1 | 4.6–7.1 | 320 |
| 60..100cm | clay | % | 28–39 | 5–54 | 320 |
| 60..100cm | sand | % | 36–61 | 12–93 | 320 |
| 60..100cm | silt | % | 10–24 | 0–39 | 320 |
| 60..100cm | bd.core | kg/m3 | 1190–1510 | 590–1700 | 320 |
| 60..100cm | soc | g/kg | 2.8–12.8 | 0.6–49.1 | 320 |
| 60..100cm | ph.h2o | pH | 5.2–6.2 | 4.6–7.3 | 320 |
