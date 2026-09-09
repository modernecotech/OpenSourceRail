# Tete civil soil screening

79 route/station sample locations; 66 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 7 |
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 66 |
| granular-density-and-groundwater-tests | 65 |

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
| 0..30cm | clay | % | 23–35 | 8–47 | 66 |
| 0..30cm | sand | % | 42–63 | 22–88 | 66 |
| 0..30cm | silt | % | 14–23 | 0–36 | 66 |
| 0..30cm | bd.core | kg/m3 | 1350–1550 | 1180–1680 | 66 |
| 0..30cm | soc | g/kg | 3.8–9.1 | 1.6–16.3 | 66 |
| 0..30cm | ph.h2o | pH | 6.3–7 | 5.2–8 | 66 |
| 30..60cm | clay | % | 27–37 | 8–49 | 66 |
| 30..60cm | sand | % | 42–59 | 23–87 | 66 |
| 30..60cm | silt | % | 15–21 | 0–39 | 66 |
| 30..60cm | bd.core | kg/m3 | 1430–1550 | 1250–1690 | 66 |
| 30..60cm | soc | g/kg | 2.4–4.7 | 0.8–8.2 | 66 |
| 30..60cm | ph.h2o | pH | 6.6–7.3 | 5.7–8.1 | 66 |
| 60..100cm | clay | % | 28–38 | 9–51 | 66 |
| 60..100cm | sand | % | 42–57 | 20–88 | 66 |
| 60..100cm | silt | % | 15–22 | 0–41 | 66 |
| 60..100cm | bd.core | kg/m3 | 1470–1560 | 1270–1730 | 66 |
| 60..100cm | soc | g/kg | 2.3–3.7 | 0.9–8.1 | 66 |
| 60..100cm | ph.h2o | pH | 6.8–7.5 | 5.7–8.5 | 66 |
