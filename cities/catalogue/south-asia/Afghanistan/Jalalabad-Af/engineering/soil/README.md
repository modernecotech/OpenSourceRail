# Jalalabad-Af civil soil screening

197 route/station sample locations; 195 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 150 |
| granular-density-and-groundwater-tests | 143 |
| silt-moisture-frost-and-erosion-review | 29 |

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
| 0..30cm | clay | % | 19–25 | 6–37 | 195 |
| 0..30cm | sand | % | 44–53 | 14–77 | 195 |
| 0..30cm | silt | % | 27–33 | 12–51 | 195 |
| 0..30cm | bd.core | kg/m3 | 1360–1480 | 1090–1650 | 195 |
| 0..30cm | soc | g/kg | 3.8–6.5 | 1.6–14.8 | 195 |
| 0..30cm | ph.h2o | pH | 7.4–8.1 | 6.4–8.6 | 195 |
| 30..60cm | clay | % | 20–26 | 7–38 | 195 |
| 30..60cm | sand | % | 42–52 | 15–81 | 195 |
| 30..60cm | silt | % | 27–33 | 9–49 | 195 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1250–1770 | 195 |
| 30..60cm | soc | g/kg | 2.6–4 | 1–8.7 | 195 |
| 30..60cm | ph.h2o | pH | 7.4–8.2 | 6.6–8.9 | 195 |
| 60..100cm | clay | % | 20–27 | 7–39 | 195 |
| 60..100cm | sand | % | 42–52 | 14–82 | 195 |
| 60..100cm | silt | % | 28–33 | 8–52 | 195 |
| 60..100cm | bd.core | kg/m3 | 1510–1630 | 1290–1880 | 195 |
| 60..100cm | soc | g/kg | 2–3.1 | 0.4–7.5 | 195 |
| 60..100cm | ph.h2o | pH | 7.5–8.3 | 6.2–9 | 195 |
