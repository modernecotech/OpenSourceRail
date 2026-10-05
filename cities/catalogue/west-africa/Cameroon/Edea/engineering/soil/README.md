# Edea civil soil screening

22 route/station sample locations; 16 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 16 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 16 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 28–33 | 16–44 | 16 |
| 0..30cm | sand | % | 38–44 | 19–69 | 16 |
| 0..30cm | silt | % | 27–30 | 12–44 | 16 |
| 0..30cm | bd.core | kg/m3 | 1010–1100 | 740–1360 | 16 |
| 0..30cm | soc | g/kg | 12.2–21.5 | 5.9–38.3 | 16 |
| 0..30cm | ph.h2o | pH | 5.5–5.8 | 4.3–7 | 16 |
| 30..60cm | clay | % | 29–35 | 15–48 | 16 |
| 30..60cm | sand | % | 37–45 | 16–69 | 16 |
| 30..60cm | silt | % | 25–30 | 6–50 | 16 |
| 30..60cm | bd.core | kg/m3 | 1060–1190 | 710–1480 | 16 |
| 30..60cm | soc | g/kg | 6.2–10.2 | 2.9–17.5 | 16 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.3–7 | 16 |
| 60..100cm | clay | % | 29–36 | 15–49 | 16 |
| 60..100cm | sand | % | 35–46 | 11–67 | 16 |
| 60..100cm | silt | % | 25–31 | 8–50 | 16 |
| 60..100cm | bd.core | kg/m3 | 1130–1230 | 710–1510 | 16 |
| 60..100cm | soc | g/kg | 5.4–6.7 | 2.3–15.8 | 16 |
| 60..100cm | ph.h2o | pH | 5.6–5.8 | 4.4–7 | 16 |
