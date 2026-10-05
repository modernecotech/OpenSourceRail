# Mbale civil soil screening

168 route/station sample locations; 168 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 74 |
| fine-soil-plasticity-and-shrink-swell-tests | 168 |
| granular-density-and-groundwater-tests | 58 |
| organic-content-and-compressibility-tests | 1 |
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
| 0..30cm | clay | % | 27–34 | 16–44 | 168 |
| 0..30cm | sand | % | 35–46 | 16–70 | 168 |
| 0..30cm | silt | % | 25–32 | 10–52 | 168 |
| 0..30cm | bd.core | kg/m3 | 1020–1190 | 790–1430 | 168 |
| 0..30cm | soc | g/kg | 10.7–28.1 | 5–50.9 | 168 |
| 0..30cm | ph.h2o | pH | 6.1–6.6 | 5.4–7.6 | 168 |
| 30..60cm | clay | % | 29–37 | 15–49 | 168 |
| 30..60cm | sand | % | 34–49 | 14–74 | 168 |
| 30..60cm | silt | % | 21–31 | 3–54 | 168 |
| 30..60cm | bd.core | kg/m3 | 1100–1220 | 850–1430 | 168 |
| 30..60cm | soc | g/kg | 7.4–12.5 | 2.7–20.8 | 168 |
| 30..60cm | ph.h2o | pH | 6–6.7 | 5.3–7.6 | 168 |
| 60..100cm | clay | % | 29–38 | 13–51 | 168 |
| 60..100cm | sand | % | 31–49 | 8–78 | 168 |
| 60..100cm | silt | % | 20–32 | 2–55 | 168 |
| 60..100cm | bd.core | kg/m3 | 1120–1230 | 850–1440 | 168 |
| 60..100cm | soc | g/kg | 5.2–9.4 | 2.3–30.6 | 168 |
| 60..100cm | ph.h2o | pH | 6–6.7 | 5.2–7.6 | 168 |
