# Raqqa civil soil screening

86 route/station sample locations; 85 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 84 |
| granular-density-and-groundwater-tests | 64 |

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
| 0..30cm | clay | % | 20–27 | 7–38 | 85 |
| 0..30cm | sand | % | 40–53 | 15–79 | 85 |
| 0..30cm | silt | % | 26–33 | 12–47 | 85 |
| 0..30cm | bd.core | kg/m3 | 1410–1460 | 1240–1610 | 85 |
| 0..30cm | soc | g/kg | 2.7–6.8 | 1.1–13.8 | 85 |
| 0..30cm | ph.h2o | pH | 7.9–8.2 | 7.4–8.7 | 85 |
| 30..60cm | clay | % | 22–29 | 5–42 | 85 |
| 30..60cm | sand | % | 39–53 | 14–83 | 85 |
| 30..60cm | silt | % | 26–33 | 7–48 | 85 |
| 30..60cm | bd.core | kg/m3 | 1420–1550 | 1230–1750 | 85 |
| 30..60cm | soc | g/kg | 1.9–3.8 | 0.3–7.4 | 85 |
| 30..60cm | ph.h2o | pH | 8–8.4 | 7.2–9.2 | 85 |
| 60..100cm | clay | % | 23–29 | 5–43 | 85 |
| 60..100cm | sand | % | 39–53 | 15–83 | 85 |
| 60..100cm | silt | % | 25–32 | 4–49 | 85 |
| 60..100cm | bd.core | kg/m3 | 1420–1610 | 1230–1920 | 85 |
| 60..100cm | soc | g/kg | 1.7–2.4 | 0.5–5.1 | 85 |
| 60..100cm | ph.h2o | pH | 8.1–8.6 | 7–9.4 | 85 |
