# Hoima civil soil screening

133 route/station sample locations; 133 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 133 |
| fine-soil-plasticity-and-shrink-swell-tests | 133 |
| granular-density-and-groundwater-tests | 78 |

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
| 0..30cm | clay | % | 33–49 | 18–57 | 133 |
| 0..30cm | sand | % | 23–51 | 9–77 | 133 |
| 0..30cm | silt | % | 16–28 | 3–40 | 133 |
| 0..30cm | bd.core | kg/m3 | 1110–1250 | 890–1450 | 133 |
| 0..30cm | soc | g/kg | 11.2–27.6 | 5.8–46 | 133 |
| 0..30cm | ph.h2o | pH | 5.6–6.1 | 4.9–7 | 133 |
| 30..60cm | clay | % | 35–51 | 18–60 | 133 |
| 30..60cm | sand | % | 22–51 | 7–81 | 133 |
| 30..60cm | silt | % | 14–28 | 0–39 | 133 |
| 30..60cm | bd.core | kg/m3 | 1170–1270 | 950–1530 | 133 |
| 30..60cm | soc | g/kg | 6.1–13.7 | 2.8–20.9 | 133 |
| 30..60cm | ph.h2o | pH | 5.5–6.1 | 4.8–7.1 | 133 |
| 60..100cm | clay | % | 36–51 | 17–61 | 133 |
| 60..100cm | sand | % | 21–50 | 5–80 | 133 |
| 60..100cm | silt | % | 14–28 | 0–39 | 133 |
| 60..100cm | bd.core | kg/m3 | 1180–1300 | 970–1580 | 133 |
| 60..100cm | soc | g/kg | 5.5–7.9 | 2.1–14.3 | 133 |
| 60..100cm | ph.h2o | pH | 5.5–6.1 | 4.8–7.1 | 133 |
