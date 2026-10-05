# Galle civil soil screening

133 route/station sample locations; 129 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 129 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 129 |
| granular-density-and-groundwater-tests | 114 |
| organic-content-and-compressibility-tests | 68 |
| silt-moisture-frost-and-erosion-review | 22 |

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
| 0..30cm | clay | % | 27–36 | 9–50 | 129 |
| 0..30cm | sand | % | 37–53 | 10–88 | 129 |
| 0..30cm | silt | % | 20–28 | 0–48 | 129 |
| 0..30cm | bd.core | kg/m3 | 370–1180 | 100–1510 | 129 |
| 0..30cm | soc | g/kg | 8–73.1 | 3.1–211.3 | 129 |
| 0..30cm | ph.h2o | pH | 5.1–5.9 | 4.2–7.1 | 129 |
| 30..60cm | clay | % | 28–38 | 7–51 | 129 |
| 30..60cm | sand | % | 35–50 | 6–91 | 129 |
| 30..60cm | silt | % | 22–29 | 0–49 | 129 |
| 30..60cm | bd.core | kg/m3 | 390–1250 | 100–1560 | 129 |
| 30..60cm | soc | g/kg | 4.8–57.8 | 1.1–127.3 | 129 |
| 30..60cm | ph.h2o | pH | 5.1–6 | 4.3–7.2 | 129 |
| 60..100cm | clay | % | 29–39 | 7–52 | 129 |
| 60..100cm | sand | % | 32–48 | 4–88 | 129 |
| 60..100cm | silt | % | 22–30 | 0–50 | 129 |
| 60..100cm | bd.core | kg/m3 | 400–1290 | 100–1620 | 129 |
| 60..100cm | soc | g/kg | 5–47.4 | 1.6–168.1 | 129 |
| 60..100cm | ph.h2o | pH | 5.2–6.2 | 4.4–7.5 | 129 |
