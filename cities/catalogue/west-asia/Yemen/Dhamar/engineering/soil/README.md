# Dhamar civil soil screening

131 route/station sample locations; 131 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 131 |
| granular-density-and-groundwater-tests | 129 |

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
| 0..30cm | clay | % | 25–31 | 8–47 | 131 |
| 0..30cm | sand | % | 38–55 | 11–83 | 131 |
| 0..30cm | silt | % | 19–31 | 0–48 | 131 |
| 0..30cm | bd.core | kg/m3 | 1350–1440 | 1140–1650 | 131 |
| 0..30cm | soc | g/kg | 4.1–8.9 | 2.5–16.1 | 131 |
| 0..30cm | ph.h2o | pH | 7.3–8 | 6.1–9.1 | 131 |
| 30..60cm | clay | % | 26–32 | 7–49 | 131 |
| 30..60cm | sand | % | 38–54 | 10–88 | 131 |
| 30..60cm | silt | % | 19–30 | 0–48 | 131 |
| 30..60cm | bd.core | kg/m3 | 1390–1440 | 1120–1670 | 131 |
| 30..60cm | soc | g/kg | 3.6–6.2 | 1.6–12.9 | 131 |
| 30..60cm | ph.h2o | pH | 7.4–8 | 6.3–9.1 | 131 |
| 60..100cm | clay | % | 27–33 | 7–50 | 131 |
| 60..100cm | sand | % | 39–53 | 10–87 | 131 |
| 60..100cm | silt | % | 19–29 | 0–47 | 131 |
| 60..100cm | bd.core | kg/m3 | 1420–1460 | 1150–1730 | 131 |
| 60..100cm | soc | g/kg | 2.4–4.6 | 0.7–10.3 | 131 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.3–9 | 131 |
