# Chittagong civil soil screening

3,272 route/station sample locations; 3,262 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3262 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 3262 |
| granular-density-and-groundwater-tests | 2808 |
| organic-content-and-compressibility-tests | 1362 |
| silt-moisture-frost-and-erosion-review | 193 |

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
| 0..30cm | clay | % | 24–34 | 7–49 | 3262 |
| 0..30cm | sand | % | 35–52 | 6–83 | 3262 |
| 0..30cm | silt | % | 23–32 | 5–51 | 3262 |
| 0..30cm | bd.core | kg/m3 | 670–1070 | 330–1500 | 3262 |
| 0..30cm | soc | g/kg | 7.7–48.1 | 1.7–139.3 | 3262 |
| 0..30cm | ph.h2o | pH | 5.7–6.3 | 4.4–7.9 | 3262 |
| 30..60cm | clay | % | 23–35 | 4–50 | 3262 |
| 30..60cm | sand | % | 33–52 | 1–85 | 3262 |
| 30..60cm | silt | % | 23–34 | 3–54 | 3262 |
| 30..60cm | bd.core | kg/m3 | 800–1160 | 390–1600 | 3262 |
| 30..60cm | soc | g/kg | 5.3–33.8 | 0.8–104.6 | 3262 |
| 30..60cm | ph.h2o | pH | 5.9–6.7 | 4.8–8 | 3262 |
| 60..100cm | clay | % | 23–35 | 5–51 | 3262 |
| 60..100cm | sand | % | 34–51 | 2–85 | 3262 |
| 60..100cm | silt | % | 24–34 | 3–54 | 3262 |
| 60..100cm | bd.core | kg/m3 | 820–1190 | 190–1630 | 3262 |
| 60..100cm | soc | g/kg | 4.5–24.3 | 0.9–205.4 | 3262 |
| 60..100cm | ph.h2o | pH | 6.1–6.9 | 4.7–8.1 | 3262 |
