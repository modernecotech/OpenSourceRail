# Naivasha civil soil screening

72 route/station sample locations; 72 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 72 |
| granular-density-and-groundwater-tests | 11 |

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
| 0..30cm | clay | % | 31–39 | 17–50 | 72 |
| 0..30cm | sand | % | 31–47 | 10–73 | 72 |
| 0..30cm | silt | % | 22–30 | 7–46 | 72 |
| 0..30cm | bd.core | kg/m3 | 1220–1370 | 1040–1570 | 72 |
| 0..30cm | soc | g/kg | 4.9–19.4 | 2.5–38.7 | 72 |
| 0..30cm | ph.h2o | pH | 6.4–7.2 | 5.5–8.1 | 72 |
| 30..60cm | clay | % | 31–40 | 15–50 | 72 |
| 30..60cm | sand | % | 31–47 | 11–71 | 72 |
| 30..60cm | silt | % | 21–30 | 6–45 | 72 |
| 30..60cm | bd.core | kg/m3 | 1250–1430 | 1050–1640 | 72 |
| 30..60cm | soc | g/kg | 4.2–9.3 | 2.1–16.3 | 72 |
| 30..60cm | ph.h2o | pH | 6.6–7.4 | 5.7–8.2 | 72 |
| 60..100cm | clay | % | 31–39 | 15–51 | 72 |
| 60..100cm | sand | % | 32–48 | 12–76 | 72 |
| 60..100cm | silt | % | 21–29 | 4–45 | 72 |
| 60..100cm | bd.core | kg/m3 | 1230–1460 | 1000–1680 | 72 |
| 60..100cm | soc | g/kg | 3–6.4 | 1.4–12 | 72 |
| 60..100cm | ph.h2o | pH | 6.7–7.5 | 5.5–8.5 | 72 |
